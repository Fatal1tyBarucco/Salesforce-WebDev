"""AI-powered impact analyzer.

Analyzes release changes and predicts their impact on users,
generates impact reports, and suggests migration actions using a resilient LLM service.
"""

from __future__ import annotations
from typing import Any

import asyncio
import logging

from dataclasses import dataclass
from pathlib import Path

from .config import RELEASES_DIR
from .feature_classifier import FeatureClassifier, FeatureType, ImpactLevel
from .heuristic_classifier import HeuristicFeatureClassifier
from .llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class ImpactArea:
    """An area affected by release changes."""

    name: str
    affected_count: int
    severity: str
    migration_required: bool


@dataclass
class ImpactReport:
    """Comprehensive impact analysis for a release."""

    release_slug: str
    total_features: int
    high_impact_count: int
    breaking_changes: list[str]
    security_fixes: list[str]
    areas: list[ImpactArea]
    migration_actions: list[str]
    risk_score: float
    executive_summary: str


class ImpactAnalyzer:
    """Analyzes release impact on users and systems using LLM."""

    def __init__(self, base_dir: str = RELEASES_DIR, llm: LLMService | None = None) -> None:
        self._base_dir = Path(base_dir)
        self._llm = llm or LLMService()
        self._classifier = FeatureClassifier(llm=self._llm)
        self._heuristic = HeuristicFeatureClassifier()

    async def analyze(self, release_slug: str) -> ImpactReport | None:
        """Analyze impact for a release using a combination of classification and LLM analysis.

        Args:
            release_slug: The release directory name.

        Returns:
            ImpactReport or None if release not found.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return None

        all_feature_texts: list[str] = []

        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue
            content = md_file.read_text(encoding="utf-8")
            all_feature_texts.extend(self._extract_feature_texts(content))

        if not all_feature_texts:
            return None

        # Classify all features in parallel with heuristic fallback
        raw_results = await asyncio.gather(
            *(self._classifier.classify_text(text) for text in all_feature_texts),
            return_exceptions=True,
        )

        classified_features = []
        for i, result in enumerate(raw_results):
            if isinstance(result, BaseException):
                logger.warning(
                    "LLM classification failed for '%s', using heuristic: %s",
                    all_feature_texts[i][:50],
                    result,
                )
                fallback = self._heuristic.classify_text(all_feature_texts[i])
                # Convert to ClassifiedFeature-like object
                classified_features.append(
                    type(
                        "HeuristicResult",
                        (),
                        {
                            "feature_type": FeatureType(fallback.get("type", "other")),
                            "impact_level": ImpactLevel(fallback.get("impact", "medium")),
                            "confidence": fallback.get("confidence", 0.3),
                        },
                    )()
                )
            else:
                classified_features.append(result)

        breaking_changes: list[str] = []
        security_fixes: list[str] = []
        high_impact_count = 0

        for text, classified in zip(all_feature_texts, classified_features):
            if classified.feature_type == FeatureType.BREAKING_CHANGE:
                breaking_changes.append(text)
            elif classified.feature_type == FeatureType.SECURITY:
                security_fixes.append(text)

            if classified.impact == ImpactLevel.HIGH:
                high_impact_count += 1

        # 2. Use LLM to generate migration actions and executive summary
        context = (
            f"Release: {release_slug}\n"
            f"Total Features: {len(all_feature_texts)}\n"
            f"Breaking Changes: {len(breaking_changes)}\n"
            f"Security Fixes: {len(security_fixes)}\n"
            f"High Impact Features: {high_impact_count}\n"
            f"Key Breaking Changes: {', '.join(breaking_changes[:5])}"
        )

        system_prompt = (
            "You are a Salesforce Solution Architect. Analyze the provided release context "
            "and generate: (1) A list of prioritized migration actions, and (2) A risk score (0.0-1.0) "
            "with a brief justification. Return as JSON: "
            '{"migration_actions": ["action 1", ...], "risk_score": 0.5, "justification": "..."}'
        )

        llm_result = await self._llm.generate_text(context, system_prompt)

        if not llm_result:
            parsed: dict[str, Any] = {}
        else:
            import json

            try:
                start_idx = llm_result.find("{")
                end_idx = llm_result.rfind("}") + 1
                parsed = json.loads(llm_result[start_idx:end_idx]) if start_idx != -1 else {}
            except (ValueError, IndexError):
                parsed = {}

        migration_actions = parsed.get(
            "migration_actions", ["Review release notes for manual updates"]
        )
        risk_score = float(parsed.get("risk_score", 0.5))
        justification = parsed.get("justification", "Based on feature volume and breaking changes.")

        # 3. Analyze areas
        areas = await self._analyze_areas(all_feature_texts)

        # 4. Generate executive summary
        executive_summary = self._generate_summary(
            release_slug,
            len(all_feature_texts),
            high_impact_count,
            len(breaking_changes),
            len(security_fixes),
            risk_score,
            justification,
        )

        return ImpactReport(
            release_slug=release_slug,
            total_features=len(all_feature_texts),
            high_impact_count=high_impact_count,
            breaking_changes=breaking_changes,
            security_fixes=security_fixes,
            areas=areas,
            migration_actions=migration_actions,
            risk_score=risk_score,
            executive_summary=executive_summary,
        )

    def _extract_feature_texts(self, content: str) -> list[str]:
        """Extract feature texts from markdown content."""
        features: list[str] = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                text = line[2:].strip()
                if len(text) > 5:
                    features.append(text)
            elif "|" in line and "RECURSO" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and len(parts[0]) > 3:
                    features.append(parts[0])
        return features

    async def _analyze_areas(self, features: list[str]) -> list[ImpactArea]:
        """Analyze impact areas from features using the classifier."""
        area_counts: dict[str, int] = {}
        area_severity: dict[str, str] = {}

        # Classify all features in parallel with heuristic fallback
        raw_results = await asyncio.gather(
            *(self._classifier.classify_text(text) for text in features),
            return_exceptions=True,
        )

        classified_features = []
        for i, result in enumerate(raw_results):
            if isinstance(result, BaseException):
                logger.warning("LLM classification failed, using heuristic: %s", result)
                fallback = self._heuristic.classify_text(features[i])
                classified_features.append(
                    type(
                        "HeuristicResult",
                        (),
                        {
                            "feature_type": FeatureType(fallback.get("type", "other")),
                            "impact_level": ImpactLevel(fallback.get("impact", "medium")),
                            "confidence": fallback.get("confidence", 0.3),
                        },
                    )()
                )
            else:
                classified_features.append(result)

        for classified in classified_features:
            area_name = self._map_type_to_area(classified.feature_type)
            area_counts[area_name] = area_counts.get(area_name, 0) + 1

            if classified.impact == ImpactLevel.HIGH:
                area_severity[area_name] = "high"
            elif classified.impact == ImpactLevel.MEDIUM and area_severity.get(area_name) != "high":
                area_severity[area_name] = "medium"
            elif area_severity.get(area_name) is None:
                area_severity[area_name] = "low"

        areas: list[ImpactArea] = []
        for name, count in sorted(area_counts.items(), key=lambda x: x[1], reverse=True):
            severity = area_severity.get(name, "low")
            migration_required = severity == "high" and name in ("security", "breaking")
            areas.append(
                ImpactArea(
                    name=name,
                    affected_count=count,
                    severity=severity,
                    migration_required=migration_required,
                )
            )

        return areas

    def _map_type_to_area(self, ftype: FeatureType) -> str:
        """Map feature type to impact area name."""
        mapping = {
            FeatureType.SECURITY: "security",
            FeatureType.PERFORMANCE: "performance",
            FeatureType.BUG_FIX: "stability",
            FeatureType.NEW_FEATURE: "functionality",
            FeatureType.IMPROVEMENT: "functionality",
            FeatureType.DEPRECATION: "compatibility",
            FeatureType.BREAKING_CHANGE: "breaking",
            FeatureType.INTEGRATION: "integration",
            FeatureType.UI_UX: "user_interface",
        }
        return mapping.get(ftype, "other")

    def _generate_summary(
        self,
        release_slug: str,
        total: int,
        high_impact: int,
        breaking: int,
        security: int,
        risk_score: float,
        justification: str,
    ) -> str:
        """Generate executive summary text."""
        name = release_slug.replace("_", " ").title()
        risk_level = "LOW"
        if risk_score > 0.7:
            risk_level = "CRITICAL"
        elif risk_score > 0.4:
            risk_level = "MEDIUM"

        lines = [
            f"## 🎯 Impact Analysis: {name}",
            "",
            f"**Risk Level:** {risk_level} ({risk_score:.0%})",
            f"*{justification}*",
            "",
            f"- **{total}** total features",
            f"- **{high_impact}** high-impact changes",
            f"- **{breaking}** breaking changes",
            f"- **{security}** security fixes",
            "",
        ]

        if breaking > 0:
            lines.append("⚠️ **Action Required:** Review breaking changes before upgrading.")

        return "\n".join(lines)
