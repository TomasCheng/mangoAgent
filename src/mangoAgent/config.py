import os
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# --- Dynamic WORKDIR Configuration ---
# 1. Dev Mode (via run.py): Uses 'work-space' inside project root
# 2. CLI Mode (via mango): Uses current working directory

if os.environ.get("MANGO_DEV_MODE"):
    # Development Mode
    project_root = os.environ.get("MANGO_PROJECT_ROOT")
    if project_root:
        BASE_DIR = Path(project_root)
    else:
        # Fallback: Guess relative to this file (less reliable if installed)
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        
    WORKDIR = BASE_DIR / "work-space"
    
    # Load .env from project root in dev mode
    load_dotenv(BASE_DIR / ".env", override=True)
else:
    # CLI Mode
    WORKDIR = Path.cwd()
    
    # Load configuration in priority order:
    # 1. ~/.mango/config (Global)
    # 2. Current directory .env (Project specific)
    
    global_config = Path.home() / ".mango" / "config"
    if global_config.exists():
        load_dotenv(global_config, override=True)
        
    load_dotenv(WORKDIR / ".env", override=True)

if not WORKDIR.exists():
    try:
        WORKDIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass 

# --- Configuration Management ---
# We now support loading JSON configs in addition to .env variables.
# Order of precedence (Higher overwrites lower):
# 1. Default Hardcoded Values
# 2. Global Config (~/.mango/config.json)
# 3. Project Config (WORKDIR/.mango/config.json) - Not yet standard but good to support
# 4. Environment Variables (.env) - Highest priority for sensitive keys usually, 
#    but for structural config, maybe JSON is better?
#    Let's stick to: JSON provides structural defaults, ENV overrides specific keys.

DEFAULTS = {
    "system_prompt_override": None,
    "model_override": None,
    "auto_compact_threshold": 100000,
    "log_level": "INFO",
    "use_reasoning": True  # Default to True for reasoning capabilities
}

def load_json_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Filter out null values to avoid overwriting defaults with null
        return {k: v for k, v in data.items() if v is not None}
    except Exception as e:
        print(f"Warning: Failed to load config from {path}: {e}")
        return {}

def get_config() -> dict:
    """
    Load and merge configuration from all sources.
    Returns a dict with the final configuration.
    """
    config = DEFAULTS.copy()
    
    # 1. Global JSON Config
    global_json = Path.home() / ".mango" / "config.json"
    config.update(load_json_config(global_json))
    
    # 2. Project JSON Config (Optional, if we want per-project settings)
    # project_json = WORKDIR / ".mango" / "config.json"
    # config.update(load_json_config(project_json))
    
    # 3. Environment Variables (Map specific env vars to config keys)
    # This allows .env to override JSON config for critical values
    if os.getenv("MODEL_ID"):
        config["model_override"] = os.getenv("MODEL_ID")
    
    if os.getenv("USE_REASONING"):
        val = os.getenv("USE_REASONING").lower()
        config["use_reasoning"] = val in ("true", "1", "yes", "on")
        
    # Add other env mappings as needed
    
    return config

# Load config once at module level? Or per call?
# Per call allows dynamic updates if file changes, but slightly slower.
# Let's do per call for get_model/get_client where it matters.

def get_client():
    """
    Get configured Anthropic client, automatically handling DeepSeek and other compatible interfaces.
    """
    base_url = os.getenv("ANTHROPIC_BASE_URL")
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    
    # If base_url is set, usually need to clear potentially conflicting default environment variables
    if base_url:
        os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
        
    return Anthropic(
        api_key=api_key,
        base_url=base_url
    )

def get_model():
    """
    Get model ID.
    Priority:
    1. Env var MODEL_ID (loaded from .env)
    2. Config JSON 'model_override'
    3. Logic based on 'use_reasoning' config:
       - If use_reasoning is True -> deepseek-reasoner
       - Else -> deepseek-chat
    """
    # Check Env first (highest priority for simple overrides)
    env_model = os.environ.get("MODEL_ID")
    if env_model:
        return env_model
        
    # Check JSON config
    conf = get_config()
    if conf.get("model_override"):
        return conf["model_override"]
    
    # Default logic based on reasoning preference
    if conf.get("use_reasoning", True):
        return "deepseek-reasoner"
        
    return "deepseek-chat"
