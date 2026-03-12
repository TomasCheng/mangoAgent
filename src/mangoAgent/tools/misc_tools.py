from mangoAgent.core.todo_manager import TodoManager
from mangoAgent.core.context_manager import ContextManager

def get_misc_tools(todo: TodoManager, ctx: ContextManager):
    tools = [
        {
            "name": "TodoWrite",
            "description": "Update task tracking list.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {"type": "string"},
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                },
                                "activeForm": {"type": "string"},
                            },
                            "required": ["content", "status", "activeForm"],
                        },
                    },
                },
                "required": ["items"],
            },
        },
        {
            "name": "compress",
            "description": "Manually compress conversation context.",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

    handlers = {
        "TodoWrite": lambda **kw: todo.update(kw["items"]),
        "compress": lambda **kw: "Compressing...",
    }

    return tools, handlers
