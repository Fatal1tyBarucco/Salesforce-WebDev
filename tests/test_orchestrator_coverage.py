"""Tests for src/orchestrator.py to reach 95% coverage."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import KNOWN_RELEASES, ReleaseInfo
from src.exceptions import GitHubError, LLMError, NotificationError
from src.orchestrator import PipelineOrchestrator, PipelineResult


@pytest.fixture(autouse=True)
def isolated_cwd(tmp_path: Path):
    """Run every test in a temp cwd."""
    original = Path.cwd()
    os.chdir(tmp_path)
    try:
        yield tmp_path
    finally:
        os.chdir(original)


def _make_config(
    dry_run: bool = True,
    llm: Any = None,
    scraper: Any = None,
    impact_parser: Any = None,
    generator: Any = None,
    translator: Any = None,
    release_filter: str | None = None,
) -> Any:
    """Create a mock config object."""
    config = MagicMock()
    config.dry_run = dry_run
    config.llm = llm
    config.scraper = scraper
    config.impact_parser = impact_parser
    config.generator = generator
    config.translator = translator
    config.release_filter = release_filter
    config.known_releases = list(KNOWN_RELEASES)
    config.event_bus = AsyncMock()  # Mock event bus to avoid real emissions
    return config


def _make_scraper() -> MagicMock:
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


def _make_parser() -> MagicMock:
    return MagicMock()


def _make_generator() -> MagicMock:
    return MagicMock()


def _make_translator() -> MagicMock:
    return MagicMock()


def _make_llm() -> MagicMock:
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=False)
    return mock


class TestPipelineOrchestratorInit:
    """Tests for PipelineOrchestrator initialization."""

    def test_init_sets_attributes(self) -> None:
        """Test __init__ sets all attributes."""
        config = _make_config()
        orch = PipelineOrchestrator(config)
        assert orch._config is config
        assert orch._bus is not None


class TestPipelineOrchestratorRun:
    """Tests for PipelineOrchestrator.run method."""

    @pytest.mark.asyncio
    async def test_run_dry_run_no_releases(self, tmp_path: Path) -> None:
        """Test run in dry_run with no new releases."""
        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()

        config = _make_config(dry_run=True)
        config.scraper = _make_scraper()
        config.impact_parser = _make_parser()
        config.generator = _make_generator()
        config.translator = _make_translator()
        config.known_releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]

        orch = PipelineOrchestrator(config)

        # Mock _detect_releases to return empty
        with patch.object(orch, "_detect_releases", new=AsyncMock(return_value=[])):
            with patch("src.documentation_service.DocumentationService") as mock_doc:
                mock_doc.return_value.update_readme_all = AsyncMock()
                result = await orch.run()

        assert result.status == "no_new_releases"
        assert result.releases_processed == []

    @pytest.mark.asyncio
    async def test_run_with_releases_dry_run(self, tmp_path: Path) -> None:
        """Test run with releases in dry_run mode."""
        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()

        config = _make_config(dry_run=True)
        config.scraper = _make_scraper()
        config.impact_parser = _make_parser()
        config.generator = _make_generator()
        config.translator = _make_translator()
        config.known_releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]

        orch = PipelineOrchestrator(config)

        mock_release = ReleaseInfo(name="Test", release_id=262, slug="test")

        with patch.object(orch, "_detect_releases", new=AsyncMock(return_value=[mock_release])):
            with patch.object(orch, "_process_release", new=AsyncMock()) as mock_process:
                with patch("src.documentation_service.DocumentationService") as mock_doc:
                    mock_doc.return_value.update_readme_all = AsyncMock()
                    result = await orch.run()

        assert result.status == "completed"
        assert "test" in result.releases_processed
        mock_process.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_with_llm_and_releases(self, tmp_path: Path) -> None:
        """Test run with LLM and releases."""
        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()

        config = _make_config(dry_run=False)
        config.scraper = _make_scraper()
        config.impact_parser = _make_parser()
        config.generator = _make_generator()
        config.translator = _make_translator()
        config.llm = _make_llm()
        config.known_releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]

        orch = PipelineOrchestrator(config)

        mock_release = ReleaseInfo(name="Test", release_id=262, slug="test")

        with patch.object(orch, "_detect_releases", new=AsyncMock(return_value=[mock_release])):
            with patch.object(orch, "_process_release", new=AsyncMock()) as mock_process:
                with patch("src.main.generate_ai_reports_async", new=AsyncMock()) as mock_ai:
                    with patch("src.documentation_service.DocumentationService") as mock_doc:
                        mock_doc.return_value.update_readme_all = AsyncMock()
                        result = await orch.run()

        assert result.status == "completed"
        assert "test" in result.releases_processed
        mock_process.assert_awaited_once()
        mock_ai.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_without_llm_not_dry_run(self, tmp_path: Path) -> None:
        """Test run without LLM and not dry_run still runs AI reports."""
        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()

        config = _make_config(dry_run=False)
        config.scraper = _make_scraper()
        config.impact_parser = _make_parser()
        config.generator = _make_generator()
        config.translator = _make_translator()
        config.llm = None
        config.known_releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]

        orch = PipelineOrchestrator(config)

        mock_release = ReleaseInfo(name="Test", release_id=262, slug="test")

        with patch.object(orch, "_detect_releases", new=AsyncMock(return_value=[mock_release])):
            with patch.object(orch, "_process_release", new=AsyncMock()):
                with patch("src.documentation_service.DocumentationService") as mock_doc:
                    mock_doc.return_value.update_readme_all = AsyncMock()
                    result = await orch.run()

        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_run_error_handling(self, tmp_path: Path) -> None:
        """Test run handles exceptions in _run_ai_reports."""
        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()

        config = _make_config(dry_run=False)
        config.scraper = _make_scraper()
        config.impact_parser = _make_parser()
        config.generator = _make_generator()
        config.translator = _make_translator()
        config.llm = _make_llm()
        config.known_releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]

        orch = PipelineOrchestrator(config)

        mock_release = ReleaseInfo(name="Test", release_id=262, slug="test")

        with patch.object(orch, "_detect_releases", new=AsyncMock(return_value=[mock_release])):
            with patch.object(orch, "_process_release", new=AsyncMock()):
                with patch("src.orchestrator.set_pipeline_status", new=AsyncMock()):
                    with patch.object(orch._bus, "emit", new=AsyncMock()):
                        with patch(
                            "src.main.generate_ai_reports_async",
                            new=AsyncMock(side_effect=LLMError("AI reports failed")),
                        ):
                            result = await orch.run()

        assert result.status == "completed_with_errors"
        assert len(result.errors) > 0


class TestPipelineOrchestratorDetectReleases:
    """Tests for _detect_releases method."""

    @pytest.mark.asyncio
    async def test_detect_releases_with_filter(self) -> None:
        """Test _detect_releases with release_filter."""
        config = _make_config(release_filter="summer_26")
        config.known_releases = [
            ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26"),
            ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26"),
        ]

        orch = PipelineOrchestrator(config)
        mock_scraper = _make_scraper()

        releases = await orch._detect_releases(mock_scraper)

        assert len(releases) == 1
        assert releases[0].slug == "summer_26"

    @pytest.mark.asyncio
    async def test_detect_releases_filter_not_found(self) -> None:
        """Test _detect_releases with filter not found."""
        config = _make_config(release_filter="nonexistent")
        config.known_releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]

        orch = PipelineOrchestrator(config)
        mock_scraper = _make_scraper()

        with patch.object(orch._bus, "emit", new=AsyncMock()):
            releases = await orch._detect_releases(mock_scraper)

        assert releases == []

    @pytest.mark.asyncio
    async def test_detect_releases_no_filter(self) -> None:
        """Test _detect_releases without filter."""
        config = _make_config()
        orch = PipelineOrchestrator(config)
        mock_scraper = _make_scraper()

        with patch("src.release_discovery.ReleaseDiscoveryService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.discover = AsyncMock(return_value=[])
            mock_service_class.return_value = mock_service

            releases = await orch._detect_releases(mock_scraper)

        assert releases == []


class TestPipelineOrchestratorProcessRelease:
    """Tests for _process_release method."""

    @pytest.mark.asyncio
    async def test_process_release_calls_process_single_release(self) -> None:
        """Test _process_release calls process_single_release."""
        config = _make_config(dry_run=False)
        orch = PipelineOrchestrator(config)

        release = ReleaseInfo(name="Test", release_id=262, slug="test")
        scraper = _make_scraper()
        impact_parser = _make_parser()
        generator = _make_generator()
        translator = _make_translator()
        llm = _make_llm()

        with patch("src.main.process_single_release", new=AsyncMock()) as mock_process:
            with patch("src.main.enrich_meta_with_classification", new=AsyncMock()) as mock_enrich:
                with patch.object(orch._bus, "emit", new=AsyncMock()):
                    await orch._process_release(
                        release, scraper, impact_parser, generator, translator, llm
                    )

        mock_process.assert_awaited_once_with(
            release, scraper, impact_parser, generator, translator, False, llm
        )
        mock_enrich.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_process_release_dry_run_skips_enrich(self) -> None:
        """Test _process_release skips enrich in dry_run."""
        config = _make_config(dry_run=True)
        orch = PipelineOrchestrator(config)

        release = ReleaseInfo(name="Test", release_id=262, slug="test")
        scraper = _make_scraper()
        impact_parser = _make_parser()
        generator = _make_generator()
        translator = _make_translator()
        llm = _make_llm()

        with patch("src.main.process_single_release", new=AsyncMock()) as mock_process:
            with patch("src.main.enrich_meta_with_classification", new=AsyncMock()) as mock_enrich:
                with patch.object(orch._bus, "emit", new=AsyncMock()):
                    await orch._process_release(
                        release, scraper, impact_parser, generator, translator, llm
                    )

        mock_process.assert_awaited_once()
        mock_enrich.assert_not_awaited()


class TestPipelineOrchestratorRunAiReports:
    """Tests for _run_ai_reports method."""

    @pytest.mark.asyncio
    async def test_run_ai_reports_llm_none(self) -> None:
        """Test _run_ai_reports when LLM is None."""
        config = _make_config(llm=None)
        orch = PipelineOrchestrator(config)

        releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.documentation_service.DocumentationService") as mock_doc:
            mock_doc.return_value.update_readme_all = AsyncMock()
            with patch("src.orchestrator.logger") as mock_logger:
                await orch._run_ai_reports(releases, None, result)

        assert result.status == "completed"
        mock_logger.info.assert_called_with("LLM not available — skipping AI reports")

    @pytest.mark.asyncio
    async def test_run_ai_reports_success(self, tmp_path: Path) -> None:
        """Test _run_ai_reports success."""
        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()

        config = _make_config()
        orch = PipelineOrchestrator(config)

        releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]
        llm = _make_llm()
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.documentation_service.DocumentationService") as mock_doc:
            mock_doc.return_value.update_readme_all = AsyncMock()
            with patch("src.main.generate_ai_reports_async", new=AsyncMock()) as mock_ai:
                await orch._run_ai_reports(releases, llm, result)

        assert result.status == "completed"
        mock_ai.assert_awaited_once_with(releases, llm=llm)

    @pytest.mark.asyncio
    async def test_run_ai_reports_llm_error(self) -> None:
        """Test _run_ai_reports handles LLMError."""
        config = _make_config()
        orch = PipelineOrchestrator(config)

        releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]
        llm = _make_llm()
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.documentation_service.DocumentationService") as mock_doc:
            mock_doc.return_value.update_readme_all = AsyncMock()
            with patch(
                "src.main.generate_ai_reports_async",
                new=AsyncMock(side_effect=LLMError("LLM failed")),
            ):
                with patch("src.orchestrator.logger"):
                    with patch.object(orch._bus, "emit", new=AsyncMock()):
                        await orch._run_ai_reports(releases, llm, result)

        assert result.status == "completed_with_errors"
        assert len(result.errors) == 1
        assert "LLM failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_run_ai_reports_github_error(self) -> None:
        """Test _run_ai_reports handles GitHubError."""
        config = _make_config()
        orch = PipelineOrchestrator(config)

        releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]
        llm = _make_llm()
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.documentation_service.DocumentationService") as mock_doc:
            mock_doc.return_value.update_readme_all = AsyncMock()
            with patch(
                "src.main.generate_ai_reports_async",
                new=AsyncMock(side_effect=GitHubError("GitHub failed")),
            ):
                with patch.object(orch._bus, "emit", new=AsyncMock()):
                    await orch._run_ai_reports(releases, llm, result)

        assert result.status == "completed_with_errors"

    @pytest.mark.asyncio
    async def test_run_ai_reports_notification_error(self) -> None:
        """Test _run_ai_reports handles NotificationError."""
        config = _make_config()
        orch = PipelineOrchestrator(config)

        releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]
        llm = _make_llm()
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.documentation_service.DocumentationService") as mock_doc:
            mock_doc.return_value.update_readme_all = AsyncMock()
            with patch(
                "src.main.generate_ai_reports_async",
                new=AsyncMock(side_effect=NotificationError("Notif failed")),
            ):
                with patch.object(orch._bus, "emit", new=AsyncMock()):
                    await orch._run_ai_reports(releases, llm, result)

        assert result.status == "completed_with_errors"

    @pytest.mark.asyncio
    async def test_run_ai_reports_os_error(self) -> None:
        """Test _run_ai_reports handles OSError."""
        config = _make_config()
        orch = PipelineOrchestrator(config)

        releases = [ReleaseInfo(name="Test", release_id=262, slug="test")]
        llm = _make_llm()
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.documentation_service.DocumentationService") as mock_doc:
            mock_doc.return_value.update_readme_all = AsyncMock()
            with patch(
                "src.main.generate_ai_reports_async",
                new=AsyncMock(side_effect=OSError("OS failed")),
            ):
                with patch.object(orch._bus, "emit", new=AsyncMock()):
                    await orch._run_ai_reports(releases, llm, result)

        assert result.status == "completed_with_errors"


class TestPipelineResult:
    """Tests for PipelineResult dataclass."""

    def test_init(self) -> None:
        """Test PipelineResult initialization."""
        result = PipelineResult(
            releases_processed=["test1", "test2"],
            errors=["error1"],
            status="completed",
        )
        assert result.releases_processed == ["test1", "test2"]
        assert result.errors == ["error1"]
        assert result.status == "completed"

    def test_init_empty(self) -> None:
        """Test PipelineResult with empty values."""
        result = PipelineResult(releases_processed=[], errors=[], status="running")
        assert result.releases_processed == []
        assert result.errors == []
        assert result.status == "running"
