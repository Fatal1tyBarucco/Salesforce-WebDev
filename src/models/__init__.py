"""Domain models — core business entities and value objects.

These models represent the heart of the domain and have no dependencies
on external frameworks, databases, or UI concerns.
"""

from __future__ import annotations

from .api import (
    DiffResponse,
    ErrorResponse,
    FeatureClassificationRequest,
    FeatureClassificationResponse,
    ReleaseResponse,
)
from .api import (
    FeatureCategory as APIFeatureCategory,
)
from .classification import (
    ClassificationResult,
    ClassifiedFeature,
    FeatureType,
    ImpactLevel,
)
from .enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
)
from .feature import (
    Feature,
    FeatureCategory,
    FeatureImpact,
)
from .release import (
    ReleaseCategory,
    ReleaseInfo,
    ReleaseMetadata,
)

__all__ = [
    "APIFeatureCategory",
    # Enrichment
    "CategoryEnrichment",
    "ClassificationResult",
    "ClassifiedFeature",
    # API
    "DiffResponse",
    "ErrorResponse",
    # Feature
    "Feature",
    "FeatureCategory",
    "FeatureClassificationRequest",
    "FeatureClassificationResponse",
    "FeatureEnrichment",
    "FeatureImpact",
    "FeatureType",
    # Classification
    "ImpactLevel",
    "ReleaseCategory",
    # Release
    "ReleaseInfo",
    "ReleaseMetadata",
    "ReleaseResponse",
]
