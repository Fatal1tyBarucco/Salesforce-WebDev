"""Tests for AI automation module."""

import json
import pytest
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from src.ai_automation import (
    AIAutomationService,
    LLMService,
    load_release_meta,
    compare_releases,
    detect_regressions,
    calculate_quality_metrics,
    generate_changelog,
    generate_regression_report,
    generate_diff_report,
    generate_quality_report,
    generate_ai_summary,
    generate_ai_summary_report,
    AISummary,
    calculate_category_impact_scores,
    predict_next_release_impact,
    generate_impact_prediction_report,
    ImpactPrediction,
    triage_release,
    generate_triage_report,
    TriageResult,
    analyze_content_changes,
    get_content_hash,
    is_content_unchanged,
    generate_deduplication_report,
    DeduplicationResult,
    filter_features_for_profile,
    generate_filtered_notification,
    generate_filtered_notification_report,
    UserProfile,
    FilteredNotification,
    generate_dynamic_badge,
    get_latest_release_badge,
    export_release_json,
    export_release_csv,
    export_all_releases,
)


@pytest.fixture
def llm_service():
    """Fixture for mocking LLMService."""
    mock = MagicMock(spec=LLMService)
    mock.generate_text = AsyncMock(return_value="AI generated content")
    return mock


@pytest.fixture
def service(llm_service):
    """Fixture for AIAutomationService with mocked LLM."""
    return AIAutomationService(llm=llm_service)


@pytest.fixture(autouse=True)
def mock_llm_class(llm_service):
    """Global patch for LLMService instantiation in module-level wrappers."""
    with patch("src.automation.service.LLMService", return_value=llm_service):
        yield llm_service


@pytest.mark.asyncio
async def test_load_release_meta_existing(tmp_path: Path) -> None:
    meta = {"name": "Test", "slug": "test", "release_id": 100, "categories": []}
    release_dir = tmp_path / "test"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        result = await load_release_meta("test")
        assert result is not None
        assert result["name"] == "Test"


@pytest.mark.asyncio
async def test_load_release_meta_missing() -> None:
    with patch("src.config.RELEASES_DIR", "/nonexistent"):
        result = await load_release_meta("missing")
        assert result is None


@pytest.mark.asyncio
async def test_compare_releases(service) -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 10}, {"name": "B", "count": 5}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}, {"name": "C", "count": 3}]}

    def mock_load(slug: str) -> Any:
        return prev if slug == "prev" else curr

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        result = await compare_releases("curr", "prev")
        assert result.current_name == "Curr"
        assert result.previous_name == "Prev"
        assert "C" in result.new_categories
        assert "B" in result.removed_categories
        assert ("A", 10, 15) in result.changed_categories


@pytest.mark.asyncio
async def test_detect_regressions(service) -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 20}, {"name": "B", "count": 10}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}, {"name": "B", "count": 12}]}

    def mock_load(slug: str) -> Any:
        return prev if slug == "prev" else curr

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        result = await detect_regressions("curr", "prev")
        assert len(result) == 1
        assert result[0].category == "A"
        assert result[0].change == -5


@pytest.mark.asyncio
async def test_calculate_quality_metrics(service) -> None:
    meta = {
        "name": "Test",
        "categories": [
            {"name": "Small", "count": 5},
            {"name": "Large", "count": 100},
            {"name": "Medium", "count": 50},
        ],
    }

    with patch.object(AIAutomationService, "load_release_meta", return_value=meta):
        result = await calculate_quality_metrics("test")
        assert result is not None
        assert result.total_features == 155
        assert result.total_categories == 3
        assert result.avg_features_per_category == 155 / 3
        assert result.largest_category == ("Large", 100)
        assert result.smallest_category == ("Small", 5)


@pytest.mark.asyncio
async def test_generate_changelog_ai(service, llm_service, tmp_path: Path) -> None:
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    meta = {"name": "Summer '26", "release_id": 262, "categories": [{"name": "A", "count": 10}]}
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        result = await generate_changelog()
        assert result == "AI generated content"
        llm_service.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_generate_changelog_fallback(service, tmp_path: Path) -> None:
    # Override llm_service to return None for fallback
    service._llm.generate_text = AsyncMock(return_value=None)

    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    meta = {"name": "Summer '26", "release_id": 262, "categories": [{"name": "A", "count": 10}]}
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        result = await generate_changelog()
        assert "Summer '26" in result
        assert "10 recursos" in result


@pytest.mark.asyncio
async def test_generate_regression_report_ai(service, llm_service) -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 20}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}]}

    def mock_load(slug: str) -> Any:
        return prev if slug == "prev" else curr

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        result = await generate_regression_report("curr", "prev")
        assert result == "AI generated content"
        llm_service.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_generate_diff_report_ai(service, llm_service) -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 10}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}]}

    def mock_load(slug: str) -> Any:
        return prev if slug == "prev" else curr

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        result = await generate_diff_report("curr", "prev")
        assert result == "AI generated content"
        llm_service.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_generate_quality_report_ai(service, llm_service, tmp_path: Path) -> None:
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    meta = {"name": "Summer '26", "categories": [{"name": "A", "count": 10}]}
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        result = await generate_quality_report()
        assert result == "AI generated content"
        llm_service.generate_text.assert_called_once()


@pytest.mark.asyncio
async def test_generate_ai_summary_growth(service, llm_service) -> None:
    prev = {
        "name": "Prev",
        "categories": [{"name": "A", "count": 10}, {"name": "B", "count": 5}],
    }
    curr = {
        "name": "Curr",
        "categories": [
            {"name": "A", "count": 20},
            {"name": "B", "count": 5},
            {"name": "C", "count": 3},
        ],
    }

    def mock_load(slug: str) -> Any:
        return prev if slug == "prev" else curr

    summary_json = json.dumps(
        {
            "headline": "Curr traz crescimento",
            "highlights": ["Novo recurso C"],
            "risk_areas": [],
            "overall_trend": "crescimento",
        }
    )
    llm_service.generate_text.return_value = summary_json

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        result = await generate_ai_summary("curr", "prev")
        assert isinstance(result, AISummary)
        assert "Curr" in result.headline
        assert result.overall_trend == "crescimento"


@pytest.mark.asyncio
async def test_generate_ai_summary_fallback(service, tmp_path: Path) -> None:
    service._llm.generate_text = AsyncMock(return_value=None)

    prev = {"name": "Prev", "categories": [{"name": "A", "count": 10}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 20}]}

    def mock_load(slug: str) -> Any:
        return prev if slug == "prev" else curr

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        result = await generate_ai_summary("curr", "prev")
        assert isinstance(result, AISummary)
        assert "Curr" in result.headline
        assert result.overall_trend == "crescimento"


@pytest.mark.asyncio
async def test_generate_ai_summary_report(service) -> None:
    with patch(
        "src.automation.reporting.generate_ai_summary",
        AsyncMock(
            return_value=AISummary(
                headline="Test Headline",
                highlights=["H1"],
                risk_areas=["R1"],
                overall_trend="estável",
            )
        ),
    ):
        result = await generate_ai_summary_report("curr", "prev")
        assert "Test Headline" in result
        assert "Destaques" in result
        assert "Áreas de Risco" in result
        assert "Tendência" in result


@pytest.mark.asyncio
async def test_calculate_category_impact_scores(service, tmp_path: Path) -> None:
    meta1 = {
        "name": "R1",
        "release_id": 1,
        "categories": [{"name": "A", "count": 10}, {"name": "B", "count": 20}],
    }
    meta2 = {
        "name": "R2",
        "release_id": 2,
        "categories": [{"name": "A", "count": 15}, {"name": "B", "count": 18}],
    }
    meta3 = {
        "name": "R3",
        "release_id": 3,
        "categories": [{"name": "A", "count": 25}, {"name": "B", "count": 15}],
    }

    r1, r2, r3 = tmp_path / "r1", tmp_path / "r2", tmp_path / "r3"
    for r, m in [(r1, meta1), (r2, meta2), (r3, meta3)]:
        r.mkdir()
        (r / ".meta.json").write_text(json.dumps(m))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        scores = await calculate_category_impact_scores()
        assert len(scores) == 2
        assert scores[0].risk_score >= 0


@pytest.mark.asyncio
async def test_predict_next_release_impact(service, tmp_path: Path) -> None:
    meta1 = {"name": "R1", "release_id": 1, "categories": [{"name": "A", "count": 10}]}
    meta2 = {"name": "R2", "release_id": 2, "categories": [{"name": "A", "count": 30}]}

    r1, r2 = tmp_path / "r1", tmp_path / "r2"
    for r, m in [(r1, meta1), (r2, meta2)]:
        r.mkdir()
        (r / ".meta.json").write_text(json.dumps(m))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        prediction = await predict_next_release_impact()
        assert isinstance(prediction, ImpactPrediction)
        assert prediction.overall_risk_level in ["alto", "moderado", "baixo", "indeterminado"]


@pytest.mark.asyncio
async def test_generate_impact_prediction_report(service, tmp_path: Path) -> None:
    meta1 = {"name": "R1", "release_id": 1, "categories": [{"name": "A", "count": 10}]}
    meta2 = {"name": "R2", "release_id": 2, "categories": [{"name": "A", "count": 25}]}

    r1, r2 = tmp_path / "r1", tmp_path / "r2"
    for r, m in [(r1, meta1), (r2, meta2)]:
        r.mkdir()
        (r / ".meta.json").write_text(json.dumps(m))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        report = await generate_impact_prediction_report()
        assert "Previsão de Impacto" in report


@pytest.mark.asyncio
async def test_triage_release_missing(service) -> None:
    with patch.object(AIAutomationService, "load_release_meta", return_value=None):
        result = await triage_release("missing")
        assert isinstance(result, TriageResult)
        assert result.risk_level == "desconhecido"


@pytest.mark.asyncio
async def test_triage_release_low_risk(service) -> None:
    meta = {"name": "Test", "categories": [{"name": "A", "count": 10}]}

    def mock_load(slug: str) -> Any:
        return meta

    with patch.object(AIAutomationService, "load_release_meta", side_effect=mock_load):
        with patch.object(
            AIAutomationService, "calculate_quality_metrics", AsyncMock(return_value=None)
        ):
            with patch.object(
                AIAutomationService,
                "predict_next_release_impact",
                AsyncMock(return_value=ImpactPrediction([], [], [], "baixo", "test")),
            ):
                result = await triage_release("test")
                assert isinstance(result, TriageResult)
                assert result.risk_level in ["mínimo", "baixo", "moderado", "alto"]


@pytest.mark.asyncio
async def test_generate_triage_report(service) -> None:
    with patch(
        "src.ai_automation.triage_release",
        AsyncMock(
            return_value=TriageResult(
                risk_level="baixo",
                risk_score=10,
                categories_at_risk=["A"],
                suggested_actions=["Act"],
                priority="normal",
                summary="Sum",
            )
        ),
    ):
        report = await generate_triage_report("test")
        assert "Triage Automatizado" in report
        assert "Nível de Risco" in report


@pytest.mark.asyncio
async def test_analyze_content_changes(service, tmp_path: Path) -> None:
    release_dir = tmp_path / "test_release"
    release_dir.mkdir()
    (release_dir / "file1.md").write_text("content1")
    (release_dir / "file2.md").write_text("content2")

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        result = await analyze_content_changes("test_release")
        assert isinstance(result, DeduplicationResult)
        assert len(result.new_files) == 2


@pytest.mark.asyncio
async def test_get_content_hash(service, tmp_path: Path) -> None:
    test_file = tmp_path / "test.md"
    test_file.write_text("hello world")

    result = await get_content_hash(str(test_file))
    assert result is not None
    assert len(result) == 32


@pytest.mark.asyncio
async def test_is_content_unchanged(service, tmp_path: Path) -> None:
    test_file = tmp_path / "test.md"
    test_file.write_text("hello world")
    correct_hash = await get_content_hash(str(test_file))
    assert correct_hash is not None

    assert await is_content_unchanged(str(test_file), correct_hash)
    assert not await is_content_unchanged(str(test_file), "wrong_hash")


@pytest.mark.asyncio
async def test_generate_deduplication_report(service, tmp_path: Path) -> None:
    release_dir = tmp_path / "test_release"
    release_dir.mkdir()
    (release_dir / "file1.md").write_text("content1")

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        report = await generate_deduplication_report("test_release")
        assert "Deduplicação de Conteúdo" in report


@pytest.mark.asyncio
async def test_filter_features_for_profile_admin(service) -> None:
    categories = [
        {"name": "Security", "count": 10},
        {"name": "Development", "count": 20},
        {"name": "Sales", "count": 5},
    ]

    profile = await filter_features_for_profile("admin", categories)
    assert isinstance(profile, UserProfile)
    assert "Security" in profile.relevant_categories


@pytest.mark.asyncio
async def test_generate_filtered_notification(service) -> None:
    meta = {
        "name": "Test",
        "categories": [{"name": "Security", "count": 10}, {"name": "Sales", "count": 5}],
    }

    with patch.object(AIAutomationService, "load_release_meta", return_value=meta):
        result = await generate_filtered_notification("test", "admin")
        assert isinstance(result, FilteredNotification)
        assert result.total_features == 15


@pytest.mark.asyncio
async def test_generate_filtered_notification_report(service) -> None:
    meta = {"name": "Test", "categories": [{"name": "Security", "count": 10}]}

    with patch.object(AIAutomationService, "load_release_meta", return_value=meta):
        report = await generate_filtered_notification_report("test", "admin")
        assert "Notificação Filtrada" in report


@pytest.mark.asyncio
async def test_export_functions(service, tmp_path: Path) -> None:
    release_dir = tmp_path / "test_rel"
    release_dir.mkdir()
    meta = {"name": "Test", "categories": [{"name": "Sec", "count": 1}]}
    (release_dir / ".meta.json").write_text(json.dumps(meta))
    (release_dir / "sec.md").write_text("| Feature | Yes | Yes | Yes | Yes |")

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        json_res = await export_release_json("test_rel")
        assert "Test" in json_res
        csv_res = await export_release_csv("test_rel")
        assert "category,feature" in csv_res
        all_res = await export_all_releases(str(tmp_path / "exports"))
        assert "test_rel" in all_res


def test_generate_dynamic_badge() -> None:
    result = generate_dynamic_badge("Test Release", 100)
    assert "Latest Release" in result
    assert "Test%20Release" in result


def test_get_latest_release_badge(tmp_path: Path) -> None:
    r1 = tmp_path / "r1"
    r1.mkdir()
    (r1 / ".meta.json").write_text(json.dumps({"name": "Rel 1", "release_id": 1}))

    with patch("src.config.RELEASES_DIR", str(tmp_path)):
        assert get_latest_release_badge() == "Rel 1"


# Module-level convenience function tests
@pytest.mark.asyncio
async def test_module_create_release_issue():
    """Module-level create_release_issue delegates to service."""
    with patch("src.ai_automation.AIAutomationService") as MockSvc:
        MockSvc.return_value.create_github_issue = AsyncMock(return_value="issue-1")
        from src.ai_automation import create_release_issue

        result = await create_release_issue("R1", 10, 5)
        assert result == "issue-1"


@pytest.mark.asyncio
async def test_module_load_all_release_metas():
    """Module-level _load_all_release_metas delegates to service."""
    with patch("src.ai_automation.AIAutomationService") as MockSvc:
        MockSvc.return_value._load_all_release_metas = AsyncMock(return_value=[{"name": "R1"}])
        from src.ai_automation import _load_all_release_metas

        result = await _load_all_release_metas()
        assert len(result) == 1


@pytest.mark.asyncio
async def test_module_load_content_cache(tmp_path):
    """Module-level _load_content_cache delegates to service."""
    from src.ai_automation import _load_content_cache

    result = await _load_content_cache(tmp_path / "nope.json")
    assert isinstance(result, dict)


@pytest.mark.asyncio
async def test_module_generate_deduplication_report():
    """Module-level generate_deduplication_report delegates to service."""
    with patch("src.ai_automation.AIAutomationService") as MockSvc:
        MockSvc.return_value.generate_deduplication_report = AsyncMock(return_value="report")
        from src.ai_automation import generate_deduplication_report

        result = await generate_deduplication_report("summer_26")
        assert result == "report"


@pytest.mark.asyncio
async def test_module_filter_features_for_profile():
    """Module-level filter_features_for_profile delegates to service."""
    with patch("src.ai_automation.AIAutomationService") as MockSvc:
        profile = UserProfile(
            profile_type="dev",
            name="dev",
            relevant_categories=[],
            filtered_features=[],
            priority_features=[],
            relevance_score=0.0,
        )
        MockSvc.return_value.filter_features_for_profile = AsyncMock(return_value=profile)
        from src.ai_automation import filter_features_for_profile

        result = await filter_features_for_profile("developer", [])
        assert result.name == "dev"


@pytest.mark.asyncio
async def test_module_generate_filtered_notification():
    """Module-level generate_filtered_notification delegates to service."""
    with patch("src.ai_automation.AIAutomationService") as MockSvc:
        up = UserProfile(
            profile_type="dev",
            name="dev",
            relevant_categories=[],
            filtered_features=[],
            priority_features=[],
            relevance_score=0.0,
        )
        notif = FilteredNotification(
            profile=up, total_features=0, relevant_count=0, priority_count=0, summary="text"
        )
        MockSvc.return_value.generate_filtered_notification = AsyncMock(return_value=notif)
        from src.ai_automation import generate_filtered_notification

        result = await generate_filtered_notification("summer_26", "developer")
        assert result.total_features == 0


@pytest.mark.asyncio
async def test_module_generate_filtered_notification_report():
    """Module-level generate_filtered_notification_report delegates to service."""
    with patch("src.ai_automation.AIAutomationService") as MockSvc:
        MockSvc.return_value.generate_filtered_notification_report = AsyncMock(
            return_value="report"
        )
        from src.ai_automation import generate_filtered_notification_report

        result = await generate_filtered_notification_report("summer_26", "developer")
        assert result == "report"


def test_module_generate_dynamic_badge():
    """Module-level generate_dynamic_badge delegates to service."""
    from src.ai_automation import generate_dynamic_badge

    result = generate_dynamic_badge("Summer '26", 100)
    assert isinstance(result, str)


def test_get_latest_release_badge_no_dir(tmp_path):
    """get_latest_release_badge returns N/A when no releases dir."""
    with patch("src.config.RELEASES_DIR", str(tmp_path / "nope")):
        from src.ai_automation import get_latest_release_badge

        result = get_latest_release_badge()
        assert result == "N/A"
