"""Tests for src/orchestrator.py — 100% coverage target."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.orchestrator import PipelineOrchestrator, PipelineResult


class TestPipelineResult:
    """PipelineResult dataclass."""

    def test_fields(self) -> None:
        r = PipelineResult(releases_processed=[], errors=[], status="running")
        assert r.status == "running"
        assert r.releases_processed == []


class TestOrchestratorInit:
    """PipelineOrchestrator.__init__: event bus wiring."""

    def test_gets_event_bus(self) -> None:
        config = MagicMock()
        config.event_bus = None
        with patch("src.orchestrator.get_event_bus") as mock_bus:
            PipelineOrchestrator(config)
            assert mock_bus.called


class TestDetectReleases:
    """_detect_releases: filter by slug, detect new, no filter."""

    @pytest.mark.asyncio
    async def test_with_filter_match(self) -> None:
        release_info = MagicMock()
        release_info.slug = "summer_26"

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = "summer_26"
        config.known_releases = [release_info]

        orch = PipelineOrchestrator(config)
        result = await orch._detect_releases(MagicMock())
        assert len(result) == 1
        assert result[0].slug == "summer_26"

    @pytest.mark.asyncio
    async def test_with_filter_no_match(self) -> None:
        release_info = MagicMock()
        release_info.slug = "summer_26"

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = "nonexistent"
        config.known_releases = [release_info]

        orch = PipelineOrchestrator(config)
        result = await orch._detect_releases(MagicMock())
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_no_filter_with_new_release(self) -> None:
        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = None
        config.known_releases = None

        mock_release = MagicMock()
        mock_release.slug = "summer_26"

        orch = PipelineOrchestrator(config)
        with patch(
            "src.main.detect_new_release", new_callable=AsyncMock, return_value=mock_release
        ):
            result = await orch._detect_releases(MagicMock())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_no_filter_no_new_release(self) -> None:
        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = None
        config.known_releases = None

        orch = PipelineOrchestrator(config)
        with patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=None):
            result = await orch._detect_releases(MagicMock())
        assert len(result) == 0


class TestRunAIReports:
    """_run_ai_reports: LLM integration, error handling."""

    @pytest.mark.asyncio
    async def test_no_releases_completes(self) -> None:
        from src.orchestrator import PipelineOrchestrator, PipelineResult

        config = MagicMock()
        config.event_bus = MagicMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.release_docs.update_readme_all", new_callable=AsyncMock):
            await orch._run_ai_reports([], None, result)
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_with_releases_completes(self) -> None:
        config = MagicMock()
        config.event_bus = MagicMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with (
            patch("src.release_docs.update_readme_all", new_callable=AsyncMock),
            patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
        ):
            await orch._run_ai_reports([MagicMock()], MagicMock(), result)
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_llm_error_sets_completed_with_errors(self) -> None:
        from src.exceptions import LLMError
        from src.orchestrator import PipelineOrchestrator, PipelineResult

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with (
            patch("src.release_docs.update_readme_all", new_callable=AsyncMock),
            patch(
                "src.main.generate_ai_reports_async",
                new_callable=AsyncMock,
                side_effect=LLMError("fail"),
            ),
        ):
            await orch._run_ai_reports([MagicMock()], MagicMock(), result)
        assert result.status == "completed_with_errors"
        assert len(result.errors) == 1
