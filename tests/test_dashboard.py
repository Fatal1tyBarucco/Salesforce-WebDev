"""Tests for src/dashboard.py — 100% coverage."""

import json
from pathlib import Path
from unittest.mock import patch

from src.dashboard import (
    _build_dashboard_data,
    _load_all_metas,
    _load_features,
    generate_dashboard,
    generate_dashboard_html,
)


class TestLoadAllMetas:
    """Tests for _load_all_metas function."""

    def test_no_releases_dir(self, tmp_path: Path) -> None:
        """Returns empty list when releases dir doesn't exist."""
        with patch("src.dashboard.RELEASES_DIR", str(tmp_path / "nope")):
            assert _load_all_metas() == []

    def test_loads_valid_metas(self, tmp_path: Path) -> None:
        """Loads .meta.json files from subdirectories."""
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(json.dumps({"name": "Summer '26", "release_id": 262}))

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            metas = _load_all_metas()
            assert len(metas) == 1
            assert metas[0]["name"] == "Summer '26"

    def test_skips_invalid_json(self, tmp_path: Path) -> None:
        """Skips directories with invalid .meta.json."""
        d = tmp_path / "bad"
        d.mkdir()
        (d / ".meta.json").write_text("not json{")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            assert _load_all_metas() == []

    def test_sorted_by_release_id(self, tmp_path: Path) -> None:
        """Metas are sorted by release_id."""
        for slug, rid in [("b_release", 262), ("a_release", 260)]:
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text(json.dumps({"release_id": rid, "slug": slug}))

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            metas = _load_all_metas()
            assert metas[0]["release_id"] == 260
            assert metas[1]["release_id"] == 262


class TestLoadFeatures:
    """Tests for _load_features function."""

    def test_no_release_dir(self, tmp_path: Path) -> None:
        """Returns empty list when release dir doesn't exist."""
        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            assert _load_features("nonexistent") == []

    def test_loads_bullet_features(self, tmp_path: Path) -> None:
        """Loads features from bullet format **name**."""
        d = tmp_path / "test_release"
        d.mkdir()
        (d / "cat.md").write_text("## My Category\n\n* **Feature One** — _generally available_\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            features = _load_features("test_release")
            assert len(features) == 1
            assert features[0]["name"] == "Feature One"
            assert features[0]["category"] == "My Category"

    def test_loads_tab_features(self, tmp_path: Path) -> None:
        """Loads features from tab-separated lines."""
        d = tmp_path / "test_release"
        d.mkdir()
        (d / "cat.md").write_text("## Category\n\nTabFeature\tDetails here\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            features = _load_features("test_release")
            assert len(features) == 1
            assert features[0]["name"] == "TabFeature"

    def test_loads_long_line_features(self, tmp_path: Path) -> None:
        """Loads features from long plain text lines."""
        d = tmp_path / "test_release"
        d.mkdir()
        long_line = "This is a very long feature description that exceeds ten chars"
        (d / "cat.md").write_text(f"## Category\n\n{long_line}\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            features = _load_features("test_release")
            assert len(features) == 1
            assert features[0]["name"] == long_line

    def test_skips_dotfiles(self, tmp_path: Path) -> None:
        """Skips .hidden.md files."""
        d = tmp_path / "test_release"
        d.mkdir()
        (d / ".hidden.md").write_text("## Hidden\n\n- **Secret**\n")
        (d / "visible.md").write_text("## Cat\n\n* **Visible Feature Here**\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            features = _load_features("test_release")
            assert len(features) == 1
            assert features[0]["name"] == "Visible Feature Here"

    def test_skips_os_errors(self, tmp_path: Path) -> None:
        """Handles OSError when reading files."""
        d = tmp_path / "test_release"
        d.mkdir()
        (d / "cat.md").write_text("## Cat\n\n- **Good Feature Here**\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            with patch("pathlib.Path.read_text", side_effect=OSError("perm")):
                features = _load_features("test_release")
                assert features == []

    def test_skips_headers_and_tables(self, tmp_path: Path) -> None:
        """Skips lines starting with #, |, or empty lines."""
        d = tmp_path / "test_release"
        d.mkdir()
        (d / "cat.md").write_text(
            "# Title\n## Category\n\n| Col | Val |\n| --- | --- |\n\n* **Valid Feature Name**\n"
        )

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            features = _load_features("test_release")
            assert len(features) == 1
            assert features[0]["name"] == "Valid Feature Name"

    def test_skips_short_tab_lines(self, tmp_path: Path) -> None:
        """Skips tab-separated lines where name is too short."""
        d = tmp_path / "test_release"
        d.mkdir()
        (d / "cat.md").write_text("## Cat\n\nAB\tshort\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            features = _load_features("test_release")
            assert len(features) == 0


class TestBuildDashboardData:
    """Tests for _build_dashboard_data function."""

    def test_builds_data_with_features(self, tmp_path: Path) -> None:
        """_build_dashboard_data aggregates releases and features."""
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps(
                {
                    "name": "Summer '26",
                    "slug": "summer_26",
                    "release_id": 262,
                    "total_features": 10,
                    "avg_confidence": 0.9,
                    "categories": [{"name": "A", "count": 5}],
                }
            )
        )
        (d / "cat.md").write_text("## A\n\n* **Test Feature Name Here**\n")

        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            data = _build_dashboard_data()
            assert data["total_releases"] == 1
            assert len(data["releases"]) == 1
            assert data["releases"][0]["name"] == "Summer '26"
            assert len(data["features"]) == 1

    def test_builds_empty_data(self, tmp_path: Path) -> None:
        """_build_dashboard_data returns empty when no releases."""
        with patch("src.dashboard.RELEASES_DIR", str(tmp_path / "nope")):
            data = _build_dashboard_data()
            assert data["total_releases"] == 0
            assert data["total_features"] == 0


class TestGenerateDashboardHtml:
    """Tests for generate_dashboard_html function."""

    def test_generates_valid_html(self) -> None:
        """generate_dashboard_html returns HTML string with data."""
        data = {
            "releases": [
                {
                    "name": "Summer '26",
                    "slug": "summer_26",
                    "release_id": 262,
                    "total_features": 10,
                    "avg_confidence": 0.9,
                    "categories": [{"name": "A", "count": 5}],
                }
            ],
            "features": [{"name": "F1", "category": "A", "release": "summer_26", "availability": ""}],
            "total_releases": 1,
            "total_features": 1,
        }
        html = generate_dashboard_html(data)
        assert "<!DOCTYPE html>" in html
        assert "Summer '26" in html
        assert "Dashboard" in html


class TestGenerateDashboard:
    """Tests for generate_dashboard function."""

    def test_returns_none_when_no_data(self, tmp_path: Path) -> None:
        """Returns None when no releases exist."""
        with patch("src.dashboard.RELEASES_DIR", str(tmp_path / "nope")):
            assert generate_dashboard(str(tmp_path / "out")) is None

    def test_generates_output_file(self, tmp_path: Path) -> None:
        """Creates dashboard.html in output_dir."""
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps(
                {
                    "name": "Summer '26",
                    "slug": "summer_26",
                    "release_id": 262,
                    "total_features": 10,
                    "categories": [],
                }
            )
        )

        out_dir = tmp_path / "output"
        with patch("src.dashboard.RELEASES_DIR", str(tmp_path)):
            result = generate_dashboard(str(out_dir))

        assert result is not None
        assert Path(result).exists()
        assert "dashboard.html" in result
