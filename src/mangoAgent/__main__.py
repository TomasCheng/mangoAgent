#!/usr/bin/env python3
import sys
import json
import os
from pathlib import Path

# No more sys.path hacks needed if installed properly

from mangoAgent.config import get_client, get_model, WORKDIR
from mangoAgent.utils.fs import detect_repo_root
from mangoAgent.utils.logger import setup_logger
from mangoAgent.utils.tui import tui

# Core Managers
from mangoAgent.core.event_bus import EventBus
from mangoAgent.core.task_manager import TaskManager
from mangoAgent.core.worktree_manager import WorktreeManager
from mangoAgent.core.agent import Agent
from mangoAgent.core.todo_manager import TodoManager
from mangoAgent.core.skill_manager import SkillManager
from mangoAgent.core.background_manager import BackgroundManager
from mangoAgent.core.message_bus import MessageBus
from mangoAgent.core.teammate_manager import TeammateManager
from mangoAgent.core.context_manager import ContextManager

# Tools
from mangoAgent.tools.base import TOOLS as BASE_TOOLS, HANDLERS as BASE_HANDLERS
from mangoAgent.tools.task_tools import get_task_tools
from mangoAgent.tools.worktree_tools import get_worktree_tools
from mangoAgent.tools.skill_tools import get_skill_tools
from mangoAgent.tools.background_tools import get_background_tools
from mangoAgent.tools.team_tools import get_team_tools
from mangoAgent.tools.misc_tools import get_misc_tools
from mangoAgent.tools.subagent_tools import get_subagent_tools

from mangoAgent.core.memory_manager import MemoryManager
from mangoAgent.tools.memory_tools import get_memory_tools

def main():
    # If in dev mode, we might want to print where we are running
    if os.environ.get("MANGO_DEV_MODE"):
        print(f"Dev Mode Active. WORKDIR: {WORKDIR}")

    real_repo_root = detect_repo_root(WORKDIR)

    # Ensure workspace exists
    if not WORKDIR.exists():
        WORKDIR.mkdir(parents=True, exist_ok=True)
        
    # Setup Logger
    # For CLI mode, we might want to hide logs or put them in a standard place
    # But sticking to WORKDIR/.logs for now is consistent
    log_dir = WORKDIR / ".logs"
    log_dir.mkdir(exist_ok=True)
    logger = setup_logger(log_dir / "agent.log")
    logger.info("MangoAgent Starting...")

    # Initialize Core Components
    client = get_client()
    model = get_model()
    
    # 1. Base Infrastructure (All data stored in WORKDIR)
    # Adjust paths to be cleaner if WORKDIR is CWD
    # E.g. .mango/tasks, .mango/worktrees
    # But to minimize refactoring risk now, keep flat structure
    events = EventBus(WORKDIR / ".worktrees" / "events.jsonl")
    tasks = TaskManager(WORKDIR / ".tasks")
    
    worktrees = WorktreeManager(WORKDIR, tasks, events)
    
    # 2. Enhanced Capabilities
    todo = TodoManager()
    
    # Configure Skill Directories
    # Logic:
    # 1. Built-in (always)
    # 2. Global User Config (~/.mango/skills)
    # 3. Project Config (WORKDIR/.mango/skills)
    # 4. Workspace Local (WORKDIR/skills)
    
    skill_dirs = [
        Path(__file__).parent / "skills",              # Built-in
        Path.home() / ".mango" / "skills",             # Global
        WORKDIR / ".mango" / "skills",                 # Project Hidden
        WORKDIR / "skills"                             # Project Visible
    ]
    
    # Filter out duplicates or non-existent (SkillManager handles non-existent)
    skills = SkillManager(skill_dirs)
    
    bg = BackgroundManager()
    bus = MessageBus(WORKDIR / ".team" / "inbox")
    
    # Memory Manager
    # CLI Mode: user_memory should be global (~/.mango/user_memory.json)
    # Project memory should be local (WORKDIR/.mango/project_memory.json)
    
    if os.environ.get("MANGO_DEV_MODE"):
         # Keep old behavior for dev mode compatibility if needed, OR align with new standard
         # Let's align with new standard but map to dev paths
         # Actually, the logic below works fine for both if configured right
         user_mem_path = WORKDIR.parent / ".mango" / "user_memory.json" 
         # In dev mode, WORKDIR is project/work-space, so parent is project root.
    else:
         # CLI Mode: 
         user_mem_path = Path.home() / ".mango" / "user_memory.json"

    project_mem_path = WORKDIR / ".mango" / "project_memory.json"

    memory = MemoryManager(
        user_memory_path=user_mem_path,
        project_memory_path=project_mem_path
    )
    
    team = TeammateManager(WORKDIR / ".team", bus, tasks, client, model)
    ctx = ContextManager(client, model, WORKDIR / ".transcripts")

    if not worktrees.git_available:
        pass

    # Initialize Tools
    task_tools, task_handlers = get_task_tools(tasks)
    worktree_tools, worktree_handlers = get_worktree_tools(worktrees, events)
    skill_tools, skill_handlers = get_skill_tools(skills)
    bg_tools, bg_handlers = get_background_tools(bg)
    team_tools, team_handlers = get_team_tools(team, bus)
    misc_tools, misc_handlers = get_misc_tools(todo, ctx)
    subagent_tools, subagent_handlers = get_subagent_tools(client, model)
    memory_tools, memory_handlers = get_memory_tools(memory)

    all_tools = (
        BASE_TOOLS + 
        task_tools + 
        worktree_tools + 
        skill_tools + 
        bg_tools + 
        team_tools + 
        misc_tools + 
        subagent_tools +
        memory_tools
    )
    
    all_handlers = {
        **BASE_HANDLERS, 
        **task_handlers, 
        **worktree_handlers,
        **skill_handlers,
        **bg_handlers,
        **team_handlers,
        **misc_handlers,
        **subagent_handlers,
        **memory_handlers
    }

    # System Prompt
    system_prompt = (
        f"You are a coding agent at {WORKDIR}. "
        "Use task + worktree tools for multi-task work. "
        "For parallel or risky changes: create tasks, allocate worktree lanes, "
        "run commands in those lanes, then choose keep/remove for closeout. "
        "Use worktree_events when you need lifecycle visibility.\n"
        "Prefer task_create/task_update/task_list for multi-step work. "
        "Use TodoWrite for short checklists.\n"
        "Use task (subagent) for delegation. Use load_skill for specialized knowledge.\n"
        f"Skills available: {skills.descriptions()}\n"
        f"{memory.compile_prompt()}"
    )

    agent = Agent(
        client, 
        model, 
        system_prompt, 
        all_tools, 
        all_handlers,
        todo_mgr=todo,
        context_mgr=ctx,
        bg_mgr=bg,
        bus_mgr=bus,
        logger=logger,
        tui=tui
    )

    # REPL Loop
    history = []
    tui.print_welcome()
    
    # Print mode info
    if os.environ.get("MANGO_DEV_MODE"):
        tui.print_system_message(f"Running in DEV MODE. Workspace: {WORKDIR}")
    else:
        tui.print_system_message(f"Running in CLI MODE. Workspace: {WORKDIR}")

    if not worktrees.git_available:
        tui.print_error("Workspace is not in a git repo. worktree_* tools will be unavailable.")
        
    while True:
        try:
            query = tui.input_prompt()
        except (EOFError, KeyboardInterrupt):
            break
            
        if query.strip().lower() in ("q", "exit"):
            break
        if query.strip() == "":
            continue
            
        # REPL Commands
        if query.strip() == "/compact":
            if history:
                tui.print_system_message("Compacting history...")
                history[:] = ctx.auto_compact(history)
            continue
            
        if query.strip() == "/tasks":
            print(tasks.list_all()) # Keep print for now or migrate to TUI
            continue
            
        if query.strip() == "/team":
            print(team.list_all())
            continue
            
        if query.strip() == "/inbox":
            print(json.dumps(bus.read_inbox("lead"), indent=2))
            continue

        history.append({"role": "user", "content": query})
        tui.print_user_message(query)
        
        try:
            agent.run(history)
        except Exception as e:
            tui.print_error(str(e))
            # raise e # Uncomment for debugging

if __name__ == "__main__":
    main()
