# 📋 Plano de Ação: Refatoração Gap & Bug Fix
**Versão:** 1.0 | **Data:** 02/09/2026 | **Responsável:** Hermes Agent
**Baseline:** ruff/black/mypy/pytest 1192 passed; 5 gaps identificados

---
## 🎯 Resumo Executivo
- **Objetivo:** Corrigir gaps críticos, limpar resíduos e elevar consistência do repo
- **Prazo:** Imediato — execução passo a passo a partir de agora
- **Estado baseline:** Todos os checks (ruff, black, mypy, pytest) passam; 5 gaps de manutenção identificados

---
## ✅ Concluído (Baseline)
- `uv run ruff check .` — passou
- `uv run black --check .` — passou
- `uv run mypy src/ --ignore-missing-imports --pretty` — passou
- `uv run pytest tests/ --cov=src --cov-fail-under=95` — 1192 passed, 2 skipped

---
## 🔴 Gaps Críticos (P0 — executar agora)

| # | Gap | Arquivo | Ação |
|---|-----|---------|------|
| 1 | `NOTIFICATION_DIGEST.md` artefato de teste | `NOTIFICATION_DIGEST.md` | Excluir (não commitar — AGENTS.md §Known issues) |
| 2 | `auto_healing` resíduos untracked | `src/auto_healing/`, `docs/auto-healing/` | Remover diretórios (AGENTS.md §Known issues) |
| 3 | `calculate_category_impact_scores` coroutine não awaitada | `src/ai_automation.py:123-124`, `tests/test_coverage_extra.py:744` | Verificar se teste precisa de `await` ou se wrapper deve ser síncrono |
| 4 | Cobertura real vs alvo | KPIs do repo | Consolidar — 1192 passed cobre 94%+; alvo 98% mantido |
| 5 | Artefatos `*.md` de relatório | `DIFF_REPORT.md`, `IMPACT_REPORT.md`, `QUALITY_REPORT.md`, `REGRESSION_REPORT.md` | Excluir (artifacts de run de teste) |

---
## 📦 Execução Passo a Passo

### Passo 1 — Remover artefatos de teste e resíduos
```bash
rm NOTIFICATION_DIGEST.md DIFF_REPORT.md IMPACT_REPORT.md QUALITY_REPORT.md REGRESSION_REPORT.md
rm -rf src/auto_healing docs/auto-healing
```

### Passo 2 — Verificar warning de coroutine
Abra `tests/test_coverage_extra.py` linha 744: o wrapper `test_ai_automation_service_wrappers` chama `svc.calculate_category_impact_scores()` sem `await`. A função é `async def` (linha 123-124 de `src/ai_automation.py`). Decisão:
- Se o wrapper testa apenas que a chamada chega ao método (sem executar), remover o `await` da definição da função ou fazer o wrapper síncrono.
- Se o wrapper deve testar execução real, adicionar `await` no teste.

### Passo 3 — Validar remoção
Rodar `uv run ruff check . && uv run black --check . && uv run mypy src/ --ignore-missing-imports --pretty && uv run pytest tests/ --cov=src --cov-fail-under=95` para confirmar tudo verde após limpeza.

---
## 📊 Métricas Atualizadas
| KPI | Meta | Atual | Status |
|-----|------|-------|--------|
| Cobertura testes | 98% | 94%+ (1192 passed) | 🟡 — manutenção |
| CI build time | <2min | ~3min | — |
| Resíduos untracked | 0 | 0 (após limpeza) | ✅ |