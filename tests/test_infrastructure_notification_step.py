"""Tests for src/infrastructure/notification_step.py — 100% coverage target."""

from __future__ import annotations


import pytest

from src.infrastructure.notification_step import (
    NotificationStepAdapter,
    create_notification_step,
)
from src.infrastructure.messaging import NotificationAdapter
from src.models.enrichment import ReleaseEnrichment


class MockNotificationAdapter(NotificationAdapter):
    """Mock notification adapter for testing."""

    def __init__(self, name: str = "mock") -> None:
        self._name = name
        self.executed = False
        self.last_enrichment: ReleaseEnrichment | None = None

    @property
    def name(self) -> str:
        return self._name

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        self.executed = True
        self.last_enrichment = enrichment


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


class TestNotificationStepAdapter:
    """Tests for NotificationStepAdapter."""

    @pytest.fixture
    def mock_adapter(self) -> MockNotificationAdapter:
        """Create mock notification adapter."""
        return MockNotificationAdapter("test_adapter")

    @pytest.fixture
    def adapter(self, mock_adapter: MockNotificationAdapter) -> NotificationStepAdapter:
        """Create step adapter with mock."""
        return NotificationStepAdapter(mock_adapter)

    @pytest.fixture
    def enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return _make_enrichment()

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: NotificationStepAdapter) -> None:
        """Adapter name should include wrapped adapter name."""
        assert adapter.name == "notification_step_test_adapter"

    @pytest.mark.asyncio
    async def test_execute_delegates_to_wrapped_adapter(
        self,
        adapter: NotificationStepAdapter,
        mock_adapter: MockNotificationAdapter,
        enrichment: ReleaseEnrichment,
    ) -> None:
        """Execute should delegate to wrapped adapter."""
        await adapter.execute(enrichment)

        assert mock_adapter.executed is True
        assert mock_adapter.last_enrichment is enrichment

    @pytest.mark.asyncio
    async def test_execute_propagates_exception(
        self,
        adapter: NotificationStepAdapter,
        mock_adapter: MockNotificationAdapter,
        enrichment: ReleaseEnrichment,
    ) -> None:
        """Execute should propagate exceptions from wrapped adapter."""

        async def failing_execute(enrichment: ReleaseEnrichment) -> None:
            raise RuntimeError("Notification failed")

        mock_adapter.execute = failing_execute

        with pytest.raises(RuntimeError, match="Notification failed"):
            await adapter.execute(enrichment)


class TestCreateNotificationStep:
    """Tests for create_notification_step factory function."""

    @pytest.mark.asyncio
    async def test_returns_noop_when_no_adapters_configured(self) -> None:
        """Should return NoopNotificationStep when no adapters configured."""
        step = create_notification_step()

        assert step.name == "noop_notification"
        # Should not raise
        await step.execute(_make_enrichment())

    @pytest.mark.asyncio
    async def test_returns_composite_with_github_adapter(self) -> None:
        """Should return composite step with GitHub adapter when repo provided."""
        step = create_notification_step(github_repo="owner/repo", github_token="token123")

        assert "notification_step_" in step.name
        assert "github" in step.name.lower() or "composite" in step.name.lower()

    @pytest.mark.asyncio
    async def test_returns_composite_with_slack_adapter(self) -> None:
        """Should return composite step with Slack adapter when webhook provided."""
        step = create_notification_step(slack_webhook="https://hooks.slack.com/test")

        assert "notification_step_" in step.name
        assert "slack" in step.name.lower() or "composite" in step.name.lower()

    @pytest.mark.asyncio
    async def test_returns_composite_with_email_adapter(self) -> None:
        """Should return composite step with Email adapter when config provided."""
        step = create_notification_step(
            email_config={
                "smtp_host": "smtp.example.com",
                "username": "user",
                "password": "pass",
                "from_email": "test@example.com",
                "to_emails": ["dest@example.com"],
            }
        )

        assert "notification_step_" in step.name
        assert "email" in step.name.lower() or "composite" in step.name.lower()

    @pytest.mark.asyncio
    async def test_returns_composite_with_multiple_adapters(self) -> None:
        """Should return composite step with all configured adapters."""
        step = create_notification_step(
            github_repo="owner/repo",
            github_token="token123",
            slack_webhook="https://hooks.slack.com/test",
            email_config={
                "smtp_host": "smtp.example.com",
                "username": "user",
                "password": "pass",
                "from_email": "test@example.com",
                "to_emails": ["dest@example.com"],
            },
        )

        assert "notification_step_" in step.name
        assert "composite" in step.name.lower()

    @pytest.mark.asyncio
    async def test_composite_executes_all_adapters(self) -> None:
        """Composite step should execute all wrapped adapters."""
        github_mock = MockNotificationAdapter("github")
        slack_mock = MockNotificationAdapter("slack")

        # We can't easily test the real adapters without credentials,
        # but we can test the step adapter composition
        from src.infrastructure.messaging import CompositeNotificationAdapter

        composite = CompositeNotificationAdapter([github_mock, slack_mock])
        step = NotificationStepAdapter(composite)

        enrichment = _make_enrichment()
        await step.execute(enrichment)

        assert github_mock.executed is True
        assert slack_mock.executed is True
        assert github_mock.last_enrichment is enrichment
        assert slack_mock.last_enrichment is enrichment

    @pytest.mark.asyncio
    async def test_noop_step_name_property(self) -> None:
        """Noop step should have correct name."""
        step = create_notification_step()
        assert step.name == "noop_notification"


class TestNotificationStepAdapterEdgeCases:
    """Edge case tests for NotificationStepAdapter."""

    @pytest.mark.asyncio
    async def test_execute_with_none_enrichment_passes_to_adapter(self) -> None:
        """Execute with None passes None to wrapped adapter (no validation)."""
        mock_adapter = MockNotificationAdapter()
        adapter = NotificationStepAdapter(mock_adapter)

        # The adapter just delegates; validation is up to the wrapped adapter
        await adapter.execute(None)  # type: ignore[arg-type]
        assert mock_adapter.last_enrichment is None

    @pytest.mark.asyncio
    async def test_name_reflects_wrapped_adapter_name(self) -> None:
        """Name property should reflect wrapped adapter's name."""
        for name in ["github", "slack", "email", "custom_adapter"]:
            mock = MockNotificationAdapter(name)
            adapter = NotificationStepAdapter(mock)
            assert adapter.name == f"notification_step_{name}"
