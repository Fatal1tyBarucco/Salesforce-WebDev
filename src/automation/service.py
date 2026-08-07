"""AIAutomationService — facade that delegates to modular functions."""

from __future__ import annotations

from typing import Any, Optional

from ..llm_service import LLMService
from . import (
    badge,
    comparison,
    content,
    export,
    github_ops,
    impact,
    notifications,
    reporting,
)
from .models import (
    AISummary,
    CategoryImpactScore,
    ContentHash,
    DeduplicationResult,
    FilteredNotification,
    ImpactPrediction,
    QualityMetrics,
    Regression,
    ReleaseComparison,
    TriageResult,
    UserProfile,
)


class AIAutomationService:
    """AI-powered automation service for release notes pipeline.

    This class acts as a facade, delegating to focused modules:
    - comparison: release comparison and regression detection
    - quality: quality metrics and reports
    - reporting: changelog, diff, AI summary reports
    - impact: impact prediction, triage
    - content: deduplication, content hashing
    - notifications: profile-based filtering
    - export: JSON/CSV export
    - github_ops: GitHub Issue creation
    - badge: dynamic badge generation
    """

    USER_PROFILES = notifications.USER_PROFILES

    def __init__(self, llm: Optional[LLMService] = None) -> None:
        self._llm = llm or LLMService()

    @staticmethod
    def load_release_meta(slug: str) -> Optional[dict[str, Any]]:
        """Load .meta.json for a release."""
        import json
        from pathlib import Path

        from ..config import RELEASES_DIR

        meta_path = Path(RELEASES_DIR) / slug / ".meta.json"
        if not meta_path.exists():
            return None
        return json.loads(meta_path.read_text(encoding="utf-8"))  # type: ignore

    # ---- Comparison ----

    async def compare_releases(self, current_slug: str, previous_slug: str) -> ReleaseComparison:
        return await comparison.compare_releases(
            self.load_release_meta, current_slug, previous_slug
        )

    async def detect_regressions(self, current_slug: str, previous_slug: str) -> list[Regression]:
        return await comparison.detect_regressions(
            self.load_release_meta, current_slug, previous_slug
        )

    async def calculate_quality_metrics(self, slug: str) -> Optional[QualityMetrics]:
        return await comparison.calculate_quality_metrics(self.load_release_meta, slug)

    async def generate_quality_report(self) -> str:
        return await comparison.generate_quality_report(
            self._llm, self.load_release_meta, self.calculate_quality_metrics
        )

    # ---- Reporting ----

    async def generate_changelog(self) -> str:
        return await reporting.generate_changelog(self._llm, self.load_release_meta)

    async def generate_regression_report(self, current_slug: str, previous_slug: str) -> str:
        comp = await self.compare_releases(current_slug, previous_slug)
        regs = await self.detect_regressions(current_slug, previous_slug)
        return await reporting.generate_regression_report(self._llm, comp, regs)

    async def generate_diff_report(self, current_slug: str, previous_slug: str) -> str:
        comp = await self.compare_releases(current_slug, previous_slug)
        return await reporting.generate_diff_report(
            self._llm, self.load_release_meta, comp, current_slug, previous_slug
        )

    async def generate_ai_summary(self, current_slug: str, previous_slug: str) -> AISummary:
        comp = await self.compare_releases(current_slug, previous_slug)
        regs = await self.detect_regressions(current_slug, previous_slug)
        cur_metrics = await self.calculate_quality_metrics(current_slug)
        prev_metrics = await self.calculate_quality_metrics(previous_slug)
        return await reporting.generate_ai_summary(self._llm, comp, regs, cur_metrics, prev_metrics)

    async def generate_ai_summary_report(self, current_slug: str, previous_slug: str) -> str:
        comp = await self.compare_releases(current_slug, previous_slug)
        regs = await self.detect_regressions(current_slug, previous_slug)
        cur_metrics = await self.calculate_quality_metrics(current_slug)
        prev_metrics = await self.calculate_quality_metrics(previous_slug)
        return await reporting.generate_ai_summary_report(
            self._llm, comp, regs, cur_metrics, prev_metrics
        )

    # ---- Impact ----

    async def _load_all_release_metas(self) -> list[dict[str, Any]]:
        return await impact._load_all_release_metas(self.load_release_meta)

    async def calculate_category_impact_scores(self) -> list[CategoryImpactScore]:
        return await impact.calculate_category_impact_scores(self.load_release_meta)

    async def predict_next_release_impact(self) -> ImpactPrediction:
        return await impact.predict_next_release_impact(self.load_release_meta, llm=self._llm)

    async def generate_impact_prediction_report(self) -> str:
        return await impact.generate_impact_prediction_report(self.load_release_meta, llm=self._llm)

    async def triage_release(self, slug: str) -> TriageResult:
        return await impact.triage_release(self.load_release_meta, slug)

    async def generate_triage_report(self, slug: str) -> str:
        return await impact.generate_triage_report(self.load_release_meta, slug)

    # ---- Content / Deduplication ----

    async def analyze_content_changes(self, release_slug: str) -> DeduplicationResult:
        return await content.analyze_content_changes(release_slug)

    def _calculate_file_hash(self, file_path: Any) -> ContentHash:
        return content.calculate_file_hash(file_path)

    def _load_content_cache(self, cache_path: Any) -> dict[str, ContentHash]:
        return content.load_content_cache(cache_path)

    def _save_content_cache(self, cache_path: Any, cache: dict[str, ContentHash]) -> None:
        content.save_content_cache(cache_path, cache)

    async def get_content_hash(self, file_path: str) -> Optional[str]:
        return await content.get_content_hash(file_path)

    async def is_content_unchanged(self, file_path: str, expected_hash: str) -> bool:
        return await content.is_content_unchanged(file_path, expected_hash)

    async def generate_deduplication_report(self, release_slug: str) -> str:
        return await content.generate_deduplication_report(release_slug)

    # ---- Notifications ----

    async def filter_features_for_profile(
        self, profile_type: str, categories: list[dict[str, Any]]
    ) -> UserProfile:
        return await notifications.filter_features_for_profile(profile_type, categories)

    async def generate_filtered_notification(
        self, slug: str, profile_type: str
    ) -> FilteredNotification:
        return await notifications.generate_filtered_notification(
            self.load_release_meta, slug, profile_type
        )

    async def generate_filtered_notification_report(self, slug: str, profile_type: str) -> str:
        return await notifications.generate_filtered_notification_report(
            self.load_release_meta, slug, profile_type
        )

    # ---- Export ----

    async def export_release_json(self, slug: str) -> str:
        return await export.export_release_json(self.load_release_meta, slug)

    async def export_release_csv(self, slug: str) -> str:
        return await export.export_release_csv(self.load_release_meta, slug)

    async def export_all_releases(self, output_dir: str = "exports") -> dict[str, list[str]]:
        return await export.export_all_releases(self.load_release_meta, output_dir)

    # ---- GitHub ----

    async def create_github_issue(
        self, release_name: str, total_features: int, categories: int
    ) -> Optional[str]:
        return await github_ops.create_github_issue(release_name, total_features, categories)

    # ---- Badge ----

    @staticmethod
    def generate_dynamic_badge(release_name: str, total_features: int) -> str:
        return badge.generate_dynamic_badge(release_name, total_features)
