# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

**Primary: Salesforce admins & architects** — Technical professionals who need to understand what changed in each Salesforce release to plan upgrades, migrations, and feature adoption. They use the product when a new release drops (3×/year) and need structured, searchable, cross-referenced release intelligence.

**Secondary: DevOps/release engineers** — Engineers building automated pipelines that consume structured release data for CI/CD, dependency updates, or compliance. They consume the REST/GraphQL API and versioned Markdown artifacts programmatically.

**Tertiary: Product managers & leadership** — Decision-makers who need executive summaries and impact analysis to prioritize feature adoption across teams. They read the AI-generated executive summaries, leadership briefs, and roadmap suggestions.

## Product Purpose

Transform Salesforce's sprawling, JavaScript-heavy Release Notes into **structured, versioned, queryable knowledge** — with AI enrichment that classifies impact, writes professional descriptions, and tracks feature evolution across releases.

**Success means:** Every Salesforce release (3×/year) automatically produces:
- Versioned Markdown per category in `releases/<slug>/<lang>/` (pt_BR + en_US)
- Cross-release feature lineage via the Salesforce Feature Evolution Ledger (SFEL)
- Executive summaries, changelogs, regression reports, and leadership briefs
- A queryable REST + GraphQL API for programmatic consumers
- An MkDocs Material documentation site (Portuguese nav, bilingual content)

## Positioning

**The only Salesforce Release Notes pipeline that tracks individual feature lineage across releases.** Neighboring products (generic scrapers, manual review, Salesforce's own docs) produce per-release snapshots. This product's **Salesforce Feature Evolution Ledger (SFEL)** detects renames, category moves, deprecations, and removals — answering "did this feature exist last release?" and "has it changed?"

**Mechanism:** 5-level matching cascade (EXACT → FUZZY → HEURISTIC → LLM) with first-match-wins, producing a queryable history per feature (`get_feature_history("Flow Builder")` → complete timeline).

**Supporting differentiators:**
- **Multi-provider LLM fallback chain** (OpenAI → Gemini → OpenCode → heuristic) — zero-config resilience, never fails closed on AI
- **Production-grade autonomy** — circuit breaker, token-bucket rate limiter, content-hash cache, exponential backoff — runs unattended in CI/CD
- **Dual output contract** — same source generates human-readable Markdown (Git/docs) AND machine API (REST/GraphQL) — two consumers, one pipeline

## Operating Context

**Release cadence:** 3×/year (Spring, Summer, Winter) — pipeline triggers on schedule or manual dispatch

**Source of truth:** Salesforce Help SPA (JavaScript-rendered) + Trailhead modules — scraped via Playwright Chromium with rate limiting (2 req/s) and circuit breaker (3 failures → 60s cooldown)

**Cache strategy:** Content-hash based (30d TTL for content, 24h for metadata) — avoids refetching unchanged pages across runs

**Artifacts produced per run:**
- `releases/<slug>/pt_BR/*.md` + `en_US/*.md` (versioned, Git-tracked)
- `releases/<slug>/.meta.json` (manifest for docs sync)
- `CHANGELOG.md`, `QUALITY_REPORT.md`, `REGRESSION_REPORT.md`, `DIFF_REPORT.md`
- `docs/ai-generated/*.md` (release-notes, leadership, roadmap — appended, never overwritten)
- GitHub Issues for high-impact features (via automation/github_ops.py)

**Documentation workflow:** Portuguese-first MkDocs Material site (`mkdocs.yml` nav in PT). English content lives in `README.en.md` and `releases/*/en_US/` — reconciled deterministically by `docs_sync_engine.py` (LLM-free, idempotent). `reconcile` → validate → commit + push is mandatory for any docs change.

**AI Docs workflow (`.github/workflows/ai-docs.yml`):** OpenRouter `:free` models only — no paid fallback. Collects Git changes since last run, classifies, generates docs, publishes via PR or direct commit.

## Capabilities and Constraints

**Confirmed capabilities:**
- Playwright-based scraping of Salesforce Help SPA (Feature Impact HTML + PDF Release-in-a-Box)
- HTML parsing → category tree + feature tables → structured Pydantic models
- Multi-provider LLM service (OpenAI, Google GenAI, OpenCode-compatible) with rate limiting, timeout, retry/backoff
- Feature enrichment: professional description + impact classification (🔴 High/🟡 Medium/🟢 Low) + audience (Users/Admins/Both)
- Release summarization: executive summary, business impact, strategic themes, top categories, migration notes
- Category introductions with AI paragraph + impact tally line
- Salesforce Feature Evolution Ledger (SFEL): cross-release feature linking, lifecycle statuses (BORN/ALIVE/RENAMED/CATEGORY_CHANGED/DEPRECATED/REMOVED), history queries
- REST API (FastAPI) + GraphQL (strawberry) with optional API_KEY auth, health/ready/metrics endpoints, OpenAPI spec
- Interactive HTML dashboard (Jinja2 template) with release overview, category breakdown, feature search
- Email/Slack/Discord notifications with filtering
- GitHub Issues auto-triage and creation
- Trailhead module integration for learning paths
- NL semantic search over release content
- i18n framework (pt_BR/en_US) with LLM translation fallback
- EventBus for async pub/sub (ledger.generated, scrape.complete, etc.)
- Prometheus metrics exposition

**Hard constraints:**
- Python >=3.14,<3.15 (uv-managed, lockfile pinned)
- mypy `strict = true` on `src/` only (tests not type-checked)
- 95%+ test coverage enforced in CI (`pytest --cov-fail-under=95`)
- Black 26.10.1 with `target-version = ["py314"]` — never write `except (A, B):` without `as` binding (produces invalid Python)
- Ruff linting with specific ignores (BLE001, S110, S112, SIM102, SIM117, PLW1510, RUF034, B017)
- OpenRouter `:free` models only for ai-docs workflow — paid models rejected by validation
- Syrupy installed via `uv pip install` in CI (not pyproject.toml) to avoid pytest downgrade; local tests need `uv run --no-sync`
- `docs_sync_engine.py` must remain stdlib-only runnable (`python3 -m py_compile` + `audit` command)
- No token can edit `.github/workflows/*` (GitHub App + GITHUB_TOKEN both refuse) — workflow fixes require human/admin

**Explicitly undecided:**
- Whether SFEL integration into main orchestrator pipeline (currently autonomous, ADR-006)
- Long-term API versioning strategy beyond current REST/GraphQL
- Whether to add paid LLM tier as optional enhancement (currently hard-constrained to :free)

## Brand Commitments

**Name:** Salesforce Release Notes Intelligence (displayed as "Salesforce Release Notes Intelligence" in README banner)

**Visual identity:** Two banner assets (`assets/banner1.png`, `assets/banner2.png`) — used in README and potentially docs

**Voice:** Technical, precise, Portuguese-primary with English reconciliation. No marketing fluff — "Knowledge-as-Code para o ecossistema Salesforce"

**Repository identity:** `Fatal1tyBarucco/Salesforce-WebDev` — GitHub Pages at `fatal1tybarucco.github.io/Salesforce-WebDev/`

**License:** Educational/technical reference (not OSI-approved open source license)

## Evidence on Hand

**Real release artifacts (3 releases, 2 languages each):**
- `releases/winter_27/pt_BR/` + `en_US/` — 19 categories, 1,123 features
- `releases/summer_26/pt_BR/` + `en_US/` — 22 categories, 1,373 features
- `releases/spring_26/pt_BR/` + `en_US/` — 21 categories, 1,438 features
- `releases/winter_26/` (archive)

**Live demonstrations:**
- MkDocs site: https://fatal1tybarucco.github.io/Salesforce-WebDev/
- REST API endpoints: `/releases`, `/releases/<slug>`, `/releases/<slug>/categories/<cat>`, `/diff/<a>/<b>`, `/graphql`
- Interactive dashboard (generated HTML)
- GitHub Actions: python-quality, release_notes_pipeline, documentation-build, ai-docs

**Test evidence:** 95%+ coverage across `src/` with 70+ SFEL-specific tests in `tests/test_ledger/`

**Absences (future work must not fabricate):**
- No real customer testimonials, case studies, or benchmarks
- No pricing, licensing, or deployment claims beyond "educational/technical reference"
- No SLA, uptime guarantees, or support commitments
- No paid tier or commercial offering

## Product Principles

1. **Autonomy over convenience** — The pipeline must run unattended in CI/CD. Circuit breakers, cache, retries, and fallback chains are not optional; they are the product.

2. **Structure enables intelligence** — Raw scraping is commodity. The value is in the Pydantic models, cross-release linking (SFEL), and dual Markdown/API output that makes the data queryable by humans and machines.

3. **Resilience through redundancy** — Multi-provider LLM fallback (OpenAI → Gemini → OpenCode → heuristic) means the pipeline never fails closed on AI. Heuristic classification is a valid output, not a degraded state.

4. **Portuguese-first, English-reconciled** — Documentation nav is Portuguese (single-language MkDocs). English content is maintained separately and deterministically synced. This is not i18n — it's a deliberate bilingual strategy with Portuguese as source of truth for structure.

5. **Versioned artifacts, not ephemeral output** — Every release produces Git-tracked Markdown with `.meta.json` manifests. The documentation site is a *view* of these artifacts, not the source. `reconcile` is the gatekeeper.

## Accessibility & Inclusion

**MkDocs Material** provides WCAG 2.1 AA baseline (semantic HTML, keyboard navigation, focus management, color contrast). The documentation site inherits this.

**No product-specific accessibility requirements established** beyond the MkDocs Material baseline. The CLI pipeline and API have no direct user-facing UI requiring a11y considerations.

**Language inclusion:** Portuguese (primary nav) + English (reconciled content) serves the Brazilian Salesforce community and international consumers. No other locales planned.