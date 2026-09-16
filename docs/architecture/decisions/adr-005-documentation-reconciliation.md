# ADR-005 Documentation Reconciliation

## Context

The repository uses a GitHub Actions workflow to keep documentation in sync with the source code. The workflow runs on pushes to `main`, on a schedule (every 6 hours), and can be manually triggered.

## Decision

We chose to use a dedicated workflow (`documentation-sync.yml`) to detect and reconcile documentation drift. The workflow performs the following steps:

1. **Checkout** the repository with full history (`fetch-depth: 0`) so the drift detection script can analyze the blob history.
2. **Guard anti-loop**: skip execution if the latest commit is an automation commit created by the workflow itself (`docs(sync)`).
3. **Cache restore**: restore the `uv` virtual environment and cache to avoid re‑installing dependencies on every run.
4. **Setup** `uv` and Python (version 3.13) in the environment.
5. **Install dependencies** (`uv sync --frozen --extra dev --extra docs`).
6. **Determine execution mode** (`incremental`, `full`, or `audit`) based on the event type or input.
7. **Deterministic drift detection**: compare the `.documentation-manifest.json` snapshot with the current repository state to identify added, modified, removed, or orphaned files.
8. **LLM reconciliation**, **link checking**, and **markdown linting**.
9. **Build documentation** with `mkdocs build --strict`. If changes are detected, the workflow commits the updated documentation and pushes it, which triggers the `documentation-build.yml` workflow that publishes the site to GitHub Pages.
10. **Concurrency control**: the `pages` concurrency group ensures that the sync and build/deploy jobs do not run in parallel on the main branch, preventing write conflicts and concurrent deployments.

## Consequences

- The workflow now prevents recursive executions, reducing the risk of infinite loops.
- Cache restoration improves performance by re‑using the virtual environment and uv cache.
- Concurrency is limited to the `pages` group, aligning with the existing deployment pipeline.
- The schedule runs every 6 hours, providing frequent drift detection while still allowing manual triggers.

## Implementation

The workflow file (`.github/workflows/documentation-sync.yml`) was updated to reflect the above steps, including:

- Updated the flow diagram and description.
- Changed the concurrency group from `documentation-sync` to `pages`.
- Added anti‑loop guard, cache restore, and explicit mode resolution steps.
- Adjusted the `mkdocs build` step to conditionally commit only when changes are detected.
- Uses setup-uv v10.1.0 (commit bec219d24cd3e171d82865faccec33120bb574f4).
