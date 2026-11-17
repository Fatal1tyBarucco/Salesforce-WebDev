#!/usr/bin/env python3
"""Pre-commit hook: run ruff check, ruff format --check, and mypy."""

import json
import subprocess
import sys


def run_cmd(cmd, desc):
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    if result.returncode != 0:
        print(f"{desc} failed:", file=sys.stderr)
        print(result.stdout.decode(), file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        return False
    return True


def main():
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Run ruff check
    if not run_cmd(["uv", "run", "ruff", "check", "."], "ruff check"):
        sys.exit(1)

    # Run ruff format --check (replaces black --check)
    if not run_cmd(["uv", "run", "ruff", "format", "--check", "."], "ruff format --check"):
        sys.exit(1)

    # Run mypy
    if not run_cmd(["uv", "run", "mypy", "src/", "--ignore-missing-imports"], "mypy"):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
