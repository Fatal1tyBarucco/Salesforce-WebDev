---
description: "Run full quality gate: format check, lint, typecheck, and parallel tests"
---

Run the following checks in order. Report pass/fail for each step.

```bash
black --check . && ruff check . && mypy src/ && pytest -n auto --cov=src --cov-report=term-missing -q 2>&1
```

If any step fails, stop and report the error. If all pass, report "All checks passed".

Notes:
- `black --check` reports violations without modifying files (matches CI behavior)
- `pytest -n auto` runs tests in parallel using all available CPU cores
- `--cov` shows coverage report at the end
