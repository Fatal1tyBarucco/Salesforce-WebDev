# C4 Container Diagram

Diagrama de containers do Salesforce Release Intelligence, seguindo a notação C4 Level 2.

## Diagrama

```mermaid
C4Container
    title Salesforce Release Intelligence — Container Diagram

    Person(user, "Usuário / Admin", "Equipe que consome release notes e dashboards")

    System_Boundary(boundary, "Salesforce-WebDev") {
        Container(spa, "Salesforce Help SPA", "JavaScript", "Portal de release notes da Salesforce — fonte de dados primária")
        Container(scraper, "Python Scraper Engine", "Python + Playwright", "Extração resiliente de conteúdo SPA com circuit breaker e rate limiting")
        Container(parser, "Semantic Parser", "Python + BeautifulSoup", "Extração de hierarquia de tópicos e tabelas de feature impact")
        Container(classifier, "Topic Classifier", "Python + LLM (multi-provider)", "Classificação semântica de releases e features")
        Container(generator, "Markdown Generator", "Python", "Geração de artefatos Markdown enriquecidos (pt_BR + en_US)")
        Container(api_server, "API Server", "Python (stdlib http.server)", "REST + GraphQL para consumo programático das releases")
        Container(mkdocs, "MkDocs Portal", "MkDocs + Material", "Publicação da documentação e release notes como site estático")
    }

    System_Ext(sf, "Salesforce Help", "Sistema externo", "Portal de release notes e feature impact da Salesforce")

    Rel(user, mkdocs, "Consome documentação", "HTTPS")
    Rel(spa, scraper, "Fornece HTML renderizado", "Playwright")
    Rel(scraper, parser, "Passa raw HTML", "BeautifulSoup")
    Rel(parser, classifier, "Fornece tópicos extraídos", "LLM classify()")
    Rel(classifier, generator, "Fornece classificação", "Markdown enriched")
    Rel(generator, mkdocs, "Atualiza docs/ e README", "Markdown files")
    Rel(generator, api_server, "Fornece dados estruturados", "JSON")
    Rel(mkdocs, user, "Publica site estático", "GitHub Pages")

    UpdateRelStyle(user, mkdocs, $offsetY="-40")
    UpdateRelStyle(scraper, parser, $offsetY="-40")
    UpdateRelStyle(generator, mkdocs, $offsetY="-40")
```

## Containers

| Container | Linguagem / Tech | Responsabilidade | Observabilidade |
|-----------|-----------------|------------------|-----------------|
| **GitHub Actions** | YAML | Orquestração do pipeline: extração, reconciliação documental, deploy | Logs do Actions, Step Summary |
| **Python Scraper Engine** | Python + Playwright | Extração de conteúdo da Salesforce Help SPA com circuit breaker e rate limiting | Logs com correlation_id, métricas de retry |
| **Semantic Parser** | Python + BeautifulSoup | Extração de árvore de tópicos e tabelas de feature impact | Snapshot tests, parser validation |
| **Topic Classifier** | Python + LLM (Gemini → OpenCode → OpenRouter) | Classificação semântica de releases e features por impacto | Logs de chamada LLM, fallback tracking |
| **Markdown Generator** | Python | Geração de Markdown enriquecido (pt_BR + en_US) com resumos AI | Geração de .meta.json, badges |
| **API Server** | Python (stdlib http.server) | REST + GraphQL para consumo das releases processadas | Health endpoints, Prometheus metrics |
| **MkDocs Portal** | MkDocs + Material | Publicação do site de documentação e release notes | Build status, link checker |

## Data Flow

```mermaid
flowchart LR
    subgraph SF["Salesforce Help (externo)"]
        SPA["Release Notes SPA"]
        IMPACT["Feature Impact Page"]
    end

    subgraph PIPELINE["Pipeline ETL"]
        SCRAPE["Scraper (Playwright)"]
        PARSE["Parser (BeautifulSoup)"]
        CLASSIFY["Classifier (LLM)"]
        GENERATE["Generator (Markdown)"]
    end

    subgraph OUTPUT["Saída"]
        RELEASES["releases/*.md"]
        META["*.meta.json"]
        API["API Server"]
        DOCS["MkDocs (docs/)"]
        README["README bilingue"]
        NOTIFY["Notificações (Slack/Email/Discord)"]
    end

    SPA --> SCRAPE
    IMPACT --> SCRAPE
    SCRAPE --> PARSE
    PARSE --> CLASSIFY
    CLASSIFY --> GENERATE
    GENERATE --> RELEASES
    GENERATE --> META
    GENERATE --> API
    GENERATE --> DOCS
    GENERATE --> README
    GENERATE --> NOTIFY
```

## Padrões de Resiliência por Container

| Container | Pattern | Implementação |
|-----------|---------|---------------|
| Scraper | Circuit Breaker + Rate Limiter | `src/circuit_breaker.py`, `src/limiters/rate_limiter.py` |
| Classifier | Fallback por provider | `src/llm_service.py` — Gemini → OpenCode → OpenRouter |
| Parser | Multi-selector fallback | `src/parser.py` — tries `.toc-container`, `ul.tree`, `[role="tree"]` |
| Generator | Cache de resumos | `src/cache_manager.py` — TTL + content-hash |
| API Server | Health checks | `src/health.py` — `/health`, `/ready`, `/metrics` |
| MkDocs | Build validation | `mkdocs build --strict` + link checker no CI |
