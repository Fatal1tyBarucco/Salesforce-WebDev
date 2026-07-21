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
