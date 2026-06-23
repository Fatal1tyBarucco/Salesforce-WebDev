"""AI-powered impact analyzer.

Analyzes release changes and predicts their impact on users,
generates impact reports, and suggests migration actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import RELEASES_DIR
from .feature_classifier import FeatureClassifier, FeatureType, ImpactLevel


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
    """Analyzes release impact on users and systems."""

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir = Path(base_dir)
        self._classifier = FeatureClassifier()

    def analyze(self, release_slug: str) -> ImpactReport | None:
        """Analyze impact for a release.

        Args:
            release_slug: The release directory name.

        Returns:
            ImpactReport or None if release not found.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return None

        all_features: list[str] = []
        breaking_changes: list[str] = []
        security_fixes: list[str] = []

        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue
            content = md_file.read_text(encoding="utf-8")
            features = self._extract_feature_texts(content)
            all_features.extend(features)

            # Classify each feature
            for text in features:
                classified = self._classifier.classify_text(text)
                if classified.feature_type == FeatureType.BREAKING_CHANGE:
                    breaking_changes.append(text)
                elif classified.feature_type == FeatureType.SECURITY:
                    security_fixes.append(text)

        if not all_features:
            return None

        # Analyze impact areas
        areas = self._analyze_areas(all_features)

        # Generate migration actions
        migration_actions = self._generate_migration_actions(breaking_changes, areas)

        # Calculate risk score
        risk_score = self._calculate_risk_score(
            len(all_features), len(breaking_changes), len(security_fixes), areas
        )

        # Count high impact features
        high_impact_count = sum(
            1
            for text in all_features
            if self._classifier.classify_text(text).impact == ImpactLevel.HIGH
        )

        # Generate executive summary
        executive_summary = self._generate_summary(
            release_slug,
            len(all_features),
            high_impact_count,
            len(breaking_changes),
            len(security_fixes),
            risk_score,
        )

        return ImpactReport(
            release_slug=release_slug,
            total_features=len(all_features),
            high_impact_count=high_impact_count,
            breaking_changes=breaking_changes,
            security_fixes=security_fixes,
            areas=areas,
            migration_actions=migration_actions,
            risk_score=risk_score,
            executive_summary=executive_summary,
        )

    def compare_releases(self, current_slug: str, previous_slug: str) -> dict[str, Any] | None:
        """Compare impact between two releases.

        Args:
            current_slug: Current release directory name.
            previous_slug: Previous release directory name.

        Returns:
            Comparison dict or None if either release not found.
        """
        current = self.analyze(current_slug)
        previous = self.analyze(previous_slug)

        if current is None or previous is None:
            return None

        return {
            "current": current_slug,
            "previous": previous_slug,
            "feature_delta": current.total_features - previous.total_features,
            "risk_delta": current.risk_score - previous.risk_score,
            "new_breaking": [
                bc for bc in current.breaking_changes if bc not in previous.breaking_changes
            ],
            "new_security_fixes": [
                sf for sf in current.security_fixes if sf not in previous.security_fixes
            ],
        }

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

    def _analyze_areas(self, features: list[str]) -> list[ImpactArea]:
        """Analyze impact areas from features."""
        area_counts: dict[str, int] = {}
        area_severity: dict[str, str] = {}

        for text in features:
            classified = self._classifier.classify_text(text)
            area_name = self._map_type_to_area(classified.feature_type)
            area_counts[area_name] = area_counts.get(area_name, 0) + 1

            # Track highest severity per area
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

    def _generate_migration_actions(
        self, breaking_changes: list[str], areas: list[ImpactArea]
    ) -> list[str]:
        """Generate migration action items."""
        actions: list[str] = []

        if breaking_changes:
            actions.append(f"Review and address {len(breaking_changes)} breaking change(s)")

        for area in areas:
            if area.migration_required:
                actions.append(f"Migrate {area.name} components ({area.affected_count} features)")

        if not actions:
            actions.append("No migration required — all changes are backward-compatible")

        return actions

    def _calculate_risk_score(
        self,
        total: int,
        breaking: int,
        security: int,
        areas: list[ImpactArea],
    ) -> float:
        """Calculate overall risk score (0.0 to 1.0)."""
        if total == 0:
            return 0.0

        # Base score from feature count
        base = min(total / 200, 0.3)

        # Breaking changes multiplier
        breaking_factor = min(breaking / 10, 0.4)

        # Security fixes (positive impact, reduces risk)
        security_factor = -min(security / 20, 0.1)

        # High severity areas
        high_areas = sum(1 for a in areas if a.severity == "high")
        area_factor = min(high_areas / 5, 0.2)

        score = base + breaking_factor + security_factor + area_factor
        return max(0.0, min(1.0, score))

    def _generate_summary(
        self,
        release_slug: str,
        total: int,
        high_impact: int,
        breaking: int,
        security: int,
        risk_score: float,
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
