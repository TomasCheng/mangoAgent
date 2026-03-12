from pathlib import Path
import subprocess
from mangoAgent.config import WORKDIR

def detect_repo_root(cwd: Path) -> Path | None:
    """Return git repo root if cwd is inside a repo, else None."""
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if r.returncode != 0:
            return None
        root = Path(r.stdout.strip())
        return root if root.exists() else None
    except Exception:
        return None

def safe_path(p: str) -> Path:
    """Safely resolve a path relative to the workspace root."""
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path
