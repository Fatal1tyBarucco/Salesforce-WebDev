#!/usr/bin/env python3
"""Pre-push hook: run pytest -x."""

import json
import subprocess
import sys


def main():
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    result = subprocess.run(
        ["uv", "run", "pytest", "-x", "tests/"],
        capture_output=True,
        timeout=120,
    )
    if result.returncode != 0:
        print("pytest -x failed:", file=sys.stderr)
        print(result.stdout.decode(), file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
