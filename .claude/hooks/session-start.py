#!/usr/bin/env python3
"""SessionStart hook: show repo state and run gates."""

import json
import subprocess
import sys


def run_cmd(cmd, desc=None):
    result = subprocess.run(cmd, capture_output=True, timeout=60, shell=True)
    output = result.stdout.decode().strip()
    if output:
        print(output)
    if result.returncode != 0 and desc:
        print(f"{desc}: FAILED", file=sys.stderr)
    return result.returncode == 0


def main():
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    print("=== REPO STATE ===")
    run_cmd("git branch --show-current")
    run_cmd("git status --short")

    print("=== GATES ===")
    run_cmd("uv run ruff check . --quiet", "ruff")
    run_cmd("uv run ruff format --check . --quiet", "ruff format")
    run_cmd("uv run mypy src/ --ignore-missing-imports >/dev/null 2>&1", "mypy")


if __name__ == "__main__":
    main()
