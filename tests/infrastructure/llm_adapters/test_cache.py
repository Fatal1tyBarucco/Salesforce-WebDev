"""Tests for LLM cache adapters - 100% coverage target."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.cache_manager import CacheManager
from src.domain.llm import LLMPrompt, LLMProvider, LLMResponse, LLMUsage
from src.infrastructure.llm_adapters.cache import LLMCacheAdapter, SemanticCacheAdapter


class TestLLMCacheAdapter:
    """Tests for LLMCacheAdapter."""

    @pytest.fixture
    def mock_cache_manager(self):
        """Create mock cache manager."""
        mock = MagicMock()
        mock.get.return_value = None
        mock.set.return_value = None
        mock.delete.return_value = None
        return mock

    @pytest.fixture
    def adapter(self, mock_cache_manager):
        """Create adapter with mock cache."""
        return LLMCacheAdapter(cache_manager=mock_cache_manager)

    @pytest.fixture
    def sample_response(self):
        """Create sample LLM response."""
        return LLMResponse(
            content="Test response",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            provider=LLMProvider.OPENROUTER,
            model="test-model",
        )

    @pytest.mark.asyncio
    async def test_get_returns_none_when_missing(self, adapter, mock_cache_manager):
        """Should return None when key not in cache."""
        mock_cache_manager.get.return_value = None
        result = await adapter.get("missing-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_returns_response_when_cached(
        self, adapter, mock_cache_manager, sample_response
    ):
        """Should return cached response."""
        mock_cache_manager.get.return_value = sample_response.model_dump_json()
        result = await adapter.get("test-key")

        assert result is not None
        assert result.content == "Test response"
        assert result.provider == LLMProvider.OPENROUTER

    @pytest.mark.asyncio
    async def test_set_stores_response(self, adapter, mock_cache_manager, sample_response):
        """Should store response in cache."""
        await adapter.set("test-key", sample_response, ttl_seconds=3600)

        mock_cache_manager.set.assert_called_once()
        call_args = mock_cache_manager.set.call_args
        assert call_args[0][0] == "llm:test-key"
        assert "Test response" in call_args[0][1]
        assert call_args[1]["ttl"] == 3600

    @pytest.mark.asyncio
    async def test_set_uses_default_ttl(self, adapter, mock_cache_manager, sample_response):
        """Should use default TTL when not specified."""
        await adapter.set("test-key", sample_response)

        call_args = mock_cache_manager.set.call_args
        assert call_args[1]["ttl"] == 7 * 24 * 3600  # 7 days

    @pytest.mark.asyncio
    async def test_invalidate_removes_key(self, adapter, mock_cache_manager):
        """Should remove key from cache."""
        await adapter.invalidate("test-key")

        mock_cache_manager.set.assert_called_once_with("llm:test-key", "", ttl=0)

    @pytest.mark.asyncio
    async def test_get_handles_json_errors(self, adapter, mock_cache_manager):
        """Should handle JSON decode errors gracefully."""
        mock_cache_manager.get.return_value = "invalid json"
        result = await adapter.get("test-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_handles_validation_errors(self, adapter, mock_cache_manager):
        """Should handle Pydantic validation errors gracefully."""
        mock_cache_manager.get.return_value = '{"invalid": "data"}'
        result = await adapter.get("test-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_treats_empty_payload_as_miss(self, adapter, mock_cache_manager):
        """Empty cached payload should be a miss."""
        mock_cache_manager.get.return_value = ""
        result = await adapter.get("test-key")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_swallows_store_errors(self, adapter, mock_cache_manager, sample_response):
        """Storage errors must not propagate."""
        mock_cache_manager.set.side_effect = OSError("disk full")

        await adapter.set("test-key", sample_response)

    @pytest.mark.asyncio
    async def test_invalidate_swallows_errors(self, adapter, mock_cache_manager):
        """Invalidation errors must not propagate."""
        mock_cache_manager.set.side_effect = OSError("disk full")

        await adapter.invalidate("test-key")


class TestSemanticCacheAdapter:
    """Tests for SemanticCacheAdapter."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create temporary cache directory."""
        return tmp_path / "semantic_cache"

    @pytest.fixture
    def adapter(self, temp_cache_dir):
        """Create semantic cache adapter."""
        return SemanticCacheAdapter(cache_dir=temp_cache_dir, threshold=0.9)

    @pytest.fixture
    def sample_prompt(self):
        """Create sample prompt."""
        return LLMPrompt(user="Test prompt", system="System prompt")

    @pytest.fixture
    def sample_response(self):
        """Create sample response."""
        return LLMResponse(
            content="Test response",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20),
            provider=LLMProvider.OPENROUTER,
            model="test-model",
        )

    @pytest.mark.asyncio
    async def test_get_returns_none_when_empty(self, adapter, sample_prompt):
        """Should return None when cache is empty."""
        result = await adapter.get(sample_prompt)
        assert result is None

    @pytest.mark.asyncio
    async def test_set_and_get_exact_match(self, adapter, sample_prompt, sample_response):
        """Should store and retrieve exact match."""
        await adapter.set(sample_prompt, sample_response)
        result = await adapter.get(sample_prompt)

        assert result is not None
        assert result.content == "Test response"

    @pytest.mark.asyncio
    async def test_get_returns_none_below_threshold(self, adapter, sample_prompt, sample_response):
        """Should return None for dissimilar prompts (below threshold)."""
        await adapter.set(sample_prompt, sample_response)

        # Different prompt should not match
        different_prompt = LLMPrompt(user="Completely different prompt", system="Different system")
        result = await adapter.get(different_prompt)
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_key_is_deterministic(self, adapter, sample_prompt):
        """Cache key should be deterministic."""
        key1 = sample_prompt.cache_key()
        key2 = sample_prompt.cache_key()
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_different_prompts_different_keys(self, adapter):
        """Different prompts should have different cache keys."""
        prompt1 = LLMPrompt(user="Test 1")
        prompt2 = LLMPrompt(user="Test 2")
        assert prompt1.cache_key() != prompt2.cache_key()

    @pytest.mark.asyncio
    async def test_embedding_similarity(self, adapter):
        """Should compute cosine similarity correctly."""
        # Same text should have similarity 1.0
        text = "test text"
        emb1 = adapter._get_embedding(text)
        emb2 = adapter._get_embedding(text)
        sim = adapter._cosine_similarity(emb1, emb2)
        assert abs(sim - 1.0) < 0.001

    @pytest.mark.asyncio
    async def test_embedding_dissimilarity(self, adapter):
        """Should compute low similarity for different texts."""
        emb1 = adapter._get_embedding("hello world")
        emb2 = adapter._get_embedding("goodbye moon")
        sim = adapter._cosine_similarity(emb1, emb2)
        assert sim < 0.5

    @pytest.mark.asyncio
    async def test_index_persistence(self, temp_cache_dir, sample_prompt, sample_response):
        """Index should persist across adapter instances."""
        adapter1 = SemanticCacheAdapter(cache_dir=temp_cache_dir, threshold=0.9)
        await adapter1.set(sample_prompt, sample_response)

        adapter2 = SemanticCacheAdapter(cache_dir=temp_cache_dir, threshold=0.9)
        result = await adapter2.get(sample_prompt)

        assert result is not None
        assert result.content == "Test response"

    @pytest.mark.asyncio
    async def test_load_index_handles_corrupted_file(self, temp_cache_dir):
        """Should handle corrupted index file gracefully."""
        # Write corrupted index
        temp_cache_dir.mkdir(parents=True, exist_ok=True)
        (temp_cache_dir / "index.json").write_text("invalid json")

        adapter = SemanticCacheAdapter(cache_dir=temp_cache_dir)
        assert adapter._index == {}

    @pytest.mark.asyncio
    async def test_save_index(self, adapter, temp_cache_dir, sample_prompt, sample_response):
        """Should save index to disk."""
        await adapter.set(sample_prompt, sample_response)

        index_file = temp_cache_dir / "index.json"
        assert index_file.exists()

        import asyncio
        import json

        index = await asyncio.to_thread(json.load, index_file.open())

        assert len(index) == 1
        key = next(iter(index.keys()))
        assert "embedding" in index[key]
        assert "prompt_hash" in index[key]
        assert "timestamp" in index[key]

    @pytest.mark.asyncio
    async def test_response_file_holds_valid_json(self, adapter, temp_cache_dir, sample_response):
        """Stored response file should round-trip through the domain model."""
        prompt = LLMPrompt(user="Persistence prompt", system="System prompt")
        await adapter.set(prompt, sample_response)

        response_file = temp_cache_dir / f"{prompt.cache_key()}.json"
        assert response_file.exists()

        restored = LLMResponse.model_validate_json(response_file.read_text())

        assert restored.content == sample_response.content
        assert restored.provider is LLMProvider.OPENROUTER

    @pytest.mark.asyncio
    async def test_get_returns_none_when_response_file_disappeared(
        self, adapter, sample_prompt, sample_response
    ):
        """Index entry without a response file must be a miss."""
        await adapter.set(sample_prompt, sample_response)
        (adapter.cache_dir / f"{sample_prompt.cache_key()}.json").unlink()

        assert await adapter.get(sample_prompt) is None

    @pytest.mark.asyncio
    async def test_get_handles_corrupted_response_file(
        self, adapter, sample_prompt, sample_response
    ):
        """Corrupted response file must be a miss, not an exception."""
        await adapter.set(sample_prompt, sample_response)
        (adapter.cache_dir / f"{sample_prompt.cache_key()}.json").write_text("{not json")

        assert await adapter.get(sample_prompt) is None

    @pytest.mark.asyncio
    async def test_save_index_swallows_write_errors(self, adapter, temp_cache_dir):
        """Index persistence errors must not propagate."""
        adapter._index_file = temp_cache_dir / "missing" / "index.json"

        adapter._save_index()

    @pytest.mark.asyncio
    async def test_set_swallows_write_errors(self, adapter, sample_prompt, sample_response):
        """Write errors must not propagate."""
        adapter._index_file = adapter.cache_dir / "missing" / "index.json"

        await adapter.set(sample_prompt, sample_response)

        assert sample_prompt.cache_key() in adapter._index

    @pytest.mark.asyncio
    async def test_set_swallows_unwritable_cache_dir(self, adapter, sample_prompt, sample_response):
        """A missing cache directory must not raise out of set()."""
        adapter.cache_dir = adapter.cache_dir / "missing"

        await adapter.set(sample_prompt, sample_response)

    @pytest.mark.asyncio
    async def test_cosine_similarity_zero_vector(self, adapter):
        """Zero vectors must yield similarity 0.0 instead of dividing by zero."""
        assert adapter._cosine_similarity([0.0] * 16, [1.0] * 16) == 0.0


class TestLLMCachePersistence:
    """Round-trip tests against the real file-based CacheManager."""

    @pytest.fixture
    def sample_response(self):
        """Create sample response with full metadata."""
        return LLMResponse(
            content="Persisted response",
            usage=LLMUsage(
                prompt_tokens=12,
                completion_tokens=34,
                total_tokens=46,
                estimated_cost_usd=0.01,
                provider=LLMProvider.OPENROUTER.value,
                model="test-model",
            ),
            provider=LLMProvider.OPENROUTER,
            model="test-model",
            finish_reason="length",
        )

    @pytest.mark.asyncio
    async def test_set_then_get_returns_same_response(self, tmp_path, sample_response):
        """set() followed by get() must return the same LLMResponse."""
        adapter = LLMCacheAdapter(cache_manager=CacheManager(cache_dir=tmp_path / "llm"))

        await adapter.set("round-trip", sample_response, ttl_seconds=600)
        restored = await adapter.get("round-trip")

        assert restored is not None
        assert restored.content == sample_response.content
        assert restored.provider is LLMProvider.OPENROUTER
        assert restored.usage == sample_response.usage
        assert restored.model == "test-model"
        assert restored.finish_reason == "length"
        assert restored.cached is False

    @pytest.mark.asyncio
    async def test_cache_survives_adapter_restart(self, tmp_path, sample_response):
        """A new adapter over the same directory must see the cached value."""
        cache_dir = tmp_path / "llm"
        writer = LLMCacheAdapter(cache_manager=CacheManager(cache_dir=cache_dir))
        await writer.set("restart", sample_response, ttl_seconds=600)

        reader = LLMCacheAdapter(cache_manager=CacheManager(cache_dir=cache_dir))
        restored = await reader.get("restart")

        assert restored is not None
        assert restored.content == "Persisted response"
        assert reader._cache.stats.hits == 1
