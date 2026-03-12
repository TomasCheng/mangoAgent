from mangoAgent.core.task_manager import TaskManager

def get_task_tools(tasks: TaskManager):
    tools = [
        {
            "name": "task_create",
            "description": "Create a new task on the shared task board.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["subject"],
            },
        },
        {
            "name": "task_list",
            "description": "List all tasks with status, owner, and worktree binding.",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "task_get",
            "description": "Get task details by ID.",
            "input_schema": {
                "type": "object",
                "properties": {"task_id": {"type": "integer"}},
                "required": ["task_id"],
            },
        },
        {
            "name": "task_update",
            "description": "Update task status or owner.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed"],
                    },
                    "owner": {"type": "string"},
                },
                "required": ["task_id"],
            },
        },
        {
            "name": "task_bind_worktree",
            "description": "Bind a task to a worktree name.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "integer"},
                    "worktree": {"type": "string"},
                    "owner": {"type": "string"},
                },
                "required": ["task_id", "worktree"],
            },
        },
    ]

    handlers = {
        "task_create": lambda **kw: tasks.create(kw["subject"], kw.get("description", "")),
        "task_list": lambda **kw: tasks.list_all(),
        "task_get": lambda **kw: tasks.get(kw["task_id"]),
        "task_update": lambda **kw: tasks.update(kw["task_id"], kw.get("status"), kw.get("owner")),
        "task_bind_worktree": lambda **kw: tasks.bind_worktree(kw["task_id"], kw["worktree"], kw.get("owner", "")),
    }

    return tools, handlers
