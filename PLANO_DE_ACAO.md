# 📋 Plano de Ação: Modernização Salesforce-WebDev
**Versão:** 1.0 | **Data:** 22/07/2026 | **Responsável:** Renato Barucco

---

## 🎯 Resumo Executivo
- **Objetivo:** Elevar o repositório de 8.2/10 para 9.5/10 (CTA-grade production ready)
- **Prazo Total:** 22/07/2026 → 09/09/2026 (7 semanas)
- **Orçamento:** $350-950/mês (LLM + Infra + Monitoramento)

---

## ✅ Fase 0: Correções Críticas (CONCLUÍDA — 22/07/2026)

| Tarefa | Status | Commit |
|--------|--------|--------|
| Pytest no CI (release pipeline) | ✅ | `fef2cd3` |
| Validação de API keys (LLMService) | ✅ | `fef2cd3` |
| MockLLMService em conftest.py | ✅ | `fef2cd3` |
| Pre-commit + pre-push hooks | ✅ | `88c69be` |
| Ruff extend-select (F401, F821, E741) | ✅ | `fef2cd3` |
| Fix CI: ruff, black, mypy, pytest errors | ✅ | 5 commits |

---

## 🔴 Fase 1: Estabilização (22/07 → 29/07)

| # | Tarefa | Risco | Esforço | Dependência |
|---|--------|-------|---------|-------------|
| 1.1 | Docker multi-stage build (otimizar image ~1.2GB → <500MB) | Alto | 1h | — |
| 1.2 | Health check no Dockerfile (HEALTHCHECK instruction) | Alto | 30min | — |
| 1.3 | Mover *.md internos para docs/internal/ | Baixo | 30min | — |
| 1.4 | Adicionar pytest --durations=10 ao pyproject.toml | Baixo | 10min | — |
| 1.5 | Rate limiting externo (429 do Salesforce) | Médio | 1h | — |

---

## 🟡 Fase 2: Performance (29/07 → 05/08)

| # | Tarefa | Risco | Esforço | Dependência |
|---|--------|-------|---------|-------------|
| 2.1 | Scraping paralelo (asyncio.gather com semáforo) | Alto | 2h | — |
| 2.2 | LLM Batching (batch_size=10 para classificações) | Crítico | 3h | — |
| 2.3 | LLM response cache (já implementado, expandir TTL) | Médio | 1h | — |

---

## 🟢 Fase 3: Arquitetura (05/08 → 19/08)

| # | Tarefa | Risco | Esforço | Dependência |
|---|--------|-------|---------|-------------|
| 3.1 | PipelineOrchestrator (extrair de main.py) | Alto | 4h | — |
| 3.2 | GraphQL parser robusto (graphql-core) | Alto | 2h | — |
| 3.3 | TrailheadService via DI (PipelineConfig) | Médio | 1h | 3.1 |
| 3.4 | CONTRIBUTING.md | Baixo | 1h | — |

---

## 🔵 Fase 4: Observabilidade (19/08 → 02/09)

| # | Tarefa | Risco | Esforço | Dependência |
|---|--------|-------|---------|-------------|
| 4.1 | Prometheus metrics (/metrics endpoint) | Alto | 2h | — |
| 4.2 | Structured logging com structlog | Médio | 2h | — |
| 4.3 | Sentry error tracking | Médio | 1h | — |

---

## ⚪ Fase 5: Infraestrutura (02/09 → 09/09)

| # | Tarefa | Risco | Esforço | Dependência |
|---|--------|-------|---------|-------------|
| 5.1 | Kubernetes manifests (k8s/) | Alto | 3h | 1.1 |
| 5.2 | GitHub Actions matrix (Python 3.12 + 3.13) | Médio | 1h | — |
| 5.3 | Semantic release (versionamento automático) | Médio | 2h | — |

---

## 📊 Métricas de Sucesso (KPIs)

| KPI | Meta | Atual | Status |
|-----|------|-------|--------|
| Cobertura testes | 98% | 94% | 🟡 |
| CI build time | <2min | ~3min | 🟡 |
| Docker image | <500MB | ~1.2GB | 🔴 |
| Custo LLM/release | <$10 | ~$15 | 🟡 |
| Nota auditoria | 9.5/10 | 8.2/10 | 🟡 |

---

## 📅 Cronograma Visual

```
Jul 22 ─────── Jul 29 ─────── Aug 05 ─────── Aug 19 ─────── Sep 02 ─────── Sep 09
  │  Fase 0 ✅  │  Fase 1 🔴  │  Fase 2 🟡  │  Fase 3 🟢  │  Fase 4 🔵  │  Fase 5 ⚪
  │  Concluída  │ Docker+Docs │ Scraping+LLM│ Orchestrator│ Prometheus  │ K8s+Matrix
  │             │ Health+Rate │ Batching    │ GraphQL+DI  │ Sentry+Log  │ Semantic
```
