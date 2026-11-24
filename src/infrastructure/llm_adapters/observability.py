"""LLM observability adapter with structured logging and metrics."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import structlog

from src.domain.llm import LLMError, LLMPrompt, LLMProvider, LLMResponse

logger = structlog.get_logger(__name__)


@dataclass
class LLMCallMetrics:
    """Metrics for a single LLM call."""

    provider: str
    model: str
    latency_ms: int
    tokens: int
    cost_usd: float
    success: bool
    error_type: str | None = None
    correlation_id: str = ""
    timestamp: float = field(default_factory=time.time)


class LLMObservabilityAdapter:
    """Observability adapter for LLM calls with structured logging."""

    def __init__(self, enable_metrics: bool = True) -> None:
        self.enable_metrics = enable_metrics
        self._metrics_buffer: list[LLMCallMetrics] = []

    def log_llm_call(
        self,
        provider: LLMProvider,
        model: str,
        prompt: LLMPrompt,
        response: LLMResponse,
        correlation_id: str,
    ) -> None:
        """Log an LLM call with full context."""
        log_data = {
            "event_type": "llm_call",
            "provider": provider.value,
            "model": model,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "cost_usd": response.usage.estimated_cost_usd,
            "latency_ms": 0,  # Will be filled by caller
            "cached": response.cached,
            "correlation_id": correlation_id,
            "timestamp": time.time(),
        }

        logger.info("llm_call_completed", **log_data)

        if self.enable_metrics:
            self._metrics_buffer.append(
                LLMCallMetrics(
                    provider=provider.value,
                    model=model,
                    latency_ms=0,
                    tokens=response.usage.total_tokens,
                    cost_usd=response.usage.estimated_cost_usd,
                    success=True,
                    correlation_id=correlation_id,
                )
            )

    def log_fallback(
        self,
        from_provider: LLMProvider,
        to_provider: LLMProvider,
        error: LLMError,
        correlation_id: str,
    ) -> None:
        """Log a fallback event."""
        logger.warning(
            "llm_fallback",
            event_type="llm_fallback",
            from_provider=from_provider.value,
            to_provider=to_provider.value,
            error_type=type(error).__name__,
            error_message=str(error),
            status_code=error.status_code,
            retryable=error.retryable,
            correlation_id=correlation_id,
            timestamp=time.time(),
        )

    def record_metrics(
        self,
        provider: str,
        model: str,
        latency_ms: int,
        tokens: int,
        cost: float,
        success: bool,
    ) -> None:
        """Record metrics for observability."""
        if self.enable_metrics:
            self._metrics_buffer.append(
                LLMCallMetrics(
                    provider=provider,
                    model=model,
                    latency_ms=latency_ms,
                    tokens=tokens,
                    cost_usd=cost,
                    success=success,
                )
            )

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get summary of collected metrics."""
        if not self._metrics_buffer:
            return {"total_calls": 0}

        total = len(self._metrics_buffer)
        successful = sum(1 for m in self._metrics_buffer if m.success)
        failed = total - successful

        total_tokens = sum(m.tokens for m in self._metrics_buffer)
        total_cost = sum(m.cost_usd for m in self._metrics_buffer)

        return {
            "total_calls": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_tokens_per_call": total_tokens / total if total > 0 else 0,
        }

    def flush_metrics(self) -> list[LLMCallMetrics]:
        """Flush and return metrics buffer."""
        metrics = self._metrics_buffer
        self._metrics_buffer = []
        return metrics


# Configure structlog
def configure_llm_structlog(json_output: bool = True) -> None:
    """Configure structlog for LLM observability."""
    from collections.abc import Callable, MutableMapping

    import structlog

    processors: list[Callable[[Any, str, MutableMapping[str, Any]], Any]] = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        (
            structlog.dev.ConsoleRenderer()
            if not json_output
            else structlog.processors.JSONRenderer()
        ),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
