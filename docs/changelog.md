# Changelog — Documentação (fundido com raiz)

> **Fonte de verdade completa:** este arquivo funde `CHANGELOG.md` (raiz, histórico oficial) + melhorias grandes da documentação/projecto. Atualizações automáticas de grande impacto são inseridas pelo bot (`update_changelog_auto.py`).

---

## Histórico oficial (CHANGELOG.md — raiz)

## 2026-10-17 — Python 3.14 upgrade

- Pinned `requires-python = ">=3.14,<3.15"` (pyproject.toml) and regenerated `uv.lock` (`==3.14.*`).
- Updated all CI workflows to `3.14` (python-quality, pipeline, docs-sync, docs-build, dependabot, copilot, intelligence-hub).
- Updated agent docs, copilot instructions, LLM fallback prompts, and guide prerequisites.
- Aligned Black `target-version` to `py314`; updated README/table references.

---

## Melhorias principais (grande impacto — refatorações + features)

### 3.14 Upgrade (Python + Tooling)

- `pyproject.toml`: pinned `>=3.14,<3.15`; `uv.lock` regenerado.
- CI workflows atualizadas para Python 3.14.
- Black `target-version` alinhado a `py314`; docs e referências sincronizadas.

### Python Quality / CI Gates

- `.github/workflows/python-quality.yml`: gates de ruff, black, mypy, testes + cobertura (>=95%).
- Pre-push hook (`.hooks/pytest-pre-push.sh`) com `pytest -x -q`.
- Lint + formatação + typecheck automatizados em PR.

### Docs Sync Engine (reconcile obrigatório)

- `.github/scripts/docs_sync_engine.py`: audit e reconcile determinístico (LLM-free).
- `docs/.documentation-manifest.json`: fonte de verdade (git-blob SHAs); idempotente.
- Reconcile obrigatório após qualquer alteração em docs; commit + push obrigatório.

### AI-Docs / .ai-logs

- `.ai-collectors`: registros de decisões e logs de agente.
- Convenção `MEMORY.md` (não versionado) para registro de conclusão/bloco.
- Integração com `opencode` (`opencode.yml`, `.github/scripts`); comentários automáticos `/oc fix`.

### Enhanced Search

- `docs/assets/javascripts/enhanced_search.js` + `docs/assets/stylesheets/enhanced_search.css`.
- `docs/maintenance/enhanced-search.md`: documentação da feature de busca aprimorada.
- Seletores CSS e ARIA documentados em `docs/SOURCE_SCHEMA.md`.

### Pipeline Core (`src/`)

- Módulos principais criados/refatorados: `main.py`, `scraper.py`, `parser.py`, `generator.py`, `pdf_parser.py`, `logger.py`.
- Pipeline ETL para extração, classificação e versionamento de release notes.
- Configuração via `config.py` e `release_notes_pipeline.yml`.

### Release Notes Pipeline (CI + K8s)

- `release_notes_pipeline.yml`: definição do pipeline.
- Workflows CI: `docs-sync`, `docs-build`, `pipeline`.
- `Dockerfile` (uv); `k8s/` para deploy; docs sincronizadas com `releases/*`.

### Documentação — Arquitetura

- `docs/architecture/decisions/`: ADRs (ex. ADR-005 — reconciliação de documentação).
- `docs/SOURCE_SCHEMA.md`: esquema de seletores CSS, atributos ARIA, formato de feature impact.
- Nav `mkdocs.yml` single-language (pt-BR); conteúdo em inglês mantido separadamente (`README.en.md`, `releases/*/<lang>/`).

---

## Atualizações automáticas (grande impacto)

Atualizado automaticamente pelo bot `update_changelog_auto.py` quando novos commits de grande impacto são detectados.

- `4f88fd6` — feat(automation): changelog automático para atualizações de grande impacto
- `54d4696` — docs(changelog): inclui todas as melhorias grandes — refatorações e features
- `160aede` — docs(changelog): fix MD001/MD025/MD024/MD032 lint errors
- `f722d2c` — docs(changelog): fix markdown lint errors (MD022/MD032)
- `b8a594e` — docs(changelog): fundir raiz (CHANGELOG.md) + melhorias grandes
- `825cd48` — feat(ai-docs): complete change context and rate-limit handling
- `c88626d` — feat(ai-docs): add OpenRouter free documentation pipeline
- `5288e02` — docs: atualização automática via IA [skip ci]
- `eab530d` — feat(design-system): extract and apply design system to dashboard
- `24c46ea` — feat(phase1): comprehensive test coverage for 95% target (#229)
- `cdabb37` — feat(phase1): add comprehensive test coverage for 95% target
- `406e877` — merge: resolve conflicts with main (Phase 1 quality gates)
- `c698ab5` — docs: fix MD024 duplicate headings in AI-generated docs
- `a9ae928` — docs: reconcile documentation manifest
- `dfb6631` — docs: sync documentation and fix markdown
- `5f59e28` — docs: reconcile navigation and inventory
- `34c8c19` — docs: fix markdown lint errors in DEBITO_TECNICO.md
- `2762747` — docs: final reconcile navigation and inventory
- `b183939` — docs: resolve manifest merge conflict
- `9cd8d75` — docs: sync with remote reconcile
- `e1b30a8` — docs: fix test file links
- `bf45058` — fix: resolve Python Quality gate failures
- `544edf1` — docs: resolve merge conflicts in manifest
- `df8c35c` — docs: refresh documentation manifest baseline after quality fix
- `2aff9fb` — docs: reconcile documentation baseline
- `900b8a6` — fix: resolve all quality gate failures and MCP 1.30.0 compatibility
- `fd9ba39` — style(format): apply Black formatting to fix Python Quality gate
- `6f976ba` — revert: restore Black Format job in Python Quality workflow
- `ed0b6a9` — style(format): apply Black formatting to pass Python Quality gate
- `a5de784` — style(quality): format codebase with black 26.10.1
- `f1761d0` — test: restore scheduled-pipeline workflow
- `d44c366` — fix: remove workflow_dispatch from scheduled-pipeline to test push trigger
- `14a93bd` — test: delete scheduled-pipeline to verify trigger source
- `c5fa520` — fix: restore scheduled-pipeline with only schedule trigger
- `825b23e` — fix: restore scheduled-pipeline with workflow_dispatch
- `344cb42` — fix: add event_name guard to scheduled-pipeline jobs to skip ghost push runs
- `6cd8d37` — refactor(workflows): rewrite AI triage as Python script to handle multiline content
- `22a498f` — feat(intelligence): evoluir para Release Intelligence Hub (release=264) — defensivo
- `885ccbc` — docs: atualização automática via IA [skip ci] (#358)
- `c950ac2` — fix: resolve merge conflicts in docs manifest and drift report
- `a7f2336` — fix: markdown lint errors in docs/index.md (MD025, MD036, MD051)
- `5b2be9e` — docs(agents): record uv.lock check gaps after issue #393 closure
- `63c23bf` — docs: atualização automática via IA [skip ci] (#400)
- `6e82d01` — ci: migrate python-quality.yml from Black to Ruff Format
