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
