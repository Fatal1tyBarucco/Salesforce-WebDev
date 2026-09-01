# AGENTS.md - AI Agent Coding Guide (Salesforce-WebDev)

This guide is for AI coding agents working in the `Salesforce-WebDev` repository (`salesforce-release-notes`).

## Project Snapshot

Salesforce-WebDev is an ETL pipeline for extracting, classifying, and versioning Salesforce Release Notes, built with Python (3.13), BeautifulSoup, Playwright, OpenAI/Google GenAI, Pydantic, and FastAPI.

Dependency management and virtual environments are handled by `uv`.

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

- Python `>=3.13,<3.14` with strict typing (`mypy strict = true`, mypy path `stubs`).
- Code style: Black (line length 100) and Ruff linting.
- Async code: Asyncio (`asyncio_mode = "auto"` in pytest).
- Commit messages: Conventional Commits (`feat(scope): ...`, `fix(scope): ...`, `refactor(scope): ...`, `test(scope): ...`, `docs(scope): ...`, `chore(scope): ...`).

## Repository Map

- `src/` - Core ETL pipeline, scrapers, classification services.
- `tests/` - Pytest test suite.
- `stubs/` - Type stubs for mypy (`mypy_path = "stubs"`).
- `docs/` - Documentation (MkDocs).
- `k8s/` - Kubernetes manifests and deployment configs.

## Key Files & Decisions

### Dependency constraints

- `pyproject.toml` specifies `Python >=3.13,<3.14`.
- `pytest==9.1.1` in `uv.lock` — **do not** add `pytest-syrupy` to `pyproject.toml` (it would downgrade pytest to 8.4.2).
- `syrupy` is installed via `uv pip install syrupy` (not via pyproject.toml). In CI, it is installed in the `tests` job step after `uv sync`.

### Tests & mypy

- `mypy strict = true` is applied globally (including `tests/`).
- `mypy_path = "stubs"` in `pyproject.toml`.
- Stub module: `stubs/syrupy/__init__.pyi` (with `py.typed`) provides `SnapshotAssertion` and `snapshot()` for mypy type checking.
- `tests/conftest.py` stubs `openai` (and `google`) in `sys.modules` to avoid import hangs during test collection.
- `tests/test_snapshot.py` and `tests/test_llm_service.py` have pre-existing mypy errors (`no-untyped-def` in fixture methods) — do not introduce new mypy errors.

### Test Data

- Factory module: `tests/factories.py` (not `tests/test_factories.py`).
- Factory provides: `make_release`, `make_topic_node`, `make_topic_tree`, `make_toc_html`, `make_feature_impact_text`, `make_feature_impact_html`, `make_release_metadata`, `make_mock_html_response`.
- Snapshots in `tests/__snapshots__/test_snapshot.ambr` (syrupy).

### Documentation

- Spec reference: `newPrompt.md` (5 gaps, Gap 3 was cancelled due to pytest hangs).
- Source selectors reference: `docs/SOURCE_SCHEMA.md` (CSS selectors, ARIA attributes, feature impact format).
- Enhanced search: `docs/assets/javascripts/enhanced_search.js` + `docs/assets/stylesheets/enhanced_search.css` + `docs/maintenance/enhanced-search.md`.
- MkDocs search configured with i18n `[en, pt]` and extra assets in `mkdocs.yml`.

### Known issues (do not re-introduce)

- `NOTIFICATION_DIGEST.md` is an artifact from test runs — do not commit.
- `datetime.utcnow()` was deprecated — use `datetime.now()` instead.

## Validation Checklist

Before finishing changes, always run:
1. `uv run ruff check .`
2. `uv run black --check .`
3. `uv run mypy src/`
4. `uv run pytest`

## GitHub Project Integration

This repository is linked to a GitHub Project used for tracking work:

- **Project:** [Salesforce Release Notes](https://github.com/users/Fatal1tyBarucco/projects/5)
- **Project ID:** `PVT_kwDOCQOIIc4BiKNM`
- **Owner:** `Fatal1tyBarucco`
- **Repo ID:** `R_kgDORbgJew`

### Status field (single-select)

| Status | Meaning |
|--------|---------|
| `Backlog` | Tasks not yet started, prioritized in the backlog |
| `In Progress` | Active work — agent is implementing the change |
| `In Review` | PR open, awaiting review / CI checks |
| `Done` | Merged and closed |

The field's option IDs (GraphQL) are:
- `Backlog` → `a368d611`
- `In Progress` → `3808f0ce`
- `In Review` → `10aa434a`
- `Done` → `f87ad5a7`

### When an agent must update the Project

Every agent working on an issue or PR **must** keep the project board in sync:

1. **When starting work on an issue:**
   - Set the issue's `Status` to `In Progress`.
2. **When opening a PR for the work:**
   - Set the linked issue's `Status` to `In Review`.
3. **After the PR is merged:**
   - Set the linked issue's `Status` to `Done`.
4. **When a new task is identified** (not in the board yet):
   - Add it as a Draft Issue to the project with `Status: Backlog`.

### CLI commands (gh project)

The `gh` CLI requires the `project` and `read:project` scopes on the auth token. Verify with:

```bash
gh auth status
```

List items:

```bash
gh project item-list 5 --owner Fatal1tyBarucco
```

View a single item:

```bash
gh project view 5 --owner Fatal1tyBarucco
```

### GraphQL examples (for automation)

**Add an existing issue to the project:**

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

**Set the status of a project item:**

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

**Add a draft issue to Backlog:**

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

- Ruff (linting)
- Black (formatting)
- Mypy (type checking)
- Tests + Coverage (`--cov-fail-under=95`)

All third-party GitHub Actions are pinned to immutable commit SHAs (not tags). Do not re-introduce mutable Action references (e.g. `@v5` instead of `@<sha>`).
