# Melhorias de Código — Fase 1 & V1 Resiliência

> Registro das melhorias estruturais e de resiliência implementadas.

## Fase 1 — Refatoração Estrutural

### Extração do OpenAPI Spec

O método `_generate_openapi_spec()` em `src/api.py` tinha **209 linhas** de especificação OpenAPI hardcoded como dicionário Python. Foi extraído para `src/openapi_spec.json`, reduzindo a função para **3 linhas** que carregam o JSON.

**Antes:**
```python
def _generate_openapi_spec() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": { ... },
        "paths": { ... },  # 209 linhas
    }
```

**Depois:**
```python
_OPENAPI_SPEC_PATH = Path(__file__).parent / "openapi_spec.json"

def _generate_openapi_spec() -> dict[str, Any]:
    return json.loads(_OPENAPI_SPEC_PATH.read_text(encoding="utf-8"))
```

### Divisão do GraphQL Executor

`_execute_graphql()` tinha **125 linhas** com lógica de parsing, seleção de campos e execução misturados. Foi dividido em:

| Função | Responsabilidade |
|--------|-----------------|
| `_select_graphql_fields()` | Mapear campos GraphQL → internos |
| `_extract_requested_fields()` | Extrair campos do query string |
| `_graphql_handle_releases()` | Handler para `{ releases }` |
| `_graphql_handle_release()` | Handler para `{ release(slug) }` |
| `_graphql_handle_diff()` | Handler para `{ diff(current, previous) }` |
| `_execute_graphql()` | Orquestrador (38 linhas) |

Constantes extraídas: `_GRAPHQL_FIELD_MAP` e `_GRAPHQL_KEYWORDS`.

### Extração do Dashboard Template

`generate_dashboard_html()` em `src/dashboard.py` tinha **202 linhas** de HTML/CSS/JS inline. O template foi extraído para `src/dashboard_template.html`, e a função agora carrega o template e injeta os dados via placeholder `{DATA_JSON}`.

## V1 — Resiliência de Integrações

### LLM Service (`src/llm_service.py`)

**Timeout:**
- Cliente OpenAI: `timeout=30.0` (conexão)
- `asyncio.wait_for()`: `timeout=60.0` (operação completa)
- Google Gemini: `asyncio.wait_for()` com `timeout=60.0`

**Retry com Backoff:**
- Decorator `@retry` do `tenacity` em `_call_openai_provider()` e `_call_google_provider()`
- 3 tentativas, backoff exponencial (1s → 10s)
- Retry apenas para erros transitórios: `APIConnectionError`, `InternalServerError`

**Hierarquia de Exceções:**
- `RateLimitError` → warning, circuit breaker
- `AuthenticationError` → warning, circuit breaker
- `APIConnectionError` / `InternalServerError` → error, retry
- `TimeoutError` → error, circuit breaker
- `Exception` genérico → error (último recurso)

### SMTP (`src/notifications.py`)

- Timeout de **30 segundos** adicionado em `smtplib.SMTP(smtp_host, smtp_port, timeout=30)`
- Previne bloqueio indefinido em conexões SMTP lentas

### Scraper (`src/scraper.py`)

- Já possuía timeout adequado (Playwright timeouts configurados)
- Já possuía retry com backoff exponencial

## Cobertura de Testes

| Métrica | Valor |
|---------|-------|
| Total de linhas | 4.209 |
| Linhas cobertas | 3.999 |
| Cobertura | **95.01%** |
| Novos testes (Fase 1 + V1) | 34 |

Módulos com 100% de cobertura: `config`, `cache_manager`, `dashboard`, `generator`, `health`, `i18n`, `impact_analyzer`, `llm_service`, `logger`, `nl_search`, `notifications`, `parser`, `release_summarizer`, `salesforce`, `smart_notifications`, `translator`, `workflow`, `feature_classifier`, `automation/models`, `automation/notifications`.

## P0 — Integração da Hierarquia de Exceções

### Diagnóstico

A hierarquia de exceções em `src/exceptions.py` (11 classes: `PipelineError`, `ScraperError`, `BrowserError`, `RateLimitError`, `ParserError`, `LLMError`, `LLMProviderExhausted`, `ConfigError`, `ExportError`, `NotificationError`, `GitHubError`) estava definida mas **nunca utilizada**. Todo o código usava `except Exception` genérico ou `raise ValueError`.

### Mudanças

| Arquivo | Antes | Depois |
|---------|-------|--------|
| `scraper.py` | 9× `except Exception` | `except (ScraperError, BrowserError, TimeoutError, OSError)` |
| `main.py` | 5× `except Exception` | `except (LLMError, GitHubError, NotificationError, OSError)` |
| `llm_service.py` | 2× `except Exception` (mantidos como último recurso) | Mantidos + import de `LLMError` |
| `salesforce.py` | 7× `raise ValueError` | 7× `raise ConfigError` |
| `github_ops.py` | 1× `except Exception` | `except (GitHubError, OSError, subprocess.SubprocessError)` |
| `automation/github_ops.py` | `except Exception` | `except (GitHubError, OSError, subprocess.SubprocessError)` |

### Benefícios

- **Rastreabilidade**: cada erro é identificável pelo tipo
- **Tratamento granular**: consumidores podem capturar exceções específicas
- **Circuit breaker**: pode diferenciar erros transitórios de fatais
- **Testes**: validam a hierarquia real, não apenas mensagens de erro

---

## Fase 2 — Automação AI Avançada

### Enriquecimento de Features (`feature_enricher.py`)

**Novo módulo** que utiliza LLM para gerar descrições profissionais e classificações de impacto para cada feature das release notes.

| Aspecto | Implementação |
|---------|---------------|
| **Batch Prompting** | 1 chamada LLM por categoria (não por feature) — custo mínimo |
| **Descrições AI** | Cada feature recebe descrição com contexto de negócio |
| **Impacto** | Classificação 🔴 Alto / 🟡 Médio / 🟢 Baixo por feature |
| **Audiência** | Identificação: Usuários / Admins / Ambos |
| **Fallback** | Classificação heurística por keywords quando LLM indisponível |

**Formato de saída:**
```markdown
| Recurso | Descrição | Impacto |
| :--- | :--- | :---: |
| **Voice Feature** | Permite interação por voz com Agentforce, reduzindo ~40% do tempo em tarefas repetitivas. | 🔴 alto |
```

### Resumos Executivos (`release_summarizer.py`)

**Refatoração completa** do módulo de sumarização, produzindo relatórios executivos profissionais.

| Campo | Descrição |
|-------|-----------|
| `executive_summary` | 3-5 frases com visão geral da release |
| `business_impact` | Parágrafo com valor concreto e exemplos reais |
| `strategic_themes` | Lista de temas (AI-First, Security, Developer Experience) |
| `top_categories` | Top 5 categorias com destaque e percentual |
| `migration_notes` | Considerações para administradores |

**Método `to_markdown()`** renderiza como documento Markdown completo.

### Introduções por Categoria

Cada arquivo de categoria agora inclui:
- Parágrafo introdutório AI sobre o tema e mudanças mais importantes
- Linha de impacto: `🔴 5 alto | 🟡 12 médio | 🟢 3 baixo`
- Tabela enriquecida com colunas `Recurso | Descrição | Impacto`

### GraphQL Parser Recursivo

Substituição do parser regex frágil por um **recursive-descent parser** completo.

| Componente | Descrição |
|------------|-----------|
| `_gql_lex()` | Lexer que tokeniza a query em tipos (LBRACE, NAME, STRING, etc.) |
| `_GQLParser` | Parser recursivo com `_peek()`, `_advance()`, `_expect()` |
| `_parse_arguments()` | Parsing de argumentos `(key: "value")` |
| `_parse_field_set()` | Parsing de seleções de campos `{ field1 field2 }` com nesting |

**Vantagens:** suporta queries aninhadas, mensagens de erro claras, sem dependências externas.

### Autenticação API

Middleware de autenticação para a API REST + GraphQL.

| Feature | Implementação |
|---------|---------------|
| **Métodos** | `X-API-Key` header ou `Authorization: Bearer <token>` |
| **Configuração** | Variável de ambiente `API_KEY` (vazio = sem auth) |
| **Endpoints públicos** | `/health`, `/ready`, `/metrics`, `/openapi.json` |
| **Resposta** | 401 com mensagem de erro clara |

### Versionamento Semântico

Campo `version` (major.minor.patch) adicionado ao `.meta.json` de cada release.

| Componente | Lógica |
|------------|--------|
| **major** | Offset do ano (2025=1, 2026=2, ...) |
| **minor** | Índice da estação (Spring=0, Summer=1, Winter=2) |
| **patch** | Contagem de re-scrapes da mesma release |

### Rate Limiting LLM

Token-bucket rate limiter assíncrono integrado ao `LLMService`.

| Configuração | Default |
|--------------|---------|
| `max_requests` | 60 |
| `window_seconds` | 60.0 |
| **Thread-safety** | `asyncio.Lock` |

### Prometheus-client Integration

Endpoint `/metrics` com dual-mode: `prometheus_client` quando instalado, fallback text/plain caso contrário.

**Métricas disponíveis:**
- `pipeline_runs_total` (counter, labels: status)
- `features_processed_total` (counter)
- `scraper_requests_total` (counter, labels: outcome)
- `pipeline_run_duration_seconds` (histogram)
- `release_feature_count` (gauge, labels: release_slug)
- `pipeline_uptime_seconds` (gauge)

### Python Version

Downgrade de Python 3.14 (alpha) para `>=3.12,<3.14` (estável).

| Arquivo | Mudança |
|---------|---------|
| `pyproject.toml` | `requires-python = ">=3.12,<3.14"` |
| `Dockerfile` | `python:3.13-slim` |
| CI matrix | `["3.12", "3.13"]` apenas |

### Cobertura de Testes

| Métrica | Valor |
|---------|-------|
| **Cobertura total** | **95%+** |
| **Testes E2E** | Pipeline, API, EventBus, Cache, Auth |
| **Testes AI** | Feature enricher, release summarizer, fallback |
