"""Tests for src/release_discovery.py — ReleaseDiscoveryService.

Covers all discovery strategies, edge cases, and metric emission.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.config import ReleaseInfo
from src.events import EventBus
from src.release_discovery import DiscoveryResult, DiscoveryStrategy, ReleaseDiscoveryService


def _make_release(release_id: int, slug: str = "", name: str = "") -> ReleaseInfo:
    if not name:
        name = f"Release {release_id}"
    if not slug:
        slug = f"release_{release_id}"
    return ReleaseInfo(name=name, release_id=release_id, slug=slug)


# ---------------------------------------------------------------------------
# find_existing_releases
# ---------------------------------------------------------------------------


class TestFindExistingReleases:
    def test_empty_when_dir_missing(self, tmp_path: Path) -> None:
        service = ReleaseDiscoveryService(releases_dir=str(tmp_path / "nope"))
        assert service.find_existing_releases() == set()

    def test_returns_slugs_with_meta(self, tmp_path: Path) -> None:
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text('{"name": "Summer 26"}')
        service = ReleaseDiscoveryService(releases_dir=str(tmp_path))
        assert "summer_26" in service.find_existing_releases()

    def test_skips_dirs_without_meta(self, tmp_path: Path) -> None:
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / "some_file.txt").write_text("hello")
        service = ReleaseDiscoveryService(releases_dir=str(tmp_path))
        assert service.find_existing_releases() == set()

    def test_skips_flat_files(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").write_text("hi")
        service = ReleaseDiscoveryService(releases_dir=str(tmp_path))
        assert service.find_existing_releases() == set()


# ---------------------------------------------------------------------------
# discover — no existing releases
# ---------------------------------------------------------------------------


class TestDiscoverNoExistingReleases:
    @pytest.mark.asyncio
    async def test_returns_latest_known_when_repo_empty(self) -> None:
        known = [_make_release(262, "summer_26"), _make_release(260, "spring_26")]
        service = ReleaseDiscoveryService(
            scraper=AsyncMock(),
            known_releases=known,
            releases_dir=str(Path("/nonexistent")),
        )
        result = await service.discover()
        assert len(result) == 1
        assert result[0].slug == "summer_26"

    @pytest.mark.asyncio
    async def test_returns_empty_when_all_known_exist(self, tmp_path: Path) -> None:
        """When all known releases exist and content is identical, return []."""
        for slug in ("summer_26", "spring_26"):
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text("{}")

        known = [_make_release(262, "summer_26"), _make_release(260, "spring_26")]

        # Scraper returns identical content for all fetches — no new release.
        identical_text = "same content " + "x" * 500
        scraper = AsyncMock()
        scraper.fetch_page_raw_text.return_value = identical_text

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
        )
        result = await service.discover()
        assert result == []


# ---------------------------------------------------------------------------
# discover — content comparison strategy
# ---------------------------------------------------------------------------


class TestDiscoverContentComparison:
    @pytest.mark.asyncio
    async def test_detects_new_release_via_content_differs(self, tmp_path: Path) -> None:
        """When current content differs from candidate, return the candidate."""
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [
            _make_release(260, "spring_26"),
            _make_release(262, "summer_26"),
        ]

        scraper = AsyncMock()
        # current (262) returns text A, candidate (264) returns text B
        scraper.fetch_page_raw_text.side_effect = [
            "current page content " + "x" * 500,
            "different content from candidate " + "y" * 500,
        ]

        bus = EventBus()
        detected: list[dict] = []

        @bus.on("release.detected")
        async def _on_detected(event) -> None:
            detected.append(event.data)

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
            event_bus=bus,
        )
        result = await service.discover()

        assert len(result) == 1
        assert result[0].release_id == 264
        assert len(detected) == 1
        assert detected[0]["strategy"] == "content_comparison"

    @pytest.mark.asyncio
    async def test_returns_empty_when_content_identical(self, tmp_path: Path) -> None:
        """When current and candidate content are identical, no new release."""
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [
            _make_release(260, "spring_26"),
            _make_release(262, "summer_26"),
        ]

        identical_text = "same content " + "z" * 600
        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = [identical_text, identical_text]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
        )
        result = await service.discover()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_fetch_fails(self, tmp_path: Path) -> None:
        """If content fetch fails (returns None), no new release is detected.

        The scraper is available, so content comparison is authoritative.
        Fetch failure does NOT fall through to the unverified ID-increment
        heuristic.
        """
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.return_value = None

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
        )
        result = await service.discover()
        assert result == []

    @pytest.mark.asyncio
    async def test_returns_empty_when_fetch_raises(self, tmp_path: Path) -> None:
        """If content fetch raises an exception, no new release is detected."""
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = Exception("network error")

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
        )
        result = await service.discover()
        assert result == []

    @pytest.mark.asyncio
    async def test_probes_multiple_offsets(self, tmp_path: Path) -> None:
        """When step=2 yields identical content, probe step=4."""
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        scraper = AsyncMock()
        # step=2: identical content → continue
        # step=4: different content → found new release
        scraper.fetch_page_raw_text.side_effect = [
            "content A " + "a" * 500,  # current (262)
            "content A " + "a" * 500,  # candidate (264) — identical
            "content A " + "a" * 500,  # current again (262)
            "content B " + "b" * 500,  # candidate (266) — differs
        ]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
            probe_ids=[2, 4],
        )
        result = await service.discover()
        assert len(result) == 1
        assert result[0].release_id == 266  # found at step=4

    @pytest.mark.asyncio
    async def test_probes_skips_already_existing_candidate(self, tmp_path: Path) -> None:
        """If the candidate slug already exists, skip and try next probe."""
        for slug in ("summer_26", "winter_27"):
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        scraper = AsyncMock()
        # step=2: winter_27 already exists → skip (no fetch needed)
        # step=4: spring_27 (266) → fetch current + candidate, content differs
        scraper.fetch_page_raw_text.side_effect = [
            "current content " + "c" * 500,  # for 262 (step=2 skipped, step=4 current)
            "different content " + "d" * 500,  # for 266
        ]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
            probe_ids=[2, 4],
        )
        result = await service.discover()
        assert len(result) == 1
        assert result[0].release_id == 266


# ---------------------------------------------------------------------------
# discover — ID increment fallback (scraper is None)
# ---------------------------------------------------------------------------


class TestDiscoverIdIncrementFallback:
    @pytest.mark.asyncio
    async def test_falls_back_when_scraper_is_none(self, tmp_path: Path) -> None:
        """Without a scraper, use the ID increment fallback."""
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        service = ReleaseDiscoveryService(
            scraper=None,
            known_releases=known,
            releases_dir=str(tmp_path),
        )
        result = await service.discover()
        assert len(result) == 1
        assert result[0].release_id == 264
        assert result[0].slug == "winter_27"  # build_release_info(264)

    @pytest.mark.asyncio
    async def test_id_increment_emits_strategy(self, tmp_path: Path) -> None:
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        bus = EventBus()
        detected: list[dict] = []

        @bus.on("release.detected")
        async def _on_detected(event) -> None:
            detected.append(event.data)

        service = ReleaseDiscoveryService(
            scraper=None,
            known_releases=known,
            releases_dir=str(tmp_path),
            event_bus=bus,
        )
        result = await service.discover()
        assert len(result) == 1
        assert len(detected) == 1
        assert detected[0]["strategy"] == "id_increment"

    @pytest.mark.asyncio
    async def test_id_increment_skips_if_candidate_exists(self, tmp_path: Path) -> None:
        """If the ID-increment candidate slug already exists, return empty."""
        for slug in ("summer_26", "winter_27"):
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        service = ReleaseDiscoveryService(
            scraper=None,
            known_releases=known,
            releases_dir=str(tmp_path),
        )
        result = await service.discover()
        assert result == []


# ---------------------------------------------------------------------------
# discover — no new release detected (metrics)
# ---------------------------------------------------------------------------


class TestDiscoverNoNewRelease:
    @pytest.mark.asyncio
    async def test_emits_zero_releases_event(self, tmp_path: Path) -> None:
        meta_dir = tmp_path / "summer_26"
        meta_dir.mkdir()
        (meta_dir / ".meta.json").write_text("{}")

        known = [_make_release(260, "spring_26"), _make_release(262, "summer_26")]

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = [
            "content identical " + "x" * 500,
            "content identical " + "x" * 500,
        ]

        bus = EventBus()
        completed: list[dict] = []

        @bus.on("discovery.completed")
        async def _on_completed(event) -> None:
            completed.append(event.data)

        service = ReleaseDiscoveryService(
            scraper=scraper,
            known_releases=known,
            releases_dir=str(tmp_path),
            event_bus=bus,
        )
        result = await service.discover()
        assert result == []
        assert len(completed) == 1
        assert completed[0]["new_releases"] == 0


# ---------------------------------------------------------------------------
# _find_current_release / _first_unprocessed
# ---------------------------------------------------------------------------


class TestFindCurrentRelease:
    def test_finds_latest_existing(self) -> None:
        known = [
            _make_release(254, "spring_25"),
            _make_release(262, "summer_26"),
            _make_release(260, "spring_26"),
        ]
        known_sorted = sorted(known, key=lambda x: x.release_id, reverse=True)
        service = ReleaseDiscoveryService(known_releases=known, releases_dir="/nope")
        result = service._find_current_release(known_sorted, {"summer_26", "spring_25"})
        assert result is not None
        assert result.release_id == 262

    def test_returns_none_when_none_exist(self) -> None:
        known = [_make_release(262, "summer_26")]
        known_sorted = sorted(known, key=lambda x: x.release_id, reverse=True)
        service = ReleaseDiscoveryService(known_releases=known, releases_dir="/nope")
        assert service._find_current_release(known_sorted, set()) is None


class TestFirstUnprocessed:
    def test_returns_latest_unseen(self) -> None:
        known = [_make_release(262, "summer_26"), _make_release(260, "spring_26")]
        known_sorted = sorted(known, key=lambda x: x.release_id, reverse=True)
        service = ReleaseDiscoveryService(known_releases=known, releases_dir="/nope")
        result = service._first_unprocessed(known_sorted, set())
        assert len(result) == 1
        assert result[0].slug == "summer_26"

    def test_returns_empty_when_all_exist(self) -> None:
        known = [_make_release(262, "summer_26")]
        known_sorted = sorted(known, key=lambda x: x.release_id, reverse=True)
        service = ReleaseDiscoveryService(known_releases=known, releases_dir="/nope")
        assert service._first_unprocessed(known_sorted, {"summer_26"}) == []


# ---------------------------------------------------------------------------
# _compare_content
# ---------------------------------------------------------------------------


class TestCompareContent:
    @pytest.mark.asyncio
    async def test_content_differs(self) -> None:
        current = _make_release(262)
        candidate = _make_release(264)

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = [
            "text A " + "x" * 200,
            "text B " + "y" * 200,
        ]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            releases_dir="/nope",
            feature_impact_url="https://example.com/{release_id}",
        )
        differs, metadata = await service._compare_content(current, candidate)
        assert differs is True
        assert metadata["probe_id"] == 264
        assert metadata["step"] == 2

    @pytest.mark.asyncio
    async def test_content_identical(self) -> None:
        current = _make_release(262)
        candidate = _make_release(264)

        text = "same content " + "z" * 300
        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = [text, text]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            releases_dir="/nope",
            feature_impact_url="https://example.com/{release_id}",
        )
        differs, _ = await service._compare_content(current, candidate)
        assert differs is False

    @pytest.mark.asyncio
    async def test_fetches_fail(self) -> None:
        current = _make_release(262)
        candidate = _make_release(264)

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = [None, None]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            releases_dir="/nope",
            feature_impact_url="https://example.com/{release_id}",
        )
        differs, _ = await service._compare_content(current, candidate)
        assert differs is False

    @pytest.mark.asyncio
    async def test_first_fetch_fails_returns_false(self) -> None:
        current = _make_release(262)
        candidate = _make_release(264)

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.side_effect = [Exception("boom"), "text"]

        service = ReleaseDiscoveryService(
            scraper=scraper,
            releases_dir="/nope",
            feature_impact_url="https://example.com/{release_id}",
        )
        differs, _ = await service._compare_content(current, candidate)
        assert differs is False


# ---------------------------------------------------------------------------
# _discover_via_id_increment
# ---------------------------------------------------------------------------


class TestDiscoverViaIdIncrement:
    def test_returns_candidate_when_not_existing(self) -> None:
        current = _make_release(262, "summer_26")
        service = ReleaseDiscoveryService(releases_dir="/nope")
        result = service._discover_via_id_increment(current, set())
        assert result is not None
        assert result.release.release_id == 264
        assert result.strategy == DiscoveryStrategy.ID_INCREMENT
        assert result.confidence == 0.3

    def test_returns_none_when_candidate_exists(self) -> None:
        current = _make_release(262, "summer_26")
        service = ReleaseDiscoveryService(releases_dir="/nope")
        result = service._discover_via_id_increment(current, {"winter_27"})
        assert result is None


# ---------------------------------------------------------------------------
# Backward compatibility: detect_new_release wrapper
# ---------------------------------------------------------------------------


class TestDetectNewReleaseWrapper:
    """``main.detect_new_release`` delegates to ReleaseDiscoveryService.discover."""

    @pytest.mark.asyncio
    async def test_wrapper_returns_release(self) -> None:
        from src.main import detect_new_release

        scraper = AsyncMock()
        known = [ReleaseInfo(name="Winter '27", release_id=264, slug="winter_27")]
        with patch(
            "src.release_discovery.ReleaseDiscoveryService.discover",
            new_callable=AsyncMock,
            return_value=known,
        ):
            result = await detect_new_release(scraper)
        assert result is not None
        assert result.slug == "winter_27"

    @pytest.mark.asyncio
    async def test_wrapper_returns_none_when_empty(self) -> None:
        from src.main import detect_new_release

        scraper = AsyncMock()
        with patch(
            "src.release_discovery.ReleaseDiscoveryService.discover",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await detect_new_release(scraper)
        assert result is None


# ---------------------------------------------------------------------------
# Strategy enum
# ---------------------------------------------------------------------------


class TestDiscoveryStrategy:
    def test_values(self) -> None:
        assert DiscoveryStrategy.CONTENT_COMPARISON.value == "content_comparison"
        assert DiscoveryStrategy.ID_INCREMENT.value == "id_increment"
        assert DiscoveryStrategy.OFFICIAL_INDEX.value == "official_index"
        assert DiscoveryStrategy.PROBING.value == "probing"


# ---------------------------------------------------------------------------
# DiscoveryResult dataclass
# ---------------------------------------------------------------------------


class TestDiscoveryResult:
    def test_fields(self) -> None:
        release = _make_release(264)
        result = DiscoveryResult(
            release=release,
            strategy=DiscoveryStrategy.CONTENT_COMPARISON,
            confidence=0.8,
            metadata={"key": "value"},
        )
        assert result.release == release
        assert result.strategy == DiscoveryStrategy.CONTENT_COMPARISON
        assert result.confidence == 0.8
        assert result.metadata == {"key": "value"}
