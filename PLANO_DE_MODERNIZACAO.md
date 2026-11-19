# Plano de Modernização — Salesforce-WebDev

> **Baseline da Auditoria FASE 0** — 2026-11-14
> Branch: `feat/phase1-consolidate-architecture` | HEAD: `8b77069`
> Python: 3.14.6 | uv: lockfile frozen | Pytest: 9.1.1 | Ruff: 0.5.x | Black: 26.10.1 | Mypy: 1.8+

---

## 1. Arquitetura Atual (Snapshot)

### Estrutura de Módulos (`src/` — 107 arquivos `.py`)

```
src/
├── core/                    # NOVO (vazio no baseline) — domínio puro, sem frameworks
│   ├── classification/
│   ├── enrichment/
│   ├── pipeline/
│   └── summarization/
├── infrastructure/          # NOVO (adapters, I/O, frameworks)
│   ├── api/                 # FastAPI routes + DI
│   ├── github/              # PyGithub adapters
│   ├── llm/                 # OpenAI/Google/OpenRouter clients
│   ├── messaging/           # Email/Slack/Discord
│   ├── notification_step/   # Step functions
│   ├── parsing/             # BeautifulSoup/Playwright adapters
│   ├── scraping/            # Playwright adapters
│   ├── storage/             # FileSystem/S3 adapters
│   ├── translation/         # LLM translation adapters
│   ├── generation.py        # Markdown generation
│   ├── github.py            # GitHub operations facade
│   ├── llm.py               # Unified LLM client (GRANDE: 36k linhas)
│   ├── messaging.py         # Messaging facade
│   ├── parsing.py           # HTML/Markdown parsing
│   ├── scraping.py          # Scraping facade
│   ├── storage.py           # Storage facade
│   └── translation.py       # Translation facade
├── models/                  # NOVO — Pydantic v2 models
│   ├── api.py
│   ├── classification.py
│   ├── enrichment.py
│   ├── feature.py
│   └── release.py
├── services/                # NOVO (vazio) — application services
├── automation/              # LEGADO — AI automation (ledger, reporting, etc.)
├── impact_propagation/      # LEGADO — graph-based impact analysis
├── limiters/                # Rate limiter + circuit breaker
├── ai/                      # LEGADO — AI orchestration, prompts, generators
│   ├── collectors/
│   ├── config/
│   ├── generators/
│   ├── integrations/
│   ├── llm/
│   ├── orchestrator.py      # 29k linhas
│   ├── prompts/
│   └── schemas/
├── *.py (raiz src/)         # LEGADO — 26 módulos monolíticos misturados
│   ├── main.py              # 32k linhas — entry point + DI + pipeline
│   ├── orchestrator.py      # 13k linhas — pipeline coordination
│   ├── scraper.py           # 26k linhas — Playwright + circuit breaker
│   ├── parser.py            # 23k linhas — Feature Impact parsing
│   ├── llm_service.py       # 15k linhas — multi-provider LLM fallback
│   ├── feature_classifier.py
│   ├── feature_enricher.py
│   ├── release_summarizer.py
│   ├── release_docs.py
│   ├── generator.py
│   ├── config.py
│   ├── exceptions.py
│   ├── circuit_breaker.py
│   ├── cache_manager.py
│   ├── health.py
│   ├── api.py               # 20k linhas — REST + GraphQL
│   ├── events.py
│   ├── models.py (DELETADO) # substituído por src/models/
│   ├── notifications.py
│   ├── salesforce.py
│   ├── feature_classifier.py
│   ├── heuristic_classifier.py
│   ├── impact_analyzer.py
│   ├── issue_triage.py
│   ├── logger.py
│   ├── translator.py
│   ├── dashboard.py
│   ├── nl_search.py
│   ├── i18n.py
│   ├── smart_notifications.py
│   ├── workflow.py
│   ├── documentation_service.py
│   ├── ai_automation.py
│   ├── analytics.py
│   └── release_discovery.py
```

### Fluxo de Dados Atual (Simplificado)

```
Salesforce Help (SPA JS)
    │
    ▼
┌─────────────────────────────────────────┐
│ scraper.py (Playwright + Circuit Breaker)│
│   → Rate Limiter (token-bucket 2 req/s)  │
│   → Cache TTL 24h/30d (content-hash)     │
└─────────────────────────────────────────┘
    │ HTML bruto
    ▼
┌─────────────────────────────────────────┐
│ parser.py (FeatureImpactParser)         │
│   → Extração de tabelas + hierarquia    │
└─────────────────────────────────────────┘
    │ Features + Topic Tree
    ▼
┌─────────────────────────────────────────┐
│ LLMService (fallback chain)             │
│   OpenRouter → OpenCode → Gemini        │
│   tenacity retry 3x, backoff 2-10s      │
│   timeout 60s                           │
└─────────────────────────────────────────┘
    │ Classificação, Enriquecimento, Sumarização
    ▼
┌─────────────────────────────────────────┐
│ generator.py / release_docs.py          │
│   → Markdown pt_BR + en_US + .meta.json │
└─────────────────────────────────────────┘
    │
    ▼
GitHub Issues / Email / Slack / CHANGELOG / Dashboard
```

---

## 2. Baseline de Qualidade (Resultados da Auditoria)

| Check | Status | Detalhes |
|-------|--------|----------|
| **Ruff** | ❌ **31 erros** | 27 fixáveis (`--fix`); 4 não-fixáveis (redefinição `get_diff`, imports não usados em testes) |
| **Black** | ❌ **8 arquivos** | `src/infrastructure/api/routes.py` + 7 arquivos de teste `test_infrastructure_*.py` |
| **Mypy** | ❌ **1 erro** | `src/infrastructure/api/routes.py:216` — `get_diff` redefinido (linha 124 e 216) |
| **Pytest + Coverage** | ❌ **93%** | Falha: `cov-fail-under=95` (atual 92.97%); 1875 passed, 2 skipped |
| **Docs Sync Audit** | ❌ **29 findings** | `DOC_NOT_IN_NAV: 3`, `MANIFEST_STALE_SHA: 5`, `MISSING_API_DOC: 21` |

### Cobertura por Módulo (abaixo de 95%)

| Módulo | Coverage | Linhas Missing |
|--------|----------|----------------|
| `src/main.py` | **74%** | 102 stmts — CLI args, dry-run, error paths, report generation |
| `src/orchestrator.py` | **73%** | 43 stmts — pipeline branches, error handling |
| `src/models/release.py` | **75%** | 10 stmts — validation paths |
| `src/models/feature.py` | **87%** | 7 stmts — edge cases |
| `src/models/classification.py` | **94%** | 3 stmts |
| `src/llm_service.py` | **93%** | 9 stmts — fallback branches, provider errors |
| `src/ai/collectors/change_collector.py` | **89%** | 10 stmts |
| `src/ai/integrations/salesforce.py` | **94%** | 4 stmts |
| `src/ai/integrations/trailhead.py` | **94%** | 2 stmts |
| `src/ai/prompts/classification.py` | **85%** | 5 stmts |
| `src/infrastructure/parsing.py` | **90%** | 6 stmts |
| `src/infrastructure/llm.py` | **91%** | 74 stmts (maior gap absoluto) |
| `src/automation/ledger/linker.py` | **92%** | — |
| `src/automation/ledger/service.py` | **93%** | — |

---

## 3. Dívidas Técnicas Identificadas

### 3.1 Arquiteturais (Críticas)

| ID | Descrição | Severidade | Localização | Esforço |
|----|-----------|------------|-------------|---------|
| **ARCH-01** | **Monólito em `src/` raiz** — 26 módulos misturam domínio, aplicação, I/O, frameworks. Viola Clean Architecture (domínio depende de FastAPI, Playwright, Pydantic). | 🔴 Crítica | `src/*.py` (raiz) | Alto |
| **ARCH-02** | **`infrastructure/llm.py` = 36k linhas** — God object: cliente unificado, retry, fallback, pooling, schemas, tudo junto. Impossível testar/mockear isoladamente. | 🔴 Crítica | `src/infrastructure/llm.py` | Alto |
| **ARCH-03** | **`ai/orchestrator.py` = 29k linhas** — Orquestração + prompts + coleta + geração + publicação. Múltiplas responsabilidades. | 🔴 Crítica | `src/ai/orchestrator.py` | Alto |
| **ARCH-04** | **`main.py` = 32k linhas** — Entry point + DI container + pipeline steps + CLI + relatórios AI. | 🔴 Crítica | `src/main.py` | Alto |
| **ARCH-05** | **`scraper.py` = 26k linhas** — Playwright + circuit breaker + rate limiter + cache + parsing misturados. | 🟠 Alta | `src/scraper.py` | Médio |
| **ARCH-06** | **`release_docs.py` = 31k linhas** — Geração Markdown + i18n + meta + templates tudo junto. | 🟠 Alta | `src/release_docs.py` | Médio |
| **ARCH-07** | **Duplicação `orchestrator.py` (raiz) vs `ai/orchestrator.py`** — Dois orquestradores com sobreposição de responsabilidades. | 🟠 Alta | `src/orchestrator.py` + `src/ai/orchestrator.py` | Médio |
| **ARCH-08** | **`automation/` e `impact_propagation/` fora das camadas** — Módulos legados não alinhados à nova estrutura `core/` + `infrastructure/`. | 🟡 Média | `src/automation/`, `src/impact_propagation/` | Baixo |

### 3.2 Qualidade de Código

| ID | Descrição | Severidade | Localização |
|----|-----------|------------|-------------|
| **QUAL-01** | `get_diff` duplicado em `routes.py` (linhas 124 e 216) — quebra mypy e ruff. | 🔴 Crítica | `src/infrastructure/api/routes.py` |
| **QUAL-02** | 27 erros ruff fixáveis (imports não usados, variáveis não usadas `F841`). | 🟠 Alta | `tests/test_infrastructure_*.py` |
| **QUAL-03** | 8 arquivos fora do padrão Black. | 🟠 Alta | `src/infrastructure/api/routes.py` + 7 testes |
| **QUAL-04** | Cobertura 93% < 95% — gaps em `main.py`, `orchestrator.py`, `llm_service.py`, `infrastructure/llm.py`. | 🟠 Alta | Múltiplos |
| **QUAL-05** | `datetime.utcnow()` deprecado — buscar ocorrências remanescentes. | 🟡 Média | Verificar codebase |
| **QUAL-06** | `except (A, B):` sem `as` — Black 26.x + py314 quebra sintaxe. Verificar se existe. | 🟡 Média | Codebase inteiro |

### 3.3 Testes

| ID | Descrição | Severidade |
|----|-----------|------------|
| **TEST-01** | Testes de infraestrutura (`test_infrastructure_*.py`) têm imports não usados e variáveis não usadas — código morto. | 🟠 Alta |
| **TEST-02** | `tests/conftest.py` stubs `openai`/`google` em `sys.modules` — necessário, mas frágil. | 🟡 Média |
| **TEST-03** | Snapshots syrupy (9) — regenerar com `--snapshot-update` se quebrar. | 🟢 Baixa |
| **TEST-04** | Paralelização `pytest-xdist` configurada mas não validada em CI. | 🟢 Baixa |

### 3.4 Documentação

| ID | Descrição | Severidade |
|----|-----------|------------|
| **DOC-01** | 29 findings no `docs_sync_engine.py audit` — `MISSING_API_DOC: 21` (maioria). | 🟠 Alta |
| **DOC-02** | `MANIFEST_STALE_SHA: 5` — manifest desatualizado vs HEAD. | 🟠 Alta |
| **DOC-03** | `DOC_NOT_IN_NAV: 3` — páginas não linkadas no `mkdocs.yml`. | 🟡 Média |
| **DOC-04** | ADR-007 existe (`docs/architecture/decisions/adr-007-clean-architecture.md`) mas não está no `mkdocs.yml` nav. | 🟡 Média |

### 3.5 CI/CD e Automação

| ID | Descrição | Severidade |
|----|-----------|------------|
| **CI-01** | **Nenhum token edita `.github/workflows/*`** — convenção do AGENTS.md: mudanças de workflow = diff pronto + bloqueio para humano. | 🔴 Crítica (processo) |
| **CI-02** | `opencode.yml` usa `mimo-v2.6-flash-free` — validar se modelo ainda existe/disponível. | 🟡 Média |
| **CI-03** | `python-quality.yml` roda `ruff`, `black`, `mypy`, `pytest` sequencial — poderia paralelizar. | 🟢 Baixa |
| **CI-04** | Cache de browsers Playwright e `uv` em CI — validar se configurado. | 🟢 Baixa |

### 3.6 IA e LLM

| ID | Descrição | Severidade |
|----|-----------|------------|
| **AI-01** | `LLMService` (src/llm_service.py) = único ponto de entrada, mas `infrastructure/llm.py` duplicia funcionalidade. | 🔴 Crítica |
| **AI-02** | Cadeia de fallback: OpenRouter → OpenCode → Gemini. Gemini ~20 req/d gratuito — risco de esgotamento. | 🟠 Alta |
| **AI-03** | Prompts em `ai/prompts/` não versionados com schema — drift silencioso. | 🟡 Média |
| **AI-04** | Telemetria de custo/token (`LLMService.usage`) não exposta em `/metrics` (Prometheus). | 🟡 Média |
| **AI-05** | Golden tests com syrupy para qualidade de saída LLM — apenas 9 snapshots. | 🟢 Baixa |

---

## 4. Riscos Priorizados (Impacto × Probabilidade)

| Risco | Impacto | Probabilidade | Score | Mitigação |
|-------|---------|---------------|-------|-----------|
| **R01** Quebra de `main.py`/`orchestrator.py` em refatoração — pipeline para de gerar releases | 🔴 Crítico | Alta | 25 | Testes de contrato + feature flags + rollback automático |
| **R02** `infrastructure/llm.py` monolítico impede troca de provedor/paralelização | 🔴 Crítico | Média | 20 | Extrair adapters (Strategy pattern) + interface única |
| **R03** Cobertura < 95% bloqueia merge — CI falha persistentemente | 🔴 Crítico | Alta | 25 | Adicionar testes nos gaps identificados ANTES de refatorar |
| **R04** `docs_sync_engine.py` audit falha → docs drift → mkdocs build falha | 🟠 Alto | Alta | 16 | `reconcile` obrigatório no fluxo de PR |
| **R05** Token sem permissão em workflows → impossível automatizar fixes de CI | 🟠 Alto | Certa | 20 | Processo humano documentado (já em AGENTS.md) |
| **R06** Black 26.x + py314 quebra `except (A, B):` sem `as` — sintaxe inválida | 🟠 Alto | Média | 12 | Grep codebase + fix preventivo |
| **R07** `ruff` 0.17.1 não linkado no Termux aarch64 — `uv run` obrigatório | 🟡 Médio | Certa | 10 | Documentado; não bloqueia CI (ubuntu-latest) |
| **R08** Playwright sem wheel ARM64 → `mkdocs build` best-effort falha no Termux | 🟡 Médio | Certa | 10 | CI roda em ubuntu; local documentar limitação |

---

## 5. Backlog Priorizado (Impacto × Esforço)

### 🎯 QUICK WINS (Alto impacto, Baixo esforço) — **Fazer IMEDIATAMENTE**

| # | Item | Esforço | Impacto | Arquivos |
|---|------|---------|---------|----------|
| **QW-01** | Fix `get_diff` duplicado + ruff `--fix` + black nos 8 arquivos | 30 min | 🔴 Resolve mypy/ruff/black | `routes.py`, 7 testes |
| **QW-02** | Remover imports/variáveis não usadas nos 7 `test_infrastructure_*.py` | 20 min | 🟠 Limpa ruff | 7 arquivos de teste |
| **QW-03** | `uv run ruff check . --fix && uv run black .` — auto-fix tudo que der | 1 min | 🔴 Gates verdes | Codebase inteiro |
| **QW-04** | Adicionar ADR-007 ao `mkdocs.yml` nav + `reconcile` docs | 15 min | 🟠 Docs sync verde | `mkdocs.yml`, `docs/` |
| **QW-05** | Verificar `except (A, B):` sem `as` — `grep -rn "except (.*):" src/` | 5 min | 🟠 Previne quebra Black | Codebase |
| **QW-06** | Atualizar `docs/.documentation-manifest.json` via `reconcile` | 2 min | 🟠 Manifest SHA = HEAD | `docs/` |

### 🏗️ FASE 1 — MODERNIZAÇÃO DE ENGENHARIA (Tooling + Qualidade + Arquitetura)

| # | Item | Esforço | Dependências | Entregável |
|---|------|---------|--------------|------------|
| **E1.1** | **Expandir regras Ruff** — ativar grupos E, F, I, UP, B, SIM, C4, PERF, RUF; remover ignores gradualmente com justificativa | 2h | QW-01..03 | `pyproject.toml` atualizado, 0 erros ruff |
| **E1.2** | **Mypy strict limpo** — eliminar `# type: ignore` desnecessários; manter apenas para deps opcionais | 2h | QW-01 | `uv run mypy src/` = 0 erros |
| **E1.3** | **Consolidar exceções** — `src/exceptions.py` única hierarquia; padronizar `except (A, B) as exc:` | 3h | E1.1 | `src/exceptions.py` + uso consistente |
| **E1.4** | **Separar camadas Clean Architecture** — mover domínio para `src/core/`, adapters para `src/infrastructure/`, models para `src/models/`, services para `src/services/` | 8h | E1.3 | Estrutura alinhada, imports unidirecionais |
| **E1.5** | **Extrair `infrastructure/llm.py`** — Strategy pattern: `LLMClient` interface + adapters `OpenRouterClient`, `OpenCodeClient`, `GeminiClient`; remover god object | 6h | E1.4 | `src/infrastructure/llm/` (pacote) |
| **E1.6** | **Unificar orquestradores** — `src/orchestrator.py` (pipeline ETL) + `src/ai/orchestrator.py` (AI docs) → `src/core/pipeline/orchestrator.py` + `ai_docs_orchestrator.py` | 4h | E1.4 | 2 serviços claros, sem duplicação |
| **E1.7** | **Slim `main.py`** — delegar para `PipelineOrchestrator` + `CLIHandler` + `ReportGenerator`; < 500 linhas | 4h | E1.6 | `src/main.py` enxuto |
| **E1.8** | **Slim `scraper.py`** — separar `PlaywrightScraper` + `CircuitBreaker` + `RateLimiter` + `CacheManager` em adapters | 4h | E1.4 | `src/infrastructure/scraping/` modular |
| **E1.9** | **Slim `release_docs.py`** — `MarkdownGenerator` + `I18nRenderer` + `MetaWriter` em `src/infrastructure/generation/` | 3h | E1.4 | Geração desacoplada |
| **E1.10** | **Benchmarks expansivos** — `tests/test_benchmarks.py` com `pytest-benchmark`; medir scraping, parsing, LLM calls, geração | 3h | E1.4 | Baseline de performance |

### 🤖 FASE 2 — IA EM TODOS OS PROCESSOS (AI-Native)

| # | Item | Esforço | Dependências | Entregável |
|---|------|---------|--------------|------------|
| **A2.1** | **`.claude/settings.json`** — hooks: PostToolUse (ruff+black), PreToolUse (block workflows/*), Stop (lembrete AGENTS.md/MEMORY.md) | 1h | — | Config versionada |
| **A2.2** | **Subagentes `.claude/agents/`** — `architect-reviewer`, `python-quality`, `security-auditor`, `docs-sync`, `performance-optimizer` | 2h | A2.1 | 5 agentes especializados |
| **A2.3** **| Skills `.claude/skills/`** — `fix-quality-issue`, `release-pipeline`, `docs-reconcile`, `add-feature` (scaffolding testes+docs+ADR) | 2h | A2.1 | 4 skills reutilizáveis |
| **A2.4** | **Code Review AI automático** — GitHub Action (`anthropics/claude-code-action@sha`) posta review no PR antes do humano | 3h | A2.1, CI-01 | PRs com review IA |
| **A2.5** | **Auto-triagem Issues** — reaproveitar `src/issue_triage.py` + GitHub Action para classificar/rotular/priorizar | 2h | A2.1 | Issues triadas automaticamente |
| **A2.6** | **LLM Service Observability** — expor `usage` (tokens, custo, latência) em `/metrics` Prometheus; alertas de cota | 2h | E1.5 | Dashboard de custos LLM |
| **A2.7** | **Cache de respostas LLM** — `CacheManager` namespace `llm` com content-hash do prompt; TTL configurável | 2h | E1.5 | Redução ~30% chamadas LLM |
| **A2.8** | **Fallback multi-provedor robusto** — health check ativo por provedor; circuit breaker por provider; métricas de sucesso/falha | 3h | E1.5, A2.6 | 99.9% disponibilidade LLM |
| **A2.9** | **Golden tests syrupy para qualidade LLM** — snapshots de classificação, enriquecimento, sumarização; threshold de similaridade | 3h | A2.7 | Qualidade de saída mensurável |
| **A2.10** | **Documentação viva** — `mkdocstrings` API reference auto; ADR template; `docs-reconcile` skill integra no fluxo | 2h | A2.3, DOC-01 | Docs sempre sincronizadas |

### 🚀 FASE 3 — CI/CD + AUTOMAÇÃO + OBSERVABILIDADE

| # | Item | Esforço | Dependências | Entregável |
|---|------|---------|--------------|------------|
| **C3.1** | **CI paralela** — jobs `ruff`, `black`, `mypy`, `test` em paralelo; cache `uv` + Playwright browsers | 2h | — | CI 40% mais rápido |
| **C3.2** | **Release automation** — Conventional Commits → `changelog` auto → tag → GitHub Release (reaproveitar `update_changelog_auto.py`) | 2h | — | Release one-click |
| **C3.3** | **Health checks completos** — `/health`, `/ready`, `/metrics` com `prometheus-client`; dashboards documentados | 2h | A2.6 | Observabilidade produção |
| **C3.4** | **Dependabot + lock refresh semanal** — `.github/dependabot.yml` para actions + Python; PRs automáticos | 1h | — | Deps sempre atualizadas |
| **C3.5** | **Security gate** — `pip-audit` / `dependency-review` em CI; SARIF upload para CodeQL | 2h | — | Zero CVEs conhecidos |
| **C3.6** | **Workflow fix process** — template PR description para mudanças em `.github/workflows/*` (humano aplica) | 30 min | CI-01 | Processo documentado |

---

## 6. Métricas de Sucesso (KPIs)

| Métrica | Baseline (2026-11-14) | Target FASE 1 | Target FASE 2 | Target FASE 3 |
|---------|----------------------|---------------|---------------|---------------|
| **Ruff errors** | 31 | 0 | 0 | 0 |
| **Black diffs** | 8 arquivos | 0 | 0 | 0 |
| **Mypy errors** | 1 | 0 | 0 | 0 |
| **Test Coverage** | 92.97% | ≥95% | ≥97% | ≥98% |
| **Branch Coverage** | ~85% | ≥90% | ≥95% | ≥95% |
| **Docs Sync Findings** | 29 | 0 | 0 | 0 |
| **CI Time (total)** | ~3 min | <2 min | <90s | <60s |
| **LLM Calls/Run** | ~200 | ~150 (cache) | ~100 (cache + batch) | ~80 |
| **LLM Cost/Run (est.)** | $0.15 | $0.10 | $0.06 | $0.05 |
| **God Objects (>1k linhas)** | 7 | 0 | 0 | 0 |
| **Cyclomatic Complexity (avg)** | ~15 | <10 | <8 | <6 |
| **Duplicate Code %** | ~12% | <5% | <3% | <2% |

---

## 7. Sequência de Execução Recomendada

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUICK WINS (Dia 1)                           │
│  QW-01 → QW-02 → QW-03 → QW-04 → QW-05 → QW-06                 │
│  ✅ Gates: ruff=0, black=0, mypy=0, docs=0                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FASE 1 — Engenharia (Semanas 1-3)              │
│  E1.1 → E1.2 → E1.3 → E1.4 → E1.5 → E1.6 → E1.7 → E1.8 → E1.9  │
│  Paralelo: E1.10 (benchmarks)                                   │
│  ✅ Gates: coverage ≥95%, 0 god objects, clean arch             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FASE 2 — AI-Native (Semanas 3-5)               │
│  A2.1 → A2.2 → A2.3 → A2.4 → A2.5 → A2.6 → A2.7 → A2.8 → A2.9  │
│  Paralelo: A2.10 (docs viva)                                    │
│  ✅ Gates: review IA em 100% PRs, custos LLM -40%, golden tests │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FASE 3 — CI/CD + Ops (Semanas 5-6)             │
│  C3.1 → C3.2 → C3.3 → C3.4 → C3.5 → C3.6                       │
│  ✅ Gates: CI <60s, release automated, observabilidade completa │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Decisões Arquiteturais (ADRs a Criar/Atualizar)

| ADR | Título | Status | Fase |
|-----|--------|--------|------|
| ADR-001 | Parser Strategy (HTML vs Markdown) | ✅ Existe | — |
| ADR-002 | GitHub Actions Pinning | ✅ Existe | — |
| ADR-003 | Topic Classification (LLM vs Heuristic) | ✅ Existe | — |
| ADR-004 | Auto-Healing Pipeline | ✅ Existe | — |
| ADR-005 | Documentation Reconciliation | ✅ Existe | — |
| ADR-006 | Feature Evolution Ledger (SFEL) | ✅ Existe | — |
| **ADR-007** | **Clean Architecture Migration** | 📝 **Rascunho existe** | **FASE 1** |
| **ADR-008** | **LLM Provider Strategy Pattern** | ❌ Novo | **FASE 1** |
| **ADR-009** | **AI-Native Development Workflow** | ❌ Novo | **FASE 2** |
| **ADR-010** | **Observability & Cost Governance** | ❌ Novo | **FASE 3** |

---

## 9. Bloqueiros Conhecidos (Honestos, Não Inventados)

| Blocker | Descrição | Workaround |
|---------|-----------|------------|
| **B01** | **Nenhum token edita `.github/workflows/*`** — GitHub App + `GITHUB_TOKEN` retornam 403 | Produzir diff pronto; humano aplica; documentar em PR |
| **B02** | **Termux aarch64: `ruff` 0.17.1 não linkado, `python3.13` indisponível, `playwright` sem wheel ARM64** | CI roda em `ubuntu-latest`; local usar `uv run`; documentar limitação |
| **B03** | **`mkdocs build` best-effort falha no Termux** | Validar docs via `python3 .github/scripts/docs_sync_engine.py audit` apenas |
| **B04** | **`pytest-syrupy` downgrade pytest 9.x → 8.4.2** | Instalar via `uv pip install` no CI apenas; local `uv run --no-sync` |
| **B05** | **`opencode` bionic build no Termux** — não é glibc oficial | Não depender de `opencode` local; CI usa ubuntu |

---

## 10. Próximos Passos Imediatos (Pós-Fase 0)

1. **Aprovar este plano** — confirmar priorização e escopo
2. **Criar branch `feat/phase1-engineering`** — iniciar Quick Wins
3. **Executar QW-01 a QW-06** — gates verdes em < 1h
4. **Atualizar `AGENTS.md`** — registrar convenções novas (ex: `reconcile` obrigatório, hooks)
5. **Atualizar `MEMORY.md` (local)** — registrar decisões desta sessão
6. **Sincronizar GitHub Project (ID 5)** — issues em `In Progress` para Quick Wins

---

> **Nota:** Este plano é vivo. Ao final de cada fase, o `REVIEWER` audita, o `OPTIMIZER` mede, e o `PLANO_DE_MODERNIZACAO.md` é atualizado com métricas reais (antes/depois), itens concluídos, e backlog ajustado. Nenhuma métrica é inventada — todas baseadas em execução real.
