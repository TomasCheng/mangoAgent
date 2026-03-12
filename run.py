#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# --- Dev Mode Configuration ---
# Set MANGO_DEV_MODE=1 to tell config.py to use the local workspace
os.environ["MANGO_DEV_MODE"] = "1"
# Set project root explicitly to avoid relative path guessing issues
os.environ["MANGO_PROJECT_ROOT"] = str(Path(__file__).parent.resolve())

# Add src to sys.path so we can run without installing (optional but helpful for quick dev)
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

try:
    from mangoAgent.__main__ import main
except ImportError:
    print("Error: mangoAgent package not found. Did you run 'pip install -e .' ?")
    sys.exit(1)

if __name__ == "__main__":
    main()
