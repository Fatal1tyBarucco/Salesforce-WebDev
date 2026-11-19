#!/usr/bin/env python3
"""Post-tool-use hook: run ruff check --fix and ruff format on edited Python files."""

import json
import subprocess
import sys
from pathlib import Path


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    path = Path(file_path)
    if not path.exists():
        sys.exit(0)

    # Run ruff check --fix
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "--fix", str(path)],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        print(f"ruff check --fix failed: {result.stderr.decode()}", file=sys.stderr)

    # Run ruff format
    result = subprocess.run(
        ["uv", "run", "ruff", "format", str(path)],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 0:
        print(f"ruff format failed: {result.stderr.decode()}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
