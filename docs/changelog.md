# Changelog — Documentação

Melhorias de grande impacto no projeto. Refatorações e features apenas; atualizações menores de releases estão em `CHANGELOG.md` (raiz).

---

## Melhorias principais

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

Formatado para leitura direta: cada seção com título claro, breve descrição e arquivos-chave envolvidos.

---

## Atualizações automáticas (grande impacto)

- `4f88fd6` — feat(automation): changelog automático para atualizações de grande impacto
- `54d4696` — docs(changelog): inclui todas as melhorias grandes — refatorações e features
