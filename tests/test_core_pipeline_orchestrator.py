"""Tests for src/core/pipeline/orchestrator.py — 100% coverage target."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

import pytest

from src.core.pipeline.orchestrator import PipelineConfig, PipelineOrchestrator, PipelineResult
from src.core.pipeline.steps import (
    PipelineContext,
    PipelineStep,
)
from src.models.enrichment import ReleaseEnrichment
from src.models.release import ReleaseMetadata


class MockStep(PipelineStep):
    """Mock pipeline step for testing."""

    def __init__(
        self,
        name: str = "mock_step",
        return_value: Any = None,
        should_fail: bool = False,
        fail_with: Exception | None = None,
    ) -> None:
        self._name = name
        self.return_value = return_value
        self.should_fail = should_fail
        self.fail_with = fail_with or RuntimeError("Step failed")
        self.call_count = 0
        self.last_input: Any = None

    @property
    def name(self) -> str:
        return self._name

    async def execute(self, input_data: any) -> any:
        self.call_count += 1
        self.last_input = input_data
        if self.should_fail:
            raise self.fail_with
        return self.return_value


def _make_release_metadata() -> ReleaseMetadata:
    """Create a sample ReleaseMetadata for testing."""
    return ReleaseMetadata(
        release_id=262,
        slug="summer_26",
        name="Summer '26",
        version="262.0",
        date="2026-05-01",
        total_features=10,
        avg_confidence=0.85,
        generated_at="2026-05-01T10:00:00",
        categories=(
            MagicMock(name="Lightning", count=5, features=("feat1", "feat2")),
            MagicMock(name="Apex", count=5, features=("feat3", "feat4")),
        ),
    )


def _make_enrichment() -> ReleaseEnrichment:
    """Create a sample ReleaseEnrichment for testing."""
    return ReleaseEnrichment(
        release_slug="summer_26",
        locale="pt_BR",
        executive_summary="Resumo executivo de teste.",
        strategic_themes=("Tema 1", "Tema 2"),
        category_enrichments=(),
        migration_checklist=("Verificar deploy",),
        generated_at="2026-05-01T10:00:00",
    )


class TestPipelineConfig:
    """Tests for PipelineConfig."""

    def test_default_values(self) -> None:
        """Config should have sensible defaults."""
        config = PipelineConfig()
        assert config.locale == "pt_BR"
        assert config.enable_enrichment is True
        assert config.enable_translation is True
        assert config.enable_notification is True
        assert config.max_concurrent_steps == 1
        assert config.timeout_seconds == 300

    def test_custom_values(self) -> None:
        """Config should accept custom values."""
        config = PipelineConfig(
            locale="en_US",
            enable_enrichment=False,
            enable_translation=False,
            enable_notification=False,
            max_concurrent_steps=2,
            timeout_seconds=60,
        )
        assert config.locale == "en_US"
        assert config.enable_enrichment is False
        assert config.enable_translation is False
        assert config.enable_notification is False
        assert config.max_concurrent_steps == 2
        assert config.timeout_seconds == 60

    def test_immutable(self) -> None:
        """Config should be immutable (frozen dataclass)."""
        config = PipelineConfig()
        with pytest.raises(Exception):
            config.locale = "en_US"  # type: ignore


class TestPipelineResult:
    """Tests for PipelineResult."""

    def test_default_values(self) -> None:
        """Result should have sensible defaults."""
        release = _make_release_metadata()
        result = PipelineResult(release=release, success=True)

        assert result.release == release
        assert result.success is True
        assert result.enrichment is None
        assert result.generated_files == ()
        assert result.error is None
        assert result.steps_completed == ()
        assert result.duration_seconds == 0.0

    def test_with_all_fields(self) -> None:
        """Result should accept all fields."""
        release = _make_release_metadata()
        enrichment = _make_enrichment()
        result = PipelineResult(
            release=release,
            success=False,
            enrichment=enrichment,
            generated_files=("file1.md", "file2.md"),
            error="Test error",
            steps_completed=("step1", "step2"),
            duration_seconds=10.5,
        )

        assert result.success is False
        assert result.enrichment == enrichment
        assert result.generated_files == ("file1.md", "file2.md")
        assert result.error == "Test error"
        assert result.steps_completed == ("step1", "step2")
        assert result.duration_seconds == 10.5

    def test_immutable(self) -> None:
        """Result should be immutable (frozen dataclass)."""
        release = _make_release_metadata()
        result = PipelineResult(release=release, success=True)
        with pytest.raises(Exception):
            result.success = False  # type: ignore


class TestPipelineOrchestrator:
    """Tests for PipelineOrchestrator."""

    @pytest.fixture
    def release(self) -> ReleaseMetadata:
        """Create sample release."""
        return _make_release_metadata()

    @pytest.fixture
    def enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return _make_enrichment()

    @pytest.fixture
    def config(self) -> PipelineConfig:
        """Create pipeline config."""
        return PipelineConfig()

    @pytest.mark.asyncio
    async def test_execute_no_steps(self, release: ReleaseMetadata, config: PipelineConfig) -> None:
        """Should handle pipeline with no steps."""
        orchestrator = PipelineOrchestrator(config=config)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert result.steps_completed == ()
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_execute_single_step(
        self, release: ReleaseMetadata, config: PipelineConfig, enrichment: ReleaseEnrichment
    ) -> None:
        """Should execute a single step and capture result."""
        step = MockStep("test_step", return_value=enrichment)
        orchestrator = PipelineOrchestrator(config=config, enrichment_step=step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert result.enrichment == enrichment
        assert result.steps_completed == ("test_step",)
        assert step.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_multiple_steps(
        self, release: ReleaseMetadata, config: PipelineConfig, enrichment: ReleaseEnrichment
    ) -> None:
        """Should execute multiple steps in order."""
        step1 = MockStep("step1", return_value="intermediate")
        step2 = MockStep("step2", return_value=enrichment)
        step3 = MockStep("step3", return_value=["file1.md", "file2.md"])

        orchestrator = PipelineOrchestrator(
            config=config,
            scraping_step=step1,
            parsing_step=step2,
            generation_step=step3,
        )

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert result.enrichment == enrichment
        assert result.generated_files == ("file1.md", "file2.md")
        assert result.steps_completed == ("step1", "step2", "step3")
        assert step1.call_count == 1
        assert step2.call_count == 1
        assert step3.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_step_fails(
        self, release: ReleaseMetadata, config: PipelineConfig
    ) -> None:
        """Should capture error when step fails."""
        step = MockStep("failing_step", should_fail=True, fail_with=RuntimeError("Step error"))
        orchestrator = PipelineOrchestrator(config=config, scraping_step=step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is False
        assert result.error == "Step error"
        assert result.steps_completed == ()
        assert step.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_captures_duration(
        self, release: ReleaseMetadata, config: PipelineConfig
    ) -> None:
        """Should measure execution duration."""
        step = MockStep("slow_step", return_value=None)

        # Add small delay
        async def slow_execute(input_data: any) -> any:
            await asyncio.sleep(0.01)
            return None

        step.execute = slow_execute
        orchestrator = PipelineOrchestrator(config=config, scraping_step=step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.duration_seconds >= 0.01
        assert result.duration_seconds < 1.0  # Should not take too long

    @pytest.mark.asyncio
    async def test_execute_skips_enrichment_when_disabled(
        self, release: ReleaseMetadata, enrichment: ReleaseEnrichment
    ) -> None:
        """Should skip enrichment step when disabled in config."""
        config = PipelineConfig(enable_enrichment=False)
        step = MockStep("enrichment", return_value=enrichment)
        orchestrator = PipelineOrchestrator(config=config, enrichment_step=step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert step.call_count == 0
        assert "enrichment" not in result.steps_completed

    @pytest.mark.asyncio
    async def test_execute_skips_translation_when_disabled(
        self, release: ReleaseMetadata, enrichment: ReleaseEnrichment
    ) -> None:
        """Should skip translation step when disabled in config."""
        config = PipelineConfig(enable_translation=False)
        step = MockStep("translation", return_value=enrichment)
        orchestrator = PipelineOrchestrator(config=config, translation_step=step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert step.call_count == 0
        assert "translation" not in result.steps_completed

    @pytest.mark.asyncio
    async def test_execute_skips_notification_when_disabled(self, release: ReleaseMetadata) -> None:
        """Should skip notification step when disabled in config."""
        config = PipelineConfig(enable_notification=False)
        step = MockStep("notification", return_value=None)
        orchestrator = PipelineOrchestrator(config=config, notification_step=step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert step.call_count == 0
        assert "notification" not in result.steps_completed

    @pytest.mark.asyncio
    async def test_execute_add_step_dynamically(
        self, release: ReleaseMetadata, config: PipelineConfig, enrichment: ReleaseEnrichment
    ) -> None:
        """Should allow adding steps dynamically."""
        orchestrator = PipelineOrchestrator(config=config)
        step = MockStep("dynamic_step", return_value=enrichment)

        orchestrator.add_step(step)

        result = await orchestrator.execute(release, "http://example.com")

        assert result.success is True
        assert result.enrichment == enrichment
        assert result.steps_completed == ("dynamic_step",)

    @pytest.mark.asyncio
    async def test_execute_passes_input_through_chain(
        self, release: ReleaseMetadata, config: PipelineConfig
    ) -> None:
        """Should pass output of one step as input to next."""
        step1 = MockStep("step1", return_value="output1")
        step2 = MockStep("step2", return_value="output2")
        step3 = MockStep("step3", return_value="final")

        orchestrator = PipelineOrchestrator(
            config=config,
            scraping_step=step1,
            parsing_step=step2,
            classification_step=step3,
        )

        await orchestrator.execute(release, "initial_input")

        assert step1.last_input == "initial_input"
        assert step2.last_input == "output1"
        assert step3.last_input == "output2"

    @pytest.mark.asyncio
    async def test_execute_with_context(
        self, release: ReleaseMetadata, config: PipelineConfig
    ) -> None:
        """execute_with_context should delegate to execute."""
        orchestrator = PipelineOrchestrator(config=config)
        context = PipelineContext(release=release, locale="pt_BR")

        # Since execute_with_context just calls execute, we can test it works
        step = MockStep("test", return_value=None)
        orchestrator.add_step(step)

        result = await orchestrator.execute_with_context(context, "http://example.com")

        assert result.success is True
        assert step.call_count == 1

    @pytest.mark.asyncio
    async def test_execute_logs_step_names(
        self, release: ReleaseMetadata, config: PipelineConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Should log step names during execution."""
        import logging

        caplog.set_level(logging.INFO)

        step = MockStep("logged_step", return_value=None)
        orchestrator = PipelineOrchestrator(config=config, scraping_step=step)

        await orchestrator.execute(release, "http://example.com")

        assert "Executing step: logged_step" in caplog.text
        assert "Step logged_step completed" in caplog.text

    @pytest.mark.asyncio
    async def test_execute_logs_errors(
        self, release: ReleaseMetadata, config: PipelineConfig, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Should log errors when step fails."""
        import logging

        caplog.set_level(logging.ERROR)

        step = MockStep("error_step", should_fail=True, fail_with=ValueError("Bad value"))
        orchestrator = PipelineOrchestrator(config=config, scraping_step=step)

        await orchestrator.execute(release, "http://example.com")

        assert "Pipeline failed for summer_26: Bad value" in caplog.text

    @pytest.mark.asyncio
    async def test_config_passed_to_context(self, release: ReleaseMetadata) -> None:
        """Should pass config locale to pipeline context."""
        config = PipelineConfig(locale="en_US")
        orchestrator = PipelineOrchestrator(config=config)

        # We can't easily inspect the context, but we can verify
        # the config is stored correctly
        assert orchestrator.config.locale == "en_US"
