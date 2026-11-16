"""Tests for the scraper observability adapter.

The tests describe the *real* contract of
``src.infrastructure.scraping.observability``:

* ``log_scrape_attempt`` emits a structured ``scrape_success`` /
  ``scrape_failure`` event and buffers the metrics;
* ``record_metrics`` only buffers, without logging;
* ``get_metrics_summary`` returns ``{"total": 0}`` while the buffer is empty
  and the seven aggregated keys once metrics exist;
* ``flush_metrics`` returns the buffered metrics and empties the buffer.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
import structlog

from src.domain.scraper import ScraperErrorCode, ScraperMetrics
from src.infrastructure.scraping import observability as observability_module
from src.infrastructure.scraping.observability import (
    ScraperObservabilityAdapter,
    configure_structlog,
)


@pytest.fixture
def restore_structlog_config():
    """Restore the global structlog configuration after the test."""
    previous = structlog.get_config()
    yield
    structlog.configure(**previous)


class TestScraperMetrics:
    """Tests for the ScraperMetrics dataclass."""

    def test_creation(self):
        """Should create metrics with all fields."""
        metrics = ScraperMetrics(
            url="https://example.com",
            attempt=1,
            success=True,
            latency_ms=100,
            content_size=5000,
            error_code=None,
            selector_used="main",
            cache_hit=False,
            circuit_breaker_state="closed",
            correlation_id="test-123",
        )

        assert metrics.url == "https://example.com"
        assert metrics.attempt == 1
        assert metrics.success is True
        assert metrics.latency_ms == 100
        assert metrics.content_size == 5000
        assert metrics.error_code is None
        assert metrics.selector_used == "main"
        assert metrics.cache_hit is False
        assert metrics.circuit_breaker_state == "closed"
        assert metrics.correlation_id == "test-123"

    def test_optional_fields_have_defaults(self):
        """Optional fields must fall back to the documented defaults."""
        metrics = ScraperMetrics(
            url="https://example.com",
            attempt=1,
            success=True,
            latency_ms=10,
            content_size=20,
        )

        assert metrics.error_code is None
        assert metrics.selector_used is None
        assert metrics.cache_hit is False
        assert metrics.circuit_breaker_state == "closed"
        assert metrics.correlation_id == ""


class TestScraperObservabilityAdapter:
    """Tests for ScraperObservabilityAdapter."""

    @pytest.fixture
    def adapter(self):
        """Create observability adapter."""
        return ScraperObservabilityAdapter(enable_metrics=True)

    @pytest.fixture
    def sample_metrics(self):
        """Create sample metrics."""
        return ScraperMetrics(
            url="https://example.com",
            attempt=1,
            success=True,
            latency_ms=100,
            content_size=5000,
            error_code=None,
            selector_used="main",
            cache_hit=False,
            circuit_breaker_state="closed",
            correlation_id="test-123",
        )

    def test_log_scrape_attempt_success(self, adapter, sample_metrics):
        """Should log a successful attempt and buffer the metrics."""
        with patch.object(observability_module, "logger") as mock_logger:
            adapter.log_scrape_attempt(sample_metrics)

        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_not_called()

        args, kwargs = mock_logger.info.call_args
        assert args == ("scrape_success",)
        assert kwargs["url"] == "https://example.com"
        assert kwargs["attempt"] == 1
        assert kwargs["success"] is True
        assert kwargs["latency_ms"] == 100
        assert kwargs["content_size"] == 5000
        assert kwargs["selector_used"] == "main"
        assert kwargs["correlation_id"] == "test-123"
        assert kwargs["event_type"] == "scrape_attempt"
        assert "timestamp" in kwargs

        assert len(adapter._metrics_buffer) == 1
        assert adapter._metrics_buffer[0].success is True

    def test_log_scrape_attempt_failure(self, adapter):
        """Should log a failed attempt as a warning."""
        metrics = ScraperMetrics(
            url="https://example.com",
            attempt=1,
            success=False,
            latency_ms=0,
            content_size=0,
            error_code=ScraperErrorCode.TIMEOUT,
            correlation_id="test-123",
        )

        with patch.object(observability_module, "logger") as mock_logger:
            adapter.log_scrape_attempt(metrics)

        mock_logger.warning.assert_called_once()
        mock_logger.info.assert_not_called()

        args, kwargs = mock_logger.warning.call_args
        assert args == ("scrape_failure",)
        assert kwargs["success"] is False
        assert kwargs["error_code"] == ScraperErrorCode.TIMEOUT

        assert len(adapter._metrics_buffer) == 1
        assert adapter._metrics_buffer[0].success is False
        assert adapter._metrics_buffer[0].error_code == ScraperErrorCode.TIMEOUT

    def test_log_layout_change(self, adapter):
        """Should emit a layout_change_detected warning."""
        with patch.object(observability_module, "logger") as mock_logger:
            adapter.log_layout_change(
                url="https://example.com",
                failed_selectors=["main", "article"],
                correlation_id="test-123",
            )

        mock_logger.warning.assert_called_once()

        args, kwargs = mock_logger.warning.call_args
        assert args == ("layout_change_detected",)
        assert kwargs["url"] == "https://example.com"
        assert kwargs["failed_selectors"] == ["main", "article"]
        assert kwargs["correlation_id"] == "test-123"
        assert kwargs["event_type"] == "layout_change"
        assert "timestamp" in kwargs

        # A layout change is not a scrape attempt: nothing is buffered.
        assert len(adapter._metrics_buffer) == 0

    def test_record_metrics(self, adapter, sample_metrics):
        """Should record metrics without logging."""
        with patch.object(observability_module, "logger") as mock_logger:
            adapter.record_metrics(sample_metrics)

        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_not_called()

        assert len(adapter._metrics_buffer) == 1
        assert adapter._metrics_buffer[0] is sample_metrics

    def test_get_metrics_summary_empty(self, adapter):
        """Should return the empty summary while nothing was recorded."""
        summary = adapter.get_metrics_summary()

        assert summary == {"total": 0}

    def test_get_metrics_summary_with_data(self, adapter):
        """Should aggregate the recorded metrics."""
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=1,
                success=True,
                latency_ms=100,
                content_size=5000,
                correlation_id="1",
            )
        )
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=2,
                success=True,
                latency_ms=200,
                content_size=6000,
                correlation_id="2",
            )
        )
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=1,
                success=False,
                latency_ms=0,
                content_size=0,
                error_code=ScraperErrorCode.TIMEOUT,
                correlation_id="3",
            )
        )
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=0,
                success=True,
                latency_ms=0,
                content_size=5000,
                cache_hit=True,
                correlation_id="4",
            )
        )

        summary = adapter.get_metrics_summary()

        assert summary["total_requests"] == 4
        assert summary["successful"] == 3
        assert summary["failed"] == 1
        assert summary["success_rate"] == 0.75
        # Only the two non-zero latencies are averaged: (100 + 200) / 2.
        assert summary["average_latency_ms"] == 150.0
        assert summary["error_breakdown"] == {"timeout": 1}
        assert summary["cache_hits"] == 1

    def test_get_metrics_summary_counts_errors_by_code(self, adapter):
        """Each error code must be counted separately."""
        for error_code in (
            ScraperErrorCode.TIMEOUT,
            ScraperErrorCode.TIMEOUT,
            ScraperErrorCode.NETWORK_ERROR,
        ):
            adapter.record_metrics(
                ScraperMetrics(
                    url="https://example.com",
                    attempt=1,
                    success=False,
                    latency_ms=0,
                    content_size=0,
                    error_code=error_code,
                    correlation_id="1",
                )
            )

        summary = adapter.get_metrics_summary()

        assert summary["error_breakdown"] == {"timeout": 2, "network_error": 1}
        assert summary["failed"] == 3
        assert summary["success_rate"] == 0.0

    def test_get_metrics_summary_ignores_zero_latency(self, adapter):
        """Metrics without latency must not drag the average down."""
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=1,
                success=True,
                latency_ms=0,
                content_size=10,
                correlation_id="1",
            )
        )
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=1,
                success=True,
                latency_ms=40,
                content_size=10,
                correlation_id="2",
            )
        )

        summary = adapter.get_metrics_summary()

        assert summary["average_latency_ms"] == 40.0

    def test_flush_metrics(self, adapter):
        """Should return the buffered metrics and empty the buffer."""
        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=1,
                success=True,
                latency_ms=100,
                content_size=5000,
                correlation_id="1",
            )
        )

        metrics = adapter.flush_metrics()

        assert len(metrics) == 1
        assert len(adapter._metrics_buffer) == 0

    def test_flush_metrics_on_empty_buffer(self, adapter):
        """Flushing an empty buffer returns an empty list."""
        assert adapter.flush_metrics() == []

    def test_metrics_disabled(self):
        """Should not record metrics when disabled."""
        adapter = ScraperObservabilityAdapter(enable_metrics=False)

        adapter.record_metrics(
            ScraperMetrics(
                url="https://example.com",
                attempt=1,
                success=True,
                latency_ms=100,
                content_size=5000,
                correlation_id="1",
            )
        )

        assert len(adapter._metrics_buffer) == 0

    def test_log_scrape_attempt_does_not_buffer_when_disabled(self):
        """Logging is kept, buffering is dropped when metrics are disabled."""
        adapter = ScraperObservabilityAdapter(enable_metrics=False)

        with patch.object(observability_module, "logger") as mock_logger:
            adapter.log_scrape_attempt(
                ScraperMetrics(
                    url="https://example.com",
                    attempt=1,
                    success=True,
                    latency_ms=100,
                    content_size=5000,
                    correlation_id="1",
                )
            )

        mock_logger.info.assert_called_once()
        assert len(adapter._metrics_buffer) == 0


class TestConfigureStructlog:
    """Tests for configure_structlog function."""

    def test_configure_with_json(self, restore_structlog_config):
        """Should install the JSON renderer."""
        configure_structlog(json_output=True)

        processors = structlog.get_config()["processors"]
        assert any(isinstance(p, structlog.processors.JSONRenderer) for p in processors)
        assert not any(isinstance(p, structlog.dev.ConsoleRenderer) for p in processors)
        assert structlog.get_config()["cache_logger_on_first_use"] is True

    def test_configure_with_console(self, restore_structlog_config):
        """Should install the console renderer."""
        configure_structlog(json_output=False)

        processors = structlog.get_config()["processors"]
        assert any(isinstance(p, structlog.dev.ConsoleRenderer) for p in processors)
        assert not any(isinstance(p, structlog.processors.JSONRenderer) for p in processors)
