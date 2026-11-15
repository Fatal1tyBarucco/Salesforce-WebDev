"""Enrichment domain service — orchestrates AI-powered feature enrichment.

This service defines the enrichment strategy and coordinates the generation
of business context, technical details, and migration guidance.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.models.classification import ClassificationResult
from src.models.enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
    ReleaseEnrichment,
)
from src.models.feature import FeatureCategory

logger = logging.getLogger(__name__)


class EnrichmentStrategy(Enum):
    """Enrichment strategy to use."""

    LLM = "llm"
    TEMPLATE = "template"  # Use predefined templates
    HYBRID = "hybrid"  # Try LLM, fall back to template


@dataclass(frozen=True)
class EnrichmentConfig:
    """Enrichment configuration — immutable value object."""

    strategy: EnrichmentStrategy = EnrichmentStrategy.HYBRID
    locale: str = "pt_BR"
    include_migration_notes: bool = True
    include_business_context: bool = True
    include_technical_context: bool = True
    max_features_per_category: int = 50
    timeout_seconds: int = 120


class EnrichmentAdapter(ABC):
    """Abstract adapter for enrichment implementations.

    The domain service depends on this interface. Concrete implementations
    (LLM-based, template-based) live in the infrastructure layer.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name for logging."""
        ...

    @abstractmethod
    async def enrich_category(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        """Enrich a category with AI-generated details."""
        ...

    @abstractmethod
    async def enrich_release(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        """Enrich an entire release with executive summary and strategic themes."""
        ...


class EnrichmentService:
    """Domain service for enriching classified features.

    Generates business context, technical details, migration guidance,
    and strategic summaries for releases.
    """

    def __init__(
        self,
        config: EnrichmentConfig | None = None,
        llm_adapter: EnrichmentAdapter | None = None,
        template_adapter: EnrichmentAdapter | None = None,
    ) -> None:
        self.config = config or EnrichmentConfig()
        self._llm_adapter = llm_adapter
        self._template_adapter = template_adapter

    async def enrich_release(
        self,
        release_slug: str,
        classification_result: ClassificationResult,
        categories: list[FeatureCategory],
    ) -> ReleaseEnrichment:
        """Enrich a full release with all categories.

        Args:
            release_slug: Release identifier.
            classification_result: Classification results for all features.
            categories: Original feature categories.

        Returns:
            Complete ReleaseEnrichment with all details.
        """
        # Build classification lookup
        classifications = {
            feat.name: {
                "impact": feat.impact.value,
                "type": feat.feature_type.value,
                "confidence": feat.confidence,
            }
            for feat in classification_result.features
        }

        # Enrich each category
        category_enrichments: list[CategoryEnrichment] = []
        for cat in categories:
            feature_names = [f.name for f in cat.features]
            if not feature_names:
                continue

            # Limit features per category
            feature_names = feature_names[: self.config.max_features_per_category]

            enrichment = await self._enrich_category(
                cat.name, feature_names, classifications, cat.locale
            )
            category_enrichments.append(enrichment)

        # Enrich release level
        release_enrichment = await self._enrich_release(
            release_slug, category_enrichments, self.config.locale
        )

        return release_enrichment

    async def _enrich_category(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        """Enrich a single category."""
        if self.config.strategy == EnrichmentStrategy.LLM:
            return await self._enrich_with_llm(category_name, features, classifications, locale)
        elif self.config.strategy == EnrichmentStrategy.TEMPLATE:
            return await self._enrich_with_template(
                category_name, features, classifications, locale
            )
        else:  # HYBRID
            try:
                return await self._enrich_with_llm(category_name, features, classifications, locale)
            except Exception as e:
                logger.warning("LLM enrichment failed for %s: %s, using template", category_name, e)
                return await self._enrich_with_template(
                    category_name, features, classifications, locale
                )

    async def _enrich_with_llm(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        """Enrich using LLM adapter."""
        if not self._llm_adapter:
            raise RuntimeError("LLM adapter not configured")

        return await self._llm_adapter.enrich_category(
            category_name, features, classifications, locale
        )

    async def _enrich_with_template(
        self,
        category_name: str,
        features: list[str],
        classifications: dict[str, Any],
        locale: str,
    ) -> CategoryEnrichment:
        """Enrich using template adapter."""
        if not self._template_adapter:
            # Fallback to minimal enrichment
            return self._minimal_category_enrichment(category_name, features, locale)

        return await self._template_adapter.enrich_category(
            category_name, features, classifications, locale
        )

    async def _enrich_release(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        """Enrich the release level with executive summary."""
        if self.config.strategy == EnrichmentStrategy.LLM and self._llm_adapter:
            try:
                return await self._llm_adapter.enrich_release(
                    release_slug, category_enrichments, locale
                )
            except Exception as e:
                logger.warning("LLM release enrichment failed: %s, using template", e)

        # Template or fallback
        if self._template_adapter:
            return await self._template_adapter.enrich_release(
                release_slug, category_enrichments, locale
            )

        return self._minimal_release_enrichment(release_slug, category_enrichments, locale)

    def _minimal_category_enrichment(
        self, category_name: str, features: list[str], locale: str
    ) -> CategoryEnrichment:
        """Minimal enrichment when no adapters available."""
        from datetime import datetime

        return CategoryEnrichment(
            category_name=category_name,
            overview=f"Categoria {category_name} com {len(features)} features.",
            key_themes=tuple(features[:5]),
            business_impact="Análise de impacto de negócio não disponível.",
            adoption_guidance="Consulte a documentação oficial do Salesforce.",
            risk_assessment="Avaliação de risco não disponível.",
            feature_enrichments=tuple(
                FeatureEnrichment(
                    feature_name=name,
                    summary="",
                    details="",
                    business_context="",
                    technical_context="",
                    locale=locale,
                    generated_at=datetime.now().isoformat(),
                )
                for name in features
            ),
            locale=locale,
            generated_at=datetime.now().isoformat(),
        )

    def _minimal_release_enrichment(
        self,
        release_slug: str,
        category_enrichments: list[CategoryEnrichment],
        locale: str,
    ) -> ReleaseEnrichment:
        """Minimal release enrichment when no adapters available."""
        from datetime import datetime

        all_features: list[str] = []
        for cat in category_enrichments:
            all_features.extend(cat.key_themes)

        return ReleaseEnrichment(
            release_slug=release_slug,
            executive_summary=f"Release {release_slug} com {len(category_enrichments)} categorias.",
            strategic_themes=tuple(all_features[:10]),
            category_enrichments=tuple(category_enrichments),
            migration_checklist=(
                "Revisar notas de versão oficiais",
                "Testar em sandbox antes de produção",
                "Comunicar mudanças às equipes afetadas",
            ),
            locale=locale,
            generated_at=datetime.now().isoformat(),
        )
