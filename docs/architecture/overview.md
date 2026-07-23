# Architecture Overview

Visão arquitetural completa do Salesforce Release Intelligence.

## Princípios de Design

1. **Resiliência** — Circuit breaker, retry com backoff, timeouts definidos
2. **Separação de Responsabilidades** — Camadas claras: scraping → parsing → lógica → saída
3. **Dependency Injection** — `PipelineConfig` para testabilidade
4. **Exceções Específicas** — Hierarquia `PipelineError` para rastreabilidade
5. **Cache Inteligente** — TTL para dados temporários, content-hash para arquivos

## Diagrama de Componentes

```mermaid
graph TB
    subgraph "Entry Points"
        CLI["CLI<br/>python src/main.py"]
        API_EP["API Server<br/>start_api_server()"]
        HEALTH_EP["Health Server<br/>start_health_server()"]
    end

    subgraph "Orchestration"
        MAIN["main.py<br/>run_pipeline(PipelineConfig)"]
        CONFIG["PipelineConfig<br/>DI Container"]
    end

    subgraph "Scraping Layer"
        SCRAPER["scraper.py<br/>SalesforceReleaseScraper"]
        CB1["CircuitBreaker"]
        RL["RateLimiter"]
        PW["Playwright<br/>Chromium headless"]
    end

    subgraph "Parsing Layer"
        NAV_PARSER["ReleaseNotesParser<br/>Árvore de navegação"]
        IMPACT_PARSER["FeatureImpactParser<br/>Tabelas de impacto"]
    end

    subgraph "LLM Layer"
        LLM["llm_service.py<br/>LLMService"]
        CB2["CircuitBreaker<br/>(por provider)"]
        OPENAI["OpenAI API"]
        GEMINI["Google Gemini"]
    end

    subgraph "Automation Layer"
        AI_SVC["AIAutomationService"]
        REPORTING["reporting.py<br/>Changelog, Diff, Quality"]
        IMPACT["impact.py<br/>Impact scores, Prediction"]
        CONTENT["content.py<br/>Deduplicação"]
        TRIAGE["issue_triage.py<br/>Triage automático"]
        CLASSIFIER["feature_classifier.py<br/>Classificação"]
    end

    subgraph "Integration Layer"
        SF["salesforce.py<br/>Trailhead mapping"]
        WF["workflow.py<br/>Git + GitHub CLI"]
        GH_OPS["github_ops.py<br/>Issues"]
    end

    subgraph "Output Layer"
        GEN["generator.py<br/>Markdown"]
        NOTIF["notifications.py<br/>Email/Slack/Discord"]
        DASH["dashboard.py<br/>HTML interativo"]
        ANALYTICS["analytics.py<br/>Estatísticas"]
    end

    subgraph "Infrastructure"
        CACHE["CacheManager<br/>TTL + content-hash"]
        HEALTH["HealthState<br/>Métricas + status"]
        LOGGER["logger.py<br/>JSON estruturado"]
        EXCEP["exceptions.py<br/>Hierarquia"]
    end

    CLI --> MAIN
    MAIN --> CONFIG
    MAIN --> SCRAPER
    MAIN --> GEN
    MAIN --> AI_SVC
    MAIN --> HEALTH

    SCRAPER --> CB1
    SCRAPER --> RL
    SCRAPER --> PW
    SCRAPER --> CACHE

    NAV_PARSER --> CONFIG
    IMPACT_PARSER --> CONFIG

    LLM --> CB2
    LLM --> OPENAI
    LLM --> GEMINI

    AI_SVC --> LLM
    AI_SVC --> REPORTING
    AI_SVC --> IMPACT
    AI_SVC --> CONTENT
    AI_SVC --> TRIAGE
    AI_SVC --> CLASSIFIER

    GEN --> CONFIG
    GEN --> SF
    NOTIF --> CONFIG
    WF --> GH_OPS

    SCRAPER --> EXCEP
    LLM --> EXCEP
    NOTIF --> EXCEP
    GH_OPS --> EXCEP

    style CB1 fill:#f39c12,stroke:#e67e22
    style CB2 fill:#f39c12,stroke:#e67e22
    style CACHE fill:#3498db,stroke:#2980b9,color:#fff
    style EXCEP fill:#e74c3c,stroke:#c0392b,color:#fff
    style HEALTH fill:#2ecc71,stroke:#27ae60,color:#fff
```

## Fluxo de Dados

```mermaid
graph LR
    subgraph "Input"
        HTML["HTML SPA<br/>Salesforce Help"]
        JSON["JSON<br/>trailhead.json"]
    end

    subgraph "Processing"
        SCRAPE["Scrape<br/>Playwright"]
        PARSE["Parse<br/>Feature Impact"]
        CLASSIFY["Classify<br/>LLM"]
        GENERATE["Generate<br/>Markdown"]
    end

    subgraph "Storage"
        RELEASES["releases/<br/>.md files"]
        META[".meta.json<br/>Metadata"]
        CACHE_F["cache/<br/>Content hashes"]
    end

    subgraph "Output"
        MD["Markdown<br/>README + docs"]
        API_R["REST API<br/>JSON"]
        NOTIFY_R["Notifications<br/>Email/Slack"]
        GH_R["GitHub<br/>Issues + PRs"]
    end

    HTML --> SCRAPE
    SCRAPE --> PARSE
    PARSE --> CLASSIFY
    CLASSIFY --> GENERATE
    JSON --> GENERATE

    GENERATE --> RELEASES
    GENERATE --> META
    SCRAPE --> CACHE_F

    RELEASES --> MD
    META --> API_R
    GENERATE --> NOTIFY_R
    GENERATE --> GH_R
```

## Hierarquia de Exceções

```mermaid
graph TB
    PE["PipelineError"]
    SE["ScraperError"]
    BE["BrowserError"]
    RLE["RateLimitError"]
    PE2["ParserError"]
    LE["LLMError"]
    LPE["LLMProviderExhausted"]
    CE["ConfigError"]
    EE["ExportError"]
    NE["NotificationError"]
    GE["GitHubError"]

    PE --> SE
    SE --> BE
    SE --> RLE
    PE --> PE2
    PE --> LE
    LE --> LPE
    PE --> CE
    PE --> EE
    PE --> NE
    PE --> GE

    style PE fill:#2ecc71,stroke:#27ae60,color:#fff
    style SE fill:#3498db,stroke:#2980b9,color:#fff
    style LE fill:#e74c3c,stroke:#c0392b,color:#fff
    style CE fill:#f39c12,stroke:#e67e22,color:#fff
```

## Circuit Breaker State Machine

```mermaid
stateDiagram-v2
    [*] --> Closed: Inicialização

    Closed --> Closed: Sucesso (reset failures)
    Closed --> Open: failures >= threshold

    Open --> Open: Rejeita requests
    Open --> HalfOpen: Cooldown expirado

    HalfOpen --> Closed: Sucesso (probe)
    HalfOpen --> Open: Falha (reopen)

    state Closed {
        [*] --> Normal
        Normal --> Normal: Sucesso
    }

    state Open {
        [*] --> Cooldown
        Cooldown --> Cooldown: Tempo passando
    }

    state HalfOpen {
        [*] --> Probe
        Probe --> Probe: Testando
    }
```

## Cache Strategy

```mermaid
graph TB
    subgraph "TTL Cache"
        A["Respostas de API"]
        B["Metadados Trailhead"]
        C["Resultados LLM"]
    end

    subgraph "Content-Hash Cache"
        D["Arquivos Markdown"]
        E[".meta.json"]
    end

    subgraph "CacheManager"
        F["set(key, data, ttl)"]
        G["get(key) → data | None"]
        H["compute_file_hash(path)"]
        I["is_content_unchanged(path, hash)"]
    end

    A --> F
    B --> F
    C --> F
    D --> H
    E --> H

    F --> J["cache_dir/<br/>sha256(key).json"]
    G --> J
    H --> K["MD5 hash"]
    I --> K
```

## Decisões Arquiteturais

| Decisão | Alternativa | Escolhido | Motivo |
|---------|------------|-----------|--------|
| Scraping | requests + BeautifulSoup | **Playwright** | SPA requer JS rendering |
| LLM | OpenAI apenas | **Multi-provider** | Fallback automático |
| Cache | Redis | **File-based** | Zero dependências externas |
| Circuit Breaker | Biblioteca externa | **Implementação própria** | Controle total, sem dependência |
| Exceções | Exception genérico | **Hierarquia customizada** | Rastreabilidade |
| DI | Framework (dependency-injector) | **Dataclass simples** | Sem dependência extra |
| API | FastAPI/Flask | **stdlib http.server** | Zero dependências |
| Logging | print/logging básico | **JSON estruturado** | Machine-readable |
