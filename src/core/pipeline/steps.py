"""Pipeline steps — individual processing stages in the ETL pipeline.

Each step is a pure domain service that transforms input to output.
No external dependencies — only domain models.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, TypeVar

from src.models.classification import ClassificationResult
from src.models.enrichment import ReleaseEnrichment
from src.models.feature import FeatureCategory
from src.models.release import ReleaseMetadata

T = TypeVar("T")
R = TypeVar("R")


class PipelineStep[T, R](ABC):
    """Abstract base class for a pipeline step.

    A step takes input of type T and produces output of type R.
    Steps can be composed into a pipeline.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique step name for logging and debugging."""
        ...

    @abstractmethod
    async def execute(self, input_data: T) -> R:
        """Execute the step with the given input."""
        ...

    async def __call__(self, input_data: T) -> R:
        """Allow step to be called directly."""
        return await self.execute(input_data)


@dataclass(frozen=True)
class PipelineContext:
    """Context passed through the pipeline — immutable value object."""

    release: ReleaseMetadata
    locale: str = "pt_BR"
    metadata: dict[str, Any] = field(default_factory=dict)


class ScrapingStep(PipelineStep[str, str]):
    """Step 1: Scrape raw HTML from Salesforce Release Notes."""

    @property
    def name(self) -> str:
        return "scraping"

    async def execute(self, url: str) -> str:
        """Fetch raw HTML content from the URL.

        This is a domain service — the actual HTTP implementation
        lives in the infrastructure layer (adapter).
        """
        # The actual scraping is delegated to an adapter
        # This step defines the contract
        raise NotImplementedError("Use ScrapingAdapter in infrastructure layer")


class ParsingStep(PipelineStep[str, list[FeatureCategory]]):
    """Step 2: Parse raw HTML into structured feature categories."""

    @property
    def name(self) -> str:
        return "parsing"

    async def execute(self, html: str) -> list[FeatureCategory]:
        """Parse HTML into feature categories.

        The actual parsing logic lives in the infrastructure layer
        (BeautifulSoup adapter). This step defines the contract.
        """
        raise NotImplementedError("Use ParsingAdapter in infrastructure layer")


class ClassificationStep(PipelineStep[list[FeatureCategory], ClassificationResult]):
    """Step 3: Classify features by impact and type."""

    @property
    def name(self) -> str:
        return "classification"

    async def execute(self, categories: list[FeatureCategory]) -> ClassificationResult:
        """Classify all features in the categories.

        The actual classification logic (LLM or heuristic) lives in
        the infrastructure layer. This step defines the contract.
        """
        raise NotImplementedError("Use ClassificationAdapter in infrastructure layer")


class EnrichmentStep(
    PipelineStep[tuple[ClassificationResult, list[FeatureCategory]], ReleaseEnrichment]
):
    """Step 4: Enrich classified features with AI-generated details."""

    @property
    def name(self) -> str:
        return "enrichment"

    async def execute(
        self, input_data: tuple[ClassificationResult, list[FeatureCategory]]
    ) -> ReleaseEnrichment:
        """Enrich classified features with AI-generated details.

        The actual enrichment logic (LLM prompts) lives in the
        infrastructure layer. This step defines the contract.
        """
        raise NotImplementedError("Use EnrichmentAdapter in infrastructure layer")


class TranslationStep(PipelineStep[ReleaseEnrichment, ReleaseEnrichment]):
    """Step 5: Translate enrichments to target locale."""

    @property
    def name(self) -> str:
        return "translation"

    async def execute(self, enrichment: ReleaseEnrichment) -> ReleaseEnrichment:
        """Translate enrichment to target locale.

        The actual translation logic lives in the infrastructure layer.
        This step defines the contract.
        """
        raise NotImplementedError("Use TranslationAdapter in infrastructure layer")


class GenerationStep(PipelineStep[ReleaseEnrichment, list[str]]):
    """Step 6: Generate Markdown files from enriched data."""

    @property
    def name(self) -> str:
        return "generation"

    async def execute(self, enrichment: ReleaseEnrichment) -> list[str]:
        """Generate Markdown files from enrichment.

        The actual generation logic lives in the infrastructure layer.
        This step defines the contract.
        """
        raise NotImplementedError("Use GenerationAdapter in infrastructure layer")


class NotificationStep(PipelineStep[ReleaseEnrichment, None]):
    """Step 7: Send notifications about processed release."""

    @property
    def name(self) -> str:
        return "notification"

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        """Send notifications about the processed release.

        The actual notification logic (GitHub, Slack, email) lives in
        the infrastructure layer. This step defines the contract.
        """
        raise NotImplementedError("Use NotificationAdapter in infrastructure layer")
