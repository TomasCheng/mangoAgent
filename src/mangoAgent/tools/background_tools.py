from mangoAgent.core.background_manager import BackgroundManager

def get_background_tools(bg: BackgroundManager):
    tools = [
        {
            "name": "background_run",
            "description": "Run command in background thread.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "timeout": {"type": "integer"},
                },
                "required": ["command"],
            },
        },
        {
            "name": "check_background",
            "description": "Check background task status.",
            "input_schema": {
                "type": "object",
                "properties": {"task_id": {"type": "string"}},
            },
        },
    ]

    handlers = {
        "background_run": lambda **kw: bg.run(kw["command"], kw.get("timeout", 120)),
        "check_background": lambda **kw: bg.check(kw.get("task_id")),
    }

    return tools, handlers
