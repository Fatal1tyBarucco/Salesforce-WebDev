"""Data models for AI automation features."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReleaseComparison:
    """Comparison between two releases."""

    current_name: str
    previous_name: str
    new_categories: list[str]
    removed_categories: list[str]
    changed_categories: list[tuple[str, int, int]]


@dataclass
class Regression:
    """Detected regression in a category."""

    category: str
    previous_count: int
    current_count: int
    change: int


@dataclass
class QualityMetrics:
    """Quality metrics for a release."""

    total_features: int
    total_categories: int
    avg_features_per_category: float
    largest_category: tuple[str, int]
    smallest_category: tuple[str, int]


@dataclass
class AISummary:
    """AI-generated summary of release comparison."""

    headline: str
    highlights: list[str]
    risk_areas: list[str]
    overall_trend: str


@dataclass
class CategoryImpactScore:
    """Impact score for a single category based on historical data."""

    category: str
    volatility: float
    trend: str
    risk_score: float
    prediction: str


@dataclass
class ImpactPrediction:
    """Predictive impact analysis for next release."""

    high_risk_categories: list[CategoryImpactScore]
    stable_categories: list[CategoryImpactScore]
    growing_categories: list[CategoryImpactScore]
    overall_risk_level: str
    summary: str


@dataclass
class TriageResult:
    """Automated triage result for a release alert."""

    risk_level: str
    risk_score: int
    categories_at_risk: list[str]
    suggested_actions: list[str]
    priority: str
    summary: str


@dataclass
class ContentHash:
    """Hash of a content file for deduplication."""

    file_path: str
    content_hash: str
    size_bytes: int
    last_modified: float


@dataclass
class DeduplicationResult:
    """Result of content deduplication analysis."""

    unchanged_files: list[str]
    changed_files: list[str]
    new_files: list[str]
    removed_files: list[str]
    total_savings_bytes: int
    cache_hit_rate: float


@dataclass
class UserProfile:
    """User profile for notification filtering."""

    profile_type: str
    name: str
    relevant_categories: list[str]
    filtered_features: list[str]
    priority_features: list[str]
    relevance_score: float


@dataclass
class FilteredNotification:
    """Filtered notification for a specific user profile."""

    profile: UserProfile
    total_features: int
    relevant_count: int
    priority_count: int
    summary: str
