"""Pydantic models for API request/response validation.

Ensures all data entering and leaving the REST/GraphQL endpoints
is strictly typed and validated at the boundary layer.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field  # type: ignore[import-not-found]

# mypy: disable-error-code="misc"


class FeatureCategory(BaseModel):  # type: ignore[misc]
    """A single feature category within a release."""

    name: str = Field(..., min_length=1, description="Category name")
    count: int = Field(..., ge=0, description="Number of features in category")


class ReleaseResponse(BaseModel):  # type: ignore[misc]
    """Validated release metadata for API responses."""

    name: str = Field(..., description="Release display name (e.g., Summer '26)")
    slug: str = Field(..., min_length=1, description="Release slug (e.g., summer_26)")
    release_id: int = Field(..., description="Salesforce release ID")
    total_features: int = Field(0, ge=0)
    avg_confidence: float = Field(0.0, ge=0.0, le=1.0)
    generated_at: str = Field("")
    categories: list[FeatureCategory] = Field(default_factory=list)


class DiffResponse(BaseModel):  # type: ignore[misc]
    """Validated diff between two releases."""

    current: str = Field(..., description="Current release name")
    previous: str = Field(..., description="Previous release name")
    total_delta: int = Field(0, description="Feature count change")
    categories: list[dict[str, Any]] = Field(default_factory=list)
    changes: list[dict[str, Any]] = Field(default_factory=list)


class FeatureClassificationRequest(BaseModel):  # type: ignore[misc]
    """Validated request for feature classification."""

    text: str = Field(..., min_length=1, description="Feature text to classify")
    categories: list[str] = Field(..., min_length=1)


class FeatureClassificationResponse(BaseModel):  # type: ignore[misc]
    """Validated response from feature classification."""

    impact: str = Field(..., pattern=r"^(high|medium|low)$")
    type: str = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)


class ErrorResponse(BaseModel):  # type: ignore[misc]
    """Standard error response for API endpoints."""

    error: str = Field(..., description="Error message")
    detail: str = Field("", description="Additional error detail")
