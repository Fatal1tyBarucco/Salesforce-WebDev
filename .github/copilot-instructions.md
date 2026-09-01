# Copilot Custom Instructions — Salesforce-WebDev

Custom instructions for GitHub Copilot agents working in the Salesforce-WebDev repository.

## Project Summary

ETL pipeline for extracting, classifying, and versioning Salesforce Release Notes. Python 3.13, BeautifulSoup, Playwright, OpenAI/Google GenAI, Pydantic, FastAPI.

## Build & Test Commands

```bash
uv sync --extra dev             # Install dependencies
uv run pytest                   # Run tests
uv run ruff check .             # Lint
uv run black --check .          # Format check
uv run mypy src/                # Type check
uv run pre-commit run --all-files
```

**Always run before committing**:
1. `uv run ruff check .`
2. `uv run black --check .`
3. `uv run mypy src/`
4. `uv run pytest --cov=src --cov-fail-under=95`

## Critical Conventions

### Dependencies
- **Never** add `pytest-syrupy` to `pyproject.toml` (it would downgrade pytest from 9.x to 8.4.2)
- Install `syrupy` via `uv pip install "syrupy>=4.9.0,<5"` — not via pyproject.toml
- Python constraint: `>=3.13,<3.14` — use `uv run` (system may have 3.14 but uv pins 3.13)

### Code Quality
- Use `datetime.now()` — never `datetime.utcnow()` (deprecated)
- `mypy strict = true` is enforced for all files including tests
- `mypy_path = "stubs"` — put type stubs in `stubs/`
- `pytest-timeout` is set to 120s globally via `addopts`

### Testing
- Factory module: `tests/factories.py` (8 functions: `make_release`, `make_topic_node`, `make_topic_tree`, `make_toc_html`, `make_feature_impact_text`, `make_feature_impact_html`, `make_release_metadata`, `make_mock_html_response`)
- Snapshots: `tests/__snapshots__/test_snapshot.ambr` (syrupy)
- `tests/conftest.py` stubs `openai` and `google` to avoid import hangs

### Commit Messages
Conventional Commits: `feat(scope): ...`, `fix(scope): ...`, `refactor(scope): ...`, `test(scope): ...`, `docs(scope): ...`, `chore(scope): ...`

## GitHub Project Board

Project: https://github.com/users/Fatal1tyBarucco/projects/5
- Project ID: `PVT_kwDOCQOIIc4BiKNM`
- Status field ID: `PVTSSF_lADOCQOIIc4BiKNMzhhDPfg`

Status options:
- `Backlog` → `a368d611`
- `In Progress` → `3808f0ce`
- `In Review` → `10aa434a`
- `Done` → `f87ad5a7`

Update the board when: starting work (In Progress), opening a PR (In Review), after merge (Done).

## Known Issues — Do Not Re-Introduce

- `NOTIFICATION_DIGEST.md` is a test artifact — do not commit
- `src/auto_healing/` and `docs/auto-healing/` are untracked leftovers from the develop branch — do not add to git
- All GitHub Actions must use pinned SHA (not tags like `@v5`)
- Pre-existing mypy warnings in `tests/test_llm_service.py` helper fixtures — do not fix those
