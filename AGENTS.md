# AGENTS.md

## Quick Commands

```bash
# Quality checks (must pass before PR merge)
ruff check .                    # Linter
black --check .                 # Formatter check
mypy automation/ src/           # Type check (strict mode)

# Tests
pytest automation/tests/        # Run all tests

# Full pipeline (manual run)
python -m src.main              # Primary pipeline (Playwright + feature impact)
python -m src.main --release summer_26  # Process specific release
```

CI order: ruff -> black -> mypy (`.github/workflows/python-quality.yml`).

## Architecture

Two systems coexist. **`src/` is the primary pipeline.**

### Primary: `src/` (Playwright-based)

Pipeline: **Playwright Scraper → FeatureImpactParser → MarkdownGenerator → ReadmeUpdater**

| Layer | File | Role |
|-------|------|------|
| Entry | `src/main.py` | Orchestrator: detect releases, fetch, parse, generate, update README |
| Config | `src/config.py` | `ReleaseInfo`, `TopicNode`, URLs, constants |
| Fetch | `src/scraper.py` | Playwright headless browser, retries, PDF download |
| Parse (tree) | `src/parser.py` → `ReleaseNotesParser` | Extracts topic hierarchy from ToC DOM |
| Parse (impact) | `src/parser.py` → `FeatureImpactParser` | Parses feature impact table (availability flags) |
| Generate | `src/generator.py` | Writes per-topic `.md` files to `releases/<slug>/` |
| Update | `src/readme_updater.py` | Replaces `<!-- RELEASE_INDEX_START/END -->` block in README |
| Logger | `src/logger.py` | `setup_logging()` for `src/` modules |

### Legacy: `automation/` (requests-based, not wired into CI)

| Layer | File | Role |
|-------|------|------|
| Entry | `automation/core/orchestrator.py` | Old pipeline entry point |
| Fetch | `automation/core/scraper.py` | `requests.get` (incomplete for SPA pages) |
| Parse | `automation/strategies/html_strategy.py` | `BeautifulSoup.get_text()` — flat text |
| Classify | `automation/core/classifier.py` | Keyword-based `TOPIC_MAPPING` (5 topics only) |
| Generate | `automation/core/generator.py` | Per-topic `.md` files |
| Update | `automation/core/readme_updater.py` | Plain list README (overwrites rich format) |

Alternate components (not wired):
- `automation/core/semantic_parser.py` — structured heading parser
- `automation/core/weighted_classifier.py` — scored classifier

## Python & Tooling

- **Python 3.11** (CI matrix), but README badge says 3.14 — keep in sync
- `line-length = 100` for both Ruff and Black
- `mypy --strict` on `automation/` and `src/`
- `pythonpath = ["."]` in pytest config (run from repo root)
- Dependencies: `requirements.txt` (runtime), `requirements-dev.txt` (dev/test)
- **Playwright required**: `playwright install chromium` before first run

## Conventions

- Release names: slugified with `python-slugify` (e.g., `Summer '26` → `summer_26`)
- Generated files: `releases/<slug>/<topic_slug>.md`
- Topics discovered dynamically from Salesforce Help ToC DOM (not hardcoded)
- Feature impact categories from `src/parser.py` `SECTION_HEADERS` (23 categories)
- `README.md` uses `<!-- RELEASE_INDEX_START/END -->` markers for auto-update
- PDFs saved in `releases/<slug>/release-in-a-box-<slug>.pdf`
- All code uses dataclasses, no Pydantic
- Logging: `src/logger.py` for `src/`, `automation/shared/logger.py` for `automation/`

## Gotchas

- Salesforce Help is SPA-rendered — `requests.get` returns shell HTML; use Playwright
- `_build_pdf_url` in `src/main.py` probes versions 5→1 with HEAD requests
- `automation/` classifier only knows 5 topics; `src/` discovers 23+ from the DOM
- `src/readme_updater.py` requires markers in README.md — won't work without them
- The `automation/core/orchestrator.py` still hardcodes `release=262` — do not use for new releases
