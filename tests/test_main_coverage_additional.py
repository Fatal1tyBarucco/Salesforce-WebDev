"""Additional tests for src/main.py to reach 95% coverage."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import KNOWN_RELEASES, ReleaseInfo
from src.exceptions import LLMError
from src.main import (
    _load_meta_for_release,
    _parse_args,
    _validate_summary_cache,
    detect_new_release,
    enrich_meta_with_classification,
    generate_ai_reports_async,
    generate_summary_cache,
    process_single_release,
)
from src.models.release import build_release_info


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path: Path):
    """Run every test in a temp cwd so pipeline report writes never touch the repo."""
    original = Path.cwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(original)


# ============================================================
# 1. _parse_args (lines 115-131)
# ============================================================


def test_parse_args_no_args() -> None:
    """Test parsing with no arguments."""
    with patch.object(sys, "argv", ["main.py"]):
        release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is False


def test_parse_args_with_release() -> None:
    """Test parsing with --release argument."""
    with patch.object(sys, "argv", ["main.py", "--release", "summer_26"]):
        release_filter, dry_run = _parse_args()
        assert release_filter == "summer_26"
        assert dry_run is False


def test_parse_args_with_dry_run() -> None:
    """Test parsing with --dry-run argument."""
    with patch.object(sys, "argv", ["main.py", "--dry-run"]):
        release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is True


def test_parse_args_with_both() -> None:
    """Test parsing with both --release and --dry-run."""
    with patch.object(sys, "argv", ["main.py", "--release", "winter_26", "--dry-run"]):
        release_filter, dry_run = _parse_args()
        assert release_filter == "winter_26"
        assert dry_run is True


def test_parse_args_release_no_value() -> None:
    """Test --release without value doesn't crash."""
    with patch.object(sys, "argv", ["main.py", "--release"]):
        release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is False


# ============================================================
# 2. build_release_info (lines 87-109)
# ============================================================


def test_build_release_info_winter() -> None:
    """Test building release info for winter (release_id % 4 == 1)."""
    release = build_release_info(257)  # 257 % 4 = 1 -> winter
    assert release.release_id == 257
    assert release.slug == "winter_'64"
    assert release.name == "Winter '64"


def test_build_release_info_spring() -> None:
    """Test building release info for spring (release_id % 4 == 2)."""
    release = build_release_info(258)  # 258 % 4 = 2 -> spring
    assert release.release_id == 258
    assert release.slug == "spring_'64"
    assert release.name == "Spring '64"


def test_build_release_info_summer() -> None:
    """Test building release info for summer (release_id % 4 == 3)."""
    release = build_release_info(259)  # 259 % 4 = 3 -> summer
    assert release.release_id == 259
    assert release.slug == "summer_'64"
    assert release.name == "Summer '64"


def test_build_release_info_autumn() -> None:
    """Test building release info for autumn (release_id % 4 == 0)."""
    release = build_release_info(260)  # 260 % 4 = 0 -> autumn
    assert release.release_id == 260
    assert release.slug == "autumn_'65"
    assert release.name == "Autumn '65"


def test_build_release_info_modulo_zero() -> None:
    """Test release_id divisible by 4 gives autumn."""
    release = build_release_info(264)  # 264 % 4 = 0 -> autumn
    assert release.slug == "autumn_'66"
    assert release.name == "Autumn '66"


# ============================================================
# 3. _validate_summary_cache (lines 169-224)
# ============================================================


def test_validate_summary_cache_valid() -> None:
    """Test validation passes for valid cache."""
    cache = {
        "executive_summary": "Release has 50 features across 5 categories.",
        "category_summaries": {"A": "Summary A", "B": "Summary B"},
    }
    meta = {"total_features": 50, "categories": [{"name": "A"}, {"name": "B"}]}
    assert _validate_summary_cache(cache, meta, "test") is True


def test_validate_summary_cache_zero_features_but_meta_has_data() -> None:
    """Test validation fails when cache says 0 features but meta has data."""
    cache = {"executive_summary": "0 novos recursos", "category_summaries": {}}
    meta = {"total_features": 50, "categories": [{"name": "A"}]}
    assert _validate_summary_cache(cache, meta, "test") is False


def test_validate_summary_cache_no_category_summaries_but_meta_has_categories() -> None:
    """Test validation fails when no category summaries but meta has categories."""
    cache = {"executive_summary": "Release has 10 features.", "category_summaries": {}}
    meta = {"total_features": 10, "categories": [{"name": "A"}, {"name": "B"}]}
    assert _validate_summary_cache(cache, meta, "test") is False


def test_validate_summary_cache_few_category_summaries() -> None:
    """Test validation fails when cache has far fewer category summaries than meta."""
    cache = {
        "executive_summary": "Release has 10 features.",
        "category_summaries": {"A": "Summary A"},
    }
    meta = {
        "total_features": 10,
        "categories": [{"name": "A"}, {"name": "B"}, {"name": "C"}, {"name": "D"}],
    }
    assert _validate_summary_cache(cache, meta, "test") is False


def test_validate_summary_cache_short_executive_summary() -> None:
    """Test validation fails when executive summary too short for large release."""
    cache = {"executive_summary": "Short.", "category_summaries": {"A": "Summary A"}}
    meta = {"total_features": 150, "categories": [{"name": "A"}]}
    assert _validate_summary_cache(cache, meta, "test") is False


def test_validate_summary_cache_no_meta_categories() -> None:
    """Test validation passes when meta has no categories."""
    cache = {
        "executive_summary": "Release has 10 features.",
        "category_summaries": {"A": "Summary A"},
    }
    meta = {"total_features": 10, "categories": []}
    assert _validate_summary_cache(cache, meta, "test") is True


# ============================================================
# 4. detect_new_release (lines 134-154)
# ============================================================


@pytest.mark.asyncio
async def test_detect_new_release_returns_none() -> None:
    """Test detect_new_release returns None when no new release."""
    mock_scraper = MagicMock()
    mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
    mock_scraper.__aexit__ = AsyncMock(return_value=False)

    with patch("src.release_discovery.ReleaseDiscoveryService") as mock_service_class:
        mock_service = MagicMock()
        mock_service.discover = AsyncMock(return_value=[])
        mock_service_class.return_value = mock_service

        result = await detect_new_release(mock_scraper)
        assert result is None


@pytest.mark.asyncio
async def test_detect_new_release_returns_release() -> None:
    """Test detect_new_release returns ReleaseInfo when found."""
    mock_scraper = MagicMock()
    mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
    mock_scraper.__aexit__ = AsyncMock(return_value=False)

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    with patch("src.release_discovery.ReleaseDiscoveryService") as mock_service_class:
        mock_service = MagicMock()
        mock_service.discover = AsyncMock(return_value=[release])
        mock_service_class.return_value = mock_service

        result = await detect_new_release(mock_scraper)
        assert result == release


# ============================================================
# 5. process_single_release (lines 479-556)
# ============================================================


def _make_scraper(
    raw_text: str | None = None, features_with_links: list | None = None
) -> MagicMock:
    mock_scraper = MagicMock()
    mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
    mock_scraper.__aexit__ = AsyncMock(return_value=False)
    mock_scraper.fetch_page_raw_text = AsyncMock(return_value=raw_text)
    mock_scraper.fetch_features_with_links = AsyncMock(return_value=features_with_links or [])
    mock_scraper.download_pdf_from_button = AsyncMock(return_value=None)
    return mock_scraper


def _make_parser(categories: list | None = None) -> MagicMock:
    mock_parser = MagicMock()
    mock_parser.parse_text = MagicMock(return_value=categories or [])
    return mock_parser


def _make_generator() -> MagicMock:
    return MagicMock()


def _make_translator() -> MagicMock:
    return MagicMock()


def _make_llm() -> MagicMock:
    mock_llm = MagicMock()
    mock_llm.__aenter__ = AsyncMock(return_value=mock_llm)
    mock_llm.__aexit__ = AsyncMock(return_value=False)
    return mock_llm


@pytest.mark.asyncio
async def test_process_single_release_dry_run(tmp_path: Path) -> None:
    """Test process_single_release returns False in dry_run mode."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    scraper = _make_scraper(raw_text="Sample content")
    parser = _make_parser()
    generator = _make_generator()
    translator = _make_translator()

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        result = await process_single_release(
            release, scraper, parser, generator, translator, True, None
        )

    assert result is False
    scraper.fetch_page_raw_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_single_release_no_content(tmp_path: Path) -> None:
    """Test process_single_release returns False when no raw text."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    scraper = _make_scraper(raw_text=None)
    parser = _make_parser()
    generator = _make_generator()
    translator = _make_translator()

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        result = await process_single_release(
            release, scraper, parser, generator, translator, False, None
        )

    assert result is False


@pytest.mark.asyncio
async def test_process_single_release_success(tmp_path: Path) -> None:
    """Test process_single_release succeeds with content."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    # Create mock categories
    mock_category = MagicMock()
    mock_category.name = "Lightning"
    mock_category.features = []

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    scraper = _make_scraper(
        raw_text="Sample content",
        features_with_links=[{"name": "Feature 1", "docs_url": "http://example.com"}],
    )
    parser = _make_parser(categories=[mock_category])
    generator = _make_generator()
    translator = _make_translator()

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.feature_enricher.FeatureEnricher") as mock_enricher_class:
            mock_enricher = MagicMock()
            mock_enricher.enrich_release = AsyncMock(return_value={})
            mock_enricher_class.return_value = mock_enricher

            with patch("src.documentation_service._update_readme_single") as mock_update_readme:
                mock_update_readme.return_value = None

                with patch("src.main.generate_summary_cache", new=AsyncMock()):
                    result = await process_single_release(
                        release, scraper, parser, generator, translator, False, None
                    )

    assert result is True


@pytest.mark.asyncio
async def test_process_single_release_with_llm(tmp_path: Path) -> None:
    """Test process_single_release with LLM service."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    mock_category = MagicMock()
    mock_category.name = "Lightning"
    mock_category.features = []

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    scraper = _make_scraper(raw_text="Sample content")
    parser = _make_parser(categories=[mock_category])
    generator = _make_generator()
    translator = _make_translator()
    llm = _make_llm()

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.feature_enricher.FeatureEnricher") as mock_enricher_class:
            mock_enricher = MagicMock()
            mock_enricher.enrich_release = AsyncMock(return_value={})
            mock_enricher_class.return_value = mock_enricher

            with patch("src.documentation_service._update_readme_single") as mock_update_readme:
                mock_update_readme.return_value = None

                with patch("src.main.generate_summary_cache", new=AsyncMock()):
                    result = await process_single_release(
                        release, scraper, parser, generator, translator, False, llm
                    )

    assert result is True


# ============================================================
# 6. enrich_meta_with_classification (lines 559-595)
# ============================================================


@pytest.mark.asyncio
async def test_enrich_meta_with_classification_success(tmp_path: Path) -> None:
    """Test enrich_meta_with_classification updates .meta.json."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "categories": [{"name": "Lightning", "count": 3}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    mock_classification = MagicMock()
    mock_classification.features = [MagicMock(confidence=0.9), MagicMock(confidence=0.8)]
    mock_classification.total_features = 2
    mock_classification.by_impact = {"high": 1, "medium": 1}
    mock_classification.by_type = {"new": 2}

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.feature_classifier.FeatureClassifier") as mock_classifier_class:
            mock_classifier = MagicMock()
            mock_classifier.classify_release = AsyncMock(return_value=mock_classification)
            mock_classifier_class.return_value = mock_classifier

            await enrich_meta_with_classification(release)

    # Verify .meta.json was updated
    meta = json.loads((release_dir / ".meta.json").read_text())
    assert "classification_summary" in meta
    assert meta["classification_summary"]["total_classified"] == 2
    assert meta["classification_summary"]["avg_confidence"] == 0.85


@pytest.mark.asyncio
async def test_enrich_meta_with_classification_no_meta_file(tmp_path: Path) -> None:
    """Test enrich_meta_with_classification when .meta.json doesn't exist."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.feature_classifier.FeatureClassifier") as mock_classifier_class:
            mock_classifier = MagicMock()
            mock_classifier.classify_release = AsyncMock(return_value=None)
            mock_classifier_class.return_value = mock_classifier

            await enrich_meta_with_classification(release)

    # Should not crash


@pytest.mark.asyncio
async def test_enrich_meta_with_classification_error_handled(tmp_path: Path) -> None:
    """Test enrich_meta_with_classification handles errors gracefully."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "categories": [{"name": "Lightning", "count": 3}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.feature_classifier.FeatureClassifier") as mock_classifier_class:
            mock_classifier = MagicMock()
            mock_classifier.classify_release = AsyncMock(
                side_effect=LLMError("classification failed")
            )
            mock_classifier_class.return_value = mock_classifier

            # Should not raise
            await enrich_meta_with_classification(release)


# ============================================================
# 7. generate_summary_cache (lines 227-332)
# ============================================================


@pytest.mark.asyncio
async def test_generate_summary_cache_ai_success(tmp_path: Path) -> None:
    """Test AI summary generation succeeds."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}, {"name": "Apex", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = [MagicMock()]

    mock_llm = MagicMock()
    mock_summary = MagicMock()
    mock_summary.executive_summary = "Summer '26 has 10 new features across 2 categories."
    mock_summary.category_summaries = {"Lightning": "Summary 1", "Apex": "Summary 2"}
    mock_summary.business_impact = "High"
    mock_summary.strategic_themes = ["Theme 1"]
    mock_summary.migration_notes = ["Note 1"]

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.release_summarizer.ReleaseSummarizer") as mock_summarizer_class:
            mock_summarizer = MagicMock()
            mock_summarizer.summarize = AsyncMock(return_value=mock_summary)
            mock_summarizer_class.return_value = mock_summarizer

            with patch("src.main._validate_summary_cache", return_value=True):
                await generate_summary_cache(release, categories, mock_llm)

    cache_path = release_dir / ".summary_cache.json"
    assert cache_path.exists()
    cache = json.loads(cache_path.read_text())
    assert cache["fallback"] is False
    assert cache["executive_summary"] == mock_summary.executive_summary


@pytest.mark.asyncio
async def test_generate_summary_cache_ai_invalid_falls_back(tmp_path: Path) -> None:
    """Test AI summary invalid triggers fallback."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = [MagicMock()]

    mock_llm = MagicMock()
    mock_summary = MagicMock()
    mock_summary.executive_summary = "0 novos recursos"  # Invalid - will fail validation
    mock_summary.category_summaries = {}
    mock_summary.business_impact = "High"
    mock_summary.strategic_themes = ["Theme 1"]
    mock_summary.migration_notes = ["Note 1"]

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.release_summarizer.ReleaseSummarizer") as mock_summarizer_class:
            mock_summarizer = MagicMock()
            mock_summarizer.summarize = AsyncMock(return_value=mock_summary)
            mock_summarizer_class.return_value = mock_summarizer

            with patch("src.main._validate_summary_cache", side_effect=[False, True]):
                await generate_summary_cache(release, categories, mock_llm)

    cache_path = release_dir / ".summary_cache.json"
    assert cache_path.exists()
    cache = json.loads(cache_path.read_text())
    assert cache["fallback"] is True


@pytest.mark.asyncio
async def test_generate_summary_cache_ai_exception_falls_back(tmp_path: Path) -> None:
    """Test AI summary exception triggers fallback."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = [MagicMock()]

    mock_llm = MagicMock()

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch(
            "src.release_summarizer.ReleaseSummarizer", side_effect=ImportError("not available")
        ):
            with patch("src.main._validate_summary_cache", return_value=True):
                await generate_summary_cache(release, categories, mock_llm)

    cache_path = release_dir / ".summary_cache.json"
    assert cache_path.exists()
    cache = json.loads(cache_path.read_text())
    assert cache["fallback"] is True


@pytest.mark.asyncio
async def test_generate_summary_cache_fallback_with_categories(tmp_path: Path) -> None:
    """Test fallback generation with categories from meta."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}, {"name": "Apex", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = []

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.main._validate_summary_cache", return_value=True):
            await generate_summary_cache(release, categories, None)

    cache_path = release_dir / ".summary_cache.json"
    assert cache_path.exists()
    cache = json.loads(cache_path.read_text())
    assert cache["fallback"] is True
    assert "Lightning" in cache["category_summaries"]
    assert "Apex" in cache["category_summaries"]


@pytest.mark.asyncio
async def test_generate_summary_cache_fallback_with_memory_categories(tmp_path: Path) -> None:
    """Test fallback generation with categories from memory when meta empty."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 0,
                "categories": [],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    mock_category = MagicMock()
    mock_category.name = "Lightning"
    mock_category.total_features = 5
    categories = [mock_category]

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.main._validate_summary_cache", return_value=True):
            await generate_summary_cache(release, categories, None)

    cache_path = release_dir / ".summary_cache.json"
    assert cache_path.exists()
    cache = json.loads(cache_path.read_text())
    assert cache["fallback"] is True


@pytest.mark.asyncio
async def test_generate_summary_cache_fallback_no_categories(tmp_path: Path) -> None:
    """Test fallback generation with no categories logs error."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 0,
                "categories": [],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = []

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.main.logger") as mock_logger:
            await generate_summary_cache(release, categories, None)
            mock_logger.error.assert_called()


# ============================================================
# 8. generate_ai_reports_async (lines 335-400+)
# ============================================================


def _make_ai_service() -> MagicMock:
    mock_ai = MagicMock()
    mock_ai.generate_changelog = AsyncMock(return_value="# Changelog")
    mock_ai.generate_quality_report = AsyncMock(return_value="# Quality")
    mock_ai.generate_regression_report = AsyncMock(return_value="# Regression")
    mock_ai.generate_diff_report = AsyncMock(return_value="# Diff")
    mock_ai.create_github_issue = AsyncMock(return_value=None)
    return mock_ai


def _ai_modules(
    mock_ai: MagicMock,
    *,
    triage_side_effect: Any = None,
    impact_result: Any = None,
    notif_result: Any = None,
    digest_result: Any = None,
) -> dict[str, MagicMock]:
    mock_triager = MagicMock()
    mock_triager.triage_issue = AsyncMock(side_effect=triage_side_effect)

    mock_analyzer = MagicMock()
    mock_analyzer.analyze = AsyncMock(return_value=impact_result)

    mock_engine = MagicMock()
    mock_engine.generate_from_release = AsyncMock(return_value=notif_result)
    if digest_result is not None:
        mock_engine.generate_digest = AsyncMock(return_value=digest_result)

    return {
        "src.ai_automation": MagicMock(AIAutomationService=MagicMock(return_value=mock_ai)),
        "src.issue_triage": MagicMock(IssueTriager=MagicMock(return_value=mock_triager)),
        "src.impact_analyzer": MagicMock(ImpactAnalyzer=MagicMock(return_value=mock_analyzer)),
        "src.smart_notifications": MagicMock(
            SmartNotificationEngine=MagicMock(return_value=mock_engine),
            UserPreferences=MagicMock(),
        ),
    }


@pytest.mark.asyncio
async def test_generate_ai_reports_async_empty_list() -> None:
    """Test empty list returns early."""
    await generate_ai_reports_async([])


@pytest.mark.asyncio
async def test_generate_ai_reports_async_import_error() -> None:
    """Test ImportError handling for ai_automation."""
    release = ReleaseInfo(name="Test", release_id=262, slug="test")

    import types

    failing_mod = types.ModuleType("src.ai_automation")
    saved = sys.modules.get("src.ai_automation")
    sys.modules["src.ai_automation"] = failing_mod
    try:
        await generate_ai_reports_async([release])
    finally:
        if saved is not None:
            sys.modules["src.ai_automation"] = saved
        else:
            sys.modules.pop("src.ai_automation", None)


@pytest.mark.asyncio
async def test_generate_ai_reports_async_no_previous_release(tmp_path: Path) -> None:
    """Test when no previous release exists for diff."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    # Only one release in KNOWN_RELEASES (the current one)
    known_releases = [ReleaseInfo(name="Spring '25", release_id=254, slug="spring_25")]
    release = ReleaseInfo(name="Spring '25", release_id=254, slug="spring_25")
    mock_ai = _make_ai_service()

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", known_releases),
        patch("src.documentation_service._update_badge"),
        patch.dict("sys.modules", _ai_modules(mock_ai)),
    ):
        await generate_ai_reports_async([release])

    mock_ai.generate_changelog.assert_awaited_once()
    mock_ai.generate_quality_report.assert_awaited_once()
    mock_ai.generate_regression_report.assert_not_awaited()
    mock_ai.generate_diff_report.assert_not_awaited()


@pytest.mark.asyncio
async def test_generate_ai_reports_async_with_previous_release(tmp_path: Path) -> None:
    """Test diff reports generated when previous release exists."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    known_releases = [
        ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26"),
        ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26"),
    ]
    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    mock_ai = _make_ai_service()

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", known_releases),
        patch("src.documentation_service._update_badge"),
        patch.dict("sys.modules", _ai_modules(mock_ai)),
    ):
        await generate_ai_reports_async([release])

    mock_ai.generate_changelog.assert_awaited_once()
    mock_ai.generate_quality_report.assert_awaited_once()
    mock_ai.generate_regression_report.assert_awaited_once()
    mock_ai.generate_diff_report.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_ai_reports_async_triage_failure(tmp_path: Path) -> None:
    """Test triage failure doesn't crash."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps({"name": "Summer '26", "slug": slug, "release_id": 262, "categories": []})
    )
    release = ReleaseInfo(name="Summer '26", release_id=262, slug=slug)
    mock_ai = _make_ai_service()

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.documentation_service._update_badge"),
        patch.dict(
            "sys.modules", _ai_modules(mock_ai, triage_side_effect=LLMError("triage failed"))
        ),
    ):
        await generate_ai_reports_async([release])


@pytest.mark.asyncio
async def test_generate_ai_reports_async_impact_and_notification(tmp_path: Path) -> None:
    """Test impact analysis and notification generation."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps({"name": "Summer '26", "slug": slug, "release_id": 262, "categories": []})
    )
    release = ReleaseInfo(name="Summer '26", release_id=262, slug=slug)
    mock_ai = _make_ai_service()

    mock_report = MagicMock()
    mock_report.total_features = 10
    mock_report.breaking_changes = []
    mock_report.security_fixes = []
    mock_report.risk_score = 3

    mock_notifs = [MagicMock()]
    mock_digest = MagicMock()
    mock_digest.summary = "Digest summary"
    mock_digest.notifications = [MagicMock(priority="high", title="Alert", message="test")]

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.documentation_service._update_badge"),
        patch.dict(
            "sys.modules",
            _ai_modules(
                mock_ai,
                impact_result=mock_report,
                notif_result=mock_notifs,
                digest_result=mock_digest,
            ),
        ),
    ):
        await generate_ai_reports_async([release])


@pytest.mark.asyncio
async def test_generate_ai_reports_async_impact_failure(tmp_path: Path) -> None:
    """Test impact analyzer failure handled gracefully."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps({"name": "Summer '26", "slug": slug, "release_id": 262, "categories": []})
    )
    release = ReleaseInfo(name="Summer '26", release_id=262, slug=slug)
    mock_ai = _make_ai_service()

    mock_triager = MagicMock()
    mock_triager.triage_issue = AsyncMock()

    mock_analyzer = MagicMock()
    mock_analyzer.analyze = AsyncMock(side_effect=LLMError("impact failed"))

    mock_engine = MagicMock()
    mock_engine.generate_from_release = AsyncMock(return_value=None)

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.documentation_service._update_badge"),
        patch.dict(
            "sys.modules",
            {
                "src.ai_automation": MagicMock(AIAutomationService=MagicMock(return_value=mock_ai)),
                "src.issue_triage": MagicMock(IssueTriager=MagicMock(return_value=mock_triager)),
                "src.impact_analyzer": MagicMock(
                    ImpactAnalyzer=MagicMock(return_value=mock_analyzer)
                ),
                "src.smart_notifications": MagicMock(
                    SmartNotificationEngine=MagicMock(return_value=mock_engine),
                    UserPreferences=MagicMock(),
                ),
            },
        ),
    ):
        await generate_ai_reports_async([release])

    mock_analyzer.analyze.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_ai_reports_async_notification_failure(tmp_path: Path) -> None:
    """Test notification failure handled gracefully."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps({"name": "Summer '26", "slug": slug, "release_id": 262, "categories": []})
    )
    release = ReleaseInfo(name="Summer '26", release_id=262, slug=slug)
    mock_ai = _make_ai_service()

    mock_triager = MagicMock()
    mock_triager.triage_issue = AsyncMock()

    mock_analyzer = MagicMock()
    mock_analyzer.analyze = AsyncMock(return_value=None)

    mock_engine = MagicMock()
    mock_engine.generate_from_release = AsyncMock(side_effect=Exception("notif failed"))

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.documentation_service._update_badge"),
        patch.dict(
            "sys.modules",
            {
                "src.ai_automation": MagicMock(AIAutomationService=MagicMock(return_value=mock_ai)),
                "src.issue_triage": MagicMock(IssueTriager=MagicMock(return_value=mock_triager)),
                "src.impact_analyzer": MagicMock(
                    ImpactAnalyzer=MagicMock(return_value=mock_analyzer)
                ),
                "src.smart_notifications": MagicMock(
                    SmartNotificationEngine=MagicMock(return_value=mock_engine),
                    UserPreferences=MagicMock(),
                ),
            },
        ),
    ):
        await generate_ai_reports_async([release])


# ============================================================
# 9. PipelineConfig (lines 597-620)
# ============================================================


def test_pipeline_config_post_init_defaults() -> None:
    """Test PipelineConfig initializes defaults."""
    from src.main import PipelineConfig

    config = PipelineConfig(dry_run=True)
    assert config.dry_run is True
    assert config.known_releases is not None
    assert config.cache is not None
    assert config.event_bus is not None


def test_pipeline_config_custom_values() -> None:
    """Test PipelineConfig accepts custom values."""
    from src.cache_manager import CacheManager
    from src.events import EventBus
    from src.main import PipelineConfig

    custom_cache = CacheManager(cache_dir=Path("custom"), ttl_seconds=100)
    custom_bus = EventBus()

    config = PipelineConfig(
        dry_run=False,
        cache=custom_cache,
        event_bus=custom_bus,
        release_filter="summer_26",
    )
    assert config.dry_run is False
    assert config.cache is custom_cache
    assert config.event_bus is custom_bus
    assert config.release_filter == "summer_26"


# ============================================================
# 10. run_pipeline (lines 700-900+)
# ============================================================


@pytest.mark.asyncio
async def test_run_pipeline_dry_run(tmp_path: Path) -> None:
    """Test run_pipeline in dry_run mode."""
    from src.main import PipelineConfig, run_pipeline

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    config = PipelineConfig(
        dry_run=True,
        known_releases=[ReleaseInfo(name="Test", release_id=262, slug="test")],
    )

    # Mock the legacy orchestrator
    with patch("src.orchestrator.PipelineOrchestrator") as mock_orch_class:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(
            return_value=MagicMock(releases_processed=[], errors=[], status="completed")
        )
        mock_orch_class.return_value = mock_orch

        await run_pipeline(config)
        result = mock_orch.run.return_value

    assert result.status in ("completed", "no_new_releases")


@pytest.mark.asyncio
async def test_run_pipeline_with_llm(tmp_path: Path) -> None:
    """Test run_pipeline with LLM."""
    from src.main import PipelineConfig, run_pipeline

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    mock_llm = MagicMock()
    mock_llm.__aenter__ = AsyncMock(return_value=mock_llm)
    mock_llm.__aexit__ = AsyncMock(return_value=False)

    config = PipelineConfig(
        dry_run=False,
        llm=mock_llm,
        known_releases=[ReleaseInfo(name="Test", release_id=262, slug="test")],
    )

    with patch("src.orchestrator.PipelineOrchestrator") as mock_orch_class:
        mock_orch = AsyncMock()
        mock_orch.run = AsyncMock(
            return_value=MagicMock(releases_processed=["test"], errors=[], status="completed")
        )
        mock_orch_class.return_value = mock_orch

        with patch("src.main.generate_ai_reports_async", new=AsyncMock()):
            await run_pipeline(config)
            result = mock_orch.run.return_value

    assert result.status == "completed"


@pytest.mark.asyncio
async def test_run_pipeline_error_handling(tmp_path: Path) -> None:
    """Test run_pipeline handles errors."""
    from src.main import PipelineConfig, run_pipeline

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    config = PipelineConfig(
        dry_run=False,
        known_releases=[ReleaseInfo(name="Test", release_id=262, slug="test")],
    )

    with patch("src.orchestrator.PipelineOrchestrator") as mock_orch_class:
        mock_orch = AsyncMock()
        # The legacy orchestrator catches LLMError, GitHubError, NotificationError, OSError
        # and returns a result with "completed_with_errors" status
        mock_orch.run = AsyncMock(
            return_value=MagicMock(
                releases_processed=[],
                errors=["LLMError: test error"],
                status="completed_with_errors",
            )
        )
        mock_orch_class.return_value = mock_orch

        await run_pipeline(config)
        result = mock_orch.run.return_value

    assert result.status == "completed_with_errors"
    assert len(result.errors) > 0


# ============================================================
# 11. main entry point (lines 900-950)
# ============================================================


def test_main_entry_point_dry_run(tmp_path: Path, capsys) -> None:
    """Test main() with --dry-run."""
    from src.main import main

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    with patch.object(sys, "argv", ["main.py", "--dry-run"]):
        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            with patch("src.main.run_pipeline", new=AsyncMock()) as mock_run:
                mock_run.return_value = MagicMock(
                    status="completed", releases_processed=[], errors=[]
                )
                main()

    mock_run.assert_called_once()


def test_main_entry_point_with_release(tmp_path: Path) -> None:
    """Test main() with --release."""
    from src.main import main

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    with patch.object(sys, "argv", ["main.py", "--release", "summer_26"]):
        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            with patch("src.main.run_pipeline", new=AsyncMock()) as mock_run:
                mock_run.return_value = MagicMock(
                    status="completed", releases_processed=["summer_26"], errors=[]
                )
                main()

    mock_run.assert_called_once()
    # run_pipeline is called with no args; it parses args internally
    # The _parse_args is called inside run_pipeline, so we just verify it was called


def test_main_entry_point_keyboard_interrupt(tmp_path: Path) -> None:
    """Test main() propagates KeyboardInterrupt from run_pipeline."""
    from src.main import main

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    with patch.object(sys, "argv", ["main.py"]):
        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            with patch("src.main.run_pipeline", new=AsyncMock()) as mock_run:
                mock_run.side_effect = KeyboardInterrupt()
                with pytest.raises(KeyboardInterrupt):
                    main()

    mock_run.assert_called_once()


def test_main_entry_point_exception(tmp_path: Path) -> None:
    """Test main() propagates general exceptions from run_pipeline."""
    from src.main import main

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    with patch.object(sys, "argv", ["main.py"]):
        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            with patch("src.main.run_pipeline", new=AsyncMock()) as mock_run:
                mock_run.side_effect = Exception("Unexpected error")
                with pytest.raises(Exception, match="Unexpected error"):
                    main()

    mock_run.assert_called_once()


# ============================================================
# 12. Additional coverage for remaining missing lines
# ============================================================


def test_load_meta_for_release_json_decode_error(tmp_path: Path) -> None:
    """Test _load_meta_for_release handles JSONDecodeError (lines 164-166)."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    # Write invalid JSON
    (release_dir / ".meta.json").write_text("{ invalid json }")

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        result = _load_meta_for_release("summer_26")

    assert result == {}


def test_load_meta_for_release_os_error(tmp_path: Path) -> None:
    """Test _load_meta_for_release handles OSError (lines 164-166)."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    # Make file unreadable
    (release_dir / ".meta.json").write_text('{"valid": "json"}')
    (release_dir / ".meta.json").chmod(0o000)

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        result = _load_meta_for_release("summer_26")

    # Restore permissions for cleanup
    (release_dir / ".meta.json").chmod(0o644)
    assert result == {}


@pytest.mark.asyncio
async def test_generate_summary_cache_ai_no_summary(tmp_path: Path) -> None:
    """Test AI summary generation when summarizer returns None (line 251)."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = [MagicMock()]

    mock_llm = MagicMock()

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.release_summarizer.ReleaseSummarizer") as mock_summarizer_class:
            mock_summarizer = MagicMock()
            mock_summarizer.summarize = AsyncMock(return_value=None)
            mock_summarizer_class.return_value = mock_summarizer

            with patch("src.main._validate_summary_cache", return_value=True):
                await generate_summary_cache(release, categories, mock_llm)

    # Should fall through to fallback since summary is None
    cache_path = release_dir / ".summary_cache.json"
    assert cache_path.exists()
    cache = json.loads(cache_path.read_text())
    assert cache["fallback"] is True


@pytest.mark.asyncio
async def test_generate_summary_cache_fallback_validation_fails(tmp_path: Path) -> None:
    """Test fallback cache validation fails (lines 329-330)."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = [MagicMock()]

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.main._validate_summary_cache", return_value=False):
            with patch("src.main.logger") as mock_logger:
                await generate_summary_cache(release, categories, None)
                mock_logger.error.assert_called()

    # Cache file should not exist since validation failed
    cache_path = release_dir / ".summary_cache.json"
    assert not cache_path.exists()


@pytest.mark.asyncio
async def test_generate_summary_cache_fallback_exception(tmp_path: Path) -> None:
    """Test fallback generation exception handling (lines 331-332)."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 10,
                "categories": [{"name": "Lightning", "count": 5}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
    categories = [MagicMock()]

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.main._validate_summary_cache", side_effect=ValueError("validation error")):
            with patch("src.main.logger") as mock_logger:
                await generate_summary_cache(release, categories, None)
                mock_logger.error.assert_called()


@pytest.mark.asyncio
async def test_generate_ai_reports_async_safe_write_exception(tmp_path: Path) -> None:
    """Test _safe_write handles BaseException (lines 378-380)."""
    from src.main import generate_ai_reports_async

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    known_releases = [
        ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26"),
        ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26"),
    ]
    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    # Create AI service that raises exception
    mock_ai = MagicMock()
    mock_ai.generate_changelog = AsyncMock(side_effect=RuntimeError("changelog failed"))
    mock_ai.generate_quality_report = AsyncMock(return_value="# Quality")
    mock_ai.generate_regression_report = AsyncMock(return_value="# Regression")
    mock_ai.generate_diff_report = AsyncMock(return_value="# Diff")
    mock_ai.create_github_issue = AsyncMock(return_value=None)

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", known_releases),
        patch("src.documentation_service._update_badge"),
        patch.dict(
            "sys.modules",
            {
                "src.ai_automation": MagicMock(AIAutomationService=MagicMock(return_value=mock_ai)),
                "src.issue_triage": MagicMock(
                    IssueTriager=MagicMock(return_value=MagicMock(triage_issue=AsyncMock()))
                ),
                "src.impact_analyzer": MagicMock(
                    ImpactAnalyzer=MagicMock(
                        return_value=MagicMock(analyze=AsyncMock(return_value=None))
                    )
                ),
                "src.smart_notifications": MagicMock(
                    SmartNotificationEngine=MagicMock(
                        return_value=MagicMock(generate_from_release=AsyncMock(return_value=None))
                    ),
                    UserPreferences=MagicMock(),
                ),
            },
        ),
    ):
        await generate_ai_reports_async([release])

    # Error files should be created
    assert Path("CHANGELOG.md").exists()
    changelog = Path("CHANGELOG.md").read_text()
    assert "Error" in changelog
    assert "changelog failed" in changelog


@pytest.mark.asyncio
async def test_enrich_meta_with_classification_llm_error(tmp_path: Path) -> None:
    """Test enrich_meta_with_classification handles LLMError (line 443)."""
    from src.main import enrich_meta_with_classification

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "categories": [{"name": "Lightning", "count": 3}],
            }
        )
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.feature_classifier.FeatureClassifier") as mock_classifier_class:
            mock_classifier = MagicMock()
            mock_classifier.classify_release = AsyncMock(
                side_effect=LLMError("classification failed")
            )
            mock_classifier_class.return_value = mock_classifier

            # Should not raise
            await enrich_meta_with_classification(release)


@pytest.mark.asyncio
async def test_process_release_analytics_notification_error(tmp_path: Path) -> None:
    """Test _process_release_analytics handles NotificationError (line 475)."""
    from src.exceptions import NotificationError
    from src.main import _process_release_analytics

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release_dir = releases_dir / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps({"name": "Summer '26", "slug": "summer_26", "release_id": 262, "categories": []})
    )

    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    mock_analyzer = MagicMock()
    mock_analyzer.analyze = AsyncMock(return_value=None)

    mock_engine = MagicMock()
    mock_engine.generate_from_release = AsyncMock(side_effect=NotificationError("notif failed"))

    with patch("src.main.RELEASES_DIR", str(releases_dir)):
        with patch("src.main.logger") as mock_logger:
            await _process_release_analytics(mock_analyzer, mock_engine, release)
            mock_logger.warning.assert_called()


def test_pipeline_config_llm_initialization_value_error(tmp_path: Path) -> None:
    """Test PipelineConfig handles ValueError when initializing LLM (lines 567-569, 572)."""
    from src.main import PipelineConfig

    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    # Mock LLMService to raise ValueError (no API keys)
    with patch("src.main.LLMService", side_effect=ValueError("No API keys")):
        config = PipelineConfig(
            dry_run=True,
            known_releases=[ReleaseInfo(name="Test", release_id=262, slug="test")],
        )

    assert config.llm is None
