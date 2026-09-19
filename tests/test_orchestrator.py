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
            "src.release_discovery.ReleaseDiscoveryService.discover",
            new_callable=AsyncMock,
            return_value=[mock_release],
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
        with patch(
            "src.release_discovery.ReleaseDiscoveryService.discover",
            new_callable=AsyncMock,
            return_value=[],
        ):
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

        with patch(
            "src.documentation_service.DocumentationService.update_readme_all",
            new_callable=AsyncMock,
        ):
            await orch._run_ai_reports([], None, result)
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_with_releases_completes(self) -> None:
        config = MagicMock()
        config.event_bus = MagicMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with (
            patch(
                "src.documentation_service.DocumentationService.update_readme_all",
                new_callable=AsyncMock,
            ),
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
            patch(
                "src.documentation_service.DocumentationService.update_readme_all",
                new_callable=AsyncMock,
            ),
            patch(
                "src.main.generate_ai_reports_async",
                new_callable=AsyncMock,
                side_effect=LLMError("fail"),
            ),
        ):
            await orch._run_ai_reports([MagicMock()], MagicMock(), result)
        assert result.status == "completed_with_errors"
        assert len(result.errors) == 1


class TestPipelineRunWithReleases:
    """Tests for PipelineOrchestrator.run() — branch coverage for decision paths."""

    @pytest.fixture
    def _base_config(self) -> MagicMock:
        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.scraper = MagicMock()
        config.scraper.__aenter__ = AsyncMock(return_value=None)
        config.scraper.__aexit__ = AsyncMock(return_value=None)
        config.impact_parser = MagicMock()
        config.generator = MagicMock()
        config.translator = MagicMock()
        config.llm = MagicMock()
        config.llm.__aenter__ = AsyncMock(return_value=None)
        config.llm.__aexit__ = AsyncMock(return_value=None)
        config.release_filter = None
        config.known_releases = None
        return config

    @pytest.mark.asyncio
    async def test_no_new_releases_updates_readme(self, _base_config: MagicMock) -> None:
        """When detection finds nothing, README is updated and status is no_new_releases."""
        _base_config.dry_run = False
        orch = PipelineOrchestrator(_base_config)
        with (
            patch.object(orch, "_detect_releases", new_callable=AsyncMock, return_value=[]),
            patch(
                "src.documentation_service.DocumentationService.update_readme_all",
                new_callable=AsyncMock,
            ),
        ):
            result = await orch.run()
        assert result.status == "no_new_releases"
        assert result.releases_processed == []

    @pytest.mark.asyncio
    async def test_dry_run_skips_ai_reports(self, _base_config: MagicMock) -> None:
        """Dry run with LLM still processes releases but skips AI reports."""
        _base_config.dry_run = True
        _base_config.llm = None
        _base_config.translator = None
        release = MagicMock()
        release.slug = "summer_26"
        release.name = "Summer '26"
        orch = PipelineOrchestrator(_base_config)
        with (
            patch.object(orch, "_detect_releases", new_callable=AsyncMock, return_value=[release]),
            patch.object(orch, "_process_release", new_callable=AsyncMock),
        ):
            result = await orch.run()
        assert result.status == "completed"
        assert result.releases_processed == ["summer_26"]

    @pytest.mark.asyncio
    async def test_no_llm_warns_and_runs_reports(self, _base_config: MagicMock) -> None:
        """Without LLM (not dry_run): warns, processes releases, runs AI reports with None."""
        _base_config.dry_run = False
        _base_config.llm = None
        _base_config.translator = None
        release = MagicMock()
        release.slug = "summer_26"
        release.name = "Summer '26"
        orch = PipelineOrchestrator(_base_config)
        with (
            patch.object(orch, "_detect_releases", new_callable=AsyncMock, return_value=[release]),
            patch.object(orch, "_process_release", new_callable=AsyncMock),
            patch(
                "src.documentation_service.DocumentationService.update_readme_all",
                new_callable=AsyncMock,
            ),
        ):
            result = await orch.run()
        assert result.status == "completed"
        assert result.releases_processed == ["summer_26"]

    @pytest.mark.asyncio
    async def test_with_llm_runs_full_flow(self, _base_config: MagicMock) -> None:
        """With LLM present (not dry_run): full pipeline including AI reports."""
        _base_config.dry_run = False
        release = MagicMock()
        release.slug = "summer_26"
        release.name = "Summer '26"
        orch = PipelineOrchestrator(_base_config)
        with (
            patch.object(orch, "_detect_releases", new_callable=AsyncMock, return_value=[release]),
            patch.object(orch, "_process_release", new_callable=AsyncMock),
            patch(
                "src.documentation_service.DocumentationService.update_readme_all",
                new_callable=AsyncMock,
            ),
            patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
            patch("src.orchestrator.set_pipeline_status"),
        ):
            result = await orch.run()
        assert result.status == "completed"
        assert result.releases_processed == ["summer_26"]


class TestProcessReleaseBranches:
    """Test _process_release with dry_run True/False."""

    @pytest.mark.asyncio
    async def test_dry_run_skips_enrich(self) -> None:
        """dry_run=True: skip enrich_meta_with_classification."""
        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.dry_run = True
        release = MagicMock()
        release.slug = "summer_26"
        release.name = "Summer '26"

        orch = PipelineOrchestrator(config)
        with (
            patch("src.main.process_single_release", new_callable=AsyncMock),
            patch(
                "src.main.enrich_meta_with_classification", new_callable=AsyncMock
            ) as mock_enrich,
        ):
            await orch._process_release(release, MagicMock(), MagicMock(), MagicMock(), None, None)
        mock_enrich.assert_not_called()

    @pytest.mark.asyncio
    async def test_not_dry_run_calls_enrich(self) -> None:
        """dry_run=False: enrich_meta_with_classification is called."""
        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.dry_run = False
        release = MagicMock()
        release.slug = "summer_26"
        release.name = "Summer '26"

        orch = PipelineOrchestrator(config)
        with (
            patch("src.main.process_single_release", new_callable=AsyncMock),
            patch(
                "src.main.enrich_meta_with_classification", new_callable=AsyncMock
            ) as mock_enrich,
        ):
            await orch._process_release(release, MagicMock(), MagicMock(), MagicMock(), None, None)
        mock_enrich.assert_called_once()
