---
description: "Fix failing tests, run quality gate, commit, push, and verify remote CI"
---

Fix failing tests or coverage drops, then ship the fix:

```bash
# 1. Run tests to identify failures
pytest tests/ -q 2>&1 | tail -15

# 2. Fix the root cause (don't just skip/exclude failing tests)

# 3. Run full quality gate
ruff check . && black --check . && mypy src/ && pytest tests/ -q

# 4. Stage, commit, and push
git add -A && git commit -m "fix: <describe root cause>" && git push

# 5. Verify remote CI passes
gh run list --limit 5
gh run watch <RUN_ID> --exit-status
```

Rules:
- Never skip or exclude failing tests — fix the root cause
- All quality checks must pass before committing
- Verify remote CI status after push
- Update AGENTS.md and MEMORY.md if the fix reveals stale references
