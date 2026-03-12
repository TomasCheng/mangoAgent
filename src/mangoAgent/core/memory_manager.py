import json
from pathlib import Path
from typing import List, Dict, Optional

class MemoryManager:
    """
    Manages long-term memories for the agent.
    - User Memory: Global preferences (e.g., ~/.mango/user_memory.json)
    - Project Memory: Project-specific context (e.g., .mango/project_memory.json)
    """
    def __init__(self, user_memory_path: Path, project_memory_path: Path):
        self.user_memory_path = user_memory_path
        self.project_memory_path = project_memory_path
        
        # Ensure directories exist
        self.user_memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.project_memory_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.user_memories = self._load(self.user_memory_path)
        self.project_memories = self._load(self.project_memory_path)

    def _load(self, path: Path) -> List[Dict]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _save(self, path: Path, memories: List[Dict]):
        path.write_text(json.dumps(memories, indent=2, ensure_ascii=False), encoding="utf-8")

    def remember(self, content: str, category: str = "general", scope: str = "project") -> str:
        """
        Store a new memory.
        scope: 'user' (global) or 'project' (local)
        """
        memory = {
            "content": content,
            "category": category,
            "timestamp": str(Path.cwd())  # simple timestamp/context
        }
        
        if scope == "user":
            self.user_memories.append(memory)
            self._save(self.user_memory_path, self.user_memories)
            return f"Stored global memory: {content}"
        else:
            self.project_memories.append(memory)
            self._save(self.project_memory_path, self.project_memories)
            return f"Stored project memory: {content}"

    def forget(self, index: int, scope: str = "project") -> str:
        """Delete a memory by index."""
        target = self.user_memories if scope == "user" else self.project_memories
        if 0 <= index < len(target):
            removed = target.pop(index)
            self._save(self.user_memory_path if scope == "user" else self.project_memory_path, target)
            return f"Forgot memory: {removed['content']}"
        return "Error: Invalid memory index"

    def list_all(self) -> str:
        lines = []
        if self.user_memories:
            lines.append("🧠 Global Memories (User):")
            for i, m in enumerate(self.user_memories):
                lines.append(f"  {i}. [{m['category']}] {m['content']}")
        
        if self.project_memories:
            lines.append("\n📁 Project Memories:")
            for i, m in enumerate(self.project_memories):
                lines.append(f"  {i}. [{m['category']}] {m['content']}")
                
        return "\n".join(lines) if lines else "(No memories yet)"

    def compile_prompt(self) -> str:
        """Generate a system prompt section containing all memories."""
        if not self.user_memories and not self.project_memories:
            return ""
            
        prompt = "\n\n<memory_bank>\n"
        if self.user_memories:
            prompt += "User Preferences:\n" + "\n".join(f"- {m['content']}" for m in self.user_memories) + "\n"
        if self.project_memories:
            prompt += "Project Context:\n" + "\n".join(f"- {m['content']}" for m in self.project_memories) + "\n"
        prompt += "</memory_bank>\n"
        return prompt
