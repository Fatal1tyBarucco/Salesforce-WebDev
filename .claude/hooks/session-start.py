#!/usr/bin/env python3
"""SessionStart hook: show repo state and run gates."""

import json
import subprocess
import sys


def run_cmd(cmd, desc=None):
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    output = result.stdout.decode().strip()
    if output:
        print(output)
    if result.returncode != 0 and desc:
        print(f"{desc}: FAILED", file=sys.stderr)
        if result.stderr:
            print(result.stderr.decode().strip(), file=sys.stderr)
    return result.returncode == 0


def main():
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        pass

    print("=== REPO STATE ===")
    run_cmd(["git", "branch", "--show-current"])
    run_cmd(["git", "status", "--short"])

    print("=== GATES ===")
    run_cmd(["uv", "run", "ruff", "check", "."], "ruff")
    run_cmd(["uv", "run", "ruff", "format", "--check", "."], "ruff format")
    run_cmd(["uv", "run", "mypy", "src/", "--ignore-missing-imports"], "mypy")


if __name__ == "__main__":
    main()
