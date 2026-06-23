"""AI-powered feature classifier.

Automatically classifies release features by impact level and type
using keyword-based heuristics and pattern matching.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .config import RELEASES_DIR


class ImpactLevel(Enum):
    """Feature impact level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeatureType(Enum):
    """Feature classification type."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    IMPROVEMENT = "improvement"
    DEPRECATION = "deprecation"
    BREAKING_CHANGE = "breaking_change"
    INTEGRATION = "integration"
    UI_UX = "ui_ux"
    OTHER = "other"


@dataclass
class ClassifiedFeature:
    """A feature with its classification."""

    name: str
    impact: ImpactLevel
    feature_type: FeatureType
    confidence: float
    keywords_matched: list[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    """Result of classifying all features in a release."""

    release_slug: str
    total_features: int
    by_impact: dict[str, int]
    by_type: dict[str, int]
    features: list[ClassifiedFeature]


# ---------------------------------------------------------------------------
# Keyword dictionaries for classification
# ---------------------------------------------------------------------------

HIGH_IMPACT_KEYWORDS: frozenset[str] = frozenset(
    {
        "breaking",
        "deprecat",
        "removed",
        "migration",
        "security",
        "vulnerability",
        "critical",
        "urgent",
        "mandatory",
        "obrigatório",
        "quebra",
        "migração",
        "removido",
        "crítico",
    }
)

MEDIUM_IMPACT_KEYWORDS: frozenset[str] = frozenset(
    {
        "improvement",
        "enhancement",
        "upgrade",
        "optimization",
        "melhoria",
        "aprimoramento",
        "atualização",
        "otimização",
        "performance",
        "new feature",
        "nova funcionalidade",
    }
)

SECURITY_KEYWORDS: frozenset[str] = frozenset(
    {
        "security",
        "segurança",
        "vulnerability",
        "vulnerabilidade",
        "auth",
        "authentication",
        "autenticação",
        "encryption",
        "criptografia",
        "permission",
        "permissão",
        "access control",
        "controle de acesso",
        "cve",
        "patch",
    }
)

PERFORMANCE_KEYWORDS: frozenset[str] = frozenset(
    {
        "performance",
        "speed",
        "velocidade",
        "latency",
        "latência",
        "optimization",
        "otimização",
        "cache",
        "query",
        "index",
        "batch",
        "async",
        "parallel",
    }
)

BUG_FIX_KEYWORDS: frozenset[str] = frozenset(
    {
        "bug",
        "fix",
        "correção",
        "resolved",
        "resolvido",
        "issue",
        "problema",
        "error",
        "erro",
        "crash",
        "broken",
        "quebrado",
    }
)

NEW_FEATURE_KEYWORDS: frozenset[str] = frozenset(
    {
        "new",
        "novo",
        "nova",
        "added",
        "adicionado",
        "introduced",
        "introduzido",
        "launch",
        "lançamento",
        "feature",
        "funcionalidade",
        "capability",
        "capacidade",
    }
)

DEPRECATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "deprecat",
        "deprecated",
        "descontinuado",
        "end of life",
        "eol",
        "sunset",
        "retiring",
        "removing",
    }
)

BREAKING_KEYWORDS: frozenset[str] = frozenset(
    {
        "breaking",
        "break",
        "incompatible",
        "incompatível",
        "migration required",
        "migração necessária",
        "must update",
        "deve atualizar",
    }
)

INTEGRATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "integration",
        "integração",
        "api",
        "webhook",
        "connector",
        "conector",
        "sync",
        "sincronização",
        "mulesoft",
        "slack",
        " Teams",
    }
)

UI_UX_KEYWORDS: frozenset[str] = frozenset(
    {
        "ui",
        "ux",
        "interface",
        "layout",
        "design",
        "theme",
        "tema",
        "component",
        "componente",
        "lightning",
        "aura",
        "lwc",
        "page",
        "página",
    }
)


class FeatureClassifier:
    """Classifies features by impact and type."""

    def classify_text(self, text: str) -> ClassifiedFeature:
        """Classify a single feature text.

        Args:
            text: The feature description text.

        Returns:
            ClassifiedFeature with impact, type, and confidence.
        """
        text_lower = text.lower()

        # Determine impact
        impact, impact_confidence = self._classify_impact(text_lower)

        # Determine type
        feature_type, type_confidence, keywords = self._classify_type(text_lower)

        # Combined confidence
        confidence = (impact_confidence + type_confidence) / 2

        return ClassifiedFeature(
            name=text.strip(),
            impact=impact,
            feature_type=feature_type,
            confidence=confidence,
            keywords_matched=keywords,
        )

    def classify_release(
        self, release_slug: str, base_dir: str = RELEASES_DIR
    ) -> ClassificationResult | None:
        """Classify all features in a release.

        Args:
            release_slug: The release directory name.
            base_dir: Base directory containing releases.

        Returns:
            ClassificationResult or None if release not found.
        """
        release_dir = Path(base_dir) / release_slug
        if not release_dir.is_dir():
            return None

        all_features: list[ClassifiedFeature] = []

        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue
            content = md_file.read_text(encoding="utf-8")
            features = self._extract_features(content)
            all_features.extend(features)

        if not all_features:
            return None

        # Aggregate stats
        by_impact: dict[str, int] = {}
        by_type: dict[str, int] = {}

        for feat in all_features:
            by_impact[feat.impact.value] = by_impact.get(feat.impact.value, 0) + 1
            by_type[feat.feature_type.value] = by_type.get(feat.feature_type.value, 0) + 1

        return ClassificationResult(
            release_slug=release_slug,
            total_features=len(all_features),
            by_impact=by_impact,
            by_type=by_type,
            features=all_features,
        )

    def _classify_impact(self, text: str) -> tuple[ImpactLevel, float]:
        """Classify impact level."""
        high_matches = sum(1 for kw in HIGH_IMPACT_KEYWORDS if kw in text)
        medium_matches = sum(1 for kw in MEDIUM_IMPACT_KEYWORDS if kw in text)

        if high_matches > 0:
            return ImpactLevel.HIGH, min(1.0, 0.7 + high_matches * 0.1)
        if medium_matches > 0:
            return ImpactLevel.MEDIUM, min(1.0, 0.5 + medium_matches * 0.1)
        return ImpactLevel.LOW, 0.3

    def _classify_type(self, text: str) -> tuple[FeatureType, float, list[str]]:
        """Classify feature type."""
        scores: dict[FeatureType, tuple[float, list[str]]] = {}

        for ftype, keywords in [
            (FeatureType.SECURITY, SECURITY_KEYWORDS),
            (FeatureType.PERFORMANCE, PERFORMANCE_KEYWORDS),
            (FeatureType.BUG_FIX, BUG_FIX_KEYWORDS),
            (FeatureType.NEW_FEATURE, NEW_FEATURE_KEYWORDS),
            (FeatureType.DEPRECATION, DEPRECATION_KEYWORDS),
            (FeatureType.BREAKING_CHANGE, BREAKING_KEYWORDS),
            (FeatureType.INTEGRATION, INTEGRATION_KEYWORDS),
            (FeatureType.UI_UX, UI_UX_KEYWORDS),
        ]:
            matched = [kw for kw in keywords if kw in text]
            if matched:
                scores[ftype] = (len(matched) / len(keywords), matched)

        if scores:
            best_type = max(scores, key=lambda k: scores[k][0])
            confidence, matched_keywords = scores[best_type]
            return best_type, min(1.0, 0.5 + confidence), matched_keywords

        return FeatureType.OTHER, 0.2, []

    def _extract_features(self, content: str) -> list[ClassifiedFeature]:
        """Extract and classify features from markdown content."""
        features: list[ClassifiedFeature] = []

        for line in content.split("\n"):
            line = line.strip()
            # Bullet points
            if line.startswith("- ") or line.startswith("* "):
                text = line[2:].strip()
                if len(text) > 5:
                    features.append(self.classify_text(text))
            # Table rows (skip headers)
            elif "|" in line and "RECURSO" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and len(parts[0]) > 3:
                    features.append(self.classify_text(parts[0]))

        return features
