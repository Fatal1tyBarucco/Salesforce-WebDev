# Relatório de Débito Técnico — Fase 0: Diagnóstico

> **Versão**: 1.0 (2026-11-15)
> **Base**: inspeção estática de `src/`, `tests/`, `.github/workflows/`, `.github/scripts/`, `pyproject.toml`, `.pre-commit-config.yaml`.
> **Método**: análise de código (grep/read), comparação `tests/` vs `src/`, leitura de workflows e scripts. **NÃO** rodou pytest/cobertura.
> **Convenção**: cada item cita `arquivo:linha` como evidência. "Não verificado" = não consegui confirmar no código.

---

## (a) Duplicação de Responsabilidades

| # | Duplicação | Evidência (arquivo:linha) | Avaliação |
|---|------------|---------------------------|-----------|
| 1 | **Scraping**: `src/scraper.py` (legacy, 668 linhas) vs `scraping.py` (adapter, 139 linhas) | `src/scraper.py:76-668` — `SalesforceReleaseScraper` com cache, circuit breaker, rate limiter, PDF download, TOC expansion internos<br>`scraping.py:27-97` — `PlaywrightScrapingAdapter` implementa `ScrapingStep` contract, apenas `execute(url) -> html` | **Confirmado**. Legacy tem toda a lógica de resiliência; adapter é interface fina. Dois caminhos para scraping. |
| 2 | **Parsing**: `src/parser.py` (legacy, 635 linhas) vs `src/infrastructure/parsing.py` (adapter, 242 linhas) | `src/parser.py:33-90` — `ReleaseNotesParser.extract_topic_tree()` usa `li[role="treeitem"]`<br>`src/parser.py:456-536` — `FeatureImpactParser.parse_text()` parsing tabular<br>`src/infrastructure/parsing.py:50-74` — `BeautifulSoupParsingAdapter.execute(html)` retorna `FeatureCategory[]` usando seletores genéricos (`section.slds-card`, `li.feature`) | **Confirmado**. Legacy parsing é específico para Salesforce (TOC + Feature Impact). Adapter é genérico e **não** replica a lógica de Feature Impact — gap funcional. |
| 3 | **LLM**: **Três** implementações de fallback chain multi-provider:<br>① `src/llm_service.py:105-490` (`LLMService`)<br>② `src/infrastructure/llm.py:153-974` (`UnifiedLLMClient` + adapters)<br>③ `src/ai/llm/client.py:259-491` (`ExistingLLMClient` — OpenRouter only) | `src/llm_service.py:49-89` — `_PROVIDER_CHAIN` (OpenRouter -> OpenCode -> Gemini)<br>`src/infrastructure/llm.py:49-89` — **Cópia idêntica** do `_PROVIDER_CHAIN`<br>`src/ai/llm/client.py:18-24` — `OPENROUTER_BASE_URL`, `MAX_ATTEMPTS=4`, `SYSTEM_PROMPT` fixo, **sem fallback** | **Confirmado**. `src/infrastructure/llm.py` **copia** o provider chain de `llm_service.py` (linhas 49-89 idênticas). `src/ai/llm/client.py` é **diferente**: só OpenRouter, quota error = exceção (linha 380-382), sem fallback para Gemini/OpenCode. |
| 4 | **Classificação**: 4 implementações coexistentes | `src/feature_classifier.py` — `FeatureClassifier.classify_text()` usa `LLMService`<br>`src/heuristic_classifier.py` — `HeuristicClassifier.classify_text()` keyword-based<br>`src/ai/integrations/salesforce.py` — `SalesforceIntegration.classify_changes()`<br>`src/ai/prompts/classification.py` — `build_classification_system_prompt()` + `parse_classification_response()`<br>`src/core/classification/service.py:69-244` — `ClassificationService` com strategy LLM/Heuristic/Hybrid + `ClassificationAdapter` contract | **Confirmado**. Clean Arch (`src/core/classification/`) define o contract correto, mas legacy modules não usam. `src/infrastructure/llm.py:797-886` implementa `OpenRouterClassificationAdapter` e `HeuristicClassificationAdapter` para o core. |
| 5 | **Entrypoints**: `src/main.py` (628 linhas) vs `main_clean.py` (não verificado — arquivo não encontrado no glob) | `src/main.py:1-628` — orquestra tudo inline, DI via `PipelineConfig`<br>ADR-007 (`docs/architecture/decisions/adr-007-clean-architecture.md`) menciona `main_clean.py` | **Parcial**. `main_clean.py` **não existe** no branch atual (grep negativo). ADR-007 refere migração planejada não concluída. |
| 6 | **Enriquecimento**: `src/feature_enricher.py` (legacy) vs `src/core/enrichment/service.py` (core) vs `src/infrastructure/llm.py:894-920` (`OpenRouterEnrichmentAdapter`) | `src/feature_enricher.py:74-137` — `enrich_category()` batch por categoria<br>`src/core/enrichment/service.py:82-278` — `EnrichmentService` com strategy LLM/Template/Hybrid<br>`src/infrastructure/llm.py:894-920` — adapter para core | **Confirmado**. Core define contract; legacy `FeatureEnricher` não usa `EnrichmentAdapter`. |
| 7 | **Sumarização**: `src/release_summarizer.py` (legacy) vs `src/core/summarization/service.py` (core) | `src/release_summarizer.py:51-525` — `ReleaseSummarizer` com cache validation + LLM + fallback<br>`src/core/summarization/service.py` — não inspecionado (arquivo existe mas não lido) | **Não verificado** — core service existe mas não confirmei duplicação funcional. |

---

## (b) Acoplamento Excessivo

| # | Problema | Evidência (arquivo:linha) | Avaliação |
|---|----------|---------------------------|-----------|
| 1 | **God Module: `src/main.py`** importa 30+ módulos e orquestra todo pipeline inline | `src/main.py:23-69` — imports de `cache_manager`, `config`, `documentation_service`, `events`, `exceptions`, `generator`, `i18n`, `llm_service`, `logger`, `parser`, `release_docs`, `scraper`, `translator`, `feature_enricher`, `release_summarizer`, `ai_automation`, `impact_analyzer`, `issue_triage`, `smart_notifications`, `feature_classifier`, `release_discovery` | **Confirmado**. `main.py` viola Single Responsibility: detecção, scraping, parsing, enriquecimento, geração, relatórios IA, tudo em um arquivo. |
| 2 | **`LLMService` (legacy) = God Object** combina: provider chain, model selection, fallback logic, retry/backoff, rate limit handling, prompt building, mock responses | `src/llm_service.py:105-490` — 385 linhas, `_PROVIDER_CHAIN`, `_dispatch_to_provider`, `_generate_gemini`, `_generate_openai_compatible`, `generate_completion`, `generate_text`, `classify_text`, `summarize`, `enrich_feature`, `__aenter__`, `__aexit__` | **Confirmado**. Mudar provider toca tudo. Testes de fallback chain não existem (cobertura ~23% per ARQUITETURA.md). |
| 3 | **`SalesforceReleaseScraper`** acopla `CacheManager`, `CircuitBreaker`, `RateLimiter` internamente (não injetados) | `src/scraper.py:92-94` — `self._cache = CacheManager(...)`, `self._circuit_breaker = CircuitBreaker()`, `self._rate_limiter = RateLimiter(...)`<br>`src/scraper.py:346-349` — usa `self._cache.get/set` direto | **Confirmado**. Testes exigem mocks complexos. Não isolável para unit tests. |
| 4 | **Singleton `get_event_bus()`** — estado global mutável | `src/events.py:176-184` — `_default_bus: EventBus &#124; None = None`;`get_event_bus()` cria se `None`<br>`src/main.py:590-591` — `config.event_bus = get_event_bus()`<br>`src/orchestrator.py:49` — `self._bus = config.event_bus or get_event_bus()` | **Confirmado**. Estado global dificulta testes isolados e reasoning sobre fluxo de eventos. |
| 5 | **Imports cruzados legacy <-> clean arch** | `src/main.py:37-39` importa `FeatureImpactParser` de `src.parser` (legacy)<br>`src/main.py:498-500` instancia `FeatureEnricher(llm=translator._llm)` — acessa atributo privado<br>`src/orchestrator.py:158` importa `enrich_meta_with_classification`, `process_single_release` de `src.main` (import circular potencial) | **Confirmado**. `main.py` e `orchestrator.py` têm dependência mútua (orchestrator chama funções de main). |
| 6 | **`FeatureEnricher` acessa `translator._llm` (atributo privado)** | `src/main.py:500` — `enricher = FeatureEnricher(llm=translator._llm if hasattr(translator, "_llm") else None)` | **Confirmado**. Viola encapsulamento; `TranslatorService` não expõe LLM publicamente. |

---

## (c) Gargalos de Performance / I/O

| # | Gargalo | Evidência (arquivo:linha) | Avaliação |
|---|---------|---------------------------|-----------|
| 1 | **Scraper Playwright: waits fixos + TOC expansion sequencial** | `src/scraper.py:210-229` — `wait_until="domcontentloaded"` + `wait_for_selector(..., timeout=15000)` + `wait_for_timeout(5000)` + `scrollTo` + `wait_for_timeout(1000)` + `_expand_toc_nodes()` (loop com `wait_for_timeout(300)` por nó) | **Confirmado**. ~15-30s por página. Em CI com 20+ categorias = 5-10 min só scraping. |
| 2 | **LLM calls sequenciais em `FeatureEnricher.enrich_release()`** | `src/feature_enricher.py:183-212` — `for md_file in sorted(pt_br_dir.glob("*.md")):` -> `await self.enrich_category()` **sequencial** (1 call LLM por categoria) | **Confirmado**. 20-30 categorias x 10-30s = 5-15 min. Poderia usar `asyncio.gather` com semáforo. |
| 3 | **`ReleaseSummarizer.summarize()` envia até 4000 chars por categoria para LLM** | `src/release_summarizer.py:184-186` — `content_fragments.append(f"=== {category_name} ({count} recursos) ===\n{content[:4000]}")` | **Confirmado**. Prompt grande -> mais tokens, mais latência, mais custo. |
| 4 | **`generate_ai_reports_async()` roda TODOS os relatórios IA concorrentemente sem rate limiting** | `src/main.py:358-393` — `asyncio.gather(*all_initial_tasks)` + `asyncio.gather(*triage_tasks)` + `asyncio.gather(*analytics_tasks)` — sem semáforo, pode estourar quota de LLM | **Confirmado**. `LLMService` tem fallback chain mas quota compartilhada; concorrência não controlada. |
| 5 | **`download_pdf_from_button()` relança browser standalone se `self._browser` não existe** | `src/scraper.py:595-606` — `if self._browser:` reusa, senão `async_playwright().start()` novo | **Confirmado**. Overhead de launch Chromium a cada PDF se browser não persistido. |

---

## (d) Riscos Operacionais (Scraper + Exceções)

| # | Risco | Evidência (arquivo:linha) | Avaliação |
|---|-------|---------------------------|-----------|
| 1 | **Seletores CSS hardcoded** — quebra se Salesforce mudar layout | `src/scraper.py:80-87` — `CONTENT_SELECTORS = ["article", "#articleViewContent", ".release-notes-content", "div.content", ".slds-card__body", "main"]`<br>`src/scraper.py:316-321` — `toc_selectors = [".toc-container", "ul.tree", '[role="tree"]', "nav.toc"]`<br>`src/parser.py:24-30` — `TOC_SELECTORS` idênticos | **Crítico**. Falha silenciosa: retorna conteúdo vazio ou parcial. Sem validação de schema do HTML. |
| 2 | **Circuit Breaker threshold=3, cooldown=60s** — pode bloquear pipeline inteiro | `src/scraper.py:71-73` — `CIRCUIT_BREAKER_THRESHOLD = 3`, `CIRCUIT_BREAKER_COOLDOWN = 60`<br>`src/scraper.py:131-133` — `if self._circuit_breaker.is_open: return None` | **Alto**. 3 falhas de rede (comuns em CI) = pipeline para por 60s. Sem métrica de "half-open" para recovery gradual. |
| 3 | **Exceções amplas (`except Exception` / `except BaseException`)** | `src/scraper.py:221` — `except TimeoutError, PlaywrightTimeout, PlaywrightError, Exception:` (tuple com `Exception`)<br>`src/scraper.py:260` — `except (ScraperError, TimeoutError, PlaywrightTimeout, OSError)`<br>`src/llm_service.py:251` — `except Exception as err:` (catch-all no fallback chain)<br>`src/infrastructure/llm.py:297-319` — mesmo padrão | **Alto**. `Exception` no tuple é anti-pattern (pypa/bandit B112). Oculta bugs reais. |
| 4 | **Content comparison frágil** — compara apenas primeiros 500 chars + length | `src/release_discovery.py:267-275` — `if len(current_text) == len(candidate_text) and current_text[:500] == candidate_text[:500]: return False` | **Médio**. False negative se conteúdo muda mas length + prefix iguais. False positive se Salesforce injeta timestamp no topo. |
| 5 | **PDF download via button click** — depende de seletor `button[title='Open PDF']` | `src/scraper.py:610-611` — `await page.wait_for_selector("button[title='Open PDF']", timeout=15000)` | **Médio**. Salesforce pode mudar title/aria-label. Fallback `download_pdf()` usa URL template fixo (linha 647-668) que assume padrão de naming. |
| 6 | **Rate limiter global (2 RPS) compartilhado por todo pipeline** | `src/scraper.py:67-69` — `RATE_LIMIT_RPS = 2`, `RATE_LIMIT_MIN_INTERVAL = 0.5`<br>`src/scraper.py:92` — `self._rate_limiter = RateLimiter(min_interval=RATE_LIMIT_MIN_INTERVAL)` | **Médio**. Gargalo serializado; não distingue entre Feature Impact page vs article pages. |

---

## (e) Gaps de Cobertura de Testes (Análise Estática: `tests/` vs `src/`)

> **Método**: listagem de `src/**/*.py` (excluindo `__init__.py`, `stubs/`) vs `tests/test_*.py`. Não rodou pytest.

| Módulo `src/` | Arquivo de Teste | Status | Evidência |
|---------------|------------------|--------|-----------|
| `src/main.py` (628 linhas) | `tests/test_main.py`, `test_main_coverage.py`, `test_main_coverage_additional.py`, `test_main_coverage_push.py`, `test_main_extra.py`, `test_src_main.py` | **Parcial** | 6 arquivos de teste mas focados em coverage push; `generate_ai_reports_async` escreve arquivos na raiz (test artifacts) — requer `isolated_cwd` fixture |
| `src/orchestrator.py` | `tests/test_orchestrator.py`, `test_orchestrator_coverage.py` | **Parcial** | Testa `PipelineOrchestrator.run()` mas mocks pesados |
| `src/scraper.py` (668 linhas) | `tests/test_scraper.py`, `test_scraper_coverage.py`, `test_scraper_refactored.py`, `test_scraper_retry.py`, `test_scraper_snapshot.py` | **Parcial** | Muitos testes mas `SalesforceReleaseScraper` usa browser real (Playwright) — testes lentos/flaky |
| `src/parser.py` (635 linhas) | `tests/test_parser.py`, `test_src_parser.py`, `test_characterization_parser.py`, `test_characterization_golden.py` | **Bom** | Parser é puro (BeautifulSoup) — testes unitários rápidos |
| `src/llm_service.py` (490 linhas) | `tests/test_llm_service.py` | **Fraco (~23%)** | Fallback chains (OpenRouter->OpenCode->Gemini) não testados; mocks de `openai`/`google.genai` em `conftest.py` stubam imports |
| `src/feature_enricher.py` (379 linhas) | `tests/test_feature_enricher.py` | **Parcial** | Testa fallback mas não path LLM real |
| `src/release_summarizer.py` (525 linhas) | `tests/test_release_summarizer.py` | **Fraco (0% LLM path)** | Cache validation testada; path LLM (`generate_text`) não coberto |
| `src/release_docs.py` (848 linhas) | `tests/test_release_docs.py`, `test_characterization_release_docs.py`, `test_characterization_generator.py` | **Fraco (~6%)** | Funções de geração Markdown (`_generate_release_files`, `_update_single_readme`, `_build_release_block`) pouco testadas |
| `src/release_discovery.py` (344 linhas) | `tests/test_release_discovery.py` | **Parcial** | Testa strategies mas scraper mockado |
| `src/feature_classifier.py` | `tests/test_feature_classifier.py`, `test_feature_classifier_coverage_push.py` | **Parcial** | |
| `src/heuristic_classifier.py` | `tests/test_heuristic_classifier.py` | **OK** | Lógica pura, bem testada |
| `src/translator.py` | `tests/test_translator.py` | **Parcial** | |
| `src/generator.py` | `tests/test_generator_coverage_push.py` | **Fraco** | |
| `src/config.py` | `tests/test_config.py` | **OK** | Constantes e dataclasses |
| `src/events.py` | `tests/test_events.py` | **OK** | EventBus simples |
| `src/cache_manager.py` | `tests/test_cache_manager.py` | **OK** | |
| `src/circuit_breaker.py` | `tests/test_circuit_breaker.py` | **OK** | |
| `src/limiters/rate_limiter.py` | `tests/test_limiters_rate_limiter.py` (não encontrado) | **Ausente** | `RateLimiter` sem teste dedicado |
| `scraping.py` | `tests/test_infrastructure_scraping.py` | **Parcial** | Adapter testado mas não integração |
| `src/infrastructure/parsing.py` | `tests/test_infrastructure_parsing.py` | **Parcial** | |
| `src/infrastructure/llm.py` (974 linhas) | `tests/test_infrastructure_llm.py`, `test_infrastructure_llm_coverage.py` | **Fraco** | `UnifiedLLMClient` + adapters — fallback chains não testados |
| `src/infrastructure/storage.py` | `tests/test_infrastructure_storage.py` | **Parcial** | |
| `src/infrastructure/translation.py` | `tests/test_infrastructure_translation.py` | **Parcial** | |
| `src/infrastructure/github.py` | `tests/test_infrastructure_github.py` | **Ausente** | Não encontrado no glob |
| `src/infrastructure/generation.py` | `tests/test_infrastructure_generation.py` | **Parcial** | |
| `src/infrastructure/notification_step.py` | `tests/test_infrastructure_notification_step.py` | **Parcial** | |
| `src/infrastructure/messaging.py` | `tests/test_infrastructure_messaging.py` | **Ausente** | Não encontrado |
| `src/core/pipeline/steps.py` | `tests/test_core_pipeline_orchestrator.py` | **Parcial** | Contracts testados via mocks |
| `src/core/classification/service.py` | `tests/test_core_classification_service.py` | **Parcial** | |
| `src/core/enrichment/service.py` | `tests/test_core_enrichment_service.py` | **Parcial** | |
| `src/core/summarization/service.py` | `tests/test_core_summarization_service.py` | **Parcial** | |
| `src/impact_propagation/engine.py` | `tests/test_impact_propagation.py` | **Parcial** | |
| `src/ai/orchestrator.py` | (sem teste dedicado) | **Ausente** | `AIOrchestrator` não testado |
| `src/ai/llm/client.py` | `tests/test_ai_docs.py`, `test_ai_docs_coverage.py` | **Parcial** | `ExistingLLMClient` testado indiretamente |
| `src/ai_automation.py` | `tests/test_ai_automation.py` | **Parcial** | |
| `src/issue_triage.py` | `tests/test_issue_triage.py` | **Parcial** | |
| `src/impact_analyzer.py` | `tests/test_impact_analyzer.py` | **Parcial** | |
| `src/smart_notifications.py` | `tests/test_smart_notifications.py` | **Parcial** | |
| `src/documentation_service.py` | `tests/test_documentation_service_coverage.py` | **Parcial** | |
| `src/workflow.py` | `tests/test_workflow.py` | **Parcial** | |
| `src/analytics.py` | `tests/test_analytics.py` | **Parcial** | |
| `src/api.py` | `tests/test_api_coverage.py`, `test_api_auth.py` | **Parcial** | |
| `src/dashboard.py` | `tests/test_dashboard.py` | **Parcial** | |
| `src/health.py` | `tests/test_health.py` | **Parcial** | |
| `src/nl_search.py` | `tests/test_nl_search.py` | **Parcial** | |
| `src/exceptions.py` | (sem teste) | **Ausente** | Exceções customizadas |
| `src/logger.py` | `tests/test_logger.py`, `test_logger_coverage_push.py`, `test_src_logger.py` | **OK** | |
| `src/salesforce.py` | `tests/test_salesforce_refactored.py`, `test_salesforce_coverage.py` | **Parcial** | |
| `src/impact_propagation/models.py` | `tests/test_impact_propagation.py` | **Parcial** | |
| `src/impact_propagation/graph_builder.py` | (sem teste dedicado) | **Ausente** | |
| `src/impact_propagation/heuristic_fallback.py` | (sem teste dedicado) | **Ausente** | |
| `src/automation/service.py` | (sem teste dedicado) | **Ausente** | |
| `src/automation/reporting.py` | `tests/test_automation_reporting.py` | **Parcial** | |
| `src/automation/notifications.py` | `tests/test_automation_notifications_coverage.py` | **Parcial** | |
| `src/automation/export.py` | `tests/test_automation_export.py` | **Parcial** | |
| `src/automation/comparison.py` | (sem teste dedicado) | **Ausente** | |
| `src/automation/badge.py` | `tests/test_automation_badge.py` | **Parcial** | |
| `src/automation/impact.py` | `tests/test_automation_impact.py` | **Parcial** | |
| `src/automation/github_ops.py` | (sem teste dedicado) | **Ausente** | |
| `src/automation/ledger/__init__.py` | `tests/test_ledger/*.py` | **Parcial** | |

**Resumo**: ~113 arquivos `.py` em `src/` (excluindo `__init__`, `stubs`). ~97 arquivos de teste em `tests/`. Muitos módulos `src/infrastructure/`, `src/ai/`, `src/automation/`, `src/impact_propagation/`, `src/core/` **sem arquivo de teste dedicado**. Cobertura real estimada 10-15% (amostragem: parser 95%, main 26%, llm_service 23%, release_docs 6%, release_summarizer 0% path LLM).

---

## (f) Configuração Duplicada / Redundante

| # | Redundância | Evidência | Avaliação |
|---|-------------|-----------|-----------|
| 1 | **Black configurado em 3 lugares** | `pyproject.toml:53-55` — `[tool.black]` line-length=100, target-version=py314<br>`.pre-commit-config.yaml:29-34` — hook local `uv run black` (usa versão do uv.lock)<br>`pyproject.toml:34` — `docs` extra inclui `black==26.10.1` | **Confirmado**. Versão pinada 3x. Pre-commit roda `uv run black` (system) — pode divergir se uv.lock não sincronizado. |
| 2 | **Ruff + Black coexistem** (ambos formatam) | `pyproject.toml:57-71` — `[tool.ruff]` line-length=100, extend-select, ignore<br>`pyproject.toml:53-55` — `[tool.black]`<br>Ruff 0.5+ tem `ruff format` (compatível Black 99%+) | **Confirmado**. Dois formatters = conflito potencial. `target-version=py314` no Black **remove parênteses de `except (A, B):`** -> syntax error em Python 3.14 (AGENTS.md known issue). |
| 3 | **Pytest version conflict**: `pyproject.toml` pin `pytest>=8.0.0,<10` (9.x no lock) mas `syrupy` força downgrade para 8.4.2 localmente | `pyproject.toml:42` — `pytest>=8.0.0,<10`<br>`pyproject.toml:81` — `addopts = "--timeout=120"`<br>CI: `uv pip install "syrupy>=4.9.0,<5"` **após** `uv sync` (python-quality.yml:190) | **Confirmado**. Ambiente local != CI. `uv run --no-sync` ou `python -m pytest` direto necessário localmente. |
| 4 | **Mypy config duplicado**: `pyproject.toml` + pre-commit args divergentes | `pyproject.toml:73-76` — `strict=true`, `mypy_path=stubs`, `warn_unused_ignores=false`<br>`.pre-commit-config.yaml:38-46` — args: `--ignore-missing-imports --disallow-untyped-defs --disallow-incomplete-defs` + `additional_dependencies` (types-*) | **Confirmado**. Pre-commit é **mais estrito** (`--disallow-untyped-defs`) que CI (`--ignore-missing-imports --pretty` only). |
| 5 | **Dependências de dev em múltiplas seções** | `pyproject.toml:39-51` — `[project.optional-dependencies.dev]`<br>`pyproject.toml:91-94` — `[dependency-groups.dev]` (pytest-asyncio, pytest-timeout) | **Confirmado**. `dependency-groups` é padrão novo (PEP 735); `optional-dependencies.dev` é legado. Dois locais para mesma coisa. |
| 6 | **Pre-commit stages inconsistentes** | `.pre-commit-config.yaml:53-59` — `pytest-fast` roda em `pre-push` (bash `.hooks/pytest-pre-push.sh`)<br>`.pre-commit-config.yaml:61-66` — `pytest-coverage` em `manual` only | **Confirmado**. `pre-push` roda testes rápidos sem coverage; `manual` roda coverage. Dois comandos diferentes. |

---

## (g) Custo / Tokens por Execução

> **Busca realizada**: `grep -r "cost\|tokens\|usage" src/ --include="*.py"`, `grep -r "cost\|tokens" .github/scripts/`, `ls docs/ai-generated/`, `ls report_parts/` (não existe), `ls intelligence/` (existe mas separado).

| Artefato | Existência | Observação |
|----------|------------|------------|
| `report_parts/` | **Não existe** | Diretório não encontrado |
| `intelligence/` | Existe | Projeto separado (`intelligence/intelligence_hub/`) com próprios scripts |
| `docs/ai-generated/` | Existe | `roadmap.md`, `release-notes.md`, `leadership.md` — outputs de AI docs pipeline |
| Tracking de custo/tokens em código | **Parcial** | `src/ai/llm/client.py:428-442` — `ExistingLLMClient.generate()` loga `usage_record` com `prompt_tokens`, `completion_tokens`, `total_tokens`, `cost_usd` (linha 436-442)<br>`src/llm_service.py` — **não loga usage/cost**<br>`src/infrastructure/llm.py` — **não loga usage/cost** |

**Conclusão**: **Não mensurável com os artefatos atuais** para o pipeline principal (`release_notes_pipeline.yml`). Apenas `ExistingLLMClient` (usado em `ai-docs.yml`) loga usage/cost. O pipeline principal usa `LLMService` (legacy) ou `UnifiedLLMClient` (infra) que **não expõem nem logam** contagem de tokens ou custo estimado. Não há relatório agregado por execução.

---

## (h) Workflows com Falhas Recentes: Documentation Sync (2026-11-15)

**Fato**: `documentation-sync.yml` teve **4 falhas seguidas antes de passar** em 2026-11-15.

**Investigação do workflow + engine**:

1. **`fix_markdown.py` não rastreia estado de fence open/close** (corrigido em 2026-11-04 per AGENTS.md, mas pode regressar):
   - `.github/scripts/fix_markdown.py` reescreve fences de fechamento (` ``` `) como se fossem de abertura, mutando docs a cada execução -> bot faz commit `docs(sync): reconcile documentation` -> checks pausam em `action_required` (precisa aprovação UI; opencode pushes rodam automaticamente).
   - AGENTS.md confirma: "After editing, run `python3 .github/scripts/fix_markdown.py` and confirm `git status` stays clean on an unchanged tree."

2. **`mkdocs build --strict` best-effort falha em android/arm64 (Termux)**:
   - `documentation-sync.yml:306` — `continue-on-error: true`
   - Playwright não tem wheel ARM64 -> `mkdocs build` falha por dependência transitória (mkdocstrings/griffe) -> não bloqueia mas sinaliza falha no step summary.

3. **Push real falha (não inventado)**:
   - `GITHUB_TOKEN` / opencode GitHub App token **recusam edição de `.github/workflows/*`** (HTTP 403 `refusing to allow a GitHub App without workflows permission`).
   - AGENTS.md: "No available token can edit `.github/workflows/*`. Both the opencode GitHub App token and the Actions `GITHUB_TOKEN` refuse with HTTP 403... Workflow-file fixes must be reported to a human/admin — never claim they were pushed."

4. **Anti-loop guard pode pular execução legítima**:
   - `documentation-sync.yml:114` — `if [ "$LAST_AUTHOR" = "github-actions[bot]" ] && [[ "$LAST_MSG" == "docs(sync)"* ]]; then echo "skip=true"`
   - Se bot comitou na execução anterior (ex.: auto-fix markdown), próxima execução pula — drift não detectado até push humano.

**Causa provável (dedução, não fato)**: Combinação de (1) `fix_markdown.py` mutando docs a cada run + (2) anti-loop guard pulando execuções subsequentes + (3) `mkdocs` best-effort falhando em ARM64 + (4) push retry logic (3 tentativas com rebase) falhando em concorrência com outros workflows no grupo `pages`. A 5ª execução passou provavelmente porque estado estabilizou (sem mudanças pendentes) ou concorrência resolveu.

---

## Resumo de Severidade

| Categoria | Crítico | Alto | Médio | Baixo |
|-----------|---------|------|-------|-------|
| Duplicação | 1 (LLM 3x) | 2 (scraping, parsing, classificação) | 1 (entrypoints) | - |
| Acoplamento | 1 (main.py god module) | 2 (LLMService, scraper DI) | 3 (event bus singleton, imports cruzados, private attr) | - |
| Gargalos | - | 2 (scraper waits, LLM sequencial) | 3 (prompt size, concorrência sem limite, PDF browser relaunch) | - |
| Riscos Scraper | 1 (seletores hardcoded) | 2 (circuit breaker, exceções amplas) | 2 (content comparison, PDF button) | - |
| Gaps Cobertura | - | 4 (llm_service, release_summarizer, release_docs, infra/llm) | 10+ módulos sem teste dedicado | - |
| Config Duplicada | - | 2 (Black 3x, Ruff+Black) | 4 (pytest conflict, mypy args, dep groups, pre-commit stages) | - |
| Custo/Tokens | - | **Não mensurável** (pipeline principal) | - | - |
| Doc Sync Falhas | - | 1 (4 falhas seguidas) | - | - |

---

## Recomendações Prioritárias (Fase 1)

1. **Consolidar LLM**: Escolher **uma** implementação (recomendo `src/infrastructure/llm.py:UnifiedLLMClient` + adapters) e remover `src/llm_service.py` + `src/ai/llm/client.py` (ou restringir `ExistingLLMClient` ao `ai-docs.yml` apenas).
2. **Migrar `main.py` -> Clean Arch**: Usar `PipelineOrchestrator` + `PipelineConfig` DI + core services. Remover lógica inline de `main.py`.
3. **Injetar dependências no Scraper**: `CacheManager`, `CircuitBreaker`, `RateLimiter` via construtor (facilita testes).
4. **Substituir Black por Ruff format**: Remove `black` de `pyproject.toml`, `.pre-commit-config.yaml`, `docs` extra. Adiciona `[tool.ruff.format] preview = true`.
5. **Fixar `fix_markdown.py` fence tracking**: Garantir idempotência (já corrigido 2026-11-04, validar).
6. **Adicionar tracking de tokens/custo** no `LLMService`/`UnifiedLLMClient` (expor `usage` property, logar agregado por execução).
7. **Parallelizar `FeatureEnricher.enrich_release()`** com `asyncio.Semaphore` (ex.: max 3 concorrentes).
8. **Criar testes dedicados** para módulos `src/infrastructure/`, `src/core/`, `src/ai/`, `src/automation/`, `src/impact_propagation/` sem cobertura.

---

*Documento gerado pela Fase 0 — Diagnóstico. Atualize a cada fase concluída.*
