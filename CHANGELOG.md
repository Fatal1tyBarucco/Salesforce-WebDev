# Changelog

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