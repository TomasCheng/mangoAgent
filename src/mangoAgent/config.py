import os
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
    
    # Load .env from CWD if present (for user convenience)
    load_dotenv(WORKDIR / ".env", override=True)
    # Also try loading from ~/.mango/config if needed later

if not WORKDIR.exists():
    # Only create if it doesn't exist? Or let main handle it?
    # In CLI mode, we don't want to mkdir unless we are initializing.
    # But for now, let's stick to existing behavior: ensure it exists.
    # Wait, if I run `mango` in `/`, I can't mkdir.
    # Better to let main() handle critical failures or user confirmation.
    # But for now, to keep it simple and working:
    try:
        WORKDIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass # Will likely fail later if we can't write, but let it slide here.

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
    Get model ID, default to deepseek-chat.
    """
    return os.environ.get("MODEL_ID", "deepseek-chat")
