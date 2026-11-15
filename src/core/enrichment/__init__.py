"""Enrichment domain service — enriches features with additional context.

This package provides the enrichment strategy interface and coordinates
between LLM and heuristic enrichers. No external dependencies.
"""

from __future__ import annotations

from .service import (
    EnrichmentAdapter,
    EnrichmentConfig,
    EnrichmentService,
    EnrichmentStrategy,
)

__all__ = [
    "EnrichmentAdapter",
    "EnrichmentConfig",
    "EnrichmentService",
    "EnrichmentStrategy",
]
