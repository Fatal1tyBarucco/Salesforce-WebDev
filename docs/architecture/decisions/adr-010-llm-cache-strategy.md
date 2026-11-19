# ADR-010 - LLM Cache Strategy

Cache duplo para LLM: exact-match (chave determinística) + semantic (embedding centrado), TTL 7 dias.

> **Atualização (ADR-011):** o embedding placeholder do semantic cache migrou de MD5 para SHA-256, o TTL passou a ser centralizado em `src/config.py` (`CACHE_LLM_TTL_SECONDS`) e o index semântico ganhou escrita atômica + leitura tolerante. A estratégia dual-cache permanece como descrita abaixo.

## Status

**Aceito** — Implementado em `src/infrastructure/llm_adapters/cache.py`.

## Contexto

O pipeline faz centenas de chamadas LLM por release (classificação por feature, enriquecimento por categoria, sumarização, relatórios). Problemas:

| Problema | Impacto |
|----------|---------|
| Custo | OpenRouter free tem quota diária; Gemini tem rate limit |
| Latência | 2-5s por chamada; pipeline serial = minutos |
| Determinismo | Mesmo prompt → output diferente (temperature > 0) |
| Reprocessamento | Re-run pipeline = re-chamar LLM para mesmas features |

Soluções parciais existentes:

- `src/cache_manager.py` — genérico, TTL-based, key-value
- `src/llm_service.py` — cache inline com chave `hash(prompt)`

Necessário: estratégia unificada, observável, com invalidação semântica.

## Decisão

### Dupla Camada de Cache

```text
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Client (Unified)                        │
├─────────────────────────────────────────────────────────────────┤
│  1. Exact Cache (LLMCacheAdapter)                                │
│     Key: sha256(system + user + model + temperature + schema)   │
│     TTL: 7 dias (604800s)                                       │
│     Hit: ~60-70% (re-runs, features repetidas)                  │
├─────────────────────────────────────────────────────────────────┤
│  2. Semantic Cache (SemanticCacheAdapter)                        │
│     Key: embedding(prompt_text) → cosine similarity ≥ 0.95      │
│     TTL: 7 dias (arquivo + index.json)                          │
│     Hit: ~10-15% (prompts similares, variações menores)         │
└─────────────────────────────────────────────────────────────────┘
```

### 1. Exact Cache — `LLMCacheAdapter`

```python
class LLMCacheAdapter:
    def __init__(
        self, cache_manager: CacheManager | None = None, cache_dir: Path = Path("cache/llm")
    ):
        self._cache = cache_manager or CacheManager(cache_dir=cache_dir)
        self._ttl_default = 7 * 24 * 3600  # 7 dias

    async def get(self, key: str) -> LLMResponse | None:
        data = self._cache.get(f"llm:{key}")
        return LLMResponse.model_validate_json(data) if data else None

    async def set(self, key: str, response: LLMResponse, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds or self._ttl_default
        self._cache.set(f"llm:{key}", response.model_dump_json(), ttl=ttl)
```

**Chave determinística** (`LLMPrompt.cache_key()` em `src/domain/llm.py`):

```python
def cache_key(self) -> str:
    """SHA256 de todos parâmetros que afetam output."""
    payload = {
        "system": self.system,
        "user": self.user,
        "model": self.model,
        "temperature": self.temperature,
        "max_tokens": self.max_tokens,
        "response_format": self.response_format,
        "schema": self.schema_hash,  # hash do JSON schema
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:32]
```

- **Namespace**: `llm:` no `CacheManager` (isolamento)
- **TTL 7 dias**: Release notes são imutáveis após publicação; 7 dias cobre re-runs + safety margin
- **Serialização**: `LLMResponse.model_dump_json()` (Pydantic v2)

### 2. Semantic Cache — `SemanticCacheAdapter`

```python
class SemanticCacheAdapter:
    def __init__(self, cache_dir: Path = Path("cache/llm/semantic"), threshold: float = 0.95):
        self.cache_dir = cache_dir
        self.threshold = threshold
        self._index_file = cache_dir / "index.json"
        self._index: dict[str, dict] = self._load_index()
```

**Embedding centrado** (discriminativo para cosine similarity):

```python
def _get_embedding(self, text: str) -> list[float]:
    hash_bytes = hashlib.md5(text.encode()).digest()
    # Centrado em zero: raw bytes [0,1] → unrelated texts score ~0.8
    return [b / 255.0 - 0.5 for b in hash_bytes[:16]]  # 16-dim vector
```

- **Por que MD5 + centering?**: Embeddings reais (OpenAI, Gemini) custam tokens e latência. Hash determinístico + centering dá distribuição uniforme no hipercubo [-0.5, 0.5]^16 → cosine similarity discriminativa (unrelated ≈ 0, similar > 0.95).
- **Threshold 0.95**: Conservador — só retorna cache se prompt **muito** similar
- **Index persistido**: `index.json` mapeia `cache_key → {embedding, prompt_hash, timestamp}`
- **Lookup**: Linear scan (index pequeno, <1000 entries). Futuro: FAISS/Annoy se crescer.

### 3. Integração no Unified Client (`src/infrastructure/llm_adapters/unified_client.py`)

```python
async def complete(self, prompt: LLMPrompt) -> LLMResponse:
    # 1. Exact cache
    exact_key = prompt.cache_key()
    if cached := await self.exact_cache.get(exact_key):
        self.metrics.exact_hits += 1
        return cached

    # 2. Semantic cache
    if cached := await self.semantic_cache.get(prompt):
        self.metrics.semantic_hits += 1
        return cached

    # 3. Call provider
    response = await self._call_provider(prompt)

    # 4. Populate both caches
    await self.exact_cache.set(exact_key, response)
    await self.semantic_cache.set(prompt, response)

    return response
```

### 4. Métricas e Observabilidade

```python
@dataclass
class LLMCacheMetrics:
    exact_hits: int = 0
    exact_misses: int = 0
    semantic_hits: int = 0
    semantic_misses: int = 0

    @property
    def exact_hit_rate(self) -> float:
        total = self.exact_hits + self.exact_misses
        return self.exact_hits / total if total else 0.0

    @property
    def semantic_hit_rate(self) -> float:
        total = self.semantic_hits + self.semantic_misses
        return self.semantic_hits / total if total else 0.0
```

- Exportado via Prometheus: `llm_cache_exact_hits_total`, `llm_cache_semantic_hits_total`
- Logado no final de cada release processada

### 5. Invalidação

| Evento | Ação |
|--------|------|
| Novo prompt versionado (v1.0 → v1.1) | `schema_hash` muda → `cache_key` muda → exact miss auto |
| Modelo trocado (openrouter → gemini) | `model` no cache_key → miss auto |
| Temperature alterada | `temperature` no cache_key → miss auto |
| Force refresh | `await exact_cache.invalidate(key)` ou `cache_dir` delete |
| TTL expiry | `CacheManager` remove auto no `get()` |

## Consequences

### Positivas

- **Hit rate combinado ~75-85%**: Exact (60-70%) + Semantic (10-15%)
- **Custo reduzido**: ~70% menos chamadas LLM por re-run
- **Latência**: Cache hit = ~5ms vs 2-5s chamada real
- **Determinismo**: Exact cache garante mesmo output para mesmo input
- **Semântico captura variações**: Prompts com whitespace, order de campos, sinônimos menores
- **Auto-invalidação**: Versionamento de prompt (schema_hash, model, temp) invalida sem ação manual
- **Observável**: Métricas por tipo de cache + hit rates no dashboard

### Negativas / Trade-offs

- **Semantic false positives**: Threshold 0.95 conservador, mas possível (mitigado: loga `semantic_hit` com score para auditoria)
- **Storage growth**: `cache/llm/` + `cache/llm/semantic/` acumulam (mitigado: TTL 7d + `clear_expired()` cron)
- **Embedding quality**: MD5-based não captura semântica real (trade-off: zero custo/latência vs precisão). Futuro: swap para embedding real se threshold insuficiente.
- **Memory**: Index JSON carregado em memória (~1000 entries = ~200KB, negligível)

## Testes

```bash
# Unit: exact + semantic cache
uv run pytest tests/infrastructure/llm_adapters/test_cache.py -v

# Integration: unified client com cache
uv run pytest tests/infrastructure/llm_adapters/test_unified_client.py -v

# Characterization: cache behavior congelado
uv run pytest tests/test_characterization.py::test_llm_cache_behavior -v
```

## Referências

- `src/infrastructure/llm_adapters/cache.py` — `LLMCacheAdapter`, `SemanticCacheAdapter`
- `src/infrastructure/llm_adapters/unified_client.py` — integração dual-cache
- `src/domain/llm.py` — `LLMPrompt`, `LLMResponse`, `cache_key()`
- `src/cache_manager.py` — `CacheManager` (base TTL + namespace)
- ADR-008 (Prompt Versioning) — `schema_hash` no cache_key invalida auto em bump
- ADR-007 (Clean Architecture) — `LLMCacheAdapter` implementa `CachePort` do Core
