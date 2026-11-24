"""Generation infrastructure — Markdown generation adapter.

Implements the GenerationStep contract for creating release documentation.
"""

from __future__ import annotations

import logging
from typing import Any

from src.core.pipeline.steps import GenerationStep
from src.core.summarization.service import SummarizationConfig, SummarizationService
from src.infrastructure.storage import StorageAdapter
from src.models.enrichment import ReleaseEnrichment
from src.models.release import ReleaseMetadata

logger = logging.getLogger(__name__)


class GenerationAdapter(GenerationStep):
    """Abstract generation adapter."""

    @property
    def name(self) -> str:
        return "generation_adapter"

    async def execute(self, enrichment: ReleaseEnrichment) -> list[str]:
        raise NotImplementedError


class MarkdownGenerationAdapter(GenerationAdapter):
    """Markdown file generation adapter."""

    def __init__(
        self,
        storage: StorageAdapter,
        summarization_config: SummarizationConfig | None = None,
    ) -> None:
        self._storage = storage
        self._summarizer = SummarizationService(summarization_config or SummarizationConfig())

    @property
    def name(self) -> str:
        return "markdown_generation"

    async def execute(self, enrichment: ReleaseEnrichment) -> list[str]:
        """Generate markdown files for all categories in both locales."""
        # Load release metadata
        release = await self._storage.load_release_metadata(enrichment.release_slug)
        if not release:
            raise ValueError(f"Release metadata not found for {enrichment.release_slug}")

        generated_files = []

        # Generate for each locale
        for locale in ["pt_BR", "en_US"]:
            # Use appropriate enrichment (translated or original)
            if locale == enrichment.locale:
                loc_enrichment = enrichment
            else:
                # For now, use original - translation would be a separate step
                loc_enrichment = enrichment

            # Generate main release notes
            markdown = self._summarizer.generate_release_notes_markdown(release, loc_enrichment)
            filepath = await self._storage.save_markdown(
                enrichment.release_slug,
                "RELEASE_NOTES",
                markdown,
                locale,
            )
            generated_files.append(filepath)

            # Generate per-category files
            for cat_enrichment in loc_enrichment.category_enrichments:
                cat_markdown = self._generate_category_markdown(release, cat_enrichment, locale)
                filepath = await self._storage.save_markdown(
                    enrichment.release_slug,
                    cat_enrichment.category_name,
                    cat_markdown,
                    locale,
                )
                generated_files.append(filepath)

        logger.info(
            "Generated %d markdown files for %s",
            len(generated_files),
            enrichment.release_slug,
        )
        return generated_files

    def _generate_category_markdown(
        self,
        release: ReleaseMetadata,
        cat_enrichment: Any,
        locale: str,
    ) -> str:
        """Generate markdown for a single category."""
        lines = [
            f"# {cat_enrichment.category_name} — {release.name}",
            "",
            f"**Release:** {release.name} (`{release.slug}`)  ",
            f"**Categoria:** {cat_enrichment.category_name}  ",
            f"**Locale:** {locale}  ",
            "",
            "## Visão Geral",
            "",
            cat_enrichment.overview or "Visão geral não disponível.",
            "",
        ]

        if cat_enrichment.key_themes:
            lines.extend(
                [
                    "## Temas Principais",
                    "",
                ]
            )
            for theme in cat_enrichment.key_themes:
                lines.append(f"- {theme}")
            lines.append("")

        if cat_enrichment.business_impact:
            lines.extend(
                [
                    "## Impacto de Negócio",
                    "",
                    cat_enrichment.business_impact,
                    "",
                ]
            )

        if cat_enrichment.adoption_guidance:
            lines.extend(
                [
                    "## Orientações de Adoção",
                    "",
                    cat_enrichment.adoption_guidance,
                    "",
                ]
            )

        if cat_enrichment.risk_assessment:
            lines.extend(
                [
                    "## Avaliação de Risco",
                    "",
                    cat_enrichment.risk_assessment,
                    "",
                ]
            )

        if cat_enrichment.feature_enrichments:
            lines.extend(
                [
                    "## Features",
                    "",
                ]
            )
            for feat in cat_enrichment.feature_enrichments:
                lines.append(f"### {feat.feature_name}")
                lines.append("")

                if feat.summary:
                    lines.append(f"**Resumo:** {feat.summary}")
                    lines.append("")

                if feat.details:
                    lines.append(f"**Detalhes:** {feat.details}")
                    lines.append("")

                if feat.business_context:
                    lines.append(f"**Contexto de Negócio:** {feat.business_context}")
                    lines.append("")

                if feat.technical_context:
                    lines.append(f"**Contexto Técnico:** {feat.technical_context}")
                    lines.append("")

                if feat.migration_notes:
                    lines.append(f"**Notas de Migração:** {feat.migration_notes}")
                    lines.append("")

                if feat.related_features:
                    lines.append("**Features Relacionadas:**")
                    for rel in feat.related_features:
                        lines.append(f"- {rel}")
                    lines.append("")

        lines.extend(
            [
                "---",
                f"*Gerado em {release.generated_at} (locale: {locale})*",
            ]
        )

        return "\n".join(lines)


class ReadmeGenerationAdapter(GenerationAdapter):
    """README generation adapter for the main README.md."""

    def __init__(self, storage: StorageAdapter) -> None:
        self._storage = storage

    @property
    def name(self) -> str:
        return "readme_generation"

    async def execute(self, enrichment: ReleaseEnrichment) -> list[str]:
        """Generate/update main README.md with release summary."""
        # This would typically read existing README and update the release section
        # For now, generate a standalone release summary
        release = await self._storage.load_release_metadata(enrichment.release_slug)
        if not release:
            return []

        lines = [
            f"# {release.name} — Release Notes Summary",
            "",
            f"**Release ID:** {release.release_id}  ",
            f"**Slug:** {release.slug}  ",
            f"**Data:** {release.date or 'N/A'}  ",
            f"**Total Features:** {release.total_features}  ",
            "",
            "## Resumo Executivo",
            "",
            enrichment.executive_summary or "Resumo não disponível.",
            "",
        ]

        if enrichment.strategic_themes:
            lines.extend(
                [
                    "## Temas Estratégicos",
                    "",
                ]
            )
            for theme in enrichment.strategic_themes:
                lines.append(f"- {theme}")
            lines.append("")

        lines.extend(
            [
                "## Categorias",
                "",
            ]
        )

        for cat in enrichment.category_enrichments:
            lines.append(f"### {cat.category_name}")
            lines.append("")
            lines.append(f"{cat.overview}")
            lines.append("")

            if cat.key_themes:
                lines.append("**Temas:**")
                for theme in cat.key_themes:
                    lines.append(f"- {theme}")
                lines.append("")

        content = "\n".join(lines)
        filepath = await self._storage.save_markdown(
            enrichment.release_slug,
            "README_SUMMARY",
            content,
            "pt_BR",
        )

        return [filepath]
