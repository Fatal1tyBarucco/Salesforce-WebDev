# ADR-007 Clean Architecture Adoption

Reorganização do projeto em arquitetura limpa com camadas e dependências unidirecionais.

## Status

**Aceito** — Implementado em `src/models/`, `src/core/`, `src/infrastructure/`, `main_clean.py`.

## Contexto

O código base acumulou acoplamento entre camadas ao longo do tempo:

- `src/main.py` (1000+ linhas) mistura orquestração, scraping, parsing, LLM calls, geração de Markdown, notificações
- `src/llm_service.py` combina fallback de providers, prompt building, caching, rate limiting
- `src/feature_classifier.py` + `src/heuristic_classifier.py` duplicam lógica de classificação
- `src/ai/integrations/`, `src/ai/prompts/` acoplados ao domínio de classificação
- `src/parser.py`, `src/scraper.py` dependem de implementações concretas (BeautifulSoup, Playwright)
- Testes difíceis de isolar devido a dependências de I/O (rede, filesystem, LLM)

Problemas resultantes:
- Mudar o parser exige mexer no orquestrador
- Testar classificação exige LLM real ou mocks complexos
- Adicionar novo provedor de LLM toca múltiplos arquivos
- Deploy de apenas uma parte (ex: só API) puxa todo o grafo de dependências

## Decisão

Adotar **Clean Architecture** com 4 camadas e dependências unidirecionais (apenas para dentro):

```
┌─────────────────────────────────────────────────────────────┐
│                    Application (Orchestration)               │
│  src/main_clean.py  — PipelineFactory, wiring de dependências│
└─────────────────────────────┬───────────────────────────────┘
                              │ usa
┌─────────────────────────────▼───────────────────────────────┐
│                      Infrastructure (Adapters)               │
│  scraping, parsing, llm, storage, github, messaging,        │
│  translation, generation, api/routes, api/graphql           │
└─────────────────────────────┬───────────────────────────────┘
                              │ implementa
┌─────────────────────────────▼───────────────────────────────┐
│                        Core (Application Services)           │
│  pipeline (orchestrator + step interfaces),                  │
│  classification (service + strategies),                      │
│  enrichment (service + strategies),                          │
│  summarization (service)                                     │
└─────────────────────────────┬───────────────────────────────┘
                              │ usa
┌─────────────────────────────▼───────────────────────────────┐
│                         Domain (Models)                      │
│  models: ReleaseMetadata, Feature, FeatureCategory,          │
│  ClassificationResult, FeatureEnrichment, ReleaseEnrichment  │
│  api: FeatureCategory, ReleaseResponse, DiffResponse (Pydantic)│
└─────────────────────────────────────────────────────────────┘
```

### Regras de Camada

| Camada | Pode depender de | Não pode depender de |
|--------|------------------|----------------------|
| Domain | stdlib apenas    | Core, Infra, App     |
| Core   | Domain           | Infra, App, frameworks|
| Infra  | Domain, Core     | App                  |
| App    | Domain, Core, Infra | —                 |

### Padrões Aplicados

1. **Pipeline Pattern** — `PipelineOrchestrator` executa `ScrapingStep → ParsingStep → ClassificationStep → EnrichmentStep → TranslationStep → GenerationStep → NotificationStep` em sequência, com configuração centralizada (`PipelineConfig`).

2. **Strategy Pattern** — `ClassificationService` aceita `ClassificationStrategy` (LLM, HEURISTIC, HYBRID). `EnrichmentService` aceita `EnrichmentStrategy` (LLM, TEMPLATE, HYBRID). Novas estratégias adicionadas sem tocar orquestrador.

3. **Adapter Pattern** — Cada sistema externo tem um adapter implementando interface do Core:
   - `ScrapingStep` → `PlaywrightScrapingAdapter`, `CachedScrapingAdapter`
   - `ParsingStep` → `BeautifulSoupParsingAdapter`
   - `ClassificationStep` → `OpenRouterClassificationAdapter`, `HeuristicClassificationAdapter`
   - `StorageAdapter` → `FileSystemStorageAdapter`, `GitHubStorageAdapter`
   - `NotificationStep` → `GitHubNotificationAdapter`, `SlackNotificationAdapter`, `EmailNotificationAdapter`, `CompositeNotificationAdapter`

4. **Dependency Injection via Factory** — `PipelineFactory` centraliza criação e wiring de todos os adapters e serviços. Configuração via env vars e dicionário.

5. **Domain Models como Data Classes Imutáveis** — `@dataclass(frozen=True)` com `to_dict()`/`from_dict()` para serialização. Sem dependências externas.

6. **Multi-provider LLM Fallback Chain** — `OpenRouterLLMAdapter` implementa cadeia: OpenRouter (free) → OpenCode → Gemini (protected quota). Heurístico como fallback final.

## Consequências

### Positivas

- **Testabilidade**: Core services testáveis com adapters mockados; domain models testáveis sem I/O
- **Substituibilidade**: Trocar Playwright por httpx, BeautifulSoup por lxml, OpenRouter por Anthropic — toca apenas um adapter
- **Deploy Seletivo**: API REST/GraphQL (`src/infrastructure/api/`) pode rodar independente do pipeline ETL
- **Evolução Independente**: Novas estratégias de classificação/enriquecimento sem quebrar pipeline
- **Observabilidade**: Cada step do pipeline tem `name` e retorna `PipelineResult` com timing, arquivos gerados, erros
- **Extensibilidade**: Adicionar step (ex: validação, indexação) = implementar interface + registrar no factory

### Negativas / Trade-offs

- **Mais arquivos**: ~25 novos arquivos vs. monolito anterior; exige navegação entre camadas
- **Boilerplate Inicial**: Interfaces (`PipelineStep`, `StorageAdapter`, etc.) + factory wiring
- **Curva de Aprendizado**: Time precisa entender fluxo Domain → Core → Infra → App
- **Duplicação Temporária**: `src/main.py` (legacy) coexiste com `main_clean.py` durante migração incremental

## Migração Incremental (Próximos Passos)

1. **Consolidar classificadores duplicados** — mover `feature_classifier.py`, `heuristic_classifier.py`, `ai/integrations/`, `ai/prompts/classification.py` → `src/core/classification/` (usar `ClassificationService`)

2. **Migrar `src/main.py` para usar `PipelineFactory`** — substituir lógica inline por chamada ao orchestrator

3. **Atualizar testes** — fixtures usam adapters mockados; testes de integração usam `PipelineFactory` real

4. **Deprecar `src/main.py`** — após validação em produção, remover código legado

5. **Documentar API pública** — `src/infrastructure/api/` pronto para uso; adicionar OpenAPI/Swagger

## Testes

```bash
# Core services (unit, mock adapters)
pytest tests/test_classification_service.py
pytest tests/test_enrichment_service.py
pytest tests/test_pipeline_orchestrator.py

# Infrastructure adapters (integration, real deps opcional)
pytest tests/test_scraping_adapter.py
pytest tests/test_parsing_adapter.py
pytest tests/test_llm_adapters.py

# Full pipeline (E2E)
pytest tests/test_main_clean.py
```

Cobertura alvo: `--cov=src --cov-fail-under=95` mantido.

## Referências

- Robert C. Martin, "Clean Architecture" (2017)
- ADR-001 (Parser Strategy) — padrão de strategy já usado no parsing
- ADR-005 (Documentation Reconciliation) — pipeline de docs separado, mesmo princípio