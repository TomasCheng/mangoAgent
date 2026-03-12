from mangoAgent.core.skill_manager import SkillManager

def get_skill_tools(skills: SkillManager):
    tools = [
        {
            "name": "load_skill",
            "description": "Load specialized knowledge by name.",
            "input_schema": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"],
            },
        },
        {
            "name": "list_skills",
            "description": "Refresh and list all available skills.",
            "input_schema": {"type": "object", "properties": {}},
        },
    ]

    handlers = {
        "load_skill": lambda **kw: skills.load(kw["name"]),
        "list_skills": lambda **kw: (skills.reload(), skills.descriptions())[1],
    }

    return tools, handlers
