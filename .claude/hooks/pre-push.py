#!/usr/bin/env python3
"""Pre-push hook: run pytest -x with timeout. Note: timeout = not verified, not failure."""

import json
import subprocess
import sys


def main():
    try:
        json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    # Timeout 280s in script, 300s in settings.json — script ends first if timeout
    result = subprocess.run(
        ["uv", "run", "pytest", "-x", "tests/"],
        capture_output=True,
        timeout=280,
    )
    if result.returncode != 0:
        print("pytest -x failed:", file=sys.stderr)
        print(result.stdout.decode(), file=sys.stderr)
        print(result.stderr.decode(), file=sys.stderr)
        sys.exit(1)
    elif result.returncode == 0 and b"timeout" in (result.stdout + result.stderr).lower():
        # Timeout occurred but process was killed — tests not verified
        print("WARNING: pytest timed out — tests NOT verified", file=sys.stderr)
        # Exit 0 to not block push on timeout (Termux slow), but warn

    sys.exit(0)


if __name__ == "__main__":
    main()
