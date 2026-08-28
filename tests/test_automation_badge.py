"""Tests for src/automation/badge.py — 100% coverage target."""

import json
from pathlib import Path
from unittest.mock import patch


class TestLatestReleaseBadge:
    """get_latest_release_badge: directory + meta scanning."""

    def test_returns_na_when_dir_missing(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path / "nonexistent"):
            assert get_latest_release_badge() == "N/A"

    def test_returns_na_when_dir_empty(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        (tmp_path / "releases").mkdir()
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path / "releases"):
            assert get_latest_release_badge() == "N/A"

    def test_returns_na_for_corrupt_json(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        rel = tmp_path / "summer_26"
        rel.mkdir(parents=True)
        (rel / ".meta.json").write_text("not json")
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert get_latest_release_badge() == "N/A"

    def test_returns_name_from_meta(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        rel = tmp_path / "summer_26"
        rel.mkdir(parents=True)
        (rel / ".meta.json").write_text(
            json.dumps({"name": "Summer '26", "release_id": 42, "categories": []})
        )
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert get_latest_release_badge() == "Summer '26"

    def test_picks_release_with_highest_id(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        for slug, rid, name in [("summer_25", 1, "Summer '25"), ("summer_26", 5, "Summer '26")]:
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text(json.dumps({"name": name, "release_id": rid}))
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert get_latest_release_badge() == "Summer '26"


class TestDynamicBadge:
    """generate_dynamic_badge: returns Shields.io-compatible string."""

    def test_returns_string(self) -> None:
        from src.automation.badge import generate_dynamic_badge

        result = generate_dynamic_badge("Summer '26", 42)
        assert isinstance(result, str)
        assert len(result) > 0


class TestReleaseHeaderBadges:
    """generate_release_header_badges: per-release category badges."""

    def test_empty_when_slug_missing(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_release_header_badges

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert generate_release_header_badges("nonexistent") == ""

    def test_empty_when_meta_corrupt(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_release_header_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text("{bad json")
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert generate_release_header_badges("summer_26") == ""

    def test_returns_string_with_meta(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_release_header_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps(
                {
                    "name": "Summer '26",
                    "categories": [
                        {"name": "Security", "count": 10},
                        {"name": "AI", "count": 5},
                    ],
                }
            )
        )
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_release_header_badges("summer_26")
        assert isinstance(result, str)


class TestCategoryBadges:
    """generate_category_badges: per-category badge by name."""

    def test_empty_when_slug_missing(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert generate_category_badges("nonexistent", "Security") == ""

    def test_returns_string_when_category_found(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps({"categories": [{"name": "Security", "count": 10}]})
        )
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_category_badges("summer_26", "Security")
        assert isinstance(result, str)

    def test_empty_when_category_not_found(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps({"categories": [{"name": "Security", "count": 10}]})
        )
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            assert generate_category_badges("summer_26", "NonExistent") == ""

    def test_returns_string_when_corrupt_json(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text("not json")
        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_category_badges("summer_26", "Security")
        assert isinstance(result, str)
