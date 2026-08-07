"""AI-powered feature enrichment.

Generates professional descriptions and impact assessments for individual
Salesforce release features using LLM analysis.  Operates in batch mode
(one LLM call per category, not per feature) to minimize cost and latency.

Refactored (Phase 1): uses structured prompts with CTA persona,
Pydantic-validated outputs, and business context.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .ai.prompts.enrichment import (
    build_enrichment_system_prompt,
    build_enrichment_user_prompt,
    build_release_context,
    parse_enrichment_response,
)
from .ai.prompts.validation import EnrichmentOutput
from .config import RELEASES_DIR
from .llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class EnrichedFeature:
    """A single feature with AI-generated metadata."""

    name: str
    description: str
    impact: str  # "alto", "médio", "baixo"
    availability: str = ""
    audience: str = ""  # "usuários", "admins", "ambos"

    def to_markdown_row(self) -> str:
        """Render as a Markdown table row."""
        impact_icon = {"alto": "🔴", "médio": "🟡", "baixo": "🟢"}.get(self.impact, "⚪")
        desc = self.description[:120] + "…" if len(self.description) > 120 else self.description
        avail = f" — _{self.availability}_" if self.availability else ""
        return f"| **{self.name}**{avail} | {desc} | {impact_icon} {self.impact} |"


@dataclass
class CategoryEnrichment:
    """Enrichment data for an entire category."""

    category_name: str
    category_slug: str
    introduction: str  # AI-generated intro paragraph
    features: list[EnrichedFeature] = field(default_factory=list)
    total_features: int = 0
    high_impact_count: int = 0
    medium_impact_count: int = 0
    low_impact_count: int = 0


class FeatureEnricher:
    """Enriches release features with AI-generated descriptions and impact analysis.

    Uses batch prompting — one LLM call per category — to keep costs low
    while producing professional-grade content.
    """

    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm or LLMService()

    async def enrich_category(
        self,
        category_name: str,
        category_slug: str,
        features: list[dict[str, str]],
        release_name: str = "",
        release_context: str = "",
    ) -> CategoryEnrichment:
        """Enrich all features in a category with a single LLM call.

        Args:
            category_name: Human-readable category name (e.g. "Agentforce").
            category_slug: URL-safe slug (e.g. "agentforce").
            features: List of dicts with at least 'name' and optionally 'availability'.
            release_name: Release name for context (e.g. "Summer '26").
            release_context: Additional context about the release.

        Returns:
            CategoryEnrichment with descriptions, impact levels, and intro paragraph.
        """
        if not features:
            return CategoryEnrichment(
                category_name=category_name,
                category_slug=category_slug,
                introduction=f"Categoria **{category_name}** sem recursos nesta release.",
                total_features=0,
            )

        # Build feature list for the prompt
        feature_names = []
        for i, f in enumerate(features, 1):
            avail = f.get("availability", "")
            name = f.get("name", "Unknown")
            feature_names.append(f"{i}. {name}" + (f" ({avail})" if avail else ""))

        features_text = "\n".join(feature_names)

        system_prompt = build_enrichment_system_prompt()

        user_prompt = build_enrichment_user_prompt(
            release_name=release_name,
            category_name=category_name,
            features_text=features_text,
            release_context=release_context,
        )

        result = await self._llm.generate_text(user_prompt, system_prompt)

        if result:
            parsed = self._parse_llm_response(result, features)
            if parsed:
                return parsed

        # Fallback: generate basic enrichment without LLM
        return self._generate_fallback_enrichment(category_name, category_slug, features)

    async def enrich_release(
        self,
        release_slug: str,
        release_name: str = "",
    ) -> dict[str, CategoryEnrichment]:
        """Enrich all categories in a release.

        Args:
            release_slug: Release directory name (e.g. 'summer_26').
            release_name: Human-readable release name.

        Returns:
            Dict mapping category slug to CategoryEnrichment.
        """
        release_dir = Path(RELEASES_DIR) / release_slug
        pt_br_dir = release_dir / "pt_BR"

        if not pt_br_dir.is_dir():
            logger.warning("No pt_BR directory found for %s", release_slug)
            return {}

        # Load release meta for context
        meta_path = release_dir / ".meta.json"
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        if not release_name:
            release_name = meta.get("name", release_slug)

        # Build release context from meta
        total = meta.get("total_features", 0)
        cats = meta.get("categories", [])
        release_context = build_release_context(
            release_name=release_name,
            total_features=total,
            categories=cats,
        )

        enrichments: dict[str, CategoryEnrichment] = {}

        for md_file in sorted(pt_br_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue

            content = md_file.read_text(encoding="utf-8")
            category_name = self._extract_category_name(content, md_file.stem)
            category_slug = md_file.stem

            # Extract features from the markdown table
            features = self._extract_features_from_markdown(content)

            if not features:
                continue

            logger.info(
                "Enriching %s/%s (%d features)",
                release_slug,
                category_slug,
                len(features),
            )

            enrichment = await self.enrich_category(
                category_name=category_name,
                category_slug=category_slug,
                features=features,
                release_name=release_name,
                release_context=release_context,
            )

            enrichments[category_slug] = enrichment

        return enrichments

    def _parse_llm_response(
        self, response: str, original_features: list[dict[str, str]]
    ) -> CategoryEnrichment | None:
        """Parse the LLM JSON response into a CategoryEnrichment.

        Uses Pydantic validation via parse_enrichment_response for type safety.
        """
        validated = parse_enrichment_response(response)
        if validated is None:
            logger.warning("Failed to parse/validate LLM enrichment response")
            return None

        return self._validated_to_enrichment(validated, original_features)

    def _validated_to_enrichment(
        self,
        validated: EnrichmentOutput,
        original_features: list[dict[str, str]],
    ) -> CategoryEnrichment:
        """Convert a validated EnrichmentOutput to CategoryEnrichment."""
        enriched_features: list[EnrichedFeature] = []
        high = medium = low = 0

        for i, feat in enumerate(validated.features):
            if feat.impact == "alto":
                high += 1
            elif feat.impact == "baixo":
                low += 1
            else:
                medium += 1

            avail = ""
            if i < len(original_features):
                avail = original_features[i].get("availability", "")

            enriched_features.append(
                EnrichedFeature(
                    name=feat.name,
                    description=feat.description,
                    impact=feat.impact,
                    availability=avail,
                    audience=feat.audience,
                )
            )

        return CategoryEnrichment(
            category_name="",
            category_slug="",
            introduction=validated.introduction,
            features=enriched_features,
            total_features=len(enriched_features),
            high_impact_count=high,
            medium_impact_count=medium,
            low_impact_count=low,
        )

    def _generate_fallback_enrichment(
        self,
        category_name: str,
        category_slug: str,
        features: list[dict[str, str]],
    ) -> CategoryEnrichment:
        """Generate basic enrichment without LLM (fallback)."""
        enriched: list[EnrichedFeature] = []
        high = medium = low = 0

        for feat in features:
            name = feat.get("name", "Unknown")
            avail = feat.get("availability", "")

            # Heuristic impact based on keywords
            name_lower = name.lower()
            if any(
                kw in name_lower for kw in ["security", "compliance", "mfa", "encryption", "audit"]
            ):
                impact = "alto"
                high += 1
            elif any(kw in name_lower for kw in ["new", "beta", "generally available", "ga"]):
                impact = "médio"
                medium += 1
            else:
                impact = "baixo"
                low += 1

            description = f"Recurso '{name}' disponível na release."
            if avail:
                description += f" Disponibilidade: {avail}."

            enriched.append(
                EnrichedFeature(
                    name=name,
                    description=description,
                    impact=impact,
                    availability=avail,
                )
            )

        return CategoryEnrichment(
            category_name=category_name,
            category_slug=category_slug,
            introduction=f"Categoria **{category_name}** com {len(features)} recursos nesta release.",
            features=enriched,
            total_features=len(enriched),
            high_impact_count=high,
            medium_impact_count=medium,
            low_impact_count=low,
        )

    @staticmethod
    def _extract_category_name(content: str, fallback: str) -> str:
        """Extract category name from markdown heading."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 🔗"):
                return line[3:].strip()
            if line.startswith("# ") and "Release" not in line:
                return line[2:].strip()
        return fallback.replace("_", " ").title()

    @staticmethod
    def _extract_features_from_markdown(content: str) -> list[dict[str, str]]:
        """Extract features from a markdown table."""
        features: list[dict[str, str]] = []
        in_table = False

        for line in content.split("\n"):
            stripped = line.strip()

            # Detect table start
            if stripped.startswith("| Recurso") or stripped.startswith("| Feature"):
                in_table = True
                continue

            # Skip separator
            if in_table and stripped.startswith("| :---"):
                continue

            # End of table
            if in_table and not stripped.startswith("|"):
                in_table = False
                continue

            # Parse table row
            if in_table and stripped.startswith("|"):
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if len(cells) >= 2:
                    name = cells[0]
                    # Clean up name
                    name = name.replace("**", "").replace(" ⚠️", "").strip()

                    # Extract availability from flags
                    flags = cells[1:5] if len(cells) >= 5 else cells[1:]
                    avail_parts = []
                    labels = ["usuários", "admins", "config", "contato"]
                    for j, flag in enumerate(flags):
                        if "✅" in flag and j < len(labels):
                            avail_parts.append(labels[j])

                    availability = ", ".join(avail_parts) if avail_parts else ""

                    if name and not name.startswith(":"):
                        features.append({"name": name, "availability": availability})

        return features
