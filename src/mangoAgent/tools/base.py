import subprocess
from mangoAgent.config import WORKDIR
from mangoAgent.utils.fs import safe_path

def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=WORKDIR,
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"

def run_read(path: str, limit: int = None, line_numbers: bool = False) -> str:
    try:
        lines = safe_path(path).read_text(encoding="utf-8").splitlines()
        if line_numbers:
            lines = [f"{i+1:4} | {line}" for i, line in enumerate(lines)]
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"

def run_replace_lines(path: str, start_line: int, end_line: int, new_content: str) -> str:
    """Replace a range of lines (1-based, inclusive) with new content."""
    try:
        fp = safe_path(path)
        lines = fp.read_text(encoding="utf-8").splitlines(keepends=True)
        
        # Adjust 1-based indexing to 0-based
        start_idx = max(0, start_line - 1)
        end_idx = min(len(lines), end_line)
        
        if start_idx >= len(lines) and start_idx > 0:
             return f"Error: Start line {start_line} is beyond file length {len(lines)}"

        new_lines = new_content.splitlines(keepends=True)
        # Ensure new_content has a newline if it's meant to be a full line
        if new_content and not new_content.endswith('\n'):
             new_content += '\n'
             new_lines = new_content.splitlines(keepends=True)

        lines[start_idx:end_idx] = new_lines
        fp.write_text("".join(lines), encoding="utf-8")
        return f"Replaced lines {start_line}-{end_line} in {path}"
    except Exception as e:
        return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} bytes"
    except Exception as e:
        return f"Error: {e}"

def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        c = fp.read_text(encoding="utf-8")
        if old_text not in c:
            return f"Error: Text not found in {path}"
        fp.write_text(c.replace(old_text, new_text, 1), encoding="utf-8")
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"

def run_patch(path: str, patch_string: str) -> str:
    """Apply a unified diff patch to a file."""
    try:
        fp = safe_path(path)
        # Create a temporary patch file
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.patch') as tmp:
            tmp.write(patch_string)
            tmp_path = tmp.name
        
        try:
            # Use 'patch' command if available
            r = subprocess.run(
                ["patch", "-u", str(fp), "-i", tmp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if r.returncode == 0:
                return f"Successfully applied patch to {path}"
            else:
                return f"Error applying patch: {r.stdout}\n{r.stderr}"
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        return f"Error: {e}"

TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command in the current workspace (blocking).",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
    {
        "name": "read_file",
        "description": "Read file contents. Set line_numbers=true to see line numbers for precise editing.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "limit": {"type": "integer"},
                "line_numbers": {"type": "boolean"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "replace_lines",
        "description": "Replace a range of lines in a file by line numbers (1-based, inclusive). Best for precise edits.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
                "new_content": {"type": "string"},
            },
            "required": ["path", "start_line", "end_line", "new_content"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "edit_file",
        "description": "Replace exact text in file. Note: if text occurs multiple times, only the first is replaced.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text"],
        },
    },
    {
        "name": "patch_file",
        "description": "Apply a Unified Diff patch to a file. Highly robust for complex edits.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "patch_string": {"type": "string"},
            },
            "required": ["path", "patch_string"],
        },
    },
]

HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit"), kw.get("line_numbers", False)),
    "replace_lines": lambda **kw: run_replace_lines(kw["path"], kw["start_line"], kw["end_line"], kw["new_content"]),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "patch_file": lambda **kw: run_patch(kw["path"], kw["patch_string"]),
}
