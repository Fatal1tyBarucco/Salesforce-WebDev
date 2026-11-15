"""Classification domain models — impact levels, feature types, and results.

Pure domain entities with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


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


class Audience(Enum):
    """Target audience for the feature."""

    USERS = "usuários"
    ADMINS = "admins"
    BOTH = "ambos"


class Priority(Enum):
    """Adoption priority."""

    CRITICAL = "crítica"
    IMPORTANT = "importante"
    OPTIONAL = "opcional"


@dataclass(frozen=True)
class ClassifiedFeature:
    """A feature with its classification — immutable value object."""

    name: str
    impact: ImpactLevel
    feature_type: FeatureType
    confidence: float
    keywords_matched: tuple[str, ...] = field(default_factory=tuple)
    audience: Audience | None = None
    priority: Priority | None = None
    justification: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "name": self.name,
            "impact": self.impact.value,
            "type": self.feature_type.value,
            "confidence": self.confidence,
            "keywords_matched": list(self.keywords_matched),
            "audience": self.audience.value if self.audience else "",
            "priority": self.priority.value if self.priority else "",
            "justification": self.justification,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ClassifiedFeature:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            impact=ImpactLevel(data["impact"]),
            feature_type=FeatureType(data["type"]),
            confidence=data["confidence"],
            keywords_matched=tuple(data.get("keywords_matched", [])),
            audience=Audience(data["audience"]) if data.get("audience") else None,
            priority=Priority(data["priority"]) if data.get("priority") else None,
            justification=data.get("justification", ""),
        )


@dataclass(frozen=True)
class ClassificationResult:
    """Result of classifying all features in a release — immutable aggregate."""

    release_slug: str
    total_features: int
    by_impact: dict[str, int]
    by_type: dict[str, int]
    features: tuple[ClassifiedFeature, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "release_slug": self.release_slug,
            "total_features": self.total_features,
            "by_impact": self.by_impact,
            "by_type": self.by_type,
            "features": [f.to_dict() for f in self.features],
        }
