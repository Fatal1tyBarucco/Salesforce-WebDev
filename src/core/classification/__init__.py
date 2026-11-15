"""Classification domain service — orchestrates feature classification.

This package provides the classification strategy interface and coordinates
between LLM and heuristic classifiers. No external dependencies.
"""

from __future__ import annotations

from .service import (
    ClassificationAdapter,
    ClassificationConfig,
    ClassificationService,
    ClassificationStrategy,
)

__all__ = [
    "ClassificationAdapter",
    "ClassificationConfig",
    "ClassificationService",
    "ClassificationStrategy",
]
