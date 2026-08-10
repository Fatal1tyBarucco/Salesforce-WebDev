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

- `src/` - Core ETL pipeline, scrapers, classification, and auto-healing services.
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
