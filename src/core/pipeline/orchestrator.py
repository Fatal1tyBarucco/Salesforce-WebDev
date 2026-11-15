"""Pipeline orchestrator — composes and executes pipeline steps.

The orchestrator is the application service that coordinates the pipeline.
It depends only on domain models and step interfaces (no external deps).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, TypeVar

from src.core.pipeline.steps import (
    ClassificationStep,
    EnrichmentStep,
    GenerationStep,
    NotificationStep,
    ParsingStep,
    PipelineContext,
    PipelineStep,
    ScrapingStep,
    TranslationStep,
)
from src.models.enrichment import ReleaseEnrichment
from src.models.release import ReleaseMetadata

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


@dataclass(frozen=True)
class PipelineConfig:
    """Pipeline configuration — immutable value object."""

    locale: str = "pt_BR"
    enable_enrichment: bool = True
    enable_translation: bool = True
    enable_notification: bool = True
    max_concurrent_steps: int = 1
    timeout_seconds: int = 300


@dataclass(frozen=True)
class PipelineResult:
    """Result of a pipeline execution — immutable value object."""

    release: ReleaseMetadata
    success: bool
    enrichment: ReleaseEnrichment | None = None
    generated_files: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None
    steps_completed: tuple[str, ...] = field(default_factory=tuple)
    duration_seconds: float = 0.0


class PipelineOrchestrator:
    """Orchestrates the ETL pipeline for Salesforce Release Notes.

    The orchestrator composes pipeline steps and executes them in order.
    Each step is an adapter that implements the domain contract.
    """

    def __init__(
        self,
        config: PipelineConfig | None = None,
        scraping_step: ScrapingStep | None = None,
        parsing_step: ParsingStep | None = None,
        classification_step: ClassificationStep | None = None,
        enrichment_step: EnrichmentStep | None = None,
        translation_step: TranslationStep | None = None,
        generation_step: GenerationStep | None = None,
        notification_step: NotificationStep | None = None,
    ) -> None:
        self.config = config or PipelineConfig()
        self._steps: list[PipelineStep[Any, Any]] = []

        # Wire up provided steps
        if scraping_step:
            self._steps.append(scraping_step)
        if parsing_step:
            self._steps.append(parsing_step)
        if classification_step:
            self._steps.append(classification_step)
        if enrichment_step and self.config.enable_enrichment:
            self._steps.append(enrichment_step)
        if translation_step and self.config.enable_translation:
            self._steps.append(translation_step)
        if generation_step:
            self._steps.append(generation_step)
        if notification_step and self.config.enable_notification:
            self._steps.append(notification_step)

    def add_step(self, step: PipelineStep[Any, Any]) -> None:
        """Add a step to the pipeline."""
        self._steps.append(step)

    async def execute(self, release: ReleaseMetadata, url: str) -> PipelineResult:
        """Execute the full pipeline for a release.

        Args:
            release: Release metadata to process.
            url: Source URL to scrape.

        Returns:
            PipelineResult with execution outcome.
        """
        import time

        start_time = time.time()
        PipelineContext(release=release, locale=self.config.locale)
        current_input: Any = url
        steps_completed: list[str] = []
        enrichment: ReleaseEnrichment | None = None
        generated_files: list[str] = []

        logger.info("Starting pipeline for release: %s", release.slug)

        try:
            for step in self._steps:
                logger.info("Executing step: %s", step.name)
                step_start = time.time()

                # Execute step with timeout
                current_input = await step.execute(current_input)

                step_duration = time.time() - step_start
                logger.info("Step %s completed in %.2fs", step.name, step_duration)
                steps_completed.append(step.name)

                # Capture enrichment and generated files from steps
                if isinstance(current_input, ReleaseEnrichment):
                    enrichment = current_input
                elif isinstance(current_input, list) and all(
                    isinstance(f, str) for f in current_input
                ):
                    generated_files = current_input

            duration = time.time() - start_time
            logger.info("Pipeline completed for %s in %.2fs", release.slug, duration)

            return PipelineResult(
                release=release,
                success=True,
                enrichment=enrichment,
                generated_files=tuple(generated_files),
                steps_completed=tuple(steps_completed),
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error("Pipeline failed for %s: %s", release.slug, e)
            return PipelineResult(
                release=release,
                success=False,
                error=str(e),
                steps_completed=tuple(steps_completed),
                duration_seconds=duration,
            )

    async def execute_with_context(self, context: PipelineContext, url: str) -> PipelineResult:
        """Execute pipeline with a pre-built context."""
        return await self.execute(context.release, url)
