"""Translation infrastructure — LLM-based translation adapter.

Implements translation of enrichments and markdown to target locales.
"""

from __future__ import annotations

import logging
from typing import Any

from src.core.pipeline.steps import TranslationStep
from src.models.enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
    ReleaseEnrichment,
)

logger = logging.getLogger(__name__)


class TranslationAdapter(TranslationStep):
    """Abstract translation adapter."""

    @property
    def name(self) -> str:
        return "translation_adapter"

    async def execute(self, enrichment: ReleaseEnrichment) -> ReleaseEnrichment:
        raise NotImplementedError


class LLMTranslationAdapter(TranslationAdapter):
    """LLM-based translation using OpenRouter or Gemini."""

    def __init__(
        self,
        llm_adapter: Any,  # OpenRouterLLMAdapter or similar
        target_locale: str = "en_US",
        source_locale: str = "pt_BR",
    ) -> None:
        self._llm = llm_adapter
        self.target_locale = target_locale
        self.source_locale = source_locale

    @property
    def name(self) -> str:
        return f"llm_translation_{self.source_locale}_to_{self.target_locale}"

    async def execute(self, enrichment: ReleaseEnrichment) -> ReleaseEnrichment:
        """Translate enrichment to target locale."""
        if enrichment.locale == self.target_locale:
            return enrichment

        # Translate release-level fields
        executive_summary = await self._translate(enrichment.executive_summary)
        strategic_themes = await self._translate_list(enrichment.strategic_themes)
        migration_checklist = await self._translate_list(enrichment.migration_checklist)

        # Translate category enrichments
        translated_categories = []
        for cat in enrichment.category_enrichments:
            translated_cat = await self._translate_category(cat)
            translated_categories.append(translated_cat)

        return ReleaseEnrichment(
            release_slug=enrichment.release_slug,
            executive_summary=executive_summary,
            strategic_themes=tuple(strategic_themes),
            category_enrichments=tuple(translated_categories),
            migration_checklist=tuple(migration_checklist),
            locale=self.target_locale,
            generated_at=enrichment.generated_at,
        )

    async def _translate(self, text: str) -> str:
        """Translate a single text."""
        if not text:
            return ""

        prompt = f"Translate from {self.source_locale} to {self.target_locale}:\n\n{text}"
        try:
            response: str = await self._llm._complete(
                prompt=prompt,
                system_prompt=f"You are a professional translator. Translate from {self.source_locale} to {self.target_locale}. Preserve technical terms, formatting, and tone.",
                temperature=0.1,
                max_tokens=2000,
            )
            return response.strip()
        except Exception as e:
            logger.warning("Translation failed: %s", e)
            return text  # Return original on failure

    async def _translate_list(self, items: tuple[str, ...]) -> tuple[str, ...]:
        """Translate a list of strings."""
        if not items:
            return ()

        # Batch translate for efficiency
        combined = "\n---\n".join(items)
        translated = await self._translate(combined)
        parts = translated.split("\n---\n")

        # Handle mismatch
        if len(parts) != len(items):
            logger.warning("Translation list length mismatch, returning originals")
            return items

        return tuple(p.strip() for p in parts)

    async def _translate_category(self, cat: CategoryEnrichment) -> CategoryEnrichment:
        """Translate a category enrichment."""
        overview = await self._translate(cat.overview)
        key_themes = await self._translate_list(cat.key_themes)
        business_impact = await self._translate(cat.business_impact)
        adoption_guidance = await self._translate(cat.adoption_guidance)
        risk_assessment = await self._translate(cat.risk_assessment)

        # Translate feature enrichments
        translated_features = []
        for feat in cat.feature_enrichments:
            translated_features.append(
                FeatureEnrichment(
                    feature_name=await self._translate(feat.feature_name),
                    summary=await self._translate(feat.summary),
                    details=await self._translate(feat.details),
                    business_context=await self._translate(feat.business_context),
                    technical_context=await self._translate(feat.technical_context),
                    migration_notes=await self._translate(feat.migration_notes),
                    related_features=await self._translate_list(feat.related_features),
                    tags=await self._translate_list(feat.tags),
                    confidence=feat.confidence,
                    locale=self.target_locale,
                    generated_at=feat.generated_at,
                )
            )

        return CategoryEnrichment(
            category_name=await self._translate(cat.category_name),
            overview=overview,
            key_themes=tuple(key_themes),
            business_impact=business_impact,
            adoption_guidance=adoption_guidance,
            risk_assessment=risk_assessment,
            feature_enrichments=tuple(translated_features),
            locale=self.target_locale,
            generated_at=cat.generated_at,
        )


class MockTranslationAdapter(TranslationAdapter):
    """Mock translation adapter for testing (no LLM required)."""

    def __init__(self, target_locale: str = "en_US") -> None:
        self.target_locale = target_locale

    @property
    def name(self) -> str:
        return f"mock_translation_to_{self.target_locale}"

    async def execute(self, enrichment: ReleaseEnrichment) -> ReleaseEnrichment:
        """Return enrichment with locale changed (no actual translation)."""
        if enrichment.locale == self.target_locale:
            return enrichment

        # Just change locale, keep content as-is (for testing)
        return ReleaseEnrichment(
            release_slug=enrichment.release_slug,
            executive_summary=enrichment.executive_summary,
            strategic_themes=enrichment.strategic_themes,
            category_enrichments=enrichment.category_enrichments,
            migration_checklist=enrichment.migration_checklist,
            locale=self.target_locale,
            generated_at=enrichment.generated_at,
        )
