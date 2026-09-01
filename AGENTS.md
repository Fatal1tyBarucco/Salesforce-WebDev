# AGENTS.md - AI Agent Coding Guide (Salesforce-WebDev)

This guide is for AI coding agents working in the `Salesforce-WebDev` repository (`salesforce-release-notes`).

## Project Snapshot

Salesforce-WebDev is an ETL pipeline for extracting, classifying, and versioning Salesforce Release Notes, built with Python (3.12+), BeautifulSoup, Playwright, OpenAI/Google GenAI, Pydantic, and FastAPI.

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

- Python `>=3.14` with strict typing (`mypy strict = true`, mypy path `stubs`).
- Code style: Black (line length 100) and Ruff linting.
- Async code: Asyncio (`asyncio_mode = "auto"` in pytest).
- Commit messages: Conventional Commits (`feat(scope): ...`, `fix(scope): ...`, `refactor(scope): ...`, `test(scope): ...`, `docs(scope): ...`, `chore(scope): ...`).

## Repository Map

- `src/` - Core ETL pipeline, scrapers, classification services.
- `tests/` - Pytest test suite.
- `stubs/` - Type stubs for mypy (`mypy_path = "stubs"`).
- `docs/` - Documentation (MkDocs).
- `k8s/` - Kubernetes manifests and deployment configs.

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
