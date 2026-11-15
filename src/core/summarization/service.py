"""Summarization domain service — generates summaries from enriched data.

This service creates executive summaries, release notes, and changelogs
from enriched release data. Pure domain logic, no external dependencies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from src.models.enrichment import CategoryEnrichment, ReleaseEnrichment
from src.models.release import ReleaseMetadata

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SummarizationConfig:
    """Summarization configuration — immutable value object."""

    locale: str = "pt_BR"
    executive_summary_max_words: int = 200
    category_summary_max_words: int = 100
    include_migration_checklist: bool = True
    include_key_themes: bool = True
    include_business_impact: bool = True


class SummarizationService:
    """Domain service for generating summaries from enriched release data.

    Creates executive summaries, category summaries, and formatted
    release notes in Markdown.
    """

    def __init__(self, config: SummarizationConfig | None = None) -> None:
        self.config = config or SummarizationConfig()

    def generate_executive_summary(self, enrichment: ReleaseEnrichment) -> str:
        """Generate an executive summary for the release."""
        if enrichment.executive_summary:
            return enrichment.executive_summary

        # Build from strategic themes
        themes = list(enrichment.strategic_themes)
        if not themes:
            return f"Release {enrichment.release_slug}: Nenhuma informação de enriquecimento disponível."

        theme_list = ", ".join(themes[:5])
        return (
            f"O release {enrichment.release_slug} introduz mudanças nas áreas: "
            f"{theme_list}. "
            f"Total de {len(enrichment.category_enrichments)} categorias impactadas."
        )

    def generate_category_summary(self, enrichment: CategoryEnrichment) -> str:
        """Generate a summary for a category."""
        if enrichment.overview:
            return enrichment.overview

        themes = list(enrichment.key_themes)
        if not themes:
            return f"Categoria {enrichment.category_name}: sem detalhes disponíveis."

        theme_list = ", ".join(themes[:3])
        return f"Categoria {enrichment.category_name}: principais temas incluem {theme_list}."

    def generate_release_notes_markdown(
        self, release: ReleaseMetadata, enrichment: ReleaseEnrichment
    ) -> str:
        """Generate full release notes in Markdown format."""
        lines = [
            f"# {release.name} — Release Notes",
            "",
            f"**Release ID:** {release.release_id}  ",
            f"**Slug:** {release.slug}  ",
            f"**Data:** {release.date or 'N/A'}  ",
            f"**Total de Features:** {release.total_features}  ",
            "",
            "## Resumo Executivo",
            "",
            self.generate_executive_summary(enrichment),
            "",
        ]

        if self.config.include_key_themes and enrichment.strategic_themes:
            lines.extend(
                [
                    "## Temas Estratégicos",
                    "",
                ]
            )
            for theme in enrichment.strategic_themes:
                lines.append(f"- {theme}")
            lines.append("")

        # Category details
        lines.append("## Categorias")
        lines.append("")

        for cat_enrichment in enrichment.category_enrichments:
            lines.extend(
                [
                    f"### {cat_enrichment.category_name}",
                    "",
                    self.generate_category_summary(cat_enrichment),
                    "",
                ]
            )

            if self.config.include_business_impact and cat_enrichment.business_impact:
                lines.extend(
                    [
                        "**Impacto de Negócio:**",
                        "",
                        cat_enrichment.business_impact,
                        "",
                    ]
                )

            if cat_enrichment.adoption_guidance:
                lines.extend(
                    [
                        "**Orientações de Adoção:**",
                        "",
                        cat_enrichment.adoption_guidance,
                        "",
                    ]
                )

            if cat_enrichment.risk_assessment:
                lines.extend(
                    [
                        "**Avaliação de Risco:**",
                        "",
                        cat_enrichment.risk_assessment,
                        "",
                    ]
                )

            # Feature enrichments
            if cat_enrichment.feature_enrichments:
                lines.append("**Features:**")
                lines.append("")
                for feat_enrichment in cat_enrichment.feature_enrichments:
                    lines.append(f"- **{feat_enrichment.feature_name}**")
                    if feat_enrichment.summary:
                        lines.append(f"  - {feat_enrichment.summary}")
                    if feat_enrichment.migration_notes:
                        lines.append(f"  - *Migração:* {feat_enrichment.migration_notes}")
                lines.append("")

        if self.config.include_migration_checklist and enrichment.migration_checklist:
            lines.extend(
                [
                    "## Checklist de Migração",
                    "",
                ]
            )
            for item in enrichment.migration_checklist:
                lines.append(f"- [ ] {item}")
            lines.append("")

        lines.extend(
            [
                "---",
                f"*Gerado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (locale: {self.config.locale})*",
            ]
        )

        return "\n".join(lines)

    def generate_changelog_entry(
        self, release: ReleaseMetadata, enrichment: ReleaseEnrichment
    ) -> str:
        """Generate a changelog entry for the release."""
        lines = [
            f"## [{release.name}] - {release.date or datetime.now().strftime('%Y-%m-%d')}",
            "",
        ]

        # Group by impact

        for cat in enrichment.category_enrichments:
            for feat in cat.feature_enrichments:
                # We don't have impact in FeatureEnrichment, use category as proxy
                pass

        # Use strategic themes as high-level changes
        for theme in enrichment.strategic_themes[:10]:
            lines.append(f"- {theme}")

        lines.append("")
        return "\n".join(lines)

    def generate_notification_digest(
        self, enrichment: ReleaseEnrichment, max_items: int = 10
    ) -> str:
        """Generate a concise notification digest."""
        lines = [
            f"🚀 **Novo Release: {enrichment.release_slug}**",
            "",
            self.generate_executive_summary(enrichment),
            "",
            "**Principais Categorias:**",
        ]

        for cat in enrichment.category_enrichments[:5]:
            theme_count = len(cat.key_themes)
            lines.append(f"- {cat.category_name} ({theme_count} temas)")

        if enrichment.migration_checklist:
            lines.extend(
                [
                    "",
                    "**Ações Recomendadas:**",
                ]
            )
            for item in enrichment.migration_checklist[:3]:
                lines.append(f"- {item}")

        return "\n".join(lines)
