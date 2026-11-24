"""Stub impact module for backward compatibility."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ImpactPrediction:
    """Predicted impact for next release."""

    predicted_categories: dict[str, float]
    confidence: float
    rationale: str


@dataclass
class TriageResult:
    """Triage result for a release."""

    slug: str
    priority: str
    categories: list[str]
    recommended_actions: list[str]


async def predict_next_release_impact() -> ImpactPrediction:
    """Predict next release impact."""
    return ImpactPrediction(
        predicted_categories={},
        confidence=0.0,
        rationale="",
    )


async def generate_impact_prediction_report() -> str:
    """Generate impact prediction report."""
    return ""


async def triage_release(slug: str) -> TriageResult:
    """Triage a release."""
    return TriageResult(
        slug=slug,
        priority="low",
        categories=[],
        recommended_actions=[],
    )


async def calculate_category_impact_scores(load_meta_fn: Any = None) -> list[dict[str, Any]]:
    """Calculate category impact scores."""
    return []


async def _load_all_release_metas() -> list[dict[str, Any]]:
    """Load all release metas."""
    return []
