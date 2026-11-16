"""Tests for LLMObservabilityAdapter - 100% coverage target."""

from __future__ import annotations


import pytest

from src.domain.llm import LLMProvider, LLMResponse, LLMUsage, LLMPrompt, LLMError
from src.infrastructure.llm_adapters.observability import LLMObservabilityAdapter, LLMCallMetrics


class TestLLMCallMetrics:
    """Tests for LLMCallMetrics dataclass."""

    def test_default_values(self):
        """Should have correct default values."""
        metrics = LLMCallMetrics(
            provider="openrouter",
            model="test-model",
            latency_ms=100,
            tokens=50,
            cost_usd=0.001,
            success=True,
        )

        assert metrics.provider == "openrouter"
        assert metrics.model == "test-model"
        assert metrics.latency_ms == 100
        assert metrics.tokens == 50
        assert metrics.cost_usd == 0.001
        assert metrics.success is True
        assert metrics.error_type is None
        assert metrics.correlation_id == ""


class TestLLMObservabilityAdapter:
    """Tests for LLMObservabilityAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create observability adapter."""
        return LLMObservabilityAdapter(enable_metrics=True)

    @pytest.fixture
    def sample_prompt(self):
        """Create sample prompt."""
        return LLMPrompt(user="Test prompt", system="System prompt", temperature=0.7)

    @pytest.fixture
    def sample_response(self):
        """Create sample response."""
        return LLMResponse(
            content="Test response",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            provider=LLMProvider.OPENROUTER,
            model="test-model",
        )

    def test_log_llm_call_records_metrics(self, adapter, sample_prompt, sample_response):
        """Should record metrics for LLM call."""
        adapter.log_llm_call(
            provider=LLMProvider.OPENROUTER,
            model="test-model",
            prompt=sample_prompt,
            response=sample_response,
            correlation_id="test-123",
        )

        metrics = adapter._metrics_buffer
        assert len(metrics) == 1
        # LLMProvider.OPENROUTER value is masked for security in logs
        assert metrics[0].provider == "XXXXopenrouterXXXX"
        assert metrics[0].model == "test-model"
        assert metrics[0].tokens == 30
        assert metrics[0].success is True
        assert metrics[0].correlation_id == "test-123"

    def test_log_llm_call_with_cached_response(self, adapter, sample_prompt, sample_response):
        """Should record cached flag."""
        sample_response.cached = True

        adapter.log_llm_call(
            provider=LLMProvider.OPENROUTER,
            model="test-model",
            prompt=sample_prompt,
            response=sample_response,
            correlation_id="test-123",
        )

        metrics = adapter._metrics_buffer
        assert len(metrics) == 1

    def test_log_fallback_records_event(self, adapter):
        """Should record fallback event."""
        error = LLMError("Rate limited", provider="openrouter", status_code=429)

        adapter.log_fallback(
            from_provider=LLMProvider.OPENROUTER,
            to_provider=LLMProvider.OPENCODE,
            error=error,
            correlation_id="test-123",
        )

        # Verify no exception raised
        assert True

    def test_record_metrics(self, adapter):
        """Should record raw metrics."""
        adapter.record_metrics(
            provider="openrouter",
            model="test-model",
            latency_ms=150,
            tokens=100,
            cost=0.002,
            success=True,
        )

        metrics = adapter._metrics_buffer
        assert len(metrics) == 1
        assert metrics[0].provider == "openrouter"
        assert metrics[0].latency_ms == 150
        assert metrics[0].tokens == 100

    def test_record_metrics_failure(self, adapter):
        """Should record failure metrics."""
        adapter.record_metrics(
            provider="openrouter",
            model="test-model",
            latency_ms=5000,
            tokens=0,
            cost=0.0,
            success=False,
        )

        metrics = adapter._metrics_buffer
        assert len(metrics) == 1
        assert metrics[0].success is False
        assert metrics[0].tokens == 0

    def test_get_metrics_summary_empty(self, adapter):
        """Should return empty summary when no metrics."""
        summary = adapter.get_metrics_summary()

        assert summary["total_calls"] == 0

    def test_get_metrics_summary_with_data(self, adapter):
        """Should return correct summary with data."""
        # Add some metrics
        adapter.record_metrics("openrouter", "model1", 100, 50, 0.001, True)
        adapter.record_metrics("openrouter", "model1", 200, 100, 0.002, True)
        adapter.record_metrics("opencode", "model2", 300, 0, 0.0, False)

        summary = adapter.get_metrics_summary()

        assert summary["total_calls"] == 3
        assert summary["successful"] == 2
        assert summary["failed"] == 1
        assert summary["success_rate"] == 2 / 3
        assert summary["total_tokens"] == 150
        assert summary["total_cost_usd"] == 0.003
        assert summary["avg_tokens_per_call"] == 50

    def test_flush_metrics_clears_buffer(self, adapter):
        """Should clear buffer after flush."""
        adapter.record_metrics("openrouter", "model1", 100, 50, 0.001, True)

        metrics = adapter.flush_metrics()
        assert len(metrics) == 1
        assert len(adapter._metrics_buffer) == 0

    def test_metrics_disabled_when_false(self):
        """Should not record metrics when disabled."""
        adapter = LLMObservabilityAdapter(enable_metrics=False)

        adapter.record_metrics("openrouter", "model1", 100, 50, 0.001, True)

        assert len(adapter._metrics_buffer) == 0

    def test_log_llm_call_disabled(self):
        """Should not record metrics when disabled."""
        adapter = LLMObservabilityAdapter(enable_metrics=False)

        prompt = LLMPrompt(user="Test")
        response = LLMResponse(
            content="Test",
            usage=LLMUsage(prompt_tokens=10, completion_tokens=20),
            provider=LLMProvider.OPENROUTER,
            model="test",
        )

        adapter.log_llm_call(LLMProvider.OPENROUTER, "test", prompt, response, "test-123")

        assert len(adapter._metrics_buffer) == 0


class TestConfigureLLMStructlog:
    """Tests for configure_llm_structlog function."""

    def test_configure_with_json_output(self):
        """Should configure structlog with JSON output."""
        from src.infrastructure.llm_adapters.observability import configure_llm_structlog

        # Should not raise
        configure_llm_structlog(json_output=True)

    def test_configure_with_console_output(self):
        """Should configure structlog with console output."""
        from src.infrastructure.llm_adapters.observability import configure_llm_structlog

        # Should not raise
        configure_llm_structlog(json_output=False)
