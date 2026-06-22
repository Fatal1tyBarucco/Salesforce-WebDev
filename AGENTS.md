# AGENTS.md

## Quick Commands

```bash
# Quality checks (must pass before PR merge)
ruff check .                    # Linter
black --check .                 # Formatter check
mypy src/                       # Type check (strict mode)

# Tests
pytest tests/                    # Run all tests

# Full pipeline (manual run)
python -m src.main              # Primary pipeline (Playwright + feature impact)
python -m src.main --release summer_26  # Process specific release
```

CI order: ruff -> black -> mypy (`.github/workflows/python-quality.yml`).

## Architecture

**`src/` is the primary pipeline.** Legacy `automation/` pipeline code has been removed.

### Primary: `src/` (Playwright-based)

Pipeline: **Playwright Scraper → FeatureImpactParser → MarkdownGenerator → ReadmeUpdater**

| Layer | File | Role |
|-------|------|------|
| Entry | `src/main.py` | Orchestrator: detect releases, fetch, parse, generate, update README |
| Config | `src/config.py` | `ReleaseInfo`, `TopicNode`, URLs, constants |
| Fetch | `src/scraper.py` | Playwright headless browser, retries, PDF download, content caching |
| Parse (tree) | `src/parser.py` → `ReleaseNotesParser` | Extracts topic hierarchy from ToC DOM |
| Parse (impact) | `src/parser.py` → `FeatureImpactParser` | Parses feature impact table (availability flags) |
| Generate | `src/generator.py` | Writes per-topic `.md` files to `releases/<slug>/` |
| Update | `src/readme_updater.py` | Replaces `<!-- RELEASE_INDEX_START/END -->` block in README |
| Analytics | `src/analytics.py` | Static HTML dashboard with charts (category breakdown, trends, confidence) |
| API | `src/api.py` | REST API server for programmatic access to release data (/releases, /diff) |
| Notifications | `src/notifications.py` | Email digest, Slack/Discord webhooks, configurable profiles |
| AI | `src/ai_automation.py` | Release comparison, regression detection, quality metrics, triage, deduplication |
| Logger | `src/logger.py` | `setup_logging()` for `src/` modules |

## Python & Tooling

- **Python 3.14** (CI matrix)
- `line-length = 100` for both Ruff and Black
- `mypy --strict` on `src/`
- `pythonpath = ["."]` in pytest config (run from repo root)
- Dependencies: `requirements.txt` (runtime), `requirements-dev.txt` (dev/test)
- **Playwright required**: `playwright install chromium` before first run
- Tests in `tests/` directory (moved from `automation/tests/`)

## Conventions

- Release names: slugified with `python-slugify` (e.g., `Summer '26` → `summer_26`)
- Generated files: `releases/<slug>/<topic_slug>.md`
- Topics discovered dynamically from Salesforce Help ToC DOM (not hardcoded)
- Feature impact categories from `src/parser.py` `SECTION_HEADERS` (23 categories)
- `README.md` uses `<!-- RELEASE_INDEX_START/END -->` markers for auto-update
- PDFs saved in `releases/<slug>/release-in-a-box-<slug>.pdf`
- All code uses dataclasses, no Pydantic
- Logging: `src/logger.py` for `src/` modules

## Gotchas

- Salesforce Help is SPA-rendered — `requests.get` returns shell HTML; use Playwright
- `_build_pdf_url` in `src/main.py` probes versions 5→1 with HEAD requests
- `src/` discovers 23+ topics from the DOM dynamically
- `src/readme_updater.py` requires markers in README.md — won't work without them
- `releases/history.json` is gitignored (runtime artifact updated by pipeline)
