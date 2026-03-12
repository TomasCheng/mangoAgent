from mangoAgent.core.subagent import run_subagent
from anthropic import Anthropic

def get_subagent_tools(client: Anthropic, model: str):
    tools = [
        {
            "name": "task",
            "description": "Spawn a subagent for isolated exploration or work.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "agent_type": {
                        "type": "string",
                        "enum": ["Explore", "general-purpose"],
                    },
                },
                "required": ["prompt"],
            },
        },
    ]

    handlers = {
        "task": lambda **kw: run_subagent(
            client, 
            model, 
            kw["prompt"], 
            kw.get("agent_type", "Explore")
        ),
    }

    return tools, handlers
