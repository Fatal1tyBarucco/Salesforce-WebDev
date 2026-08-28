"""Tests for src/main.py — CLI argument parsing and entry points."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.config import ReleaseInfo


class TestParseArgs:
    """_parse_args: parses --release and --dry-run CLI flags."""

    def test_defaults_when_no_args(self) -> None:
        from src.main import _parse_args

        with patch("sys.argv", ["main.py"]):
            release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is False

    def test_parses_release_flag(self) -> None:
        from src.main import _parse_args

        with patch("sys.argv", ["main.py", "--release", "summer_26"]):
            release_filter, dry_run = _parse_args()
        assert release_filter == "summer_26"
        assert dry_run is False

    def test_parses_dry_run_flag(self) -> None:
        from src.main import _parse_args

        with patch("sys.argv", ["main.py", "--dry-run"]):
            release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is True


class TestDetectNewRelease:
    """detect_new_release: returns latest known or None when all exist."""

    @pytest.mark.asyncio
    async def test_returns_latest_when_no_existing(self) -> None:
        from src.main import detect_new_release

        scraper = AsyncMock()
        known = [ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")]

        with (
            patch("src.main._find_existing_releases", return_value=set()),
            patch("src.main.KNOWN_RELEASES", known),
        ):
            result = await detect_new_release(scraper)
        assert result is not None
        assert result.slug == "summer_26"

    @pytest.mark.asyncio
    async def test_returns_none_when_all_exist(self) -> None:
        from src.main import detect_new_release

        scraper = AsyncMock()
        known = [ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")]

        with (
            patch("src.main._find_existing_releases", return_value={"summer_26"}),
            patch("src.main.KNOWN_RELEASES", known),
        ):
            result = await detect_new_release(scraper)
        assert result is None


class TestEnrichMetaWithClassification:
    """enrich_meta_with_classification: no-op when meta file missing."""

    @pytest.mark.asyncio
    async def test_handles_missing_meta_file(self, tmp_path: Path) -> None:
        from src.main import enrich_meta_with_classification

        release = ReleaseInfo(name="Test", release_id=999, slug="test_999")
        with patch("src.main.RELEASES_DIR", str(tmp_path)):
            await enrich_meta_with_classification(release)
