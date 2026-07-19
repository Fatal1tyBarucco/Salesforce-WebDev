"""Tests for src/analytics.py — 100% coverage."""

import json
from pathlib import Path
from unittest.mock import patch

from src.analytics import (
    ReleaseStats,
    _parse_generated_at,
    _svg_bar_chart,
    _svg_gauge,
    _svg_line_chart,
    compute_stats,
    generate_analytics,
    generate_dashboard_html,
    load_all_metas,
)


class TestLoadAllMetas:
    """Tests for load_all_metas."""

    def test_no_dir(self, tmp_path: Path) -> None:
        with patch("src.analytics.RELEASES_DIR", str(tmp_path / "nope")):
            assert load_all_metas() == []

    def test_loads_and_sorts(self, tmp_path: Path) -> None:
        for slug, rid in [("b", 262), ("a", 260)]:
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text(json.dumps({"release_id": rid}))
        with patch("src.analytics.RELEASES_DIR", str(tmp_path)):
            metas = load_all_metas()
            assert len(metas) == 2
            assert metas[0]["release_id"] == 260

    def test_skips_invalid(self, tmp_path: Path) -> None:
        d = tmp_path / "bad"
        d.mkdir()
        (d / ".meta.json").write_text("not json{")
        with patch("src.analytics.RELEASES_DIR", str(tmp_path)):
            assert load_all_metas() == []


class TestParseGeneratedAt:
    """Tests for _parse_generated_at."""

    def test_valid_timestamp(self) -> None:
        meta = {"generated_at": "2025-01-15T10:00:00+00:00"}
        ts = _parse_generated_at(meta)
        assert ts > 0

    def test_empty_timestamp(self) -> None:
        assert _parse_generated_at({}) == 0.0

    def test_invalid_timestamp(self) -> None:
        assert _parse_generated_at({"generated_at": "not-a-date"}) == 0.0

    def test_naive_timestamp(self) -> None:
        """Naive datetime gets UTC timezone attached."""
        meta = {"generated_at": "2025-01-15T10:00:00"}
        ts = _parse_generated_at(meta)
        assert ts > 0


class TestComputeStats:
    """Tests for compute_stats."""

    def test_empty(self) -> None:
        stats = compute_stats([])
        assert stats.total_releases == 0
        assert stats.total_features == 0

    def test_single_release(self) -> None:
        metas = [
            {
                "name": "Summer '26",
                "total_features": 100,
                "avg_confidence": 0.9,
                "categories": [{"name": "A", "count": 50}],
            }
        ]
        stats = compute_stats(metas)
        assert stats.total_releases == 1
        assert stats.total_features == 100
        assert len(stats.categories) == 1
        assert stats.categories[0].trend == "stable"

    def test_trend_up(self) -> None:
        metas = [
            {"total_features": 10, "categories": [{"name": "A", "count": 10}]},
            {"total_features": 20, "categories": [{"name": "A", "count": 30}]},
        ]
        stats = compute_stats(metas)
        assert stats.categories[0].trend == "up"

    def test_trend_down(self) -> None:
        metas = [
            {"total_features": 20, "categories": [{"name": "A", "count": 30}]},
            {"total_features": 10, "categories": [{"name": "A", "count": 10}]},
        ]
        stats = compute_stats(metas)
        assert stats.categories[0].trend == "down"

    def test_trend_stable(self) -> None:
        """Category with small delta is stable."""
        metas = [
            {"total_features": 10, "categories": [{"name": "A", "count": 10}]},
            {"total_features": 20, "categories": [{"name": "A", "count": 12}]},
        ]
        stats = compute_stats(metas)
        assert stats.categories[0].trend == "stable"

    def test_single_category(self) -> None:
        """Single category has stable trend and delta 0."""
        metas = [{"total_features": 10, "categories": [{"name": "A", "count": 5}]}]
        stats = compute_stats(metas)
        assert stats.categories[0].trend == "stable"
        assert stats.categories[0].trend_delta == 0

    def test_with_generated_at(self) -> None:
        """Days between releases is computed from generated_at."""
        metas = [
            {"total_features": 10, "generated_at": "2025-01-01T00:00:00+00:00", "categories": []},
            {"total_features": 20, "generated_at": "2025-01-31T00:00:00+00:00", "categories": []},
        ]
        stats = compute_stats(metas)
        assert len(stats.days_between) == 1
        assert stats.days_between[0] == 30.0


class TestSvgCharts:
    """Tests for SVG chart generators."""

    def test_bar_chart_empty(self) -> None:
        assert "Sem dados" in _svg_bar_chart([], [])

    def test_bar_chart_with_data(self) -> None:
        svg = _svg_bar_chart(["A", "B"], [10, 20])
        assert "<svg" in svg
        assert "A" in svg

    def test_line_chart_empty(self) -> None:
        assert "Sem dados" in _svg_line_chart([], {})

    def test_line_chart_empty_series(self) -> None:
        assert "Sem dados" in _svg_line_chart(["A"], {"s": []})

    def test_line_chart_with_data(self) -> None:
        svg = _svg_line_chart(["A", "B", "C"], {"series1": [1.0, 2.0, 3.0]})
        assert "<svg" in svg
        assert "polyline" in svg

    def test_gauge(self) -> None:
        svg = _svg_gauge(75, 100, "Test")
        assert "<svg" in svg
        assert "Test" in svg

    def test_gauge_zero_max(self) -> None:
        svg = _svg_gauge(0, 0, "Zero")
        assert "<svg" in svg


class TestGenerateDashboardHtml:
    """Tests for generate_dashboard_html."""

    def test_with_data(self) -> None:
        from src.analytics import CategoryStats

        stats = ReleaseStats(
            total_releases=2,
            total_features=100,
            avg_confidence=0.85,
            release_names=["R1", "R2"],
            feature_counts=[40, 60],
            confidence_values=[0.8, 0.9],
            categories=[
                CategoryStats("Security", [10, 20], 15.0, 10, 20, "up", 10),
                CategoryStats("Performance", [5, 3], 4.0, 3, 5, "down", -2),
            ],
            days_between=[30.0],
        )
        html_out = generate_dashboard_html(stats)
        assert "<!DOCTYPE html>" in html_out
        assert "Security" in html_out
        assert "Crescendo" in html_out or "📈" in html_out

    def test_single_release_no_trends(self) -> None:
        stats = ReleaseStats(
            total_releases=1,
            total_features=10,
            avg_confidence=0.5,
            release_names=["R1"],
            feature_counts=[10],
            confidence_values=[0.5],
            categories=[],
            days_between=[],
        )
        html_out = generate_dashboard_html(stats)
        assert "<!DOCTYPE html>" in html_out


class TestGenerateAnalytics:
    """Tests for generate_analytics."""

    def test_no_data(self, tmp_path: Path) -> None:
        with patch("src.analytics.RELEASES_DIR", str(tmp_path / "nope")):
            assert generate_analytics(str(tmp_path / "out")) is None

    def test_generates_file(self, tmp_path: Path) -> None:
        d = tmp_path / "r1"
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps({"release_id": 260, "total_features": 10, "avg_confidence": 0.8})
        )
        out = tmp_path / "output"
        with patch("src.analytics.RELEASES_DIR", str(tmp_path)):
            result = generate_analytics(str(out))
        assert result is not None
        assert Path(result).exists()
