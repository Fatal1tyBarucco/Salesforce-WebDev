# AGENTS.md - AI Agent Coding Guide (Salesforce-WebDev)

This guide is for AI coding agents working in the `Salesforce-WebDev` repository (`salesforce-release-notes`).

## Project Snapshot

Salesforce-WebDev is an ETL pipeline for extracting, classifying, and versioning Salesforce Release Notes, built with Python (3.14), BeautifulSoup, Playwright, OpenAI/Google GenAI, Pydantic, and FastAPI.

Dependency management and virtual environments are handled by `uv`. The project runs under **Python 3.14** via `uv` (system default may be 3.14, but `uv` pins to 3.14 via `requires-python = ">=3.14,<3.15"`).

## Setup & Development Commands

- **Install dependencies:** `uv sync --extra dev`
- **Install Playwright browsers:** `uv run playwright install chromium`
- **Run tests:** `uv run pytest` (or `uv run pytest tests/`)
- **Run lint / formatting check:**
  - `uv run ruff check .`
  - `uv run ruff format --check .`
- **Run typecheck:** `uv run mypy src/`
- **Run all pre-commit checks manually:** `uv run pre-commit run --all-files`
  - Pre-push hook (`.claude/hooks/pre-push.py`) runs `pytest tests/ -x` on push (timeout 300s; timeout = not verified); it uses `uv run`, so ensure deps are in the active venv.

## Stack & Conventions

- Python `>=3.14,<3.15` (via `uv`; system may have 3.14, lock file pins to 3.14).
- `addopts = "-q --tb=short --durations=10 --timeout=120"` in pyproject.toml; `--timeout=120` (pytest-timeout) enforces a 120s per-test limit.
- Code style: **Ruff** (lint + format, line length 100).
- Async code: Asyncio (`asyncio_mode = "auto"` in pytest).
- `pythonpath = ["."]` in pyproject.toml — `src` modules are importable without installation.
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
2. `uv run ruff format --check .`
3. `uv run mypy src/`
4. `uv run pytest --cov=src --cov-fail-under=95 --cov-report=term-missing --cov-report=xml:coverage.xml`

### Feature: Python Quality + /oc fix auto-comment (2026-09-23)
Quando `python-quality.yml` falha, ele cria um issue automaticamente e comenta `/oc fix for ruff, mypy and test errors.` para acionar `opencode` (`opencode.yml`). Modelo configurado: `opencode/mimo-v2.6-flash-free` (v2.5 removida). Requer `OPENCODE_API_KEY` + `GITHUB_TOKEN` no `opencode.yml`. Se o `opencode` reagir, ele cria PR automaticamente; caso contrário, a correção é manual (`uv run ruff check . --fix`, `uv run ruff format .`, `uv run mypy src/`).

### Quality issue fix convention (updated 2026-09-22)
When an open issue reports "Python Quality falhou": fix with `uv run ruff check . --fix`, `uv run ruff format .`, commit to main, push, then close all related issues (#141-143 pattern). Remove test artifacts (`NOTIFICATION_DIGEST.md`, `DIFF_REPORT.md`, etc.). Verify with `uv run pytest --cov=src --cov-fail-under=95`.

#### Atualização de conclusão (2026-10-17 — Renato / Termux aarch64-android)
- Issue #184 fechada; PR #188 mergeada; repo sincronizado para 93cf8c2.
- MEMORY.md criado local (não versionado) com registro da conclusão e bloqueio (ruff 0.17.1 não linkado, python3.13 indisponível).
- **Atenção**: Projeto agora é **Ruff-only** (lint + format). No Termux/ARM64, `ruff` pode não estar linkado — formatação e lint só rodam no CI ou máquina com Ruff funcional.
- Bloqueio documentado honestamente: não inventado.

## Key Files & Decisions

### Dependency constraints

- `pyproject.toml` specifies `requires-python = ">=3.14,<3.15"`.
- `pytest>=8.0.0,<10` — pytest 9.x in `uv.lock` (`pytest==9.1.1`).
- **Do not** add `pytest-syrupy` to `pyproject.toml` — it would downgrade pytest to 8.4.2.
- `syrupy` is installed via `uv pip install "syrupy>=4.9.0,<5"` in the CI tests job (after `uv sync`), NOT via pyproject.toml.
  - This downgrades pytest from 9.x to 8.4.2 for local venvs. When running tests locally with syrupy installed, use `uv run --no-sync` (or `python -m pytest` directly) to prevent `uv` from re-syncing and reverting the pytest downgrade.
- `pytest-timeout>=2.4.0` is in dev dependencies; `--timeout=120` is set globally via `addopts`.

### mypy

- `mypy strict = true` is in `pyproject.toml`. CI and pre-commit check `src/` only (`uv run mypy src/`); tests are not type-checked.
- `mypy_path = "stubs"` — stub modules go in `stubs/`.
- CI runs `uv run mypy src/ --ignore-missing-imports --pretty` — the `--ignore-missing-imports` flag is intentional to suppress import errors for optional deps.
- Stub module: `stubs/syrupy/__init__.pyi` (with `py.typed`) provides `SnapshotAssertion` and `snapshot()` for mypy type checking.

### Tests

- `tests/conftest.py` stubs `openai` and `google` in `sys.modules` to avoid import hangs during test collection.
- `tests/test_snapshot.py` and `tests/test_llm_service.py` may have pre-existing mypy errors in helper fixtures — do not introduce new errors.
- Factory module: `tests/factories.py` (8 functions: `make_release`, `make_topic_node`, `make_topic_tree`, `make_toc_html`, `make_feature_impact_text`, `make_feature_impact_html`, `make_release_metadata`, `make_mock_html_response`).
- Snapshots in `tests/__snapshots__/test_snapshot.ambr` (syrupy, 9 snapshots).
  - Regenerate with `pytest tests/test_snapshot.py --snapshot-update`.

### Documentation

- Source selectors: `docs/SOURCE_SCHEMA.md` (CSS selectors, ARIA attributes, feature impact format).
- Enhanced search: `docs/assets/javascripts/enhanced_search.js` + `docs/assets/stylesheets/enhanced_search.css` + `docs/maintenance/enhanced-search.md`.
- MkDocs site is **single-language** (nav in `mkdocs.yml` is Portuguese). English user-facing content is maintained separately in `README.en.md` and `releases/*/<lang>/`, and is reconciled alongside the Portuguese docs by `.github/scripts/docs_sync_engine.py` (`python3 .github/scripts/docs_sync_engine.py audit` → 0 findings).
- Documentation sync: `.github/scripts/docs_sync_engine.py` (deterministic, LLM-free; `audit`/`reconcile` commands; source of truth = `releases/*/.meta.json`; idempotent — a second run on a clean tree is a no-op). Design decisions: `docs/architecture/decisions/adr-005-documentation-reconciliation.md`.
- Baseline manifest: `docs/.documentation-manifest.json` (git-blob SHAs of tracked docs; regenerated by `reconcile`, excluded from its own inventory to avoid self-reference).
- Rewrite/audit scope: `rewritable_markdown()` in `docs_sync_engine.py` limits `strip_dead_refs()` and the link audit to `docs/` + `DOC_ROOT_FILES`. `tests/golden/**`, `releases/**`, `.claude/`, `.github/` are content and are never rewritten (unwrapping a golden link corrupts byte-exact fixtures and fails characterization tests). Regenerate goldens only via `CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_*.py` — never hand-edit them.

### Documentação — Reconcile obrigatório + Sincronia Absoluta (ADR-012, 2026-11-20)
- Qualquer alteração em docs exige: `reconcile` → valida (lint + links + mkdocs strict best-effort) → `commit` + `push` obrigatório.
- `docs/.documentation-manifest.json` é fonte de verdade; repo_sha deve coincidir com HEAD após o commit.
- **ADR-012 — Sincronia Absoluta**: `python3 .github/scripts/docs_contract.py validate` é gate DURO no Documentation Sync (v2.3) e no Documentation Build; qualquer divergência ÓRFÃO/OMITO/OBSOLETO/DIVERGENTE falha o CI. Subcomandos: `validate`, `report` (inclui cruzamento `automation_coverage()` com `.last-processed-ref`), `parity` (4 camadas: READMEs, sets bilíngues `releases/*/pt_BR×en_US`, superfície EN `docs/en/index.md`, varredura por página). O build roda `reconcile` ANTES do gate (corrida sync×build: o bot commita o baseline corrigido com skip-ci e não re-dispara o build). **Após QUALQUER commit que toque arquivos rastreados (inclusive pyproject/uv.lock/workflows), regenere o manifest antes de push** — baseline stale = gate vermelho no build.
- Remoções determinísticas (evocadores órfãos, nav morto) registram histórico append-only em `manifest["removals"]` (path, removed_at, commit, reason). Evocadores de pacote (`__init__.py`) são legítimos. Referências a arquivos novos no disco (untracked) NÃO são encurtadas pelo `strip_dead_refs`.
- Superfícies fora do índice público: `docs/ai-generated/`, `docs/internal/`, `docs/plans/` (`exclude_docs` no mkdocs.yml; permanecem no repo). Páginas virtuais do mkdocs-gen-files (`docs/reference/code-tree.md`) são whitelisted em `GENERATED_PAGES`; `docs/reference/repo-index.md` é gerado pelo engine (não editar manualmente). Órfãs falham o próprio `mkdocs build --strict` via hook `docs/hooks/orphan_guard.py` (respeita `exclude_docs`).
- Publicação: mike (ledger no branch `gh-pages`, versões = tags + versão do pyproject) materializado em `site/` e deploy oficial via `upload-pages-artifact` + `deploy-pages`. **Push do ledger NÃO atualiza o site publicado** — rodar o build depois do backfill. `mike deploy` NÃO tem flag `--no-push` (default é local-only; `--push` é opt-in); checkout do build exige `fetch-depth: 0`. Backfill de tags antigas: injetar `mike`+`pillow`+`cairosvg` no venv da tag (tags pré-ADR-012 não têm mike no extra docs). Social cards só em CI (`enabled: !ENV [CI, false]` + extra `imaging`); **pillow>=13** (11.x/12.x têm advisories críticos bloqueados pelo Dependency Review). `uv run --no-sync` após `uv sync --extra docs --extra imaging` (uv run implícito remove extras). `check-yaml` do pre-commit usa `--unsafe` (tag !ENV do Material). Refresh do tema por release: `docs-deps-refresh.yml`.
- Analytics placeholder removido; reativação só via segredo `GA_PROPERTY` + `!ENV`.
- IA: prompt de reconciliação versionado em `prompts/reconciliation/v1.yaml`, casos promptfoo de fidelidade ao manifest (asserts inspecionam o prompt renderizado; eval keyless via `scripts/promptfoo_echo.py` + `PROMPTFOO_PYTHON=.venv/bin/python`); `ai-docs.yml` valida saída (contrato + markdownlint + link checker + strict) ANTES de commitar e commita na convenção do sync (`github-actions[bot]` + `docs(sync): reconcile documentation — [data]` com skip-ci).
- `MEMORY.md` NÃO é versionado; atualizar ao finalizar cada tarefa. `AGENTS.md` é versionado e deve refletir convenções atualizadas (ex: reconcile obrigatório, push obrigatório, não inventar resultados de push, reportar bloqueios honestamente: mkdocs best-effort bloqueado por android/arm64 + playwright sem wheel; push falha = bloqueador real, não inventado).

### Known issues (do not re-introduce)

- `NOTIFICATION_DIGEST.md` is an artifact from test runs — do not commit.
- `datetime.utcnow()` was deprecated — use `datetime.now()` instead.
- **`uv lock --check` is a CI gate** (first step of the Ruff job). `uv.lock` must embed the same
  project `version` as `pyproject.toml` — bumping one without the other fails the whole workflow.
  Fix with `uv lock` (or `uv sync`, which rewrites it), never hand-edit.
  - **release-please desync (2026-11-17, gate skip landed 2026-11-18):** release-please
    (`release-type: python`) bumps `pyproject.toml` version without refreshing `uv.lock`, so
    release PRs and the subsequent push to `main` failed this gate (issues #339–#342, #404, #406).
    **Durable fix landed in `f0f86fa`** (admin commit): the step now runs
    `if: "!contains(github.event.head_commit.message, 'release-please') && !contains(github.event.head_commit.message, 'sync uv.lock')"` —
    push events whose head commit message contains either string skip the gate. Caveat: on
    `pull_request` events `github.event.head_commit` is null → the gate **runs**, so the PR branch
    must have `uv.lock` in sync with `pyproject.toml` (release 0.3.1 PR #405 did — `uv lock --check`
    green on its head). Manual fallback after any release merge: run `uv lock` on `main`; never
    hand-edit `uv.lock`.
- **`tests/infrastructure/mcp/test_knowledge_server.py` must target the `MCPServer` API** of
  `src/infrastructure/mcp/knowledge_server.py` as locked by `mcp==2.3.0` (bumped from 1.30.0 by
  the production-dependencies group in #435, 2026-11-23 — that bump is what broke mypy/tests):
  in 2.x `mcp.server.fastmcp` is only a shim that raises `ModuleNotFoundError` and points to
  `mcp.server.mcpserver.MCPServer`; the low-level `Server` kwargs used in reverted merge commits
  (`on_list_tools=`, `ServerRequestContext`, `get_request_handler`, `server._build_tools`) do not
  exist either. Tool results come from `await server.mcp.call_tool(...)` (returns a
  `CallToolResult` model — read `result.structured_content["result"]`, never tuple-index it) and
  `await server.mcp.list_tools()` (returns `list[Tool]`); unknown tools raise
  `mcp.server.mcpserver.exceptions.ToolError`. Do **not** "fix" a future breakage by re-pinning
  `mcp<2` — dependabot's dependency group bumps it back; migrate the code instead.
- **`_build_release_block` output is frozen by `tests/golden/summarizer/readme_block_{pt,en}.md`
  and `readme_pt_updated.md`.** The leading `lines = [""]` and the blank separators after each
  `</details>` are intentional (they match the committed `README.md`/`README.en.md`) — the
  2026-11-16 "docs: reconcile" commits stripped them and desynced the goldens. If that function
  changes, regenerate the goldens with `CHAR_GOLDEN_UPDATE=1 uv run pytest
  tests/test_characterization_summarizer.py`.
- **`drift_report.json` self-referential `MANIFEST_STALE_SHA` (pre-existing, never fails CI):**
  the Documentation Sync workflow runs `audit` (which writes `./drift_report.json`) **before**
  `write_manifest()` reads `git ls-files -s` (the index), then `git add -A` commits the new
  report — so the committed baseline lags one generation and the next audit reports exactly 1
  finding (`drift_report.json` blob SHA changed). `main` carries this state too; `cmd_audit`
  returns 0 regardless of findings, so nothing is blocked. Fix recipe after any merge/conflict
  resolution: `git checkout -- drift_report.json` → `python3 .github/scripts/docs_sync_engine.py
  reconcile` → re-audit with `DRIFT_REPORT=/tmp/...` (keeps the tree clean) → commit the
  regenerated `docs/.documentation-manifest.json`. Do **not** treat this finding as a regression.
- **CI runs created by the Actions `GITHUB_TOKEN` (`github-actions[bot]`) on PR heads conclude
  `action_required`** (observed 2026-11-18 pushing to `release-please--branches--main`: the 5
  `pull_request` runs — Python Quality, AI PR Review, Documentation Sync, Dependency Review,
  AI Triage — were all created but hold for maintainer approval in the UI; runs pushed by a human
  execute normally). The token has no `actions: write`/`checks: write` → `gh run rerun`,
  `gh workflow run`, and check-suite `rerequest` all return HTTP 403. Verify every gate locally
  with the full Validation Checklist, report results honestly, and state that a human must
  approve the runs (or a PAT must push) — never claim CI ran when it did not.
- **`.gitleaks.toml` allowlist `paths` globs panic gitleaks v8.30.1 (since `9cfbab3`, 2026-11-18):**
  globs like `tests/fixtures/**`, `tests/golden/**`, `*.example`, `*.template` are compiled as RE2
  (`bad repetition operator` from `re2.cc`) → the `AI PR Review → Security Audit` job fails on
  **every** run. It is a non-required check (PRs merged with it red); do not attribute the failure
  to PR content. Fix not applied yet — rewrite globs as RE2 (`tests/fixtures/.*`, `.*\.example$`)
  only after verifying locally against gitleaks v8.30.1.

## GitHub Project Integration

This repository is linked to a GitHub Project for tracking work:

- **Project:** [Salesforce Release Notes](https://github.com/users/Fatal1tyBarucco/projects/5)
- **Project ID:** `PVT_kwDOCQOIIc4BiKNM`
- **Owner:** `Fatal1tyBarucco`
- **Repo ID:** `R_kgDORbgJew`

### Status field (single-select)

| Status | Meaning |
|--------|---------|
| `Backlog` | Tasks not yet started |
| `In Progress` | Agent is actively working |
| `In Review` | PR open, awaiting review / CI checks |
| `Done` | Merged and closed |

Option IDs (GraphQL):
- Backlog → `a368d611`
- In Progress → `3808f0ce`
- In Review → `10aa434a`
- Done → `f87ad5a7`

### When to update the Project

Every agent **must** keep the board in sync:

1. Start work on an issue → set Status to `In Progress`
2. Open a PR → set linked issue's Status to `In Review`
3. PR merged → set Status to `Done`
4. New task identified → add Draft Issue with Status `Backlog`

### CLI commands

Requires `project` + `read:project` scopes. Verify:

```bash
gh auth status
```

```bash
gh project item-list 5 --owner Fatal1tyBarucco
gh project view 5 --owner Fatal1tyBarucco
```

### GraphQL examples

**Add existing issue to project:**

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

**Set item status:**

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

**Add draft issue to Backlog:**

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

- **Ruff** — `uv run ruff check .`
- **Ruff Format** — `uv run ruff format --check .` (migrated from Black in `6e82d01`, 2026-11-18; the `black` job was merged into the `ruff` job — "Ruff Lint & Format")
- **Mypy** — `uv run mypy src/ --ignore-missing-imports --pretty`
- **Tests + Coverage** — `uv run pytest tests/ --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=95`

  CI installs deps with `uv sync --frozen --extra dev --group dev` (ruff job) or `uv sync --frozen --extra dev --extra healing --group dev` (mypy/tests jobs). Syrupy lives in the `dev` dependency group (`>=7.0.2`) — no separate install step.

All third-party GitHub Actions are pinned to immutable commit SHAs. Do not reintroduce mutable references (e.g. `@v5` instead of `@<sha>`).

### CodeQL e segurança de workflows (2026-11-19)

- CodeQL roda via **default setup** do GitHub (languages: actions+python, query suite `extended`, threat model `remote`) — não há arquivo de workflow; gerenciar via API `code-scanning/default-setup` ou UI Security.
- **Nunca interpolar campos de payload externo** (`github.event.workflow_run.*`, `github.event.pull_request.*`, etc.) em blocos `run:` — usar `env:` (contexto de expressão, seguro) + variáveis shell entre aspas. `ci-repair.yml` foi hardened assim (fix de injeção critical + guard `head_repository.full_name == github.repository` em ambos os jobs; checkout de ref só é confiável sob esse guard).
- Falsos positivos dismissados com justificativa: `.github/actions/ci-visual/action.yml` — `github.action_path`/`HELPER_PATH` são caminhos controlados pelo runner, não input de usuário (alertas #112–#114).
- Decisão do owner: manter CodeQL (detectou injeção real no ci-repair + masks 0o644 no cache novo, corrigidos com 0o600).

## Codebase Pitfalls (learned the hard way — do not re-introduce)

- **Black 26.10.0 with `target-version = ["py314"]` removes the parentheses from `except (A, B):` clauses that have no `as` binding, producing invalid Python.** Never write `except (A, B):` without `as` in any `.py` file — use `except Exception:` in defensive best-effort wrappers or `except (A, B) as exc:` when the binding is needed. `except (A, B) as e:` is black-stable.
- **`actions/upload-artifact` ≥ v4.4 excludes hidden files/directories by default.** Any artifact path starting with a dot (e.g. `docs/.ai-logs/`) requires `include-hidden-files: true`, otherwise the step succeeds with `total_count: 0`. Use `if-no-files-found: warn` (not `ignore`) so missing artifacts are visible.
- **Tests must never write repo-root files.** `src/main.py` `generate_ai_reports_async` writes `CHANGELOG.md`, `QUALITY_REPORT.md`, `REGRESSION_REPORT.md`, `DIFF_REPORT.md` relative to cwd; tests invoking it need a temp cwd (see autouse `isolated_cwd` fixture in `tests/test_main_coverage.py`).
- **`.github/scripts/docs_sync_engine.py` must stay runnable** (`python3` stdlib-only, no third-party deps); after editing it, verify with `python3 -m py_compile` and `python3 .github/scripts/docs_sync_engine.py audit`. Docs changes require `reconcile` → validate → commit + push.
- **`ruff format --check .` também formata blocos de código Python dentro de Markdown** (docs/*.md). Restaurar versões antigas de docs pode quebrar o gate de format (aconteceu com SOURCE_SCHEMA.md, run 44574630482) — rode `uv run ruff format <doc>.md` após restaurar. O hook local ruff-format (types: python) não pega .md; só o CI pega.
- **Plugins do `mkdocs.yml` exigem dependência correspondente no extra `docs`** (minify→mkdocs-minify-plugin, htmlproofer→mkdocs-htmlproofer-plugin, adicionados 2026-11-19 após Deploy Docs quebrar desde 51528de). A opção do htmlproofer é `validate_external_urls` (não `validate_external`). `ruff` no extra docs restaura a formatação de signatures do mkdocstrings (black removido na migração Ruff-only). Verificar com `uv sync --extra docs && uv run mkdocs build --strict`.
- **`.github/scripts/fix_markdown.py` `fix_md040_fence_language` must track fence open/close state** (fixed 2026-11-04). Rewriting a *closing* fence as if it were an opener mutates docs on every Documentation Sync run → the bot pushes a `github-actions[bot]` commit → that commit's checks pause at `action_required` — **API approval works** (verified 2026-11-19): `gh api -X POST repos/<owner>/<repo>/actions/runs/<run_id>/approve` with a write-scope token, no UI needed; GITHUB_TOKEN pushes pause the same way — see the known issue above. Never commit the script's output alone: its MD029 pass renumbers continuing lists to 1..n (e.g. `docs/index.md` steps 5–7 → 1–3, semantically wrong), and only the Documentation Sync's layer-2 `markdownlint-cli2 --fix` reverts that (verified in run `44299414704`: layer 1 "Fixed files: docs/index.md", layer 2 "3 fixes in 1 file" → net zero). When validating locally, run layer 1 followed by `npx --yes markdownlint-cli2 "docs/**/*.md" --fix --config-file .markdownlint.json --ignore node_modules`, then confirm `git status` stays clean on an unchanged tree.
- **Documentation Sync bot cycle quirk:** every human push to a PR triggers the bot's reconcile, which rewrites `drift_report.json` *after* computing the manifest baseline → 1 cosmetic `MANIFEST_STALE_SHA` finding (drift_report self-reference). Do not chase it with refresh commits — the bot regenerates it on the next push; it is not content drift. Link checker hardening (2fcc61d): `retryOn429`/`retryCount`/`fallbackRetryDelay` + ignore self-repo `blob/` links — github.com returns transient 429/503 under CI load (run 44561979136 failed on a 503, not a dead link; the real bug found alongside was a stale anchor in docs/index.md → README.en.md `#-available-releases`).
- **`unittest.mock.patch` targets must name the module where the name is looked up at call time**, not a re-export. `generate_toggle_html` lives in `src/i18n.py` and is called inside `src/release_docs.py::_generate_release_files`; `src/main.py` only re-exports `_generate_release_files` and never imports the toggle helper. Patching `src.main.generate_toggle_html` raised `AttributeError` at test setup (run 45480205126, 2026-11-24) — patch `src.release_docs.generate_toggle_html` instead. General rule: for a helper used by a function defined in module B and imported into module A, patch B (where the function body resolves the global), even if the test imports the function via A.

## Atualização de conclusão — Auditoria de IA (2026-10-18 — Renato / Termux)
- `MEMORY.md` atualizado (não versionado) com registro completo da auditoria e envio para canais de mensagem.
- `AGENTS.md` atualizado (versionado): esta seção documenta que auditorias de IA exigem inspeção real (`read_file` + `search_files` + `execute_code`), sem suposições; que `reconcile` obrigatório continua válido para docs; que `push` obrigatório para commits; que bloqueios devem ser reportados honestamente (ex: `opencode` bionic no Termux aarch64, `python3.13` indisponível, `ruff` 0.17.1 não linkado, `mkdocs` best-effort bloqueado por `playwright` sem wheel ARM64).
- Artefato de auditoria (`IA_AUDIT_REPORT.md`) produzido no workspace, enviado via `hermes send` para Telegram (`8523376387`, msg IDs 25, 26, 29) e WhatsApp (`3105680842754@lid`, msg IDs `3EB0CB8A...`, `3EB055B2...`, `3EB03B37...`). WhatsApp self-chat não notifica — documentado honestamente, não inventado.
- Convenção reforçada: ao finalizar qualquer tarefa, atualizar obrigatoriamente `MEMORY.md` (fatos duráveis, não sensíveis) e `AGENTS.md` (convenções atualizadas, versionado). Nenhum resultado de push, entrega ou execução deve ser inventado; se falhar, reportar o bloqueio real.

## Atualização automática (gatilho) — 2026-10-18T03:06:47-03:00
- Gatilho executado: `auto_complete_memory_agents.sh`. Atualiza MEMORY.md (fatos duráveis, não sensíveis) e AGENTS.md (convenções, versionado) a cada finalização de tarefa. Nenhum resultado inventado; bloqueios reportados honestamente.

## Estabilização de CI — pacote permanente (2026-11-19)

Regras duráveis após a cascata de falhas recorrentes em PRs (bot × release-please × hooks):

- **Documentation Sync**: triggers apenas `push: main` + schedule (6h) + dispatch. NÃO roda em pull_request nem em branches '*' — bot não commita em branches de PR/release (eliminava checks `action_required`, corridas de push e conflitos em release PRs). Commits do bot levam `[skip ci]` (não re-disparam workflows nem release-please). Reports (`drift_report.json`, `reconcile_summary.md`) vão para `/tmp`, nunca commitados.
- **`drift_report.json`, `reconcile_summary.md`, `pr_body.md` são untracked** (.gitignore) e excluídos do inventário do engine (`REPORT_RELS`). Versioná-los criava self-reference: baseline stale a cada run do bot + conflitos perpétuos em release PRs. O manifest (`docs/.documentation-manifest.json`) continua tracked e é a fonte de verdade.
- **release-please "Sync uv.lock"**: guard de commit vazio (`git diff --cached --quiet`) + `git pull --rebase` antes do push + marcador skip-ci. Lock já em sync no release PR → step não falha mais.
- **Janela transitória pós-release eliminada (2026-11-19, run 44587552679)**: `dependabot-lock-refresh.yml` agora roda também em PRs release-please (guard same-repo mantido) — o lock é sincronizado NO PR, então o merge commit passa no gate. Belt-and-suspenders: o gate `uv lock --check` do python-quality pula commits cuja mensagem contém `chore(main): release` (a mensagem do squash de release NÃO contém `release-please`, então o skip antigo nunca casou).
- **Cuidado com o marcador skip-ci em mensagens de commit**: o GitHub escaneia a mensagem INTEIRA (subject + body). Citar o marcador literal no corpo de um commit (ex.: descrevendo um commit anterior que o usou) faz o push inteiro ser pulado por todos os workflows. Descreva como "skip-ci" ou similar sem os colchetes.
- **pre-commit exclude global**: `^(tests/golden/|tests/__snapshots__/|releases/)` — conteúdo byte-exact NUNCA passa por whitespace/EOF fix (corrompia characterization tests e invalidaria fingerprints de release).
- **Após sweep de higiene em docs, re-reconcile ANTES de commitar o manifest** — o baseline precisa refletir os blobs finais (esquecer isso deixa MANIFEST_STALE_SHA em main).
- Hooks pre-push com stash conflict abortam o push mesmo com gates verdes; se o tree já está limpo de fixes, o push passa. `--no-verify` só com justificativa registrada.

## Cache Layer conventions (ADR-011, 2026-11-19)

- **Facade única**: `src/cache_manager.py` (`CacheManager`/`CacheStats`). Primitivas transversais em `src/cache_io.py` (escrita atômica temp+fsync+os.replace, `FileLock` fcntl/msvcrt, checksum SHA-256 canônico, quarentena rotacionada). Estado incremental em `src/processed_releases.py` (`ProcessedReleasesStore`, fingerprint + single-flight).
- **Toda escrita de cache passa pela camada** — nunca `write_text` direto em arquivos de cache. Payloads carregam `schema_version` + `checksum`; corrupção → quarentena + rebuild + miss, nunca exceção não tratada.
- **TTLs, budgets e nomes centralizados** em `src/config.py` (seção "Cache Layer (ADR-011)"). `ttl=-1` = nunca expira; `ttl=0` = expiração imediata (semântica legada dos adapters de invalidate, congelada por testes).
- **`PARSER_VERSION`** em config.py: bump manual quando mudanças no parser alterarem conteúdo gerado (invalida fingerprints).
- **`clear_expired()` é preguiçoso** (namespaces tocados na sessão); varredura completa só via `full_scan=True`, `maintenance()` ou `scripts/cache_maintenance.py` (finalizer de CI). Limpeza toca SOMENTE `cache/` runtime — nunca `releases/`.
- **`cache/` é runtime, NÃO versionado** (contradição doc×.gitignore resolvida pelo ADR-011). Histórico auditável = artefato `pipeline-cache` dos workflows + `releases/`.
- **Testes de cache**: relógio injetado (`clock=`), proibido `time.sleep`; multiprocesso via `os.fork` + `os.pipe` (kernel Termux/Android bloqueia semáforos POSIX — `multiprocessing.Event/Pool/Queue` falham com PermissionError).
- **mutmut**: usar `mutmut==2.5.0` neste kernel (3.x usa Pool/semáforos). Config `[tool.mutmut]` no pyproject (escopo cache). Execução local via adapter de thread quando semáforos são bloqueados; em CI ubuntu o runner padrão funciona. Baseline py3.14 com `except A, B:` (PEP 758) precisa normalização para parso. Resultado autoritativo = visão do feeder (`get_cached_mutation_statuses`), NÃO agregação SQL crua da tabela `Mutant` — runs interrompidos deixam linhas órfãs `untested` com mapeamento line/index antigo que não correspondem aos mutantes do código atual.
- **Cobertura do módulo de cache ≥95%** (atual: cache_io 100%, processed_releases 100%, cache_manager 97%).
- `except (A, B) as exc:` com binding é a forma black-estável; PEP 758 sem parênteses é válido em py3.14 mas quebra parso/ferramentas antigas.
