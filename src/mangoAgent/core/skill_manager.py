import re
from pathlib import Path
from typing import Dict, Any, List

class SkillManager:
    def __init__(self, skill_dirs: List[Path]):
        self.skill_dirs = skill_dirs
        self.skills: Dict[str, Any] = {}
        self.reload()

    def reload(self):
        """Reload all skills from all configured directories."""
        self.skills.clear()
        
        # Iterate through directories in order. Later paths overwrite earlier ones if duplicate names exist.
        for d in self.skill_dirs:
            if d.exists():
                for f in sorted(d.rglob("SKILL.md")):
                    try:
                        text = f.read_text(encoding="utf-8")
                        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
                        meta, body = {}, text
                        
                        if match:
                            for line in match.group(1).strip().splitlines():
                                if ":" in line:
                                    k, v = line.split(":", 1)
                                    meta[k.strip()] = v.strip()
                            body = match.group(2).strip()
                        
                        name = meta.get("name", f.parent.name)
                        # Add source path for debugging/info
                        meta["_source_path"] = str(f)
                        self.skills[name] = {"meta": meta, "body": body}
                    except Exception as e:
                        print(f"Warning: Failed to load skill from {f}: {e}")

    def descriptions(self) -> str:
        if not self.skills:
            return "(no skills)"
        return "\n".join(
            f"  - {n}: {s['meta'].get('description', '-')} (from {s['meta'].get('_source_path')})" 
            for n, s in sorted(self.skills.items())
        )

    def load(self, name: str) -> str:
        # Auto-reload if skill is not found, to support newly created skills
        if name not in self.skills:
            self.reload()
            
        s = self.skills.get(name)
        if not s:
            return f"Error: Unknown skill '{name}'. Available: {', '.join(self.skills.keys())}"
        return f"<skill name=\"{name}\">\n{s['body']}\n</skill>"
