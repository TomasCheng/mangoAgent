import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List
from anthropic import Anthropic

from mangoAgent.core.message_bus import MessageBus
from mangoAgent.core.task_manager import TaskManager
from mangoAgent.config import WORKDIR
from mangoAgent.tools.base import HANDLERS as BASE_HANDLERS

class TeammateManager:
    def __init__(
        self, 
        team_dir: Path, 
        bus: MessageBus, 
        task_mgr: TaskManager, 
        client: Anthropic, 
        model: str
    ):
        self.team_dir = team_dir
        self.team_dir.mkdir(exist_ok=True)
        self.bus = bus
        self.task_mgr = task_mgr
        self.client = client
        self.model = model
        self.config_path = team_dir / "config.json"
        self.config = self._load()
        self.threads: Dict[str, threading.Thread] = {}
        
        # Teammate tools definition
        self.tools = [
            {"name": "bash", "description": "Run command.", "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
            {"name": "read_file", "description": "Read file.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
            {"name": "write_file", "description": "Write file.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
            {"name": "edit_file", "description": "Edit file.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
            {"name": "send_message", "description": "Send message.", "input_schema": {"type": "object", "properties": {"to": {"type": "string"}, "content": {"type": "string"}}, "required": ["to", "content"]}},
            {"name": "idle", "description": "Signal no more work.", "input_schema": {"type": "object", "properties": {}}},
            {"name": "claim_task", "description": "Claim task by ID.", "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"]}},
        ]

    def _load(self) -> Dict[str, Any]:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text(encoding="utf-8"))
        return {"team_name": "default", "members": []}

    def _save(self):
        self.config_path.write_text(json.dumps(self.config, indent=2), encoding="utf-8")

    def _find(self, name: str) -> Dict[str, Any]:
        for m in self.config["members"]:
            if m["name"] == name: 
                return m
        return None

    def spawn(self, name: str, role: str, prompt: str) -> str:
        member = self._find(name)
        if member:
            if member["status"] not in ("idle", "shutdown"):
                return f"Error: '{name}' is currently {member['status']}"
            member["status"] = "working"
            member["role"] = role
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
        
        self._save()
        t = threading.Thread(
            target=self._loop, 
            args=(name, role, prompt), 
            daemon=True
        )
        t.start()
        self.threads[name] = t
        return f"Spawned '{name}' (role: {role})"

    def _set_status(self, name: str, status: str):
        member = self._find(name)
        if member:
            member["status"] = status
            self._save()

    def list_all(self) -> str:
        if not self.config["members"]: 
            return "No teammates."
        lines = [f"Team: {self.config['team_name']}"]
        for m in self.config["members"]:
            lines.append(f"  {m['name']} ({m['role']}): {m['status']}")
        return "\n".join(lines)

    def member_names(self) -> List[str]:
        return [m["name"] for m in self.config["members"]]

    def _loop(self, name: str, role: str, prompt: str):
        team_name = self.config["team_name"]
        sys_prompt = (
            f"You are '{name}', role: {role}, team: {team_name}, at {WORKDIR}. "
            f"Use idle when done with current work. You may auto-claim tasks."
        )
        messages = [{"role": "user", "content": prompt}]
        
        while True:
            # -- WORK PHASE --
            for _ in range(50):
                inbox = self.bus.read_inbox(name)
                for msg in inbox:
                    if msg.get("type") == "shutdown_request":
                        self._set_status(name, "shutdown")
                        return
                    messages.append({"role": "user", "content": json.dumps(msg)})
                
                try:
                    response = self.client.messages.create(
                        model=self.model, 
                        system=sys_prompt, 
                        messages=messages,
                        tools=self.tools, 
                        max_tokens=8000
                    )
                except Exception:
                    self._set_status(name, "shutdown")
                    return
                
                messages.append({"role": "assistant", "content": response.content})
                
                if response.stop_reason != "tool_use":
                    break
                
                results = []
                idle_requested = False
                
                for block in response.content:
                    if block.type == "tool_use":
                        if block.name == "idle":
                            idle_requested = True
                            output = "Entering idle phase."
                        elif block.name == "claim_task":
                            # Note: S12 TaskManager bind_worktree is complex.
                            # For simplified teammate claiming, we might need a simpler update
                            # or just set owner field.
                            output = self.task_mgr.update(block.input["task_id"], owner=name, status="in_progress")
                        elif block.name == "send_message":
                            output = self.bus.send(name, block.input["to"], block.input["content"])
                        else:
                            # Re-use base handlers
                            handler = BASE_HANDLERS.get(block.name)
                            if handler:
                                try:
                                    output = handler(**block.input)
                                except Exception as e:
                                    output = f"Error: {e}"
                            else:
                                output = "Unknown tool"
                                
                        print(f"  [{name}] {block.name}: {str(output)[:120]}")
                        results.append({
                            "type": "tool_result", 
                            "tool_use_id": block.id, 
                            "content": str(output)
                        })
                
                messages.append({"role": "user", "content": results})
                if idle_requested:
                    break
            
            # -- IDLE PHASE --
            self._set_status(name, "idle")
            resume = False
            # Poll interval 5s, timeout 60s
            for _ in range(12): 
                time.sleep(5)
                inbox = self.bus.read_inbox(name)
                if inbox:
                    for msg in inbox:
                        if msg.get("type") == "shutdown_request":
                            self._set_status(name, "shutdown")
                            return
                        messages.append({"role": "user", "content": json.dumps(msg)})
                    resume = True
                    break
                
                # Auto-claim logic (simplified for now)
                # In real S12, tasks might need worktree binding.
                # Here we just look for pending tasks without owner.
                # We need to list all tasks to check.
                # Accessing TaskManager internal dir for glob is safe here since we are in same process/module context.
                # But using TaskManager public methods is better.
                # ... implementing simple auto-claim ...
                
            if not resume:
                self._set_status(name, "shutdown")
                return
            
            self._set_status(name, "working")
