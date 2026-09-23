"""Release discovery service — resilient, multi-strategy release detection.

Extracted from ``src.main.detect_new_release`` to decouple the orchestrator
from the ``release_id + 2`` heuristic and filesystem-scanning details.

Strategies (tried in order of preference):
  1. **Content comparison** — fetch the Feature Impact page for the current
     release and candidate release IDs, compare content.
  2. **ID increment** — simple ``release_id + 2`` fallback (no verification).

A third *official index* strategy can be added later without changing the
public ``discover()`` interface.

Usage::

    from src.release_discovery import ReleaseDiscoveryService

    service = ReleaseDiscoveryService(scraper=scraper)
    releases = await service.discover()
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from .config import (
    FEATURE_IMPACT_URL,
    KNOWN_RELEASES,
    RELEASES_DIR,
    ReleaseInfo,
    build_release_info,
)
from .events import EventBus, get_event_bus

logger = logging.getLogger(__name__)


class DiscoveryStrategy(Enum):
    """Discovery strategies in order of preference (highest first)."""

    CONTENT_COMPARISON = "content_comparison"
    ID_INCREMENT = "id_increment"
    OFFICIAL_INDEX = "official_index"
    PROBING = "probing"


@dataclass(frozen=True)
class DiscoveryResult:
    """Outcome of discovering a single candidate release."""

    release: ReleaseInfo
    strategy: DiscoveryStrategy
    confidence: float  # 0.0–1.0
    metadata: dict[str, object] = field(default_factory=dict)


@runtime_checkable
class ScraperProtocol(Protocol):
    """Minimal scraper interface required by the discovery service."""

    async def fetch_page_raw_text(self, url: str) -> str | None:
        """Fetch a URL and return its raw text content."""
        ...


class ReleaseDiscoveryService:
    """Discover Salesforce releases that need processing.

    Replaces the fragile ``release_id + 2`` heuristic in
    ``main.detect_new_release`` with a structured, testable service that
    tries content comparison first and falls back to the ID increment
    strategy.

    Args:
        scraper: Scraper capable of ``fetch_page_raw_text``.
            If ``None``, only non-network strategies are used.
        known_releases: Ordered list of known releases.  Defaults to
            ``config.KNOWN_RELEASES``.
        releases_dir: Root directory for release artifacts.
        feature_impact_url: Template for Feature Impact pages
            (must contain ``{release_id}``).
        event_bus: Event bus for emitting discovery metrics/events.
        probe_ids: Release-ID offsets to probe when running the
            content-comparison strategy (default ``[2, 4, 6]``).
    """

    #: Release-ID increments to probe (in order of preference)
    DEFAULT_PROBE_IDS: list[int] = [2, 4, 6]

    def __init__(
        self,
        scraper: Any = None,
        known_releases: list[ReleaseInfo] | None = None,
        releases_dir: str = RELEASES_DIR,
        feature_impact_url: str = FEATURE_IMPACT_URL,
        event_bus: EventBus | None = None,
        probe_ids: list[int] | None = None,
    ) -> None:
        self._scraper = scraper
        self._known_releases: list[ReleaseInfo] = (
            list(known_releases) if known_releases else list(KNOWN_RELEASES)
        )
        self._releases_dir = Path(releases_dir)
        self._feature_impact_url = feature_impact_url
        self._bus = event_bus or get_event_bus()
        self._probe_ids = probe_ids if probe_ids is not None else list(self.DEFAULT_PROBE_IDS)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_existing_releases(self) -> set[str]:
        """Return slugs for release dirs that already exist in ``releases/``.

        A directory counts as an "existing release" when it contains a
        ``.meta.json`` file.
        """
        if not self._releases_dir.exists():
            return set()
        return {
            d.name
            for d in self._releases_dir.iterdir()
            if d.is_dir() and (d / ".meta.json").exists()
        }

    async def discover(self) -> list[ReleaseInfo]:
        """Discover releases that need processing.

        Returns:
            A list with zero or one ``ReleaseInfo`` entries.  An empty list
            means no new release was detected.
        """
        existing_slugs = self.find_existing_releases()
        known_sorted = sorted(self._known_releases, key=lambda x: x.release_id, reverse=True)

        current = self._find_current_release(known_sorted, existing_slugs)

        if current is None:
            # No existing releases at all — process the latest known release.
            return self._first_unprocessed(known_sorted, existing_slugs)

        # Strategy 1: content comparison — requires a scraper for verification.
        # When the scraper is available this is the authoritative strategy:
        # * content differs  → new release found
        # * identical / fetch failed → no new release (do NOT fall through
        #   to the unverified ID-increment heuristic, per original behaviour)
        if self._scraper is not None:
            result = await self._discover_via_content_comparison(current, existing_slugs)
            if result is not None:
                await self._emit_result(result)
                return [result.release]
            await self._emit_completed(strategy=None, count=0)
            return []

        # Strategy 2: ID increment heuristic (no network verification).
        # Only used when no scraper is available — cannot verify content.
        result = self._discover_via_id_increment(current, existing_slugs)
        if result is not None:
            await self._emit_result(result)
            return [result.release]
        await self._emit_completed(strategy=None, count=0)
        return []

    # ------------------------------------------------------------------
    # Strategy helpers
    # ------------------------------------------------------------------

    def _find_current_release(
        self, known_sorted: list[ReleaseInfo], existing_slugs: set[str]
    ) -> ReleaseInfo | None:
        """Find the most-recent known release that already exists on disk."""
        for r in known_sorted:
            if r.slug in existing_slugs:
                return r
        return None

    def _first_unprocessed(
        self, known_sorted: list[ReleaseInfo], existing_slugs: set[str]
    ) -> list[ReleaseInfo]:
        """Return the latest known release that has not been processed yet."""
        for r in known_sorted:
            if r.slug not in existing_slugs:
                logger.info("No releases in repo, processing latest known: %s", r.name)
                return [r]
        logger.info("All known releases already exist in repo")
        return []

    async def _discover_via_content_comparison(
        self, current: ReleaseInfo, existing_slugs: set[str]
    ) -> DiscoveryResult | None:
        """Strategy 1: probe candidate release IDs and compare page content.

        Tries each offset in ``self._probe_ids``.  For each candidate that
        hasn't been processed yet, fetches the Feature Impact page for both
        *current* and *candidate* and compares their content.
        """
        if self._scraper is None:
            return None

        for step in self._probe_ids:
            next_id = current.release_id + step
            candidate = build_release_info(next_id)

            if candidate.slug in existing_slugs:
                logger.debug("Skipping %s — already exists", candidate.slug)
                continue

            differs, metadata = await self._compare_content(current, candidate)

            if differs:
                logger.info(
                    "New release detected via content comparison: %s (next_id=%d, step=%d)",
                    candidate.name,
                    next_id,
                    step,
                )
                return DiscoveryResult(
                    release=candidate,
                    strategy=DiscoveryStrategy.CONTENT_COMPARISON,
                    confidence=0.8,
                    metadata=metadata,
                )

        return None

    async def _compare_content(
        self, current: ReleaseInfo, candidate: ReleaseInfo
    ) -> tuple[bool, dict[str, object]]:
        """Fetch and compare Feature Impact pages for two releases.

        Returns:
            ``(content_differs, metadata_dict)``.
        """
        current_url = self._feature_impact_url.format(release_id=current.release_id)
        candidate_url = self._feature_impact_url.format(release_id=candidate.release_id)

        results = await asyncio.gather(
            self._scraper.fetch_page_raw_text(current_url),  # type: ignore[union-attr]
            self._scraper.fetch_page_raw_text(candidate_url),  # type: ignore[union-attr]
            return_exceptions=True,
        )
        current_text = results[0] if not isinstance(results[0], BaseException) else None
        candidate_text = results[1] if not isinstance(results[1], BaseException) else None

        metadata: dict[str, object] = {
            "current_url": current_url,
            "candidate_url": candidate_url,
            "current_length": len(current_text or ""),
            "candidate_length": len(candidate_text or ""),
            "probe_id": candidate.release_id,
            "step": candidate.release_id - current.release_id,
        }

        if not current_text or not candidate_text:
            logger.info(
                "Could not fetch pages for comparison (current=%s, candidate=%s)",
                bool(current_text),
                bool(candidate_text),
            )
            return False, metadata

        # Content is considered "the same" when lengths match and the first
        # 500 characters are identical.
        if len(current_text) == len(candidate_text) and current_text[:500] == candidate_text[:500]:
            logger.info(
                "Release %s not yet available (content identical to %s)",
                candidate.name,
                current.name,
            )
            return False, metadata

        return True, metadata

    def _discover_via_id_increment(
        self, current: ReleaseInfo, existing_slugs: set[str]
    ) -> DiscoveryResult | None:
        """Strategy 2 fallback: assume ``release_id + 2`` without fetching.

        This is the original heuristic.  Only used when content comparison
        could not determine a new release (e.g. scraper unavailable).
        """
        next_id = current.release_id + 2
        candidate = build_release_info(next_id)

        if candidate.slug in existing_slugs:
            return None

        logger.info(
            "New release detected via ID increment: %s (next_id=%d)",
            candidate.name,
            next_id,
        )
        return DiscoveryResult(
            release=candidate,
            strategy=DiscoveryStrategy.ID_INCREMENT,
            confidence=0.3,
            metadata={"probe_id": next_id, "step": 2},
        )

    # ------------------------------------------------------------------
    # Event / metric emission
    # ------------------------------------------------------------------

    async def _emit_result(self, result: DiscoveryResult) -> None:
        """Emit discovery metrics and release.detected events."""
        await self._bus.emit(
            "release.detected",
            {
                "slug": result.release.slug,
                "name": result.release.name,
                "release_id": result.release.release_id,
                "strategy": result.strategy.value,
                "confidence": result.confidence,
            },
            source="release_discovery",
        )
        await self._bus.emit(
            "discovery.completed",
            {
                "new_releases": 1,
                "strategy": result.strategy.value,
                "confidence": result.confidence,
            },
            source="release_discovery",
        )
        logger.info(
            "Discovery complete: %s (strategy=%s, confidence=%.2f)",
            result.release.name,
            result.strategy.value,
            result.confidence,
        )

    async def _emit_completed(self, strategy: str | None, count: int) -> None:
        """Emit discovery.completed metrics event."""
        await self._bus.emit(
            "discovery.completed",
            {"new_releases": count, "strategy": strategy},
            source="release_discovery",
        )
