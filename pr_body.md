## Summary

Removes push triggers from 5 workflows that were causing bot commit loops (Class C workflow design failures).

## Changes

| Workflow | Issue | Fix |
|----------|-------|-----|
| `scheduled-pipeline.yml` | Push trigger + dummy job causing empty runs | Removed push trigger, removed dummy job, removed `if: github.event_name != 'push'` checks |
| `ai-triage.yml` | Push trigger on `no-push-trigger` branch | Removed push trigger entirely |
| `ci-repair.yml` | **Bot loop**: Python Quality (push) → CI Repair (workflow_run) → commit → push → Python Quality... | Removed push trigger, removed dummy job, fixed job conditions to not check `event_name != 'push'` |
| `ai-pr-review.yml` | Push trigger + dummy job | Removed push trigger, removed dummy job |
| `opencode.yml` | Push trigger + dummy job | Removed push trigger, removed dummy job |

## Root Cause Analysis

The CI Repair workflow was the most critical - it triggers on `workflow_run` of Python Quality. When Python Quality runs on push to main (or any branch), CI Repair runs, commits fixes, and pushes - which triggers Python Quality again, creating an infinite loop.

All 5 workflows had the same pattern: a push trigger on a non-existent branch `no-push-trigger` with a dummy job that did nothing. This was likely an attempt to prevent the loop but didn't work because the workflow still ran on push.

## Validation

Local quality gates all pass:
- `uv lock --check` ✅
- `uv run ruff check .` ✅  
- `uv run black --check --diff .` ✅
- `uv run mypy src/ --ignore-missing-imports` ✅
- `uv run pytest tests/ -q` ✅ (2370 passed, 3 skipped)

## Note on OpenCode

The OpenCode workflow has a Class B (transient infrastructure) failure where the `anomalyco/opencode/github` action hits GitHub API rate limits when fetching the latest version. This is a third-party action issue and would require forking the action to add retry logic.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>