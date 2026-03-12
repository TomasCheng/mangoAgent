import json
from anthropic import Anthropic
from mangoAgent.tools.base import HANDLERS as BASE_HANDLERS

def run_subagent(client: Anthropic, model: str, prompt: str, agent_type: str = "Explore") -> str:
    print(f"\033[36m[Subagent({agent_type})] Started with prompt: {prompt[:100]}...\033[0m")
    
    sub_tools = [
        {
            "name": "bash", 
            "description": "Run command.",
            "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}
        },
        {
            "name": "read_file", 
            "description": "Read file.",
            "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}
        },
    ]
    
    if agent_type != "Explore":
        sub_tools += [
            {
                "name": "write_file", 
                "description": "Write file.",
                "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}
            },
            {
                "name": "edit_file", 
                "description": "Edit file.",
                "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}
            },
        ]
        
    sub_handlers = {
        "bash": BASE_HANDLERS["bash"],
        "read_file": BASE_HANDLERS["read_file"],
        "write_file": BASE_HANDLERS["write_file"],
        "edit_file": BASE_HANDLERS["edit_file"],
    }
    
    sub_msgs = [{"role": "user", "content": prompt}]
    resp = None
    
    for i in range(30):
        print(f"\033[36m[Subagent] Step {i+1}...\033[0m")
        resp = client.messages.create(
            model=model, 
            messages=sub_msgs, 
            tools=sub_tools, 
            max_tokens=8000
        )
        sub_msgs.append({"role": "assistant", "content": resp.content})
        
        for block in resp.content:
            if block.type == "text":
                print(f"\033[34m[Subagent Assistant]:\033[0m {block.text}")

        if resp.stop_reason != "tool_use":
            break
            
        results = []
        for b in resp.content:
            if b.type == "tool_use":
                print(f"\033[33m[Subagent Tool]: {b.name}\033[0m")
                print(f"\033[33m[Input]: {json.dumps(b.input, indent=2, ensure_ascii=False)}\033[0m")
                
                h = sub_handlers.get(b.name, lambda **kw: "Unknown tool")
                try:
                    out = h(**b.input)
                except Exception as e:
                    out = f"Error: {e}"
                
                print(f"\033[32m[Result]: {str(out)[:200]}\033[0m")
                results.append({
                    "type": "tool_result", 
                    "tool_use_id": b.id, 
                    "content": str(out)[:50000]
                })
        sub_msgs.append({"role": "user", "content": results})
        
    print(f"\033[36m[Subagent] Finished.\033[0m")
    if resp:
        summary = "".join(b.text for b in resp.content if hasattr(b, "text")) or "(no summary)"
        return summary
    return "(subagent failed)"
