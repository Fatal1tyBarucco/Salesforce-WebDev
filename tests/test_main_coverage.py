"""Targeted tests for uncovered lines in src/main.py."""

import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.exceptions import LLMError, NotificationError

from src.config import KNOWN_RELEASES, ReleaseInfo
from src.main import (
    RELEASE_SECTION_HEADING,
    generate_ai_reports_async,
    _generate_release_files,
    update_readme_all,
)
from src.parser import FeatureImpactCategory, FeatureImpactEntry


def _make_ai_service() -> MagicMock:
    mock_ai = MagicMock()
    mock_ai.generate_changelog = AsyncMock(return_value="# Changelog")
    mock_ai.generate_quality_report = AsyncMock(return_value="# Quality")
    mock_ai.generate_regression_report = AsyncMock(return_value="# Regression")
    mock_ai.generate_diff_report = AsyncMock(return_value="# Diff")
    mock_ai.create_github_issue = AsyncMock(return_value=None)
    return mock_ai


def _make_pipeline_scraper(*, raw_text: str | None = None) -> MagicMock:
    mock_scraper = MagicMock()
    mock_scraper.__aenter__ = AsyncMock(return_value=mock_scraper)
    mock_scraper.__aexit__ = AsyncMock(return_value=False)
    mock_scraper.fetch_page_raw_text = AsyncMock(return_value=raw_text)
    mock_scraper.download_pdf_from_button = AsyncMock(return_value=None)
    return mock_scraper


def _ai_modules(
    mock_ai: MagicMock,
    *,
    triage_side_effect: Any = None,
    impact_result: Any = None,
    notif_result: Any = None,
    digest_result: Any = None,
) -> dict[str, MagicMock]:
    mock_triager = MagicMock()
    mock_triager.triage_issue = AsyncMock(
        side_effect=triage_side_effect if triage_side_effect is None else triage_side_effect
    )

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


# ============================================================
# 1. generate_ai_reports_async (lines 161-265)
# ============================================================


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_empty_list() -> None:
    await generate_ai_reports_async([])


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_normal_execution(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": slug,
                "release_id": 262,
                "categories": [{"name": "Test", "count": 3}],
            }
        )
    )
    release = ReleaseInfo(name="Summer '26", release_id=262, slug=slug)
    mock_ai = _make_ai_service()

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.main._update_badge"),
        patch.dict("sys.modules", _ai_modules(mock_ai)),
    ):
        await generate_ai_reports_async([release])

    mock_ai.generate_changelog.assert_awaited_once()
    mock_ai.generate_quality_report.assert_awaited_once()
    mock_ai.generate_regression_report.assert_awaited_once()
    mock_ai.generate_diff_report.assert_awaited_once()


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_import_error() -> None:
    """Test ImportError handling (lines 264-265)."""
    release = ReleaseInfo(name="Test", release_id=262, slug="test")

    import types

    # A module missing AIAutomationService attribute — `from X import Y`
    # raises ImportError when Y is absent from the module.
    failing_mod = types.ModuleType("src.ai_automation")

    # Save current value so we can restore it
    saved = sys.modules.get("src.ai_automation")

    # Temporarily replace the module so `from .ai_automation import AIAutomationService`
    # will raise ImportError (AIAutomationService not in failing_mod)
    sys.modules["src.ai_automation"] = failing_mod
    try:
        await generate_ai_reports_async([release])
    finally:
        if saved is not None:
            sys.modules["src.ai_automation"] = saved
        else:
            sys.modules.pop("src.ai_automation", None)


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_no_previous_release(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release = ReleaseInfo(name="Spring '25", release_id=254, slug="spring_25")
    mock_ai = _make_ai_service()
    known_releases = sorted(KNOWN_RELEASES, key=lambda x: x.release_id, reverse=True)

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", known_releases),
        patch("src.main._update_badge"),
        patch.dict("sys.modules", _ai_modules(mock_ai)),
    ):
        await generate_ai_reports_async([release])

    mock_ai.generate_changelog.assert_awaited_once()
    mock_ai.generate_regression_report.assert_not_awaited()


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_triage_failure(tmp_path: Path) -> None:
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
        patch("src.main._update_badge"),
        patch.dict(
            "sys.modules",
            _ai_modules(mock_ai, triage_side_effect=LLMError("triage failed")),
        ),
    ):
        await generate_ai_reports_async([release])


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_impact_and_notification(tmp_path: Path) -> None:
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
        patch("src.main._update_badge"),
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
async def testgenerate_ai_reports_async_impact_failure(tmp_path: Path) -> None:
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

    mock_impact_fail = MagicMock()
    mock_impact_fail.analyze = AsyncMock(side_effect=LLMError("impact failed"))

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.main._update_badge"),
        patch.dict("sys.modules", _ai_modules(mock_ai, impact_result=None)),
    ):
        # Override the analyzer in the module to simulate failure
        pass

    # The impact analyzer mock needs the analyze to raise. Let me adjust _ai_modules.
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
        patch("src.main._update_badge"),
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
async def testgenerate_ai_reports_async_notification_failure(tmp_path: Path) -> None:
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
    mock_engine.generate_from_release = AsyncMock(side_effect=NotificationError("notif failed"))

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.main._update_badge"),
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

    mock_engine.generate_from_release.assert_awaited_once()


@pytest.mark.asyncio
async def testgenerate_ai_reports_async_issue_url_logged(tmp_path: Path) -> None:
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
    mock_ai.create_github_issue = AsyncMock(return_value="https://github.com/repo/issues/42")

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.KNOWN_RELEASES", KNOWN_RELEASES),
        patch("src.main._update_badge"),
        patch.dict("sys.modules", _ai_modules(mock_ai)),
    ):
        await generate_ai_reports_async([release])

    mock_ai.create_github_issue.assert_awaited_once()


# ============================================================
# 2. Feature classification in run_pipeline (lines 344-373)
# ============================================================


def _setup_classification_pipeline(
    tmp_path: Path,
    *,
    classification: Any,
    meta_content: dict[str, Any] | None = None,
) -> tuple[ReleaseInfo, MagicMock]:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir(exist_ok=True)
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    if meta_content is not None:
        (release_dir / ".meta.json").write_text(json.dumps(meta_content))

    release = ReleaseInfo(name="Summer '26", release_id=262, slug=slug)

    mock_classifier = MagicMock()
    mock_classifier.classify_release = AsyncMock(return_value=classification)
    mock_classifier_cls = MagicMock(return_value=mock_classifier)

    return release, mock_classifier_cls


@pytest.mark.asyncio
async def test_feature_classification_enriches_meta(tmp_path: Path) -> None:
    meta: dict[str, Any] = {
        "name": "Summer '26",
        "slug": "summer_26",
        "release_id": 262,
        "categories": [{"name": "Test", "count": 2}],
    }

    release, mock_cls = _setup_classification_pipeline(
        tmp_path,
        classification=MagicMock(
            features=[MagicMock(confidence=0.95), MagicMock(confidence=0.85)],
            total_features=2,
            by_impact={"high": 1, "low": 1},
            by_type={"new": 2},
        ),
        meta_content=meta,
    )
    releases_dir = tmp_path / "releases"

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.update_readme_all", new_callable=AsyncMock),
        patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
        patch("src.health.set_pipeline_status"),
        patch("src.main.logger"),
        patch.dict(
            "sys.modules", {"src.feature_classifier": MagicMock(FeatureClassifier=mock_cls)}
        ),
    ):
        from src.main import run_pipeline

        with (
            patch(
                "src.main.SalesforceReleaseScraper",
                return_value=_make_pipeline_scraper(raw_text="Sales\n- Feature1\n"),
            ),
            patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=release),
            patch("src.main.FEATURE_IMPACT_URL", "http://example.com/{release_id}"),
        ):
            await run_pipeline()

    updated_meta = json.loads((releases_dir / "summer_26" / ".meta.json").read_text())
    assert "classification_summary" in updated_meta
    s = updated_meta["classification_summary"]
    assert s["total_classified"] == 2
    assert s["avg_confidence"] == 0.9
    assert s["by_impact"] == {"high": 1, "low": 1}
    assert s["by_type"] == {"new": 2}


@pytest.mark.asyncio
async def test_feature_classification_no_meta_path(tmp_path: Path) -> None:
    release, mock_cls = _setup_classification_pipeline(
        tmp_path,
        classification=MagicMock(
            features=[MagicMock(confidence=0.9)],
            total_features=1,
            by_impact={},
            by_type={},
        ),
    )
    releases_dir = tmp_path / "releases"

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.update_readme_all", new_callable=AsyncMock),
        patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
        patch("src.health.set_pipeline_status"),
        patch("src.main.logger"),
        patch.dict(
            "sys.modules", {"src.feature_classifier": MagicMock(FeatureClassifier=mock_cls)}
        ),
    ):
        from src.main import run_pipeline

        with (
            patch(
                "src.main.SalesforceReleaseScraper",
                return_value=_make_pipeline_scraper(raw_text="Sales\n- Feature1\n"),
            ),
            patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=release),
            patch("src.main.FEATURE_IMPACT_URL", "http://example.com/{release_id}"),
        ):
            await run_pipeline()


@pytest.mark.asyncio
async def test_feature_classification_exception(tmp_path: Path) -> None:
    release, mock_cls = _setup_classification_pipeline(
        tmp_path,
        classification=None,
        meta_content={
            "name": "Summer '26",
            "slug": "summer_26",
            "release_id": 262,
            "categories": [],
        },
    )
    releases_dir = tmp_path / "releases"

    mock_classifier = mock_cls.return_value
    mock_classifier.classify_release = AsyncMock(side_effect=LLMError("classifier error"))

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.update_readme_all", new_callable=AsyncMock),
        patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
        patch("src.health.set_pipeline_status"),
        patch("src.main.logger"),
        patch.dict(
            "sys.modules", {"src.feature_classifier": MagicMock(FeatureClassifier=mock_cls)}
        ),
    ):
        from src.main import run_pipeline

        with (
            patch(
                "src.main.SalesforceReleaseScraper",
                return_value=_make_pipeline_scraper(raw_text="Sales\n- Feature1\n"),
            ),
            patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=release),
            patch("src.main.FEATURE_IMPACT_URL", "http://example.com/{release_id}"),
        ):
            await run_pipeline()


@pytest.mark.asyncio
async def test_feature_classification_empty_features(tmp_path: Path) -> None:
    release, mock_cls = _setup_classification_pipeline(
        tmp_path,
        classification=MagicMock(
            features=[],
            total_features=0,
            by_impact={},
            by_type={},
        ),
        meta_content={
            "name": "Summer '26",
            "slug": "summer_26",
            "release_id": 262,
            "categories": [],
        },
    )
    releases_dir = tmp_path / "releases"

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.update_readme_all", new_callable=AsyncMock),
        patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
        patch("src.health.set_pipeline_status"),
        patch("src.main.logger"),
        patch.dict(
            "sys.modules", {"src.feature_classifier": MagicMock(FeatureClassifier=mock_cls)}
        ),
    ):
        from src.main import run_pipeline

        with (
            patch(
                "src.main.SalesforceReleaseScraper",
                return_value=_make_pipeline_scraper(raw_text="Sales\n- Feature1\n"),
            ),
            patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=release),
            patch("src.main.FEATURE_IMPACT_URL", "http://example.com/{release_id}"),
        ):
            await run_pipeline()

    updated_meta = json.loads((releases_dir / "summer_26" / ".meta.json").read_text())
    assert updated_meta["classification_summary"]["avg_confidence"] == 0.0


# ============================================================
# 3. Subcategory entry translation (lines 506-511)
# ============================================================


@pytest.mark.asyncio
async def test_subcategory_entry_translation_en_us(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release = ReleaseInfo(name="Test", release_id=262, slug="test")

    cat = FeatureImpactCategory(name="Test Category", description="Description")
    cat.entries.append(FeatureImpactEntry(name="Feature Principal"))
    cat.subcategories["Sub Test"] = [FeatureImpactEntry(name="Feature Sub")]

    mock_translator = AsyncMock()
    mock_translator.translate_feature = AsyncMock(side_effect=lambda name, *_: f"EN:{name}")

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.generate_toggle_html", return_value="<div>toggle</div>"),
        patch("src.salesforce.generate_category_trailhead_section", return_value="Trailhead"),
    ):
        await _generate_release_files(release, [cat], MagicMock(), mock_translator, locale="en_US")

    assert mock_translator.translate_feature.await_count == 2
    # Translation operates on a deep copy, so original cat is unchanged
    # Verify translator was called with both entries
    calls = mock_translator.translate_feature.call_args_list
    translated_names = [c.args[0] for c in calls]
    assert "Feature Principal" in translated_names
    assert "Feature Sub" in translated_names


@pytest.mark.asyncio
async def test_no_translation_for_pt_br(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    release = ReleaseInfo(name="Test", release_id=262, slug="test")

    cat = FeatureImpactCategory(name="Test Category", description="Description")
    cat.entries.append(FeatureImpactEntry(name="Feature Principal"))
    cat.subcategories["Sub"] = [FeatureImpactEntry(name="Sub Feature")]

    mock_translator = AsyncMock()
    mock_translator.translate_feature = AsyncMock()

    with (
        patch("src.main.RELEASES_DIR", str(releases_dir)),
        patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
        patch("src.main.generate_toggle_html", return_value="<div>toggle</div>"),
        patch("src.salesforce.generate_category_trailhead_section", return_value="Trailhead"),
    ):
        await _generate_release_files(release, [cat], MagicMock(), mock_translator, locale="pt_BR")

    mock_translator.translate_feature.assert_not_awaited()


# ============================================================
# 4. English README generation (lines 754, 779, 790-792, 813-818, 841-857)
# ============================================================


@pytest.mark.asyncio
async def testupdate_readme_all_english_with_heading(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    meta = {
        "name": "Summer '26",
        "slug": slug,
        "release_id": 262,
        "categories": [{"name": "Admin", "count": 3}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    mock_summarizer = MagicMock()
    mock_summary = MagicMock()
    mock_summary.summary_text = "Executive summary text here"
    mock_summarizer.summarize = AsyncMock(return_value=mock_summary)

    original_dir = Path.cwd()
    try:
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\nOld content.\n\n## Next\n",
            encoding="utf-8",
        )
        (tmp_path / "README.en.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\nOld EN.\n\n## Next\n", encoding="utf-8"
        )
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    updated_en = (tmp_path / "README.en.md").read_text(encoding="utf-8")
    assert "Summer '26" in updated_en
    assert "Executive Summary" in updated_en
    assert "features" in updated_en
    assert "Full details" in updated_en


@pytest.mark.asyncio
async def testupdate_readme_all_english_no_heading_creates_file(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    meta = {
        "name": "Summer '26",
        "slug": slug,
        "release_id": 262,
        "categories": [{"name": "Admin", "count": 1}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    mock_summarizer = MagicMock()
    mock_summary = MagicMock()
    mock_summary.summary_text = "Summary"
    mock_summarizer.summarize = AsyncMock(return_value=mock_summary)

    original_dir = Path.cwd()
    try:
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\nContent.\n\n## Next\n", encoding="utf-8"
        )
        (tmp_path / "README.en.md").write_text(
            "# Title\n\nSome old content without heading.\n", encoding="utf-8"
        )
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    en_content = (tmp_path / "README.en.md").read_text(encoding="utf-8")
    assert "English" in en_content or "en_US" in en_content


@pytest.mark.asyncio
async def testupdate_readme_all_english_no_existing_file(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    meta = {
        "name": "Summer '26",
        "slug": slug,
        "release_id": 262,
        "categories": [{"name": "Admin", "count": 1}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    mock_summarizer = MagicMock()
    mock_summary = MagicMock()
    mock_summary.summary_text = "Summary"
    mock_summarizer.summarize = AsyncMock(return_value=mock_summary)

    original_dir = Path.cwd()
    try:
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\nContent.\n\n## Next\n", encoding="utf-8"
        )
        en_file = tmp_path / "README.en.md"
        if en_file.exists():
            en_file.unlink()
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    assert not (tmp_path / "README.en.md").exists()


@pytest.mark.asyncio
async def testupdate_readme_all_old_releases_collapsed(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    for slug, name, rid in [("summer_26", "Summer '26", 262), ("spring_26", "Spring '26", 260)]:
        rd = releases_dir / slug
        rd.mkdir()
        (rd / ".meta.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "slug": slug,
                    "release_id": rid,
                    "categories": [{"name": "Admin", "count": 2}],
                }
            )
        )

    mock_summarizer = MagicMock()
    mock_summary = MagicMock()
    mock_summary.summary_text = "Summary text"
    mock_summarizer.summarize = AsyncMock(return_value=mock_summary)

    original_dir = Path.cwd()
    try:
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\nContent.\n\n## Next\n", encoding="utf-8"
        )
        en_file = tmp_path / "README.en.md"
        if en_file.exists():
            en_file.unlink()
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    readme_content = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "### ☀️ Summer '26" in readme_content
    assert "<details>" in readme_content
    assert "<summary><h3>🌸 Spring '26</h3></summary>" in readme_content


@pytest.mark.asyncio
async def testupdate_readme_all_english_category_labels(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    meta = {
        "name": "Summer '26",
        "slug": slug,
        "release_id": 262,
        "categories": [{"name": "Sales", "count": 5}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    mock_summarizer = MagicMock()
    mock_summarizer.summarize = AsyncMock(return_value=None)

    original_dir = Path.cwd()
    try:
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\n## Next\n", encoding="utf-8"
        )
        (tmp_path / "README.en.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\n## Next\n", encoding="utf-8"
        )
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    en_content = (tmp_path / "README.en.md").read_text(encoding="utf-8")
    assert "features" in en_content
    assert "Full details" in en_content


@pytest.mark.asyncio
async def testupdate_readme_all_no_summary(tmp_path: Path) -> None:
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    meta = {
        "name": "Summer '26",
        "slug": slug,
        "release_id": 262,
        "categories": [{"name": "Admin", "count": 1}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    mock_summarizer = MagicMock()
    mock_summarizer.summarize = AsyncMock(return_value=None)

    original_dir = Path.cwd()
    try:
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n\nContent.\n\n## Next\n", encoding="utf-8"
        )
        en_file = tmp_path / "README.en.md"
        if en_file.exists():
            en_file.unlink()
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    readme_content = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Summer '26" in readme_content
    assert "Executive Summary" not in readme_content


# ============================================================
# 5. AI reports exception in run_pipeline (lines 377-381)
# ============================================================


@pytest.mark.asyncio
async def test_run_pipeline_ai_reports_exception(tmp_path: Path) -> None:
    """Test that generate_ai_reports_async exception sets completed_with_errors."""
    (tmp_path / "releases").mkdir()
    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    with (
        patch("src.main.RELEASES_DIR", str(tmp_path / "releases")),
        patch("src.release_docs.RELEASES_DIR", str(tmp_path / "releases")),
        patch("src.main.update_readme_all", new_callable=AsyncMock),
        patch(
            "src.main.generate_ai_reports_async",
            new_callable=AsyncMock,
            side_effect=LLMError("AI failed"),
        ),
        patch("src.health.set_pipeline_status") as mock_status,
        patch("src.main.logger"),
    ):
        from src.main import run_pipeline

        with (
            patch(
                "src.main.SalesforceReleaseScraper",
                return_value=_make_pipeline_scraper(raw_text="Sales\n- F1\n"),
            ),
            patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=release),
            patch("src.main.FEATURE_IMPACT_URL", "http://example.com/{release_id}"),
        ):
            await run_pipeline()

    mock_status.assert_any_call("completed_with_errors")


# ============================================================
# 6. en_US README with no next heading (line 846)
# ============================================================


@pytest.mark.asyncio
async def testupdate_readme_all_en_us_no_next_heading(tmp_path: Path) -> None:
    """Test en_US README where heading is at end of file (next_heading == -1)."""
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()
    slug = "summer_26"
    release_dir = releases_dir / slug
    release_dir.mkdir()
    meta = {
        "name": "Summer '26",
        "slug": slug,
        "release_id": 262,
        "categories": [{"name": "Admin", "count": 1}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    mock_summarizer = MagicMock()
    mock_summarizer.summarize = AsyncMock(return_value=None)

    original_dir = Path.cwd()
    try:
        # pt_BR README: heading is at end, no "\n## " after it
        (tmp_path / "README.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n", encoding="utf-8"
        )
        # en_US README: heading at end, no "\n## " after it → next_heading == -1
        (tmp_path / "README.en.md").write_text(
            "# Title\n\n" + RELEASE_SECTION_HEADING + "\n", encoding="utf-8"
        )
        os.chdir(tmp_path)
        with (
            patch("src.main.RELEASES_DIR", str(releases_dir)),
            patch("src.release_docs.RELEASES_DIR", str(releases_dir)),
            patch("src.release_summarizer.ReleaseSummarizer", return_value=mock_summarizer),
        ):
            await update_readme_all()
    finally:
        os.chdir(original_dir)

    updated_en = (tmp_path / "README.en.md").read_text(encoding="utf-8")
    assert "Summer '26" in updated_en
