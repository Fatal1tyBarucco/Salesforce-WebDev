"""Enrichment domain models — AI-generated feature and category enrichments.

Pure domain entities with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class FeatureEnrichment:
    """AI-generated enrichment for a single feature — immutable value object."""

    feature_name: str
    summary: str = ""
    details: str = ""
    business_context: str = ""
    technical_context: str = ""
    migration_notes: str = ""
    related_features: tuple[str, ...] = field(default_factory=tuple)
    tags: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 0.0
    locale: str = "pt_BR"
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "feature_name": self.feature_name,
            "summary": self.summary,
            "details": self.details,
            "business_context": self.business_context,
            "technical_context": self.technical_context,
            "migration_notes": self.migration_notes,
            "related_features": list(self.related_features),
            "tags": list(self.tags),
            "confidence": self.confidence,
            "locale": self.locale,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FeatureEnrichment:
        """Deserialize from dictionary."""
        return cls(
            feature_name=data["feature_name"],
            summary=data.get("summary", ""),
            details=data.get("details", ""),
            business_context=data.get("business_context", ""),
            technical_context=data.get("technical_context", ""),
            migration_notes=data.get("migration_notes", ""),
            related_features=tuple(data.get("related_features", [])),
            tags=tuple(data.get("tags", [])),
            confidence=data.get("confidence", 0.0),
            locale=data.get("locale", "pt_BR"),
            generated_at=data.get("generated_at", ""),
        )


@dataclass(frozen=True)
class CategoryEnrichment:
    """AI-generated enrichment for an entire category — immutable aggregate."""

    category_name: str
    overview: str = ""
    key_themes: tuple[str, ...] = field(default_factory=tuple)
    business_impact: str = ""
    adoption_guidance: str = ""
    risk_assessment: str = ""
    feature_enrichments: tuple[FeatureEnrichment, ...] = field(default_factory=tuple)
    locale: str = "pt_BR"
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "category_name": self.category_name,
            "overview": self.overview,
            "key_themes": list(self.key_themes),
            "business_impact": self.business_impact,
            "adoption_guidance": self.adoption_guidance,
            "risk_assessment": self.risk_assessment,
            "feature_enrichments": [f.to_dict() for f in self.feature_enrichments],
            "locale": self.locale,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CategoryEnrichment:
        """Deserialize from dictionary."""
        enrichments = tuple(
            FeatureEnrichment.from_dict(f) for f in data.get("feature_enrichments", [])
        )
        return cls(
            category_name=data["category_name"],
            overview=data.get("overview", ""),
            key_themes=tuple(data.get("key_themes", [])),
            business_impact=data.get("business_impact", ""),
            adoption_guidance=data.get("adoption_guidance", ""),
            risk_assessment=data.get("risk_assessment", ""),
            feature_enrichments=enrichments,
            locale=data.get("locale", "pt_BR"),
            generated_at=data.get("generated_at", ""),
        )


@dataclass(frozen=True)
class ReleaseEnrichment:
    """AI-generated enrichment for an entire release — immutable aggregate."""

    release_slug: str
    executive_summary: str = ""
    strategic_themes: tuple[str, ...] = field(default_factory=tuple)
    category_enrichments: tuple[CategoryEnrichment, ...] = field(default_factory=tuple)
    migration_checklist: tuple[str, ...] = field(default_factory=tuple)
    locale: str = "pt_BR"
    generated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "release_slug": self.release_slug,
            "executive_summary": self.executive_summary,
            "strategic_themes": list(self.strategic_themes),
            "category_enrichments": [c.to_dict() for c in self.category_enrichments],
            "migration_checklist": list(self.migration_checklist),
            "locale": self.locale,
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReleaseEnrichment:
        """Deserialize from dictionary."""
        enrichments = tuple(
            CategoryEnrichment.from_dict(c) for c in data.get("category_enrichments", [])
        )
        return cls(
            release_slug=data["release_slug"],
            executive_summary=data.get("executive_summary", ""),
            strategic_themes=tuple(data.get("strategic_themes", [])),
            category_enrichments=enrichments,
            migration_checklist=tuple(data.get("migration_checklist", [])),
            locale=data.get("locale", "pt_BR"),
            generated_at=data.get("generated_at", ""),
        )
