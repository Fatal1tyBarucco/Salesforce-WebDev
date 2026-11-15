# Changelog

<!-- gerado por IA em 2026-11-15T14:30:24+00:00 — revisar antes de publicar -->

## [Unreleased]

### Changed
- Refactored `src/infrastructure/api/__init__.py` by adding the missing newline at end of file to satisfy the Black formatting gate; no logic or behavior changes were made.

<!-- gerado por IA em 2026-11-15T14:23:21+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added `syrupy` plugin registration in `conftest.py` to resolve fixture snapshot errors.

### Changed
- Updated `docs/.documentation-manifest.json` with new checksums for `pyproject.toml`, `src/infrastructure/api/__init__.py`, `uv.lock`, and added entry for `test_infrastructure_api_graphql.py`.

### Fixed
- Fixed `strawberry-graphql` import error that caused `ModuleNotFoundError` in 11 tests, restoring build capacity and increasing test coverage to 95.35%.

<!-- gerado por IA em 2026-11-15T12:47:38+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added comprehensive test coverage for core, infrastructure, models, and main modules.
- Added Strawberry GraphQL types using ChangeType and added strawberry-graphql dependency to resolve CI test failures.

### Changed
- Refactored the application into Clean Architecture layers in src/core and src/infrastructure, with core, infrastructure, and models modules.
- Updated the documentation manifest and mkdocs navigation for new API and architecture decision documents.

### Fixed
- Fixed the LLMService fallback chain.
- Fixed the GraphQL schema by replacing the generic dict type with ChangeType and corrected API module exports.

### Breaking Changes
- The Clean Architecture refactor may break imports referencing legacy modules.

<!-- gerado por IA em 2026-11-14T06:19:14+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added design system to the dashboard with dark mode support and accessibility features (high impact).

### Fixed
- Fixed fence state tracking in fix_markdown.py to correctly distinguish opening and closing markdown fences.

### Changed
- Updated actions/setup-python to v7.1.0.
- Updated astral-sh/setup-uv to v10.3.3.
- Updated pyasn1 to 0.6.5.
- Updated uv group dependencies (certifi, filelock, langgraph-sdk, virtualenv).
- Updated aiohttp to 3.14.4.
- Updated black to 26.10.1.

<!-- gerado por IA em 2026-10-19T14:57:56+00:00 — revisar antes de publicar -->

## [Unreleased]

### Fixed
- Fixed GitHub Pages deployment by adding site build job, artifact upload, and separate deploy step, restoring publication of release artifacts.
- Adjusted Markdown headers for MD001/MD036 compliance in impact report generator.
- Changed ai-docs workflow to warn on missing files and include hidden files in AI log artifact upload.

### Added
- Added output token budget management in LLM client with environment variables and exponential max_tokens scaling on retries.
- Added coverage tests for AI and documentation modules.

### Changed
- Simplified exception handling in docs_sync_engine by replacing specific OSError/ValueError blocks with a generic Exception catch.
- Updated documentation manifest with references to new AI-generated artifacts.

### Breaking Changes
- None

### Security
- None

<!-- gerado por IA em 2026-10-19T03:48:57+00:00 — revisar antes de publicar -->

## [Unreleased]

### Fixed
- Fixed LLM completions returning empty responses, restoring documentation generation functionality.
- Prevented duplicate headings in automatic changelog updates.
- Corrected paths in documentation sync pipeline for CI consistency.

### Added
- Implemented new OpenRouter free-tier documentation pipeline with rate-limiting support.
- Expanded change collector with enhanced Git/GitHub change capture capabilities.
- Added failure diagnostics exposure with validated test coverage.

### Changed
- Aligned Black target-version to py314 for Python 3.14 compatibility.
- Updated documentation manifest with new files including README.en.md and ai-docs-audit-logs.md.

## 2026-10-17 — Python 3.14 upgrade

- Pinned `requires-python = ">=3.14,<3.15"` (pyproject.toml) and regenerated `uv.lock` (`==3.14.*`).
- Updated all CI workflows to `3.14` (python-quality, pipeline, docs-sync, docs-build, dependabot, copilot, intelligence-hub).
- Updated agent docs, copilot instructions, LLM fallback prompts, and guide prerequisites.
- Aligned Black `target-version` to `py314`; updated README/table references.