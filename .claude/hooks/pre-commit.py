#!/usr/bin/env python3
"""Pre-commit hook: run ruff check, ruff format --check, mypy, and uv lock --check."""

import json
import subprocess
import sys


def run_cmd(cmd, desc, timeout=60):
    result = subprocess.run(cmd, capture_output=True, timeout=timeout)
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

    # Run ruff format --check
    if not run_cmd(["uv", "run", "ruff", "format", "--check", "."], "ruff format --check"):
        sys.exit(1)

    # Run mypy (longer timeout for large codebase)
    if not run_cmd(["uv", "run", "mypy", "src/", "--ignore-missing-imports"], "mypy", timeout=120):
        sys.exit(1)

    # Run uv lock --check (gate from CLAUDE.md)
    if not run_cmd(["uv", "lock", "--check"], "uv lock --check"):
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
