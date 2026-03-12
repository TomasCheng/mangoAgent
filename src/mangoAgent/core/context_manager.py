import json
import time
from pathlib import Path
from anthropic import Anthropic

class ContextManager:
    def __init__(self, client: Anthropic, model: str, transcript_dir: Path):
        self.client = client
        self.model = model
        self.transcript_dir = transcript_dir
        self.transcript_dir.mkdir(parents=True, exist_ok=True)
        self.token_threshold = 100000

    def estimate_tokens(self, messages: list) -> int:
        return len(json.dumps(messages, default=str)) // 4

    def microcompact(self, messages: list):
        indices = []
        for i, msg in enumerate(messages):
            if msg["role"] == "user" and isinstance(msg.get("content"), list):
                for part in msg["content"]:
                    if isinstance(part, dict) and part.get("type") == "tool_result":
                        indices.append(part)
        
        if len(indices) <= 3:
            return
            
        for part in indices[:-3]:
            if isinstance(part.get("content"), str) and len(part["content"]) > 100:
                part["content"] = "[cleared]"

    def auto_compact(self, messages: list) -> list:
        path = self.transcript_dir / f"transcript_{int(time.time())}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for msg in messages:
                f.write(json.dumps(msg, default=str) + "\n")
                
        conv_text = json.dumps(messages, default=str)[:80000]
        resp = self.client.messages.create(
            model=self.model,
            messages=[{
                "role": "user", 
                "content": f"Summarize for continuity:\n{conv_text}"
            }],
            max_tokens=2000,
        )
        summary = resp.content[0].text
        
        return [
            {
                "role": "user", 
                "content": f"[Compressed. Transcript: {path}]\n{summary}"
            },
            {
                "role": "assistant", 
                "content": "Understood. Continuing with summary context."
            },
        ]
