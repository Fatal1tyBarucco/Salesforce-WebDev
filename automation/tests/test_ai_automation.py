"""Tests for AI automation module."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

from src.ai_automation import (
    load_release_meta,
    compare_releases,
    detect_regressions,
    calculate_quality_metrics,
    generate_changelog,
    generate_regression_report,
    generate_ai_summary,
    generate_ai_summary_report,
    AISummary,
    calculate_category_impact_scores,
    predict_next_release_impact,
    generate_impact_prediction_report,
    ImpactPrediction,
)


def test_load_release_meta_existing(tmp_path: Path) -> None:
    meta = {"name": "Test", "slug": "test", "release_id": 100, "categories": []}
    release_dir = tmp_path / "test"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    with patch("src.ai_automation.RELEASES_DIR", str(tmp_path)):
        result = load_release_meta("test")
        assert result is not None
        assert result["name"] == "Test"


def test_load_release_meta_missing() -> None:
    with patch("src.ai_automation.RELEASES_DIR", "/nonexistent"):
        result = load_release_meta("missing")
        assert result is None


def test_compare_releases(tmp_path: Path) -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 10}, {"name": "B", "count": 5}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}, {"name": "C", "count": 3}]}

    def mock_load(slug: str) -> Any:
        if slug == "prev":
            return prev
        return curr

    with patch("src.ai_automation.load_release_meta", side_effect=mock_load):
        result = compare_releases("curr", "prev")
        assert result.current_name == "Curr"
        assert result.previous_name == "Prev"
        assert "C" in result.new_categories
        assert "B" in result.removed_categories
        assert ("A", 10, 15) in result.changed_categories


def test_detect_regressions(tmp_path: Path) -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 20}, {"name": "B", "count": 10}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}, {"name": "B", "count": 12}]}

    def mock_load(slug: str) -> Any:
        if slug == "prev":
            return prev
        return curr

    with patch("src.ai_automation.load_release_meta", side_effect=mock_load):
        result = detect_regressions("curr", "prev")
        assert len(result) == 1
        assert result[0].category == "A"
        assert result[0].change == -5


def test_calculate_quality_metrics(tmp_path: Path) -> None:

    meta = {
        "name": "Test",
        "categories": [
            {"name": "Small", "count": 5},
            {"name": "Large", "count": 100},
            {"name": "Medium", "count": 50},
        ],
    }

    with patch("src.ai_automation.load_release_meta", return_value=meta):
        result = calculate_quality_metrics("test")
        assert result is not None
        assert result.total_features == 155
        assert result.total_categories == 3
        assert result.avg_features_per_category == 155 / 3
        assert result.largest_category == ("Large", 100)
        assert result.smallest_category == ("Small", 5)


def test_generate_changelog(tmp_path: Path) -> None:
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    meta = {"name": "Summer '26", "release_id": 262, "categories": [{"name": "A", "count": 10}]}
    (release_dir / ".meta.json").write_text(json.dumps(meta))

    with patch("src.ai_automation.RELEASES_DIR", str(tmp_path)):
        result = generate_changelog()
        assert "Summer '26" in result
        assert "10 recursos" in result


def test_generate_regression_report() -> None:
    prev = {"name": "Prev", "categories": [{"name": "A", "count": 20}]}
    curr = {"name": "Curr", "categories": [{"name": "A", "count": 15}]}

    def mock_load(slug: str) -> Any:
        if slug == "prev":
            return prev
        return curr

    with patch("src.ai_automation.load_release_meta", side_effect=mock_load):
        result = generate_regression_report("curr", "prev")
        assert "Prev" in result
        assert "Curr" in result
        assert "Regressões Detectadas" in result
        assert "A" in result


def test_generate_ai_summary_growth() -> None:
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
        if slug == "prev":
            return prev
        return curr

    with patch("src.ai_automation.load_release_meta", side_effect=mock_load):
        result = generate_ai_summary("curr", "prev")
        assert isinstance(result, AISummary)
        assert "Curr" in result.headline
        assert len(result.highlights) > 0
        assert result.overall_trend == "crescimento"


def test_generate_ai_summary_decline() -> None:
    prev = {
        "name": "Prev",
        "categories": [{"name": "A", "count": 50}, {"name": "B", "count": 30}],
    }
    curr = {
        "name": "Curr",
        "categories": [{"name": "A", "count": 20}],
    }

    def mock_load(slug: str) -> Any:
        if slug == "prev":
            return prev
        return curr

    with patch("src.ai_automation.load_release_meta", side_effect=mock_load):
        result = generate_ai_summary("curr", "prev")
        assert result.overall_trend == "declínio"
        assert len(result.risk_areas) > 0


def test_generate_ai_summary_no_changes() -> None:
    data = {"name": "Same", "categories": [{"name": "A", "count": 10}]}

    with patch("src.ai_automation.load_release_meta", return_value=data):
        result = generate_ai_summary("same", "same")
        assert "sem alterações" in result.headline
        assert result.overall_trend == "estável"


def test_generate_ai_summary_report() -> None:
    prev = {
        "name": "Prev",
        "categories": [{"name": "A", "count": 10}, {"name": "B", "count": 5}],
    }
    curr = {
        "name": "Curr",
        "categories": [
            {"name": "A", "count": 15},
            {"name": "B", "count": 5},
            {"name": "C", "count": 3},
        ],
    }

    def mock_load(slug: str) -> Any:
        if slug == "prev":
            return prev
        return curr

    with patch("src.ai_automation.load_release_meta", side_effect=mock_load):
        result = generate_ai_summary_report("curr", "prev")
        assert "Resumo Inteligente" in result
        assert "Destaques" in result
        assert "Áreas de Risco" in result
        assert "Tendência Geral" in result


def test_generate_ai_summary_report_no_changes() -> None:
    data = {"name": "Same", "categories": [{"name": "A", "count": 10}]}

    with patch("src.ai_automation.load_release_meta", return_value=data):
        result = generate_ai_summary_report("same", "same")
        assert "sem alterações" in result
        assert "Nenhuma área de risco" in result


def test_calculate_category_impact_scores() -> None:
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

    def mock_load_all() -> list[dict[str, Any]]:
        return [meta1, meta2, meta3]

    with patch("src.ai_automation._load_all_release_metas", side_effect=mock_load_all):
        scores = calculate_category_impact_scores()
        assert len(scores) == 2
        assert scores[0].category in ["A", "B"]
        assert scores[0].risk_score >= 0


def test_calculate_category_impact_scores_insufficient_data() -> None:
    with patch("src.ai_automation._load_all_release_metas", return_value=[]):
        scores = calculate_category_impact_scores()
        assert scores == []


def test_predict_next_release_impact() -> None:
    meta1 = {"name": "R1", "release_id": 1, "categories": [{"name": "A", "count": 10}]}
    meta2 = {"name": "R2", "release_id": 2, "categories": [{"name": "A", "count": 30}]}

    def mock_load_all() -> list[dict[str, Any]]:
        return [meta1, meta2]

    with patch("src.ai_automation._load_all_release_metas", side_effect=mock_load_all):
        prediction = predict_next_release_impact()
        assert isinstance(prediction, ImpactPrediction)
        assert prediction.overall_risk_level in ["alto", "moderado", "baixo", "indeterminado"]
        assert isinstance(prediction.summary, str)


def test_predict_next_release_impact_no_data() -> None:
    with patch("src.ai_automation._load_all_release_metas", return_value=[]):
        prediction = predict_next_release_impact()
        assert prediction.overall_risk_level == "indeterminado"
        assert "insuficientes" in prediction.summary


def test_generate_impact_prediction_report() -> None:
    meta1 = {"name": "R1", "release_id": 1, "categories": [{"name": "A", "count": 10}]}
    meta2 = {"name": "R2", "release_id": 2, "categories": [{"name": "A", "count": 25}]}

    def mock_load_all() -> list[dict[str, Any]]:
        return [meta1, meta2]

    with patch("src.ai_automation._load_all_release_metas", side_effect=mock_load_all):
        report = generate_impact_prediction_report()
        assert "Previsão de Impacto" in report
        assert "Nível de Risco Geral" in report


def test_generate_impact_prediction_report_no_data() -> None:
    with patch("src.ai_automation._load_all_release_metas", return_value=[]):
        report = generate_impact_prediction_report()
        assert "Previsão de Impacto" in report
        assert "insuficientes" in report
