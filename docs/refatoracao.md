# Refatoração Python — Status & Auditoria

> Iniciativa contínua de refatoração, auditoria e otimização do código Python de `Salesforce-WebDev`, conduzida sob a diretriz de **Engenheiro de Software Python Sênior + Arquiteto de Integrações Web**.

## Contexto

O repositório automatiza a extração, classificação e versionamento de *Release Notes* da Salesforce (Trailhead) como artefatos Markdown estruturados, com integrações externas (Salesforce Help/SPA via Playwright, LLMs OpenAI/Gemini, GitHub CLI, SMTP/Slack/Discord, API REST/GraphQL).

- **Stack:** `uv` + Python 3.14 · `ruff` · `black` (line-length=100, target py314) · `mypy` (strict em `src/`).
- **Cobertura mínima:** **≥95%** (`--cov-fail-under=95`).
- **Workflow:** 1 branch `refactor/<escopo>` por tarefa → commit incremental → merge em `main` + exclusão da branch; push exige aprovação.

## Regras de Código (tolerância zero)

1. **Null-safety** — tratar `None`/chaves ausentes (`.get()`, Pydantic/Dataclass); nunca `KeyError`/`AttributeError`/`TypeError`.
2. **Nomenclatura explícita** + PEP 8 estrita (sem abreviações).
3. **Resiliência em integrações** — `try/catch` explícito, `timeout` definidos, `retry` (ex.: `tenacity`); evitar `except Exception:` genérico.
4. **Type hints estritos** em todo código novo/refatorado (parâmetros e retornos).
5. **SoC** — separar camada web (Flask/FastAPI/Django) de lógica de negócio e integração; controllers magros.

**Qualidade:** parsear JSON com modelos (Pydantic); testes `pytest` >95% com mocks (`unittest.mock`/`responses`); docstrings (Google/Sphinx).

> Texto canônico da diretriz: [`AGENT_DIRECTIVE.md`](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/blob/main/AGENT_DIRECTIVE.md).

## Status de Conclusão

| Item | Tarefa | Estado | Commit |
|---|---|---|---|
| Fase 1 | `ai_automation.py` (1428 ln) → pacote `src/automation/` (20 arquivos) | ✅ | — |
| Fase 1 | Wrappers duplicados avaliados como obsoletos (sem duplicação real) | ✅ | — |
| Fase 1 | Config hardcoded → `config.py` centralizada (tópicos dinâmicos) | ✅ | — |
| T1 (#2) | Decompor `main.py` (~960→~145 ln); criado `src/release_docs.py` (~323 ln) | ✅ | `06fd95e` |
| T2 (#5) | Higiene de exceções (6 `except...: pass` silenciosos → logging) | ✅ | `d227704` |
| T3 (#3) | Wrappers marcados como resolvidos (`run_gh` vs `_run_gh` distintos; sem remoção de código) | ✅ | `a434213` |
| #20 | Docker support (Dockerfile + `playwright install --with-deps chromium`) | ✅ | `b255f50` |
| #21 | Pre-commit hooks (sem `ruff-format` conflitante com `black`) | ✅ | `af24705` |
| F1 | OpenAPI spec extraída para `src/openapi_spec.json` (209 ln → 3 ln) | ✅ | `7056bf6` |
| F1 | `_execute_graphql()` dividida em 4 handlers menores | ✅ | `7056bf6` |
| F1 | Dashboard HTML extraído para `src/dashboard_template.html` | ✅ | `7056bf6` |
| V1 | LLM: timeout (30s client / 60s asyncio) + retry tenacity (3 tentativas, backoff exponencial) | ✅ | `—` |
| V1 | LLM: hierarquia de exceções corrigida (tipos específicos antes de Exception genérico) | ✅ | `—` |
| V1 | SMTP: timeout de 30s adicionado em `smtplib.SMTP()` | ✅ | `—` |
| V1 | Testes: 30+ novos testes para cobertura (95.01%) | ✅ | `—` |
| CI | Black py314 + `except A, B:` (PEP 758) + `allow-prereleases` em todos os workflows | ✅ | `—` |
| P0 | Hierarquia `exceptions.py` integrada: `ConfigError`, `ScraperError`, `BrowserError`, `LLMError`, `NotificationError`, `GitHubError` | ✅ | `—` |
| P0 | 18 blocos `except Exception` substituídos por exceções específicas | ✅ | `—` |
| P0 | 7 `raise ValueError` em `salesforce.py` → `ConfigError` | ✅ | `—` |
| P0 | Testes atualizados para validar hierarquia de exceções | ✅ | `—` |
| P1 | CircuitBreaker extraído para `src/circuit_breaker.py` (reutilizável, thread-safe) | ✅ | `—` |
| P1 | `scraper.py`: CircuitBreaker inline → módulo compartilhado | ✅ | `—` |
| P1 | `llm_service.py`: ProviderState → CircuitBreaker unificado | ✅ | `—` |
| P1 | `PipelineConfig` dataclass com DI em `run_pipeline()` | ✅ | `—` |

_Status detalhado por tarefa/branch: [`REFATORACAO_STATUS.md`](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/blob/main/REFATORACAO_STATUS.md)._

## Pendente (planejado)

- **T4** (#6) Type stubs · **T5** (#7) Cache com invalidação por content-hash · **T6** (#8) Dependency Injection · **T7** (#9) Event System · **T8** (#10) Async Context Managers.
- **Testes** #11 integração real · #12 property-based · #13 snapshot.
- **Performance** #14 scraping paralelo · #15 updates incrementais · #16 streaming.
- **DX/Infra** #17 CLI (click/typer) · #18 logging estruturado (structlog) · #19 Prometheus · #22 semantic release · #23 GH Actions matrix · #25 benchmarks.

## Auditoria de Integração (Comando de Inicialização)

Maiores vulnerabilidades/anti-patterns mapeados, em ordem de prioridade (V1 → V3):

### V1 — Resiliência de integrações ausente (Regra #3) — **PRÓXIMA**
- `src/llm_service.py`: chamadas OpenAI/Gemini **sem `timeout`** e sem `retry`/`tenacity`; bloco `except (..., Exception)` que torna as capturas específicas redundantes e classifica erros por *string matching* (`"429" in error_msg`, `"quota"`).
- `src/scraper.py::fetch_page`: loop de retry **sem backoff** (`asyncio.sleep`) e sem reset de `self._browser = None` em falha — inconsistente com `fetch_page_raw_text`, que já faz ambos.
- `src/notifications.py`: `smtplib.SMTP(...)` **sem `timeout`** (pode bloquear indefinidamente).

### V2 — Cache fragmentado / sem invalidação por content-hash (SoC / T5)
- `CacheManager` (TTL) instanciado em `scraper.py` **e** cache JSON manual em `salesforce.py` (`notifications/trailhead_cache.json`, caminho hardcoded). Nenhum utiliza content-hash.

### V3 — Violação de SoC / god-modules + singletons globais (Regra #5 / T6)
- `src/api.py` (617 ln): roteamento HTTP + **GraphQL implementado por regex** + geração de spec OpenAPI no mesmo arquivo.
- `src/salesforce.py` (537 ln): mapeamento de dados + cálculo de org-limits + geração de markdown + cache, com singleton global mutável.
- `SalesforceReleaseScraper` cria seu próprio `CacheManager` internamente (não DI-injetável).

## Próximo passo

Iniciar **V1 — Resiliência de Integrações**: `timeout` + `tenacity` (retry/backoff) + tratamento por **tipo** em LLM / scraper / SMTP, mantendo a cobertura ≥95%.
