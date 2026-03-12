from mangoAgent.core.memory_manager import MemoryManager

def get_memory_tools(memories: MemoryManager):
    tools = [
        {
            "name": "remember",
            "description": "Save a piece of knowledge, rule, or preference to long-term memory.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The fact/rule to remember."},
                    "category": {"type": "string", "description": "Tag (e.g., 'coding_style', 'architecture').", "default": "general"},
                    "scope": {"type": "string", "enum": ["user", "project"], "default": "project", "description": "'user' for global preferences, 'project' for this repo only."}
                },
                "required": ["content"],
            },
        },
        {
            "name": "list_memories",
            "description": "Show all stored memories.",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

    handlers = {
        "remember": lambda **kw: memories.remember(kw["content"], kw.get("category", "general"), kw.get("scope", "project")),
        "list_memories": lambda **kw: memories.list_all(),
    }

    return tools, handlers
