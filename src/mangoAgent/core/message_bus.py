import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

class MessageBus:
    def __init__(self, inbox_dir: Path):
        self.inbox_dir = inbox_dir
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def send(
        self, 
        sender: str, 
        to: str, 
        content: str,
        msg_type: str = "message", 
        extra: Optional[Dict[str, Any]] = None
    ) -> str:
        msg = {
            "type": msg_type, 
            "from": sender, 
            "content": content,
            "timestamp": time.time()
        }
        if extra:
            msg.update(extra)
        
        with open(self.inbox_dir / f"{to}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(msg) + "\n")
        
        return f"Sent {msg_type} to {to}"

    def read_inbox(self, name: str) -> List[Dict[str, Any]]:
        path = self.inbox_dir / f"{name}.jsonl"
        if not path.exists():
            return []
        
        msgs = [
            json.loads(l) 
            for l in path.read_text(encoding="utf-8").strip().splitlines() 
            if l
        ]
        path.write_text("", encoding="utf-8")
        return msgs

    def broadcast(self, sender: str, content: str, names: List[str]) -> str:
        count = 0
        for n in names:
            if n != sender:
                self.send(sender, n, content, "broadcast")
                count += 1
        return f"Broadcast to {count} teammates"
