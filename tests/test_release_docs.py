"""Tests for src/release_docs.py — 100% coverage target."""

from pathlib import Path
from unittest.mock import patch

from src.config import ReleaseInfo, BILINGUAL_TEMPLATES


class TestBuildReleaseName:
    """_build_release_name: maps release IDs to seasonal names."""

    def test_fallback_for_unexpected_id(self) -> None:
        from src.release_docs import _build_release_name

        name = _build_release_name(200)
        assert "Spring" in name or "Summer" in name or "Winter" in name


class TestBuildReleaseSlug:
    """_build_release_slug: produces URL-safe slugs."""

    def test_slug_is_lowercase_with_underscore(self) -> None:
        from src.release_docs import _build_release_slug

        slug = _build_release_slug(262)
        assert "_" in slug
        assert slug.islower()


class TestFindExistingReleases:
    """_find_existing_releases: scans RELEASES_DIR for subdirs with .meta.json."""

    def test_empty_when_dir_missing(self, tmp_path: Path) -> None:
        from src.release_docs import _find_existing_releases

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path / "nope")):
            assert _find_existing_releases() == set()

    def test_returns_slugs(self, tmp_path: Path) -> None:
        from src.release_docs import _find_existing_releases

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text('{"name": "Summer 26"}')

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            result = _find_existing_releases()
        assert "summer_26" in result


class TestSlugifyCategory:
    """_slugify_category: ASCII-safe slug generation."""

    def test_pt_br_lowercases_and_replaces_spaces(self) -> None:
        from src.release_docs import _slugify_category

        assert _slugify_category("Análise de dados") == "analise_de_dados"

    def test_ascii_passthrough(self) -> None:
        from src.release_docs import _slugify_category

        assert _slugify_category("Security") == "security"


class TestGetReleaseEmoji:
    """_get_release_emoji: maps season names to emoji."""

    def test_summer(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "☀" in _get_release_emoji("Summer '26")

    def test_spring(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "🌸" in _get_release_emoji("Spring '26")

    def test_winter(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "❄" in _get_release_emoji("Winter '26")

    def test_unknown_defaults_to_spring(self) -> None:
        from src.release_docs import _get_release_emoji

        assert "🌸" in _get_release_emoji("Unknown '26")


class TestBuildResourceFooter:
    """_build_resource_footer: generates markdown link list."""

    def test_returns_non_empty_list(self) -> None:
        from src.release_docs import _build_resource_footer

        release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
        templates = BILINGUAL_TEMPLATES.get("pt_BR", BILINGUAL_TEMPLATES["en_US"])
        footer = _build_resource_footer(release, templates, "pt_BR")
        assert isinstance(footer, list)
        assert len(footer) > 0
