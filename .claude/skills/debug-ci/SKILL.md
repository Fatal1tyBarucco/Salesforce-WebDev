---
name: debug-ci
description: Diagnosticar falhas de CI/CD: Python Quality, tests, docs sync, release-please. Inclui: logs, reprodução local, fix comum, re-run.
---

# Skill: debug-ci

## Quando Usar
- Workflow `python-quality.yml` falha (ruff, mypy, pytest)
- Workflow `documentation-sync.yml` falha (reconcile, lint, mkdocs)
- Workflow `release_notes_pipeline.yml` falha (scraper, LLM, commit/push)
- Workflow `release-please.yml` não cria Release PR

## Passos

### 1. Identificar Job Falho
```bash
gh run list --workflow=python-quality.yml --limit 5 --json conclusion,createdAt
gh run view <RUN_ID> --log-failed
```

### 2. Reproduzir Localmente
```bash
# Ruff
uv run ruff check .
# Mypy
uv run mypy src/ --ignore-missing-imports
# Tests (sem syrupy conflict)
uv run --no-sync pytest tests/ -x -q
# Tests + coverage (com syrupy)
uv pip install "syrupy>=4.9.0,<5" && uv run pytest tests/ --cov=src --cov-fail-under=95
```

### 3. Fixes Comuns
| Erro | Fix |
|------|-----|
| `ruff` lint errors | `uv run ruff check . --fix` |
| `ruff format` | `uv run ruff format .` |
| `mypy` missing imports | Adicione `types-*` em `pyproject.toml` ou `--ignore-missing-imports` |
| `pytest` ImportError syrupy | `uv pip install "syrupy>=4.9.0,<5"` (downgrade pytest 8.4.2) |
| `pytest` coverage < 95% | Adicione testes ou ajuste `--cov-fail-under` temporário em ADR |
| `docs_sync` mkdocs ARM64 | `continue-on-error: true` já configurado; ignore se best-effort |
| `docs_sync` fix_markdown mutação | `python3 .github/scripts/fix_markdown.py` → `git status` deve ficar limpo |
| Push workflows 403 | **Não fixável por bot** — reporte a humano/admin |

### 4. Re-run Workflow
```bash
gh run rerun <RUN_ID> --failed-jobs
# Ou push commit vazio
git commit --allow-empty -m "ci: trigger re-run" && git push
```

## Validação
Todos os gates passam localmente antes de push.
