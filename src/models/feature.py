"""Feature domain models — features, categories, and impact.

Pure domain entities with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FeatureImpact(Enum):
    """Feature impact severity."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeatureStatus(Enum):
    """Feature processing status."""

    RAW = "raw"
    CLASSIFIED = "classified"
    ENRICHED = "enriched"
    TRANSLATED = "translated"
    PUBLISHED = "published"


@dataclass(frozen=True)
class Feature:
    """A single feature — immutable value object.

    Represents a raw feature extracted from Salesforce Release Notes
    before any AI processing.
    """

    name: str
    description: str = ""
    category: str = ""
    raw_text: str = ""
    status: FeatureStatus = FeatureStatus.RAW
    locale: str = "pt_BR"
    source_url: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "raw_text": self.raw_text,
            "status": self.status.value,
            "locale": self.locale,
            "source_url": self.source_url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Feature:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            raw_text=data.get("raw_text", ""),
            status=FeatureStatus(data.get("status", "raw")),
            locale=data.get("locale", "pt_BR"),
            source_url=data.get("source_url", ""),
        )


@dataclass(frozen=True)
class FeatureCategory:
    """A category of features within a release — immutable aggregate."""

    name: str
    features: tuple[Feature, ...] = field(default_factory=tuple)
    locale: str = "pt_BR"
    total_count: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "total_count", len(self.features))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "name": self.name,
            "features": [f.to_dict() for f in self.features],
            "locale": self.locale,
            "total_count": self.total_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureCategory:
        """Deserialize from dictionary."""
        features = tuple(Feature.from_dict(f) for f in data.get("features", []))
        return cls(
            name=data["name"],
            features=features,
            locale=data.get("locale", "pt_BR"),
        )


@dataclass(frozen=True)
class FeatureImpactCategory:
    """Feature impact category for impact propagation analysis."""

    name: str
    impact: FeatureImpact
    features: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "name": self.name,
            "impact": self.impact.value,
            "features": list(self.features),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureImpactCategory:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            impact=FeatureImpact(data["impact"]),
            features=tuple(data.get("features", [])),
            confidence=data.get("confidence", 0.0),
        )
