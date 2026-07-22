"""Pipeline orchestrator — coordinates the full release-notes pipeline.

Encapsulates the detection → scraping → parsing → generation → AI → distribution
workflow that was previously inlined in ``main.run_pipeline``.

Usage::

    from src.orchestrator import PipelineOrchestrator
    from src.main import PipelineConfig

    config = PipelineConfig()
    orchestrator = PipelineOrchestrator(config)
    await orchestrator.run()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .config import KNOWN_RELEASES, ReleaseInfo
from .events import EventBus, get_event_bus
from .exceptions import GitHubError, LLMError, NotificationError
from .health import set_pipeline_status
from .logger import new_correlation_id

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Outcome of a pipeline run."""

    releases_processed: list[str]
    errors: list[str]
    status: str  # "completed" | "completed_with_errors" | "no_new_releases"


class PipelineOrchestrator:
    """Orchestrates the full release-notes pipeline.

    Args:
        config: Pipeline configuration (dependencies, flags).
    """

    def __init__(self, config: Any) -> None:
        self._config = config
        self._bus: EventBus = config.event_bus or get_event_bus()

    async def run(self) -> PipelineResult:
        """Execute the full pipeline.

        Returns:
            PipelineResult with processed releases, errors, and final status.
        """
        cid = new_correlation_id()
        logger.info("Starting pipeline (correlation_id=%s)", cid)
        set_pipeline_status("running")

        result = PipelineResult(releases_processed=[], errors=[], status="running")
        await self._bus.emit(
            "pipeline.started", {"dry_run": self._config.dry_run}, source="orchestrator"
        )

        scraper = self._config.scraper
        impact_parser = self._config.impact_parser
        generator = self._config.generator
        translator = self._config.translator
        llm = self._config.llm

        assert scraper is not None
        assert impact_parser is not None
        assert generator is not None
        assert translator is not None
        assert llm is not None

        if self._config.dry_run:
            logger.info("[DRY RUN] Modo simulacao ativado — nenhum arquivo sera escrito")

        releases = await self._detect_releases(scraper)
        if not releases:
            from .release_docs import _update_readme_all

            await _update_readme_all()
            result.status = "no_new_releases"
            await self._bus.emit("pipeline.completed", {"new_releases": 0}, source="orchestrator")
            return result

        async with scraper:
            async with llm:
                for release in releases:
                    await self._process_release(
                        release, scraper, impact_parser, generator, translator
                    )
                    result.releases_processed.append(release.slug)

                await self._run_ai_reports(releases, llm, result)

        set_pipeline_status(result.status)
        await self._bus.emit(
            "pipeline.completed",
            {"new_releases": len(releases), "status": result.status},
            source="orchestrator",
        )
        return result

    # ── Private pipeline stages ──────────────────────────────────

    async def _detect_releases(self, scraper: Any) -> list[ReleaseInfo]:
        """Detect which releases need processing."""
        release_filter = self._config.release_filter

        if release_filter:
            for r in KNOWN_RELEASES:
                if r.slug == release_filter:
                    return [r]
            logger.error("Release '%s' not found in KNOWN_RELEASES", release_filter)
            await self._bus.emit(
                "pipeline.error", {"error": "release not found"}, source="orchestrator"
            )
            return []

        from .main import detect_new_release

        new_release = await detect_new_release(scraper)
        if new_release:
            await self._bus.emit(
                "release.detected",
                {"slug": new_release.slug, "name": new_release.name},
                source="orchestrator",
            )
            return [new_release]

        return []

    async def _process_release(
        self,
        release: ReleaseInfo,
        scraper: Any,
        impact_parser: Any,
        generator: Any,
        translator: Any,
    ) -> None:
        """Process a single release: scrape, parse, generate files."""
        from .main import _enrich_meta_with_classification, _process_single_release

        await _process_single_release(
            release, scraper, impact_parser, generator, translator, self._config.dry_run
        )
        await self._bus.emit(
            "release.processed",
            {"slug": release.slug, "name": release.name},
            source="orchestrator",
        )

        if not self._config.dry_run:
            await _enrich_meta_with_classification(release, classifier=None)
            await self._bus.emit(
                "release.classified", {"slug": release.slug}, source="orchestrator"
            )

    async def _run_ai_reports(
        self, releases: list[ReleaseInfo], llm: Any, result: PipelineResult
    ) -> None:
        """Generate AI reports and update README."""
        from .main import _generate_ai_reports_async  # noqa: F811
        from .release_docs import _update_readme_all  # noqa: F811

        await _update_readme_all()

        try:
            await _generate_ai_reports_async(releases, llm=llm)
            result.status = "completed"
        except (LLMError, GitHubError, NotificationError, OSError) as e:
            logger.warning("Failed to generate AI reports: %s", e)
            result.errors.append(str(e))
            result.status = "completed_with_errors"
            await self._bus.emit("pipeline.error", {"error": str(e)}, source="orchestrator")
