# Changelog

## 2026-10-17 — Python 3.14 upgrade

- Pinned `requires-python = ">=3.14,<3.15"` (pyproject.toml) and regenerated `uv.lock` (`==3.14.*`).
- Updated all CI workflows to `3.14` (python-quality, pipeline, docs-sync, docs-build, dependabot, copilot, intelligence-hub).
- Updated agent docs, copilot instructions, LLM fallback prompts, and guide prerequisites.
- Aligned Black `target-version` to `py314`; updated README/table references.