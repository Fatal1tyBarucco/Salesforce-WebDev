"""Core domain — pipeline, use cases, and domain services.

This layer contains the application logic orchestrated by the use cases.
It depends only on domain models (src.models) and has no external dependencies.
"""

from __future__ import annotations

from .classification.service import (
    ClassificationService,
    ClassificationStrategy,
)
from .enrichment.service import (
    EnrichmentService,
    EnrichmentStrategy,
)
from .pipeline.orchestrator import (
    PipelineConfig,
    PipelineOrchestrator,
    PipelineResult,
)
from .pipeline.steps import (
    ClassificationStep,
    EnrichmentStep,
    GenerationStep,
    NotificationStep,
    ParsingStep,
    PipelineStep,
    ScrapingStep,
    TranslationStep,
)
from .summarization.service import (
    SummarizationService,
)

__all__ = [
    # Classification
    "ClassificationService",
    "ClassificationStep",
    "ClassificationStrategy",
    # Enrichment
    "EnrichmentService",
    "EnrichmentStep",
    "EnrichmentStrategy",
    "GenerationStep",
    "NotificationStep",
    "ParsingStep",
    "PipelineConfig",
    "PipelineOrchestrator",
    "PipelineResult",
    # Pipeline
    "PipelineStep",
    "ScrapingStep",
    # Summarization
    "SummarizationService",
    "TranslationStep",
]
