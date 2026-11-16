# ADR-009 - Scraper Resilience

Resiliência do scraper: circuit breaker, selector contracts, cache, rate limiter, retry com jitter.

## Status

**Aceito** — Implementado em `src/infrastructure/scraping/` + `src/circuit_breaker.py` + `src/limiters/`.

## Contexto

O scraper acessa `help.salesforce.com` (SPA React) via Playwright. Fontes de instabilidade:

| Fonte | Sintoma | Frequência |
|-------|---------|------------|
| Deploy Salesforce | DOM muda, selectors quebram | ~1x/mês |
| Rate limiting | HTTP 429 / timeout | ~5% requests |
| Flakiness rede | Timeout, browser crash | ~2% requests |
| Mudança de layout | TOC não expande, tabela vazia | ~1x/quarter |
| Manutenção programada | Site indisponível | Agendado |

Antes: lógica de retry/spread em `src/scraper.py` monolítica, sem observabilidade, cache TTL fixo, sem circuit breaker.

## Decisão

### Arquitetura em Camadas (Defense in Depth)

```text
┌─────────────────────────────────────────────────────────────┐
│                    PlaywrightScraperAdapter                  │
│  (implementa ScraperPort — interface do Domain)             │
├─────────────────────────────────────────────────────────────┤
│  1. Selector Contracts        → Detecção de layout change   │
│  2. Cache (TTL + content-hash) → Evita refetch desnecessário│
│  3. Rate Limiter (token bucket) → Respeita limites do site  │
│  4. Circuit Breaker           → Fail fast, protege downstream│
│  5. Retry + Exponential Backoff + Jitter → Recupera transient│
│  6. Observability (metrics, logs, correlation IDs)          │
└─────────────────────────────────────────────────────────────┘
```

### 1. Selector Contracts (`src/domain/scraper.py`)

```python
@dataclass(frozen=True)
class SelectorContract:
    name: str                    # "toc", "feature_table", "content"
    selectors: tuple[str, ...]   # Fallback chain: [".toc-container", "ul.tree", '[role="tree"]']
    required: bool = True        # Se True, falha loga layout change
    min_content_size: int = 100  # Validação mínima de conteúdo
```

- **Fallback chain**: Tenta selectors em ordem; primeiro que retorna elemento válido vence
- **Cache de selector funcionando**: `_selector_cache` evita re-tentar selectors quebrados
- **Validação de layout**: `_validate_layout()` roda após fetch bem-sucedido; loga `layout_change` no observability
- **Contratos versionados**: `DEFAULT_SELECTOR_CONTRACTS` em `domain/scraper.py` — alteração = novo contrato

### 2. Cache Multi-Nível (`src/infrastructure/scraping/cache_adapter.py` + `src/cache_manager.py`)

| Nível | Chave | TTL | Invalidação |
|-------|-------|-----|-------------|
| HTML renderizado | `sha256(url)[:16]` | 24h (config) | TTL expiry + content-hash |
| Texto extraído | `text:{url}` | 24h | TTL expiry |
| Selector válido | `{contract}:{hash(selectors)}` | In-memory | Browser restart |

- **Content-hash**: `CacheManager.compute_file_hash()` detecta se HTML cached mudou (para arquivos locais)
- **Namespace**: `sfscraper` isola cache do scraper

### 3. Rate Limiter (`src/infrastructure/scraping/rate_limiter.py`)

```python
class AsyncRateLimiter:
    def __init__(self, rps: float = 2.0, burst: int = 3):
        # Token bucket: rps tokens/sec, burst capacity
```

- **Default**: 2 req/s, burst 3 (respeita `robots.txt` e bom cidadão)
- **Configurável**: `ScraperConfig.rate_limit_rps`, `rate_limit_burst`
- **Async**: `await limiter.acquire()` antes de cada `page.goto()`

### 4. Circuit Breaker (`src/circuit_breaker.py`)

```python
CircuitBreaker(threshold=3, cooldown=60.0)
```

- **Estados**: CLOSED (normal) → OPEN (3 falhas consecutivas, 60s cooldown) → HALF-OPEN (probe)
- **Integração**: `_circuit_breaker.is_open` verificado antes de cada fetch
- **Métricas**: `circuit_breaker_state` em `ScraperMetrics`

### 5. Retry com Exponential Backoff + Jitter (`src/infrastructure/scraping/playwright_adapter.py`)

```python
def calculate_jittered_delay(base_delay: float, attempt: int, max_delay: float = 60.0) -> float:
    exponential_delay = min(base_delay * (2**attempt), max_delay)
    jitter = random.uniform(0, base_delay)
    return min(exponential_delay + jitter, max_delay)
```

- **Base delay**: 2s (config: `RETRY_BASE_DELAY_SECONDS`)
- **Max attempts**: 3 (config: `max_retry_attempts`)
- **Max delay**: 60s (config: `max_retry_delay_seconds`)
- **Retryable errors**: Timeout, PlaywrightError, OSError — NÃO retry: 4xx, selector validation fail

### 6. Observability (`src/infrastructure/scraping/observability.py`)

```python
@dataclass
class ScraperMetrics:
    url: str
    attempt: int
    success: bool
    latency_ms: int
    content_size: int
    cache_hit: bool = False
    error_code: ScraperErrorCode | None = None
    correlation_id: str
    circuit_breaker_state: str = "closed"
```

- **Correlation ID**: UUID v4 (12 chars) — rastreia request end-to-end
- **Structured logs**: `[{correlation_id}] message` — grepável
- **Metrics export**: Prometheus counters (`scraper_fetch_total`, `scraper_latency_ms`, `scraper_cache_hits`, `scraper_layout_changes`)

### 7. Health Check

```python
async def health_check(self) -> bool:
    # Navega para help.salesforce.com, verifica DOM básico
```

- Usado por k8s liveness probe e CI pre-flight

## Consequences

### Positivas

- **Fail fast**: Circuit breaker evita hammering site indisponível
- **Auto-recovery**: Half-open probe restaura serviço sem intervenção
- **Layout change detection**: Selector contracts alertam antes de quebrar parsing
- **Cache hit rate >80%**: Reduz carga no Salesforce e latência
- **Rate limiting**: Bom cidadão, evita 429/IP ban
- **Observabilidade completa**: Correlation IDs + metrics + structured logs = debugging rápido
- **Testável**: Cada camada mockável independentemente (`ScraperPort` interface)

### Negativas / Trade-offs

- **Complexidade**: 6 camadas vs. função única anterior
- **Configuração**: 15+ parâmetros em `ScraperConfig` (mitigado: defaults sensíveis)
- **Latência primeira request**: Browser launch + cache miss + rate limit = ~5-10s
- **Memory**: Browser instance mantido vivo entre requests (config: `browser_idle_timeout`)

## Testes

```bash
# Unit: circuit breaker, rate limiter, cache
uv run pytest tests/infrastructure/scraping/test_circuit_breaker.py
uv run pytest tests/infrastructure/scraping/test_rate_limiter.py
uv run pytest tests/infrastructure/scraping/test_cache_adapter.py

# Integration: playwright adapter (marked slow, requires browsers)
uv run pytest tests/infrastructure/scraping/test_playwright_scraper_adapter.py -v

# Characterization (golden files)
uv run pytest tests/test_characterization.py -v
```

## Referências

- `src/domain/scraper.py` — `ScraperPort`, `SelectorContract`, `ScraperConfig`, `ScraperErrorCode`
- `src/infrastructure/scraping/playwright_adapter.py` — implementação principal
- `src/infrastructure/scraping/cache_adapter.py` — `ScraperCacheAdapter`
- `src/infrastructure/scraping/rate_limiter.py` — `AsyncRateLimiter`
- `src/infrastructure/scraping/observability.py` — `ScraperObservabilityAdapter`, `ScraperMetrics`
- `src/circuit_breaker.py` — `CircuitBreaker`
- `src/cache_manager.py` — `CacheManager` (TTL + content-hash + namespace)
- Michael Nygard, "Release It!" (2018) — Circuit Breaker pattern
