# Plano de Modernização — Salesforce-WebDev

> Gerado em 2026-11-14 | Baseline: commit `eab530d` (HEAD)

---

## 1. Arquitetura Atual (Snapshot)

### 1.1 Visão Geral
Pipeline ETL para extração, classificação e versionamento das Salesforce Release Notes:
- **Linguagem**: Python 3.14 (via `uv`, `requires-python = ">=3.14,<3.15"`)
- **Core**: BeautifulSoup4, Playwright (Chromium), Pydantic v2, FastAPI
- **IA**: `LLMService` com cadeia OpenRouter → OpenCode → Gemini (fallback automático, retry/backoff)
- **Qualidade**: Ruff, Black (py314), Mypy strict, Pytest (95%+ cobertura, branch)
- **CI/CD**: GitHub Actions (pinned SHAs), pre-commit hooks, Dependabot
- **Docs**: MkDocs Material + `docs_sync_engine.py` (determinístico, LLM-free)
- **Deploy**: Docker multi-stage, K8s manifests (`k8s/`)

### 1.2 Estrutura de Módulos (`src/`)
```
src/
├── main.py                    # Entry point + PipelineConfig + DI
├── orchestrator.py            # PipelineOrchestrator (coordenação)
├── scraper.py                 # Playwright + Circuit Breaker + Rate Limiter
├── parser.py                  # FeatureImpactParser (HTML → estruturado)
├── llm_service.py             # Multi-provider LLM (núcleo de IA)
├── feature_classifier.py      # Classificação via LLM
├── feature_enricher.py        # Enriquecimento AI por feature
├── release_summarizer.py      # Resumos executivos por release
├── release_docs.py            # Geração de documentação por release
├── generator.py               # MarkdownGenerator
├── config.py                  # Configuração central (dataclasses)
├── exceptions.py              # Hierarquia de exceções
├── circuit_breaker.py         # Circuit Breaker unificado
├── cache_manager.py           # Cache TTL + content-hash
├── health.py                  # Health checks + Prometheus metrics
├── api.py                     # REST + GraphQL + Auth + OpenAPI
├── events.py                  # EventBus pub/sub assíncrono
├── models.py                  # Modelos Pydantic
├── notifications.py           # Email/Slack/Discord
├── salesforce.py              # Trailhead integration
├── feature_classifier.py      # Classificação via LLM
├── heuristic_classifier.py    # Classificação heurística (fallback)
├── impact_analyzer.py         # Análise de impacto
├── issue_triage.py            # Triage automático de issues
├── logger.py                  # Logging JSON + Sentry
├── translator.py              # Tradução via LLM
├── dashboard.py               # Dashboard HTML interativo
├── dashboard_template.html    # Template do dashboard
├── nl_search.py               # Busca semântica
├── i18n.py                    # Internacionalização
├── workflow.py                # Workflow orchestration
├── documentation_service.py   # Serviço de documentação
├── ai_automation.py           # Automação AI facade
├── analytics.py               # Analytics
├── smart_notifications.py     # Notificações inteligentes
└── automation/                # Pacote de automação AI
    ├── service.py             # AIAutomationService
    ├── reporting.py           # Relatórios AI
    ├── comparison.py          # Comparação entre releases
    ├── impact.py              # Scores de impacto + predição
    ├── content.py             # Deduplicação + content-hash
    ├── export.py              # Exportação JSON/CSV
    ├── github_ops.py          # GitHub Issues
    ├── notifications.py       # Notificações filtradas
    ├── models.py              # Dataclasses
    ├── badge.py               # Badges dinâmicos
    └── ledger/                # Salesforce Feature Evolution Ledger (SFEL)
        ├── models.py          # Pydantic v2: FeatureSnapshot, FeatureLink, LedgerDiff...
        ├── linker.py          # FeatureLinker: 5 níveis matching
        ├── prompts.py         # Prompt builder LLM
        └── service.py         # FeatureEvolutionLedgerService
```

### 1.3 Fluxo de Dados (Pipeline)
```
Salesforce Help (SPA JS) ──► Playwright Scraper ──► FeatureImpactParser
                                                         │
                                                         ▼
                                    ┌─────────────────────────────────┐
                                    │      LLMService (cadeia)        │
                                    │  OpenRouter → OpenCode → Gemini │
                                    └─────────────────────────────────┘
                                                         │
                    ┌────────────────────────────────────┼────────────────────────────────────┐
                    ▼                                    ▼                                    ▼
           feature_classifier.py              feature_enricher.py              release_summarizer.py
           (classificação)                    (enriquecimento)                 (sumarização)
                    │                                    │                                    │
                    └────────────────────────────────────┼────────────────────────────────────┘
                                                         ▼
                                                release_docs.py / generator.py
                                                         ▼
                                                releases/<slug>/<lang>/*.md + .meta.json
                                                         ▼
                                                AI Automation (changelog, diff, relatórios)
                                                         ▼
                                                Distribuição: GitHub Issues, Email, Slack, CHANGELOG
```

---

## 2. Baseline de Qualidade (Executado em 2026-11-14)

| Check | Status | Detalhes |
|-------|--------|----------|
| **Ruff** | ⚠️ 11 erros | ISC004 (concatenação implícita) em `.github/scripts/build_failure_issue.py` (4), `src/ai/llm/client.py` (1), `intelligence/` (6 - UP006, UP045) |
| **Black** | ✅ 0 diffs | Formatação correta |
| **Mypy** | ⚠️ 4 erros | Import errors para `bs4`, `playwright._impl._errors`, `playwright.async_api` — CI usa `--ignore-missing-imports` |
| **Pytest** | ❌ 1 falha + 10 erros | Falha: `test_pipeline_warns_when_prompt_tokens_exceed_context_budget` (git rev-parse falha no test). Erros: fixture `snapshot` ausente (syrupy não instalado local) |
| **Docs Sync Audit** | ⚠️ 17 findings | 3 `MANIFEST_STALE_SHA` (.gitignore, README.en.md, dashboard_template.html), 11 `MANIFEST_NEW_FILE` (design-system), 3 `DOC_NOT_IN_NAV` (ai-generated/*) |

### Cobertura de Testes
- **Total de testes**: ~150 arquivos em `tests/`
- **Testes de snapshot**: 9 snapshots em `tests/__snapshots__/test_snapshot.ambr` (syrupy)
- **Factories**: `tests/factories.py` (8 funções factory)
- **Cobertura alvo**: ≥95% (branch coverage habilitado)

---

## 3. Dívidas Técnicas Identificadas

### 3.1 Críticas (Bloqueiam Modernização)
| ID | Item | Localização | Severidade | Esforço |
|----|------|-------------|------------|---------|
| DT-01 | Testes de snapshot quebrados (fixture `snapshot` ausente) | `tests/test_snapshot.py` | Crítica | Baixo |
| DT-02 | Teste `test_pipeline_warns_when_prompt_tokens_exceed_context_budget` falha (git rev-parse) | `tests/test_ai_docs.py:680` | Crítica | Baixo |
| DT-03 | Ruff errors em scripts CI (ISC004) | `.github/scripts/build_failure_issue.py`, `src/ai/llm/client.py` | Crítica | Baixo |
| DT-04 | Mypy import errors (bs4, playwright) — não bloqueiam CI mas poluem output local | `src/parser.py:15`, `src/scraper.py:20,22,455` | Alta | Médio |
| DT-05 | `intelligence/` directory com código legado (UP006, UP045) | `intelligence/intelligence_hub/` | Alta | Médio |

### 3.2 Arquiteturais (Refatoração Necessária)
| ID | Item | Descrição | Severidade | Esforço |
|----|------|-----------|------------|---------|
| AR-01 | Separação de camadas incompleta | `src/` tem 30+ arquivos na raiz; mistura pipeline, serviços, I/O, modelos | Alta | Alto |
| AR-02 | Duplicação entre classificadores | `feature_classifier.py`, `heuristic_classifier.py`, `ai/integrations/`, `ai/prompts/classification.py` | Alta | Médio |
| AR-03 | Exceções não centralizadas o suficiente | `exceptions.py` existe mas nem todos módulos usam; tratamento inconsistente | Média | Baixo |
| AR-04 | Configuração dispersa | `config.py` + variáveis de ambiente + hardcoded em vários arquivos | Média | Médio |
| AR-05 | `src/automation/` mistura domínios | ledger, reporting, comparison, impact, content, export, github_ops, notifications, badge | Média | Alto |

### 3.3 Performance e Observabilidade
| ID | Item | Descrição | Severidade | Esforço |
|----|------|-----------|------------|---------|
| PE-01 | Benchmarks básicos apenas | `tests/test_benchmarks.py` existe mas cobertura limitada | Média | Médio |
| PE-02 | Cache policies não instrumentadas | `cache_manager.py` tem TTL mas sem métricas Prometheus de hit/miss | Média | Baixo |
| PE-03 | Circuit breaker sem métricas | `circuit_breaker.py` não expõe state changes | Média | Baixo |
| PE-04 | LLM cost/token tracking manual | `llm_service.py` loga mas não agrega em métricas | Alta | Médio |

### 3.4 IA e Automação
| ID | Item | Descrição | Severidade | Esforço |
|----|------|-----------|------------|---------|
| AI-01 | Prompts hardcoded em múltiplos locais | `ai/prompts/`, `feature_enricher.py`, `release_summarizer.py`, `automation/ledger/prompts.py` | Alta | Médio |
| AI-02 | Fallback chain sem telemetria de qualidade | Não há avaliação automática de qualidade de saída (golden tests) | Alta | Alto |
| AI-03 | `opencode.yml` usa modelo deprecated | `opencode/mimo-v2.6-flash-free` — verificar disponibilidade | Média | Baixo |
| AI-04 | `ai-docs.yml` depende de OpenRouter `:free` apenas | Sem fallback se OpenRouter indisponível | Alta | Médio |

### 3.5 Documentação e Sync
| ID | Item | Descrição | Severidade | Esforço |
|----|------|-----------|------------|---------|
| DS-01 | 3 arquivos ai-generated fora do nav MkDocs | `docs/ai-generated/{release-notes,leadership,roadmap}.md` | Média | Baixo |
| DS-02 | 11 novos arquivos design-system não no manifest | `src/design-system/` | Baixa | Baixo |
| DS-03 | 3 arquivos com SHA stale no manifest | `.gitignore`, `README.en.md`, `src/dashboard_template.html` | Média | Baixo |

---

## 4. Gargalos e Riscos

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **R-01**: Falha total da cadeia LLM (3 provedores down) | Média | Crítico | Implementar classificação heurística robusta como último fallback; alertar via `smart_notifications` |
| **R-02**: Mudança breaking no Salesforce Help SPA | Alta | Alto | Testes de contrato em `parser.py`; monitorar seletores em `docs/SOURCE_SCHEMA.md` |
| **R-03**: Playwright sem wheel ARM64 (Termux/Android) | Confirmado | Médio | Documentar limitação; CI roda em ubuntu-latest (x64) |
| **R-04**: Cota Gemini gratuita esgotada (~20 req/d) | Alta | Médio | Priorizar OpenRouter/OpenCode; implementar budget tracking em `llm_service.py` |
| **R-05**: Token GitHub não edita `.github/workflows/*` | Confirmado | Alto | Nunca prometer push de workflow; produzir diff para humano/admin |
| **R-06**: Syrupy downgrade pytest 9.x → 8.4.2 local | Confirmado | Médio | Usar `uv run --no-sync` ou `python -m pytest` local; CI instala separado |
| **R-07**: Black 26.x + py314 quebra `except (A, B):` sem `as` | Confirmado | Crítico | Regra obrigatória: sempre `except (A, B) as e:` ou `except Exception:` |

---

## 5. Backlog Priorizado (Impacto × Esforço)

### Fase 1 — Engenharia e Qualidade (Semanas 1-2)
| Prioridade | ID | Item | Impacto | Esforço | Responsável |
|------------|----|------|---------|---------|-------------|
| 1 | DT-01 | Fix snapshot tests (instalar syrupy local / ajustar conftest) | Crítico | Baixo | ENGINEER |
| 2 | DT-02 | Fix test_pipeline_warns_when_prompt_tokens_exceed_context_budget | Crítico | Baixo | ENGINEER |
| 3 | DT-03 | Fix Ruff ISC004 em scripts CI | Crítico | Baixo | ENGINEER |
| 4 | DT-04 | Resolver mypy import errors (stubs bs4/playwright) | Alto | Médio | ENGINEER |
| 5 | DT-05 | Mover/remover `intelligence/` legado ou modernizar | Alto | Médio | ENGINEER |
| 6 | AR-03 | Centralizar exceções em `exceptions.py` | Médio | Baixo | ENGINEER |
| 7 | PE-02 | Instrumentar cache_manager com Prometheus hit/miss | Médio | Baixo | OPTIMIZER |
| 8 | PE-03 | Instrumentar circuit_breaker state changes | Médio | Baixo | OPTIMIZER |
| 9 | DS-01 | Adicionar ai-generated/* ao nav MkDocs | Médio | Baixo | ENGINEER |
| 10 | DS-02/03 | Atualizar manifest + reconcile docs | Médio | Baixo | ENGINEER |

### Fase 2 — Arquitetura e Refatoração (Semanas 3-4)
| Prioridade | ID | Item | Impacto | Esforço | Responsável |
|------------|----|------|---------|---------|-------------|
| 11 | AR-01 | Reorganizar `src/` em camadas (pipeline/, services/, io/, models/, core/) | Alto | Alto | ARCHITECT + ENGINEER |
| 12 | AR-02 | Consolidar classificadores (unificar feature_classifier + heuristic + ai/) | Alto | Médio | ENGINEER |
| 13 | AR-04 | Centralizar configuração (Pydantic Settings + env) | Médio | Médio | ENGINEER |
| 14 | AR-05 | Separar `automation/` em subpacotes por domínio | Médio | Alto | ARCHITECT + ENGINEER |
| 15 | AI-01 | Centralizar prompts em `ai/prompts/` com versionamento | Alto | Médio | ENGINEER |
| 16 | AI-03 | Atualizar/validar modelo opencode em `opencode.yml` | Médio | Baixo | ENGINEER |

### Fase 3 — IA Nativa e Automação (Semanas 5-6)
| Prioridade | ID | Item | Impacto | Esforço | Responsável |
|------------|----|------|---------|---------|-------------|
| 17 | AI-02 | Implementar golden tests + avaliação qualidade LLM output | Alto | Alto | ENGINEER + OPTIMIZER |
| 18 | AI-04 | Adicionar fallback provider em `ai-docs.yml` | Alto | Médio | ENGINEER |
| 19 | — | Configurar `.claude/agents/` subagentes especializados | Alto | Médio | ARCHITECT |
| 20 | — | Configurar `.claude/skills/` para fluxos recorrentes | Alto | Médio | ARCHITECT |
| 21 | — | Integrar Claude Code GitHub Action (anthropics/claude-code-action) | Alto | Médio | ENGINEER |
| 22 | — | Auto-triagem de issues com IA (reaproveitar `issue_triage.py`) | Médio | Médio | ENGINEER |
| 23 | — | Code review automático de PRs por agente revisor | Alto | Alto | ENGINEER |

### Fase 4 — Observabilidade e Performance (Semanas 7-8)
| Prioridade | ID | Item | Impacto | Esforço | Responsável |
|------------|----|------|---------|---------|-------------|
| 24 | PE-01 | Expandir benchmarks (scraper, parser, LLM, generator) | Médio | Médio | OPTIMIZER |
| 25 | PE-04 | LLM cost/token tracking em Prometheus + alertas | Alto | Médio | OPTIMIZER |
| 26 | — | Health checks completos (DB, cache, LLM providers) | Médio | Baixo | ENGINEER |
| 27 | — | Dashboard Grafana/Prometheus documentado | Médio | Médio | OPTIMIZER |

### Fase 5 — CI/CD e Release (Semanas 9-10)
| Prioridade | ID | Item | Impacto | Esforço | Responsável |
|------------|----|------|---------|---------|-------------|
| 28 | — | Paralelizar jobs CI (ruff/black/mypy/test independentes) | Médio | Baixo | ENGINEER |
| 29 | — | Cache uv + Playwright browsers em CI | Médio | Baixo | ENGINEER |
| 30 | — | Release automation: Conventional Commits → changelog → tag → GitHub Release | Alto | Médio | ENGINEER |
| 31 | — | Dependabot para actions + Python (já existe lock refresh) | Baixo | Baixo | ENGINEER |

---

## 6. Métricas de Sucesso (Antes/Depois)

| Métrica | Baseline (Atual) | Alvo Pós-Modernização |
|---------|------------------|------------------------|
| **Ruff errors** | 11 | 0 |
| **Black diffs** | 0 | 0 |
| **Mypy errors (src/)** | 4 (import) | 0 |
| **Pytest pass rate** | ~94% (1 falha + 10 errors) | 100% |
| **Cobertura (branch)** | ~95% | ≥95% |
| **Docs sync findings** | 17 | 0 |
| **CI tempo total** | ~8-10 min | <5 min (paralelização + cache) |
| **LLM call latency (p95)** | Não medido | <10s |
| **Cache hit rate** | Não medido | >80% |
| **Circuit breaker trips/day** | Não medido | <5 |
| **Token cost/run (USD)** | Não rastreado | <$0.50 |
| **Arquivos em `src/` raiz** | 30+ | <10 (camadas) |
| **Duplicação código (CPD)** | Não medido | <5% |

---

## 7. Decisões Arquiteturais (ADRs a Criar/Atualizar)

| ADR | Título | Status |
|-----|--------|--------|
| ADR-001 | Parser Strategy | ✅ Existente |
| ADR-002 | GitHub Actions | ✅ Existente |
| ADR-003 | Topic Classification | ✅ Existente |
| ADR-004 | Auto-Healing | ✅ Existente |
| ADR-005 | Documentation Reconciliation | ✅ Existente |
| ADR-006 | Feature Evolution Ledger | ✅ Existente |
| **ADR-007** | **Layered Architecture (Clean Architecture)** | 🔄 **Novo** |
| **ADR-008** | **LLM Provider Abstraction & Fallback Policy** | 🔄 **Novo** |
| **ADR-009** | **AI-Native CI/CD (Claude Code + OpenCode)** | 🔄 **Novo** |
| **ADR-010** | **Observability Stack (Prometheus + Health + Tracing)** | 🔄 **Novo** |
| **ADR-011** | **Configuration Management (Pydantic Settings)** | 🔄 **Novo** |
| **ADR-012** | **Prompt Versioning & Golden Tests** | 🔄 **Novo** |

---

## 8. Próximos Passos Imediatos

1. **ENGINEER**: Criar branch `feat/modernization-phase1-quality` e corrigir DT-01 a DT-05, AR-03, PE-02/03, DS-01/02/03
2. **REVIEWER**: Auditar correções antes do merge (ruff, black, mypy, pytest, docs sync)
3. **ARCHITECT**: Desenhar estrutura de camadas para AR-01 (entregar diagrama + convenções)
4. **OPTIMIZER**: Definir benchmarks base para PE-01 e instrumentação para PE-04

---

## 9. Riscos de Execução

| Risco | Mitigação |
|-------|-----------|
| Mudanças em `src/` quebram testes existentes | Rodar suite completa a cada PR; `tests/factories.py` como fonte única de truth |
| Refatoração AR-01 é grande e arriscada | Fazer em PRs pequenos por camada; feature flags se necessário |
| IA em CI aumenta custo/tempo | Limitar a PRs >500 linhas; cache de respostas LLM; models `:free` only |
| Token não edita workflows | Nunca prometer; sempre entregar diff pronto para humano |
| Syrupy/pytest version conflict | Documentar `uv run --no-sync` no CONTRIBUTING.md |

---

*Este plano será atualizado a cada fase concluída. Métricas antes/depois serão registradas no final de cada fase.*