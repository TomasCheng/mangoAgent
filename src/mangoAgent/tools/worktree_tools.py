from mangoAgent.core.worktree_manager import WorktreeManager
from mangoAgent.core.event_bus import EventBus

def get_worktree_tools(worktrees: WorktreeManager, events: EventBus):
    tools = [
        {
            "name": "worktree_create",
            "description": "Create a git worktree and optionally bind it to a task.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "task_id": {"type": "integer"},
                    "base_ref": {"type": "string"},
                },
                "required": ["name"],
            },
        },
        {
            "name": "worktree_list",
            "description": "List worktrees tracked in .worktrees/index.json.",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "worktree_status",
            "description": "Show git status for one worktree.",
            "input_schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "worktree_run",
            "description": "Run a shell command in a named worktree directory.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "command": {"type": "string"},
                },
                "required": ["name", "command"],
            },
        },
        {
            "name": "worktree_remove",
            "description": "Remove a worktree and optionally mark its bound task completed.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "force": {"type": "boolean"},
                    "complete_task": {"type": "boolean"},
                },
                "required": ["name"],
            },
        },
        {
            "name": "worktree_keep",
            "description": "Mark a worktree as kept in lifecycle state without removing it.",
            "input_schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "worktree_events",
            "description": "List recent worktree/task lifecycle events from .worktrees/events.jsonl.",
            "input_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer"}},
            },
        },
    ]

    handlers = {
        "worktree_create": lambda **kw: worktrees.create(kw["name"], kw.get("task_id"), kw.get("base_ref", "HEAD")),
        "worktree_list": lambda **kw: worktrees.list_all(),
        "worktree_status": lambda **kw: worktrees.status(kw["name"]),
        "worktree_run": lambda **kw: worktrees.run(kw["name"], kw["command"]),
        "worktree_keep": lambda **kw: worktrees.keep(kw["name"]),
        "worktree_remove": lambda **kw: worktrees.remove(kw["name"], kw.get("force", False), kw.get("complete_task", False)),
        "worktree_events": lambda **kw: events.list_recent(kw.get("limit", 20)),
    }

    return tools, handlers
