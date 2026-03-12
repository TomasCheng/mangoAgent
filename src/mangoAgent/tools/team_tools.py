from mangoAgent.core.teammate_manager import TeammateManager
from mangoAgent.core.message_bus import MessageBus

def get_team_tools(team: TeammateManager, bus: MessageBus):
    tools = [
        {
            "name": "spawn_teammate",
            "description": "Spawn a persistent autonomous teammate.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "role": {"type": "string"},
                    "prompt": {"type": "string"},
                },
                "required": ["name", "role", "prompt"],
            },
        },
        {
            "name": "list_teammates",
            "description": "List all teammates.",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "send_message",
            "description": "Send a message to a teammate.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "content": {"type": "string"},
                    "msg_type": {"type": "string"},
                },
                "required": ["to", "content"],
            },
        },
        {
            "name": "read_inbox",
            "description": "Read and drain the lead's inbox.",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "broadcast",
            "description": "Send message to all teammates.",
            "input_schema": {
                "type": "object",
                "properties": {"content": {"type": "string"}},
                "required": ["content"],
            },
        },
        {
            "name": "shutdown_request",
            "description": "Request a teammate to shut down.",
            "input_schema": {
                "type": "object",
                "properties": {"teammate": {"type": "string"}},
                "required": ["teammate"],
            },
        },
    ]

    # Helper for shutdown request
    def handle_shutdown_request(teammate: str) -> str:
        import uuid
        req_id = str(uuid.uuid4())[:8]
        bus.send("lead", teammate, "Please shut down.", "shutdown_request", {"request_id": req_id})
        return f"Shutdown request {req_id} sent to '{teammate}'"

    handlers = {
        "spawn_teammate": lambda **kw: team.spawn(kw["name"], kw["role"], kw["prompt"]),
        "list_teammates": lambda **kw: team.list_all(),
        "send_message": lambda **kw: bus.send("lead", kw["to"], kw["content"], kw.get("msg_type", "message")),
        "read_inbox": lambda **kw: str(bus.read_inbox("lead")),
        "broadcast": lambda **kw: bus.broadcast("lead", kw["content"], team.member_names()),
        "shutdown_request": lambda **kw: handle_shutdown_request(kw["teammate"]),
    }

    return tools, handlers
