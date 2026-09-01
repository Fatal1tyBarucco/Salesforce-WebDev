# AGENTS.md - AI Agent Coding Guide (Salesforce-WebDev)

This guide is for AI coding agents working in the `Salesforce-WebDev` repository (`salesforce-release-notes`).

## Project Snapshot

Salesforce-WebDev is an ETL pipeline for extracting, classifying, and versioning Salesforce Release Notes, built with Python (3.13), BeautifulSoup, Playwright, OpenAI/Google GenAI, Pydantic, and FastAPI.

Dependency management and virtual environments are handled by `uv`. The project runs under **Python 3.13** via `uv` (system default may be 3.14, but `uv` pins to 3.13 via `requires-python = ">=3.13,<3.14"`).

## Setup & Development Commands

- **Install dependencies:** `uv sync --extra dev`
- **Install Playwright browsers:** `uv run playwright install chromium`
- **Run tests:** `uv run pytest` (or `uv run pytest tests/`)
- **Run lint / formatting check:**
  - `uv run ruff check .`
  - `uv run black --check .`
- **Run typecheck:** `uv run mypy src/`
- **Run all pre-commit checks manually:** `uv run pre-commit run --all-files`

## Stack & Conventions

- Python `>=3.13,<3.14` (via `uv`; system may have 3.14, but lock file pins to 3.13).
- `pytest-timeout` is configured globally via `addopts = "--timeout=120"` (120s per test).
- Code style: Black (line length 100) and Ruff linting.
- Async code: Asyncio (`asyncio_mode = "auto"` in pytest).
- Commit messages: Conventional Commits (`feat(scope): ...`, `fix(scope): ...`, `refactor(scope): ...`, `test(scope): ...`, `docs(scope): ...`, `chore(scope): ...`).

## Repository Map

- `src/` - Core ETL pipeline, scrapers, classification services.
- `tests/` - Pytest test suite.
- `stubs/` - Type stubs for mypy (`mypy_path = "stubs"`).
- `docs/` - Documentation (MkDocs).
- `k8s/` - Kubernetes manifests and deployment configs.
- `src/auto_healing/` - **Untracked** directory (exists locally from develop branch; deleted in main, pending cleanup).
- `docs/auto-healing/` - **Untracked** directory (same as above).

## Validation Checklist

Before finishing changes, always run:
1. `uv run ruff check .`
2. `uv run black --check .`
3. `uv run mypy src/`
4. `uv run pytest --cov=src --cov-fail-under=95 --cov-report=term-missing --cov-report=xml:coverage.xml`

## Key Files & Decisions

### Dependency constraints

- `pyproject.toml` specifies `requires-python = ">=3.13,<3.14"`.
- `pytest>=8.0.0,<10` — pytest 9.x in `uv.lock` (`pytest==9.1.1`).
- **Do not** add `pytest-syrupy` to `pyproject.toml` — it would downgrade pytest to 8.4.2.
- `syrupy` is installed via `uv pip install "syrupy>=4.9.0,<5"` in the CI tests job (after `uv sync`), NOT via pyproject.toml.
- `pytest-timeout>=2.4.0` is in dev dependencies; `--timeout=120` is set globally via `addopts`.

### mypy

- `mypy strict = true` is in `pyproject.toml` (applied to all files including tests).
- `mypy_path = "stubs"` — stub modules go in `stubs/`.
- CI runs `uv run mypy src/ --ignore-missing-imports --pretty` — the `--ignore-missing-imports` flag is intentional to suppress import errors for optional deps.
- Stub module: `stubs/syrupy/__init__.pyi` (with `py.typed`) provides `SnapshotAssertion` and `snapshot()` for mypy type checking.

### Tests

- `tests/conftest.py` stubs `openai` and `google` in `sys.modules` to avoid import hangs during test collection.
- `tests/test_snapshot.py` and `tests/test_llm_service.py` may have pre-existing mypy errors in helper fixtures — do not introduce new errors.
- Factory module: `tests/factories.py` (8 functions: `make_release`, `make_topic_node`, `make_topic_tree`, `make_toc_html`, `make_feature_impact_text`, `make_feature_impact_html`, `make_release_metadata`, `make_mock_html_response`).
- Snapshots in `tests/__snapshots__/test_snapshot.ambr` (syrupy, 9 snapshots).

### Documentation

- Spec reference: `newPrompt.md` (untracked file, reference only).
- Source selectors: `docs/SOURCE_SCHEMA.md` (CSS selectors, ARIA attributes, feature impact format).
- Enhanced search: `docs/assets/javascripts/enhanced_search.js` + `docs/assets/stylesheets/enhanced_search.css` + `docs/maintenance/enhanced-search.md`.
- MkDocs configured in `mkdocs.yml` with i18n `[en, pt]` and extra assets.

### Known issues (do not re-introduce)

- `NOTIFICATION_DIGEST.md` is an artifact from test runs — do not commit.
- `datetime.utcnow()` was deprecated — use `datetime.now()` instead.
- `src/auto_healing/` and `docs/auto-healing/` are untracked leftovers from the develop branch — do not add to git without justification.

## GitHub Project Integration

This repository is linked to a GitHub Project for tracking work:

- **Project:** [Salesforce Release Notes](https://github.com/users/Fatal1tyBarucco/projects/5)
- **Project ID:** `PVT_kwDOCQOIIc4BiKNM`
- **Owner:** `Fatal1tyBarucco`
- **Repo ID:** `R_kgDORbgJew`

### Status field (single-select)

| Status | Meaning |
|--------|---------|
| `Backlog` | Tasks not yet started |
| `In Progress` | Agent is actively working |
| `In Review` | PR open, awaiting review / CI checks |
| `Done` | Merged and closed |

Option IDs (GraphQL):
- Backlog → `a368d611`
- In Progress → `3808f0ce`
- In Review → `10aa434a`
- Done → `f87ad5a7`

### When to update the Project

Every agent **must** keep the board in sync:

1. Start work on an issue → set Status to `In Progress`
2. Open a PR → set linked issue's Status to `In Review`
3. PR merged → set Status to `Done`
4. New task identified → add Draft Issue with Status `Backlog`

### CLI commands

Requires `project` + `read:project` scopes. Verify:

```bash
gh auth status
```

```bash
gh project item-list 5 --owner Fatal1tyBarucco
gh project view 5 --owner Fatal1tyBarucco
```

### GraphQL examples

**Add existing issue to project:**

```bash
ISSUE_ID=$(gh issue view <N> --json id -q .id)
gh api graphql -f query="
  mutation {
    addProjectV2ItemById(input: {
      projectId: \"PVT_kwDOCQOIIc4BiKNM\"
      contentId: \"$ISSUE_ID\"
    }) { item { id } }
  }"
```

**Set item status:**

```bash
gh api graphql -f query="
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: \"PVT_kwDOCQOIIc4BiKNM\"
      itemId: \"<PROJECT_ITEM_ID>\"
      fieldId: \"PVTSSF_lADOCQOIIc4BiKNMzhhDPfg\"
      value: { singleSelectOptionId: \"<OPTION_ID>\" }
    }) { projectV2Item { id } }
  }"
```

**Add draft issue to Backlog:**

```bash
ITEM_ID=$(gh api graphql -f query="
  mutation {
    addProjectV2DraftIssue(input: {
      projectId: \"PVT_kwDOCQOIIc4BiKNM\"
      title: \"<TITLE>\"
      body: \"<DESCRIPTION>\"
    }) { projectItem { id } }
  }" --jq '.data.addProjectV2DraftIssue.projectItem.id')

gh api graphql -f query="
  mutation {
    updateProjectV2ItemFieldValue(input: {
      projectId: \"PVT_kwDOCQOIIc4BiKNM\"
      itemId: \"$ITEM_ID\"
      fieldId: \"PVTSSF_lADOCQOIIc4BiKNMzhhDPfg\"
      value: { singleSelectOptionId: \"a368d611\" }
    }) { projectV2Item { id } }
  }"
```

## CI Workflow Notes

The Python Quality workflow (`.github/workflows/python-quality.yml`) runs on every push to `main` and `develop` and on PRs. Gates:

- **Ruff** — `uv run ruff check .`
- **Black** — `uv run black --check .`
- **Mypy** — `uv run mypy src/ --ignore-missing-imports --pretty`
- **Tests + Coverage** — `uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=95`

All third-party GitHub Actions are pinned to immutable commit SHAs. Do not reintroduce mutable references (e.g. `@v5` instead of `@<sha>`).
