"""Release domain models — release metadata and categories.

Pure domain entities with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ReleaseCategory:
    """A single feature category within a release — immutable value object."""

    name: str
    count: int = 0
    features: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "name": self.name,
            "count": self.count,
            "features": list(self.features),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReleaseCategory:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            count=data.get("count", 0),
            features=tuple(data.get("features", [])),
        )


@dataclass(frozen=True)
class ReleaseMetadata:
    """Release metadata — immutable value object."""

    release_id: int
    slug: str
    name: str
    version: str = ""
    date: str = ""
    total_features: int = 0
    avg_confidence: float = 0.0
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    categories: tuple[ReleaseCategory, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API/transport."""
        return {
            "release_id": self.release_id,
            "slug": self.slug,
            "name": self.name,
            "version": self.version,
            "date": self.date,
            "total_features": self.total_features,
            "avg_confidence": self.avg_confidence,
            "generated_at": self.generated_at,
            "categories": [c.to_dict() for c in self.categories],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReleaseMetadata:
        """Deserialize from dictionary."""
        return cls(
            release_id=data["release_id"],
            slug=data["slug"],
            name=data["name"],
            version=data.get("version", ""),
            date=data.get("date", ""),
            total_features=data.get("total_features", 0),
            avg_confidence=data.get("avg_confidence", 0.0),
            generated_at=data.get("generated_at", datetime.now().isoformat()),
            categories=tuple(ReleaseCategory.from_dict(c) for c in data.get("categories", [])),
        )


# Backward compatibility alias
ReleaseInfo = ReleaseMetadata


def build_release_info(release_id: int) -> ReleaseMetadata:
    """Build ReleaseMetadata from a release ID.

    This is a pure function that computes the release slug and name
    from the numeric ID — no I/O, no external dependencies.
    """
    season_map = {
        1: ("winter", "Winter"),
        2: ("spring", "Spring"),
        3: ("summer", "Summer"),
        4: ("autumn", "Autumn"),
    }
    year = 2000 + (release_id // 4)
    season_idx = (release_id % 4) or 4
    season_slug, season_name = season_map[season_idx]
    suffix = f"'{str(year)[2:]}"
    slug = f"{season_slug}_{suffix}"
    name = f"{season_name} {suffix}"
    return ReleaseMetadata(
        release_id=release_id,
        slug=slug,
        name=name,
    )
