"""Stub module for backward compatibility with ai_automation.

This module provides minimal type definitions for the legacy ai_automation
compatibility layer. All functionality is mocked in tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ContentHash:
    """Content hash for deduplication."""

    path: str
    hash: str


@dataclass
class CategoryImpactScore:
    """Impact score per category."""

    category: str
    score: float
    feature_count: int


@dataclass
class DeduplicationResult:
    """Result of content deduplication analysis."""

    release_slug: str
    unchanged_files: list[str]
    changed_files: list[str]
    new_files: list[str]
    deleted_files: list[str]


@dataclass
class FilteredNotification:
    """Filtered notification for a user profile."""

    slug: str
    profile_type: str
    features: list[dict[str, Any]]
    summary: str


@dataclass
class ImpactPrediction:
    """Predicted impact for next release."""

    predicted_categories: dict[str, float]
    confidence: float
    rationale: str


@dataclass
class QualityMetrics:
    """Quality metrics for a release."""

    slug: str
    total_features: int
    categories: int
    avg_quality: float
    issues: list[str]


@dataclass
class Regression:
    """Regression detected between releases."""

    feature_id: str
    title: str
    severity: str
    description: str


@dataclass
class ReleaseComparison:
    """Comparison between two releases."""

    current: str
    previous: str
    added: list[str]
    removed: list[str]
    changed: list[str]
    stats: dict[str, int]


@dataclass
class TriageResult:
    """Triage result for a release."""

    slug: str
    priority: str
    categories: list[str]
    recommended_actions: list[str]


@dataclass
class UserProfile:
    """User profile for filtered notifications."""

    profile_type: str
    categories: list[str]
    keywords: list[str]


@dataclass
class AISummary:
    """AI-generated summary."""

    summary: str
    key_changes: list[str]
    impact_assessment: str


class AIAutomationService:
    """Stub service for backward compatibility.

    All methods are async no-ops. Tests mock this class entirely.
    """

    def load_release_meta(self, slug: str) -> dict[str, Any] | None:
        return None

    async def compare_releases(self, current_slug: str, previous_slug: str) -> ReleaseComparison:
        return ReleaseComparison(
            current=current_slug,
            previous=previous_slug,
            added=[],
            removed=[],
            changed=[],
            stats={},
        )

    async def detect_regressions(self, current_slug: str, previous_slug: str) -> list[Regression]:
        return []

    async def calculate_quality_metrics(self, slug: str) -> QualityMetrics | None:
        return None

    async def generate_changelog(self) -> str:
        return ""

    async def generate_regression_report(self, current_slug: str, previous_slug: str) -> str:
        return ""

    async def generate_diff_report(self, current_slug: str, previous_slug: str) -> str:
        return ""

    async def generate_quality_report(self) -> str:
        return ""

    async def generate_ai_summary(self, current_slug: str, previous_slug: str) -> AISummary:
        return AISummary(summary="", key_changes=[], impact_assessment="")

    async def generate_ai_summary_report(self, current_slug: str, previous_slug: str) -> str:
        return ""

    async def calculate_category_impact_scores(self) -> list[CategoryImpactScore]:
        return []

    async def predict_next_release_impact(self) -> ImpactPrediction:
        return ImpactPrediction(
            predicted_categories={},
            confidence=0.0,
            rationale="",
        )

    async def generate_impact_prediction_report(self) -> str:
        return ""

    async def triage_release(self, slug: str) -> TriageResult:
        return TriageResult(
            slug=slug,
            priority="low",
            categories=[],
            recommended_actions=[],
        )

    async def generate_triage_report(self, slug: str) -> str:
        return ""

    async def analyze_content_changes(self, release_slug: str) -> DeduplicationResult:
        return DeduplicationResult(
            release_slug=release_slug,
            unchanged_files=[],
            changed_files=[],
            new_files=[],
            deleted_files=[],
        )

    async def get_content_hash(self, file_path: str) -> str | None:
        return None

    async def is_content_unchanged(self, file_path: str, expected_hash: str) -> bool:
        return True

    async def create_github_issue(
        self, release_name: str, total_features: int, categories: int
    ) -> str | None:
        return None

    async def _load_all_release_metas(self) -> list[dict[str, Any]]:
        return []

    def _load_content_cache(self, cache_path: Any) -> dict[str, ContentHash]:
        return {}

    async def generate_deduplication_report(self, release_slug: str) -> str:
        return ""

    async def filter_features_for_profile(
        self, profile_type: str, categories: list[dict[str, Any]]
    ) -> UserProfile:
        return UserProfile(profile_type=profile_type, categories=[], keywords=[])

    async def generate_filtered_notification(
        self, slug: str, profile_type: str
    ) -> FilteredNotification:
        return FilteredNotification(slug=slug, profile_type=profile_type, features=[], summary="")

    async def generate_filtered_notification_report(self, slug: str, profile_type: str) -> str:
        return ""

    async def export_release_json(self, slug: str) -> str:
        return ""

    async def export_release_csv(self, slug: str) -> str:
        return ""

    async def export_all_releases(self, output_dir: str = "exports") -> dict[str, list[str]]:
        return {}


def generate_dynamic_badge(version: str, color: str = "blue") -> str:
    """Generate a dynamic badge."""
    return f"![{version}]({color})"


def get_latest_release_badge() -> str:
    """Get latest release badge."""
    return "![latest](blue)"
