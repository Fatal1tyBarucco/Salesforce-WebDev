"""AI-powered automation features for release notes pipeline.

This module re-exports from the ``automation`` package for backward
compatibility.  All new code should import from ``src.automation``
directly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .automation.badge import generate_dynamic_badge, get_latest_release_badge
from .automation.service import AIAutomationService
from .config import RELEASES_DIR
from .llm_service import LLMService

try:
    from .automation.models import AISummary
except (ImportError, AttributeError):

    @dataclass
    class AISummary:
        headline: str = ""
        highlights: list[str] = field(default_factory=list)
        risk_areas: list[str] = field(default_factory=list)
        overall_trend: str = "estável"
        current_name: str = ""
        previous_name: str = ""


try:
    from .automation.models import CategoryImpactScore
except (ImportError, AttributeError):

    @dataclass
    class CategoryImpactScore:
        category: str = ""
        score: float = 0.0
        risk_level: str = "baixo"
        trend: str = "stable"


try:
    from .automation.models import ContentHash
except (ImportError, AttributeError):

    @dataclass
    class ContentHash:
        file_path: str = ""
        content_hash: str = ""
        size_bytes: int = 0
        last_modified: float = 0.0


try:
    from .automation.models import DeduplicationResult
except (ImportError, AttributeError):

    @dataclass
    class DeduplicationResult:
        unchanged_files: list[str] = field(default_factory=list)
        changed_files: list[str] = field(default_factory=list)
        new_files: list[str] = field(default_factory=list)
        removed_files: list[str] = field(default_factory=list)
        total_savings_bytes: int = 0
        cache_hit_rate: float = 0.0


try:
    from .automation.models import FilteredNotification
except (ImportError, AttributeError):

    @dataclass
    class FilteredNotification:
        total_features: int = 0
        profile: Any = None
        categories: list[dict[str, Any]] = field(default_factory=list)
        features: list[dict[str, Any]] = field(default_factory=list)


try:
    from .automation.models import ImpactPrediction
except (ImportError, AttributeError):

    @dataclass
    class ImpactPrediction:
        overall_risk_level: str = "indeterminado"
        category_scores: list[Any] = field(default_factory=list)
        high_risk_categories: list[str] = field(default_factory=list)


try:
    from .automation.models import QualityMetrics
except (ImportError, AttributeError):

    @dataclass
    class QualityMetrics:
        total_features: int = 0
        total_categories: int = 0
        avg_features_per_category: float = 0.0
        largest_category: tuple[str, int] = ("", 0)
        smallest_category: tuple[str, int] = ("", 0)


try:
    from .automation.models import Regression
except (ImportError, AttributeError):

    @dataclass
    class Regression:
        category: str = ""
        change: int = 0
        previous_count: int = 0
        current_count: int = 0


try:
    from .automation.models import ReleaseComparison
except (ImportError, AttributeError):

    @dataclass
    class ReleaseComparison:
        current_name: str = ""
        previous_name: str = ""
        new_categories: list[str] = field(default_factory=list)
        removed_categories: list[str] = field(default_factory=list)
        changed_categories: list[tuple[str, int, int]] = field(default_factory=list)


try:
    from .automation.models import TriageResult
except (ImportError, AttributeError):

    @dataclass
    class TriageResult:
        risk_level: str = "desconhecido"
        risk_score: int = 0
        suggested_actions: list[str] = field(default_factory=list)
        issues: list[str] = field(default_factory=list)


try:
    from .automation.models import UserProfile
except (ImportError, AttributeError):

    @dataclass
    class UserProfile:
        profile_type: str = "admin"
        preferred_categories: list[str] = field(default_factory=list)


__all__ = [
    "RELEASES_DIR",
    "AIAutomationService",
    "AISummary",
    "CategoryImpactScore",
    "ContentHash",
    "DeduplicationResult",
    "FilteredNotification",
    "ImpactPrediction",
    "LLMService",
    "QualityMetrics",
    "Regression",
    "ReleaseComparison",
    "TriageResult",
    "UserProfile",
    "analyze_content_changes",
    "calculate_category_impact_scores",
    "calculate_quality_metrics",
    "compare_releases",
    "create_github_issue",
    "create_release_issue",
    "detect_regressions",
    "export_all_releases",
    "export_release_csv",
    "export_release_json",
    "filter_features_for_profile",
    "generate_ai_summary",
    "generate_ai_summary_report",
    "generate_changelog",
    "generate_deduplication_report",
    "generate_diff_report",
    "generate_dynamic_badge",
    "generate_filtered_notification",
    "generate_filtered_notification_report",
    "generate_impact_prediction_report",
    "generate_quality_report",
    "generate_regression_report",
    "generate_triage_report",
    "get_content_hash",
    "get_latest_release_badge",
    "is_content_unchanged",
    "load_release_meta",
    "predict_next_release_impact",
    "triage_release",
]

# ---------------------------------------------------------------------------
# Backward Compatibility Wrappers
# ---------------------------------------------------------------------------


def load_release_meta(slug: str) -> dict[str, Any] | None:
    return AIAutomationService().load_release_meta(slug)


async def compare_releases(current_slug: str, previous_slug: str) -> ReleaseComparison:
    return await AIAutomationService().compare_releases(current_slug, previous_slug)


async def detect_regressions(current_slug: str, previous_slug: str) -> list[Regression]:
    return await AIAutomationService().detect_regressions(current_slug, previous_slug)


async def calculate_quality_metrics(slug: str) -> QualityMetrics | None:
    return await AIAutomationService().calculate_quality_metrics(slug)


async def generate_changelog() -> str:
    return await AIAutomationService().generate_changelog()


async def generate_regression_report(current_slug: str, previous_slug: str) -> str:
    return await AIAutomationService().generate_regression_report(current_slug, previous_slug)


async def generate_diff_report(current_slug: str, previous_slug: str) -> str:
    return await AIAutomationService().generate_diff_report(current_slug, previous_slug)


async def generate_quality_report() -> str:
    return await AIAutomationService().generate_quality_report()


async def generate_ai_summary(current_slug: str, previous_slug: str) -> AISummary:
    return await AIAutomationService().generate_ai_summary(current_slug, previous_slug)


async def generate_ai_summary_report(current_slug: str, previous_slug: str) -> str:
    return await AIAutomationService().generate_ai_summary_report(current_slug, previous_slug)


async def calculate_category_impact_scores() -> list[CategoryImpactScore]:
    return await AIAutomationService().calculate_category_impact_scores()


async def predict_next_release_impact() -> ImpactPrediction:
    return await AIAutomationService().predict_next_release_impact()


async def generate_impact_prediction_report() -> str:
    return await AIAutomationService().generate_impact_prediction_report()


async def triage_release(slug: str) -> TriageResult:
    return await AIAutomationService().triage_release(slug)


async def generate_triage_report(slug: str) -> str:
    return await AIAutomationService().generate_triage_report(slug)


async def analyze_content_changes(release_slug: str) -> DeduplicationResult:
    return await AIAutomationService().analyze_content_changes(release_slug)


async def get_content_hash(file_path: str) -> str | None:
    return await AIAutomationService().get_content_hash(file_path)


async def is_content_unchanged(file_path: str, expected_hash: str) -> bool:
    return await AIAutomationService().is_content_unchanged(file_path, expected_hash)


async def create_github_issue(
    release_name: str, total_features: int, categories: int
) -> str | None:
    return await AIAutomationService().create_github_issue(release_name, total_features, categories)


async def create_release_issue(
    release_name: str, total_features: int, categories: int
) -> str | None:
    return await create_github_issue(release_name, total_features, categories)


async def _load_all_release_metas() -> list[dict[str, Any]]:
    return await AIAutomationService()._load_all_release_metas()


def _load_content_cache(cache_path: Path) -> dict[str, ContentHash]:
    return AIAutomationService()._load_content_cache(cache_path)


async def generate_deduplication_report(release_slug: str) -> str:
    return await AIAutomationService().generate_deduplication_report(release_slug)


async def filter_features_for_profile(
    profile_type: str, categories: list[dict[str, Any]]
) -> UserProfile:
    return await AIAutomationService().filter_features_for_profile(profile_type, categories)


async def generate_filtered_notification(slug: str, profile_type: str) -> FilteredNotification:
    return await AIAutomationService().generate_filtered_notification(slug, profile_type)


async def generate_filtered_notification_report(slug: str, profile_type: str) -> str:
    return await AIAutomationService().generate_filtered_notification_report(slug, profile_type)


async def export_release_json(slug: str) -> str:
    return await AIAutomationService().export_release_json(slug)


async def export_release_csv(slug: str) -> str:
    return await AIAutomationService().export_release_csv(slug)


async def export_all_releases(output_dir: str = "exports") -> dict[str, list[str]]:
    return await AIAutomationService().export_all_releases(output_dir)
