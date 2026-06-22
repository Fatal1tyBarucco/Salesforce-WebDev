---
description: "Find and fix test coverage gaps to reach 100%"
---

Find files below 100% coverage and add targeted tests:

```bash
# 1. Check current coverage
pytest --cov=src --cov-report=term-missing -q 2>&1 | grep -E "src/.*[0-9]+%"

# 2. For each file below 100%, identify uncovered lines from the report
# 3. Read the uncovered source lines to understand what needs testing
# 4. Add targeted tests in automation/tests/test_coverage_gaps.py
# 5. Run full suite to verify
pytest -n auto -q && pytest --cov=src --cov-report=term-missing -q 2>&1 | grep -E "^TOTAL|src/.*\.py"
```

For each gap, add a minimal test that exercises the specific uncovered code path. Don't over-test — one focused test per gap.

After fixing, commit and push with message: "test: improve coverage for [file] from X% to Y%"
