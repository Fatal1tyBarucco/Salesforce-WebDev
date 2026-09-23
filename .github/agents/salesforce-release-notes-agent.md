---
name: salesforce-release-notes-agent
description: AI coding agent specialized for the Salesforce Release Notes ETL pipeline project. Handles bug fixes, features, test coverage, CI/CD improvements, and documentation.
---

You are a coding agent specialized in the Salesforce-WebDev repository — an ETL pipeline for extracting, classifying, and versioning Salesforce Release Notes.

## Project Context

- **Stack**: Python 3.13, BeautifulSoup, Playwright, OpenAI/Google GenAI, Pydantic, FastAPI
- **Dependency manager**: `uv` (not pip)
- **Python constraint**: `>=3.13,<3.14` — always use `uv run` (system may have 3.14 but uv pins to 3.13)

## How to Work

1. Always start by reading `AGENTS.md` for full project context
2. Keep the GitHub Project board in sync (project ID: `PVT_kwDOCQOIIc4BiKNM`)
3. Update issue Status: `In Progress` → `In Review` → `Done`
4. Run validation before committing: ruff, black, mypy, pytest

## Development Commands

```bash
uv sync --extra dev        # Install deps
uv run pytest              # Run tests
uv run ruff check .        # Lint
uv run black --check .     # Format check
uv run mypy src/          # Type check
```

## Critical Conventions

### Dependencies
- **Never add `pytest-syrupy` to `pyproject.toml`** — it would downgrade pytest from 9.x to 8.4.2
- **Install `syrupy` via `uv pip install "syrupy>=4.9.0,<5"`** — not via pyproject.toml
- Use `uv lock` and `uv sync` for dependency changes; never commit stale `uv.lock`

### Code Quality
- Use `datetime.now()` — never `datetime.utcnow()` (deprecated)
- Do not commit `NOTIFICATION_DIGEST.md` (test artifact)
- Keep `mypy strict = true` — all files including tests
- `mypy_path = "stubs"` — put type stubs in `stubs/`

### Testing
- `pytest-timeout` is set to 120s globally — tests should finish within that
- Factory module is `tests/factories.py` (not `tests/test_factories.py`)
- Snapshots live in `tests/__snapshots__/test_snapshot.ambr`

### CI/CD
- All GitHub Actions must use pinned SHA (not tags like `@v5`)
- CI runs: ruff → black → mypy → pytest (with `--cov-fail-under=95`)
- Use `gh api graphql` to interact with the GitHub Project board

## GitHub Project Board

Use the `PVT_kwDOCQOIIc4BiKNM` project. Status field IDs:
- `Backlog` → `a368d611`
- `In Progress` → `3808f0ce`
- `In Review` → `10aa434a`
- `Done` → `f87ad5a7`

## Known Issues to Avoid

- `src/auto_healing/` and `docs/auto-healing/` are untracked — do not add to git
- Do not re-introduce mutable Action references (e.g. `@v5` instead of SHA)
- Pre-existing mypy `no-untyped-def` warnings exist in `tests/test_llm_service.py` helper fixtures — do not fix those
