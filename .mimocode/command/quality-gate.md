---
description: "Run full quality gate: format, lint, typecheck, and test"
---

Run the following checks in order. Report pass/fail for each step.

```bash
black . 2>/dev/null && ruff check . && mypy automation/ src/ && pytest automation/tests/ -q 2>&1
```

If any step fails, stop and report the error. If all pass, report "All checks passed".
