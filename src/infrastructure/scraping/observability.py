"""Scraper observability adapter with structured logging and metrics."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict
from typing import Any

import structlog

from src.domain.scraper import ScraperMetrics

logger = structlog.get_logger(__name__)


class ScraperObservabilityAdapter:
    """Observability adapter for scraper with structured logging."""

    def __init__(self, enable_metrics: bool = True) -> None:
        self.enable_metrics = enable_metrics
        self._metrics_buffer: list[ScraperMetrics] = []

    def log_scrape_attempt(self, metrics: ScraperMetrics) -> None:
        """Log a scrape attempt with full metrics."""
        log_data = asdict(metrics)
        log_data["timestamp"] = time.time()
        log_data["event_type"] = "scrape_attempt"

        if metrics.success:
            logger.info("scrape_success", **log_data)
        else:
            logger.warning("scrape_failure", **log_data)

        if self.enable_metrics:
            self._metrics_buffer.append(metrics)

    def log_layout_change(self, url: str, failed_selectors: list[str], correlation_id: str) -> None:
        """Log detected layout change."""
        logger.warning(
            "layout_change_detected",
            url=url,
            failed_selectors=failed_selectors,
            correlation_id=correlation_id,
            event_type="layout_change",
            timestamp=time.time(),
        )

    def record_metrics(self, metrics: ScraperMetrics) -> None:
        """Record metrics for observability."""
        if self.enable_metrics:
            self._metrics_buffer.append(metrics)

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self._metrics_buffer:
            return {"total": 0}

        total = len(self._metrics_buffer)
        successful = sum(1 for m in self._metrics_buffer if m.success)
        failed = total - successful

        error_counts: dict[str, int] = {}
        for m in self._metrics_buffer:
            if m.error_code:
                error_counts[m.error_code.value] = error_counts.get(m.error_code.value, 0) + 1

        avg_latency = sum(m.latency_ms for m in self._metrics_buffer if m.latency_ms > 0) / max(
            1, sum(1 for m in self._metrics_buffer if m.latency_ms > 0)
        )

        return {
            "total_requests": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "average_latency_ms": round(avg_latency, 2),
            "error_breakdown": error_counts,
            "cache_hits": sum(1 for m in self._metrics_buffer if m.cache_hit),
        }

    def flush_metrics(self) -> list[ScraperMetrics]:
        """Flush and return metrics buffer."""
        metrics = self._metrics_buffer
        self._metrics_buffer = []
        return metrics


# Configure structlog for JSON output
def configure_structlog(json_output: bool = True) -> None:
    """Configure structlog for structured logging."""
    from collections.abc import Callable, MutableMapping

    processors: list[Callable[[Any, str, MutableMapping[str, Any]], Any]] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.ConsoleRenderer() if not json_output else structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
