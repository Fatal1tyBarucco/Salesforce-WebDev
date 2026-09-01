"""Tests for src/automation/impact.py — 100% coverage target."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.automation.impact import (
    _load_all_release_metas,
    calculate_category_impact_scores,
)


class TestCategoryImpactScores:
    """calculate_category_impact_scores: trend analysis across releases."""

    @pytest.mark.asyncio
    async def test_empty_when_insufficient_releases(self, tmp_path: Path) -> None:
        def load_meta_fn(slug: str) -> dict | None:
            return {"categories": [{"name": "Security", "count": 10}]}

        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()
        (releases_dir / "summer_25").mkdir()

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert result == []

    @pytest.mark.asyncio
    async def test_trend_crescimento(self, tmp_path: Path) -> None:
        call_count = {"n": 0}

        def load_meta_fn(slug: str) -> dict | None:
            call_count["n"] += 1
            if call_count["n"] <= 2:
                return {
                    "release_id": call_count["n"],
                    "categories": [{"name": "Security", "count": 10}],
                }
            return {
                "release_id": call_count["n"],
                "categories": [{"name": "Security", "count": 60}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)

        assert len(result) == 1
        assert result[0].category == "Security"
        assert result[0].trend == "crescimento"

    @pytest.mark.asyncio
    async def test_trend_declinio(self, tmp_path: Path) -> None:
        call_count = {"n": 0}

        def load_meta_fn(slug: str) -> dict | None:
            call_count["n"] += 1
            counts = [60, 30, 10]
            return {
                "release_id": call_count["n"],
                "categories": [{"name": "AI", "count": counts[call_count["n"] - 1]}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)

        assert len(result) == 1
        assert result[0].trend == "declínio"

    @pytest.mark.asyncio
    async def test_trend_estavel(self, tmp_path: Path) -> None:
        call_count = {"n": 0}

        def load_meta_fn(slug: str) -> dict | None:
            call_count["n"] += 1
            return {
                "release_id": call_count["n"],
                "categories": [{"name": "AI", "count": 50 + call_count["n"]}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)

        assert len(result) == 1
        assert result[0].trend == "estável"

    @pytest.mark.asyncio
    async def test_high_volatility_high_risk(self, tmp_path: Path) -> None:
        call_count = {"n": 0}

        def load_meta_fn(slug: str) -> dict | None:
            call_count["n"] += 1
            counts = [10, 100, 10, 100]
            return {
                "release_id": call_count["n"],
                "categories": [{"name": "Security", "count": counts[call_count["n"] - 1]}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s24", "s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)

        assert len(result) == 1
        assert result[0].risk_score > 20
        assert "significativa" in result[0].prediction

    @pytest.mark.asyncio
    async def test_empty_categories_returns_empty(self, tmp_path: Path) -> None:
        def load_meta_fn(slug: str) -> dict | None:
            return {"categories": []}

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert result == []


class TestLoadAllReleaseMetas:
    """_load_all_release_metas: scans RELEASES_DIR for meta files."""

    @pytest.mark.asyncio
    async def test_returns_empty_when_dir_missing(self) -> None:
        def load_meta_fn(slug: str) -> dict | None:
            return {"categories": [{"name": "X", "count": 1}]}

        with patch("src.config.RELEASES_DIR", "/nonexistent/path"):
            result = await _load_all_release_metas(load_meta_fn)
        assert result == []

    @pytest.mark.asyncio
    async def test_loads_releases_with_meta(self, tmp_path: Path) -> None:
        def load_meta_fn(slug: str) -> dict | None:
            return {"release_id": 1, "categories": [{"name": "X", "count": 5}]}

        releases_dir = tmp_path / "releases"
        (releases_dir / "summer_25").mkdir(parents=True)
        (releases_dir / "summer_26").mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await _load_all_release_metas(load_meta_fn)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_skips_none_meta(self, tmp_path: Path) -> None:
        def load_meta_fn(slug: str) -> dict | None:
            return None

        releases_dir = tmp_path / "releases"
        (releases_dir / "summer_25").mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await _load_all_release_metas(load_meta_fn)
        assert result == []
