"""Tests for src/infrastructure/messaging.py — 100% coverage target."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.messaging import (
    CompositeNotificationAdapter,
    EmailNotificationAdapter,
    EmailNotificationConfig,
    GitHubNotificationAdapter,
    GitHubNotificationConfig,
    NotificationAdapter,
    SlackNotificationAdapter,
    SlackNotificationConfig,
)
from src.models.enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
    ReleaseEnrichment,
)


class TestNotificationAdapter:
    """Tests for the abstract NotificationAdapter base class."""

    @pytest.mark.asyncio
    async def test_abstract_execute_raises_not_implemented(self) -> None:
        """Abstract execute should raise NotImplementedError."""
        adapter = NotificationAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.execute(MagicMock())

    @pytest.mark.asyncio
    async def test_abstract_send_raises_not_implemented(self) -> None:
        """Abstract send should raise NotImplementedError."""
        adapter = NotificationAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.send("message")

    def test_name_property(self) -> None:
        """Base adapter name property."""
        adapter = NotificationAdapter()
        assert adapter.name == "notification_adapter"


class TestGitHubNotificationConfig:
    """Tests for GitHubNotificationConfig."""

    def test_init_with_defaults(self) -> None:
        """Should initialize with default values."""
        config = GitHubNotificationConfig(repo="owner/repo", token="test_token")
        assert config.repo == "owner/repo"
        assert config.token == "test_token"
        assert config.issue_template == "release_notes"
        assert config.create_issue is True
        assert config.update_existing is True


class TestGitHubNotificationAdapter:
    """Tests for GitHubNotificationAdapter."""

    @pytest.fixture
    def config(self) -> GitHubNotificationConfig:
        """Create GitHub notification config."""
        return GitHubNotificationConfig(repo="owner/repo", token="test_token")

    @pytest.fixture
    def adapter(self, config: GitHubNotificationConfig) -> GitHubNotificationAdapter:
        """Create GitHub notification adapter."""
        return GitHubNotificationAdapter(config)

    @pytest.fixture
    def sample_enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary="Resumo executivo de teste.",
            strategic_themes=("Tema 1", "Tema 2"),
            category_enrichments=(
                CategoryEnrichment(
                    category_name="Lightning",
                    overview="Visão geral do Lightning.",
                    key_themes=("Tema Lightning",),
                    business_impact="Alto impacto",
                    adoption_guidance="Adotar imediatamente.",
                    risk_assessment="Baixo risco.",
                    feature_enrichments=(
                        FeatureEnrichment(
                            feature_name="Lightning Feature",
                            summary="Resumo da feature",
                            details="Detalhes completos",
                            business_context="Contexto negócio",
                            technical_context="Contexto técnico",
                            migration_notes="Notas migração",
                            related_features=("Outra feature",),
                            tags=("tag1",),
                            confidence=0.9,
                            locale="pt_BR",
                            generated_at="2026-05-01T10:00:00",
                        ),
                    ),
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            migration_checklist=("Verificar deploy", "Testar funcionalidade"),
            generated_at="2026-05-01T10:00:00",
        )

    def test_init_sets_properties(
        self, adapter: GitHubNotificationAdapter, config: GitHubNotificationConfig
    ) -> None:
        """Should initialize with correct properties."""
        assert adapter.config is config
        assert adapter._gh_adapter is None

    def test_name_property(self, adapter: GitHubNotificationAdapter) -> None:
        """Adapter name should be correct."""
        assert adapter.name == "github_notification"

    @pytest.mark.asyncio
    async def test_get_adapter_creates_github_operations_adapter(
        self, adapter: GitHubNotificationAdapter
    ) -> None:
        """_get_adapter should create GitHubOperationsAdapter."""
        with patch("src.infrastructure.github.GitHubOperationsAdapter") as mock_gh_ops:
            mock_adapter = MagicMock()
            mock_gh_ops.return_value = mock_adapter

            result = await adapter._get_adapter()

            assert result is mock_adapter
            mock_gh_ops.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_adapter_caches_adapter(self, adapter: GitHubNotificationAdapter) -> None:
        """_get_adapter should cache the adapter."""
        with patch("src.infrastructure.github.GitHubOperationsAdapter") as mock_gh_ops:
            mock_adapter = MagicMock()
            mock_gh_ops.return_value = mock_adapter

            result1 = await adapter._get_adapter()
            result2 = await adapter._get_adapter()

            assert result1 is result2
            mock_gh_ops.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_creates_issue(
        self, adapter: GitHubNotificationAdapter, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """execute should create GitHub issue."""
        mock_gh_adapter = AsyncMock()
        mock_gh_adapter.create_issue = AsyncMock(return_value={"number": 123})

        with patch.object(adapter, "_get_adapter", return_value=mock_gh_adapter):
            with patch.object(adapter, "_find_existing_issue", return_value=None):
                await adapter.execute(sample_enrichment)

        mock_gh_adapter.create_issue.assert_called_once()
        call_args = mock_gh_adapter.create_issue.call_args
        assert call_args.kwargs["title"] == "📢 Release Notes: summer_26"
        assert "Release Notes: summer_26" in call_args.kwargs["body"]
        assert call_args.kwargs["labels"] == ["release-notes", "automated"]

    @pytest.mark.asyncio
    async def test_execute_updates_existing_issue(
        self, adapter: GitHubNotificationAdapter, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """execute should update existing issue when update_existing is True."""
        mock_gh_adapter = AsyncMock()
        mock_gh_adapter.update_issue = AsyncMock()

        with patch.object(adapter, "_get_adapter", return_value=mock_gh_adapter):
            with patch.object(adapter, "_find_existing_issue", return_value={"number": 456}):
                await adapter.execute(sample_enrichment)

        mock_gh_adapter.update_issue.assert_called_once()
        # Check the call was made with issue number and body
        call_args = mock_gh_adapter.update_issue.call_args
        assert call_args[0][0] == 456
        assert "body" in call_args.kwargs
        mock_gh_adapter.create_issue.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_skips_when_create_issue_false(
        self, config: GitHubNotificationConfig, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """execute should skip when create_issue is False."""
        config.create_issue = False
        adapter = GitHubNotificationAdapter(config)

        await adapter.execute(sample_enrichment)

        # Should not call any GitHub API
        assert adapter._gh_adapter is None

    @pytest.mark.asyncio
    async def test_find_existing_issue_returns_none(
        self, adapter: GitHubNotificationAdapter
    ) -> None:
        """_find_existing_issue should return None (simplified implementation)."""
        mock_gh_adapter = MagicMock()
        result = await adapter._find_existing_issue(mock_gh_adapter, "summer_26")
        assert result is None

    def test_format_issue_body(
        self, adapter: GitHubNotificationAdapter, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """_format_issue_body should format enrichment into markdown."""
        body = adapter._format_issue_body(sample_enrichment)

        assert "# Release Notes: summer_26" in body
        assert "Resumo executivo de teste." in body
        assert "## Temas Estratégicos" in body
        assert "- Tema 1" in body
        assert "- Tema 2" in body
        assert "## Categorias" in body
        assert "### Lightning" in body
        assert "Visão geral do Lightning." in body
        assert "**Temas:**" in body
        assert "- Tema Lightning" in body
        assert "## Checklist de Migração" in body
        assert "- [ ] Verificar deploy" in body
        assert "- [ ] Testar funcionalidade" in body
        assert "Gerado automaticamente" in body

    @pytest.mark.asyncio
    async def test_send_returns_false(self, adapter: GitHubNotificationAdapter) -> None:
        """send should return False for generic messages (not implemented)."""
        result = await adapter.send("Test message")
        assert result is False


class TestSlackNotificationConfig:
    """Tests for SlackNotificationConfig."""

    def test_init_with_defaults(self) -> None:
        """Should initialize with default values."""
        config = SlackNotificationConfig(webhook_url="https://hooks.slack.com/test")
        assert config.webhook_url == "https://hooks.slack.com/test"
        assert config.channel is None
        assert config.username == "Salesforce WebDev"
        assert config.icon_emoji == ":salesforce:"

    def test_init_uses_env_webhook(self) -> None:
        """Should use SLACK_WEBHOOK_URL from environment when not provided."""
        with patch.dict("os.environ", {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/env"}):
            config = SlackNotificationConfig(webhook_url=None)
            assert config.webhook_url == "https://hooks.slack.com/env"


class TestSlackNotificationAdapter:
    """Tests for SlackNotificationAdapter."""

    @pytest.fixture
    def config(self) -> SlackNotificationConfig:
        """Create Slack notification config."""
        return SlackNotificationConfig(webhook_url="https://hooks.slack.com/test")

    @pytest.fixture
    def adapter(self, config: SlackNotificationConfig) -> SlackNotificationAdapter:
        """Create Slack notification adapter."""
        return SlackNotificationAdapter(config)

    @pytest.fixture
    def sample_enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary="Resumo executivo de teste.",
            strategic_themes=(
                "Tema 1",
                "Tema 2",
                "Tema 3",
                "Tema 4",
                "Tema 5",
                "Tema 6",
            ),
            category_enrichments=(
                CategoryEnrichment(
                    category_name="Lightning",
                    overview="Visão geral do Lightning.",
                    key_themes=("Tema Lightning",),
                    business_impact="Alto impacto",
                    adoption_guidance="Adotar imediatamente.",
                    risk_assessment="Baixo risco.",
                    feature_enrichments=(),
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            migration_checklist=(
                "Verificar deploy",
                "Testar funcionalidade",
                "Comunicar equipes",
            ),
            generated_at="2026-05-01T10:00:00",
        )

    def test_init_sets_properties(
        self, adapter: SlackNotificationAdapter, config: SlackNotificationConfig
    ) -> None:
        """Should initialize with correct properties."""
        assert adapter.config is config

    def test_name_property(self, adapter: SlackNotificationAdapter) -> None:
        """Adapter name should be correct."""
        assert adapter.name == "slack_notification"

    @pytest.mark.asyncio
    async def test_execute_sends_webhook(
        self, adapter: SlackNotificationAdapter, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """execute should send webhook with formatted payload."""
        with patch.object(adapter, "_send_webhook", return_value=True) as mock_send:
            await adapter.execute(sample_enrichment)
            mock_send.assert_called_once()
            payload = mock_send.call_args[0][0]
            assert payload["username"] == "Salesforce WebDev"
            assert payload["icon_emoji"] == ":salesforce:"
            assert len(payload["blocks"]) > 0

    def test_format_slack_payload(
        self, adapter: SlackNotificationAdapter, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """_format_slack_payload should create correct Slack blocks."""
        payload = adapter._format_slack_payload(sample_enrichment)

        assert payload["username"] == "Salesforce WebDev"
        assert payload["icon_emoji"] == ":salesforce:"
        assert "blocks" in payload

        blocks = payload["blocks"]
        # Header block
        assert blocks[0]["type"] == "header"
        assert "summer_26" in blocks[0]["text"]["text"]

        # Section with executive summary
        assert blocks[1]["type"] == "section"
        assert "Resumo executivo" in blocks[1]["text"]["text"]

        # Divider
        assert blocks[2]["type"] == "divider"

        # Strategic themes section
        assert blocks[3]["type"] == "section"
        assert "Temas Estratégicos" in blocks[3]["text"]["text"]
        assert "Tema 1" in blocks[3]["text"]["text"]
        assert "Tema 5" in blocks[3]["text"]["text"]
        # Should limit to 5 themes
        assert "Tema 6" not in blocks[3]["text"]["text"]

        # Migration checklist section
        assert blocks[4]["type"] == "section"
        assert "Ações Recomendadas" in blocks[4]["text"]["text"]
        assert "Verificar deploy" in blocks[4]["text"]["text"]
        # Should limit to 3 items - "Comunicar equipes" IS the 3rd item so it should be included
        assert "Comunicar equipes" in blocks[4]["text"]["text"]

        # Context block
        assert blocks[5]["type"] == "context"
        assert "Gerado automaticamente" in blocks[5]["elements"][0]["text"]

    @pytest.mark.asyncio
    async def test_send_webhook_success(self, adapter: SlackNotificationAdapter) -> None:
        """_send_webhook should return True on success."""

        class MockResponse:
            def __init__(self, status):
                self.status = status

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class MockPostContext:
            def __init__(self, status):
                self.status = status

            async def __aenter__(self):
                return MockResponse(self.status)

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def __init__(self, status):
                self.status = status

            def post(self, *args, **kwargs):
                return MockPostContext(self.status)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_session = MockSession(200)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await adapter._send_webhook({"test": "payload"})

        assert result is True

    @pytest.mark.asyncio
    async def test_send_webhook_failure(self, adapter: SlackNotificationAdapter) -> None:
        """_send_webhook should return False on HTTP error."""

        class MockResponse:
            def __init__(self, status):
                self.status = status

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class MockPostContext:
            def __init__(self, status):
                self.status = status

            async def __aenter__(self):
                return MockResponse(self.status)

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def __init__(self, status):
                self.status = status

            def post(self, *args, **kwargs):
                return MockPostContext(self.status)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_session = MockSession(500)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await adapter._send_webhook({"test": "payload"})

        assert result is False

    @pytest.mark.asyncio
    async def test_send_webhook_exception(self, adapter: SlackNotificationAdapter) -> None:
        """_send_webhook should return False on exception."""

        class MockPostContext:
            def __init__(self, exc):
                self.exc = exc

            async def __aenter__(self):
                raise self.exc

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def __init__(self, exc):
                self.exc = exc

            def post(self, *args, **kwargs):
                return MockPostContext(self.exc)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_session = MockSession(Exception("Network error"))

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await adapter._send_webhook({"test": "payload"})

        assert result is False

    @pytest.mark.asyncio
    async def test_send_simple_message(self, adapter: SlackNotificationAdapter) -> None:
        """send should send simple text message."""

        class MockResponse:
            def __init__(self, status):
                self.status = status

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class MockPostContext:
            def __init__(self, status):
                self.status = status

            async def __aenter__(self):
                return MockResponse(self.status)

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def __init__(self, status):
                self.status = status

            def post(self, *args, **kwargs):
                return MockPostContext(self.status)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_session = MockSession(200)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await adapter.send("Test message")

        assert result is True

    @pytest.mark.asyncio
    async def test_send_returns_false_without_webhook(self) -> None:
        """send should return False when no webhook configured."""
        config = SlackNotificationConfig(webhook_url=None)
        with patch.dict("os.environ", {}, clear=True):
            adapter = SlackNotificationAdapter(config)
            result = await adapter.send("Test message")
            assert result is False


class TestEmailNotificationConfig:
    """Tests for EmailNotificationConfig."""

    def test_init_with_defaults(self) -> None:
        """Should initialize with default values."""
        config = EmailNotificationConfig(
            smtp_host="smtp.example.com",
            username="user",
            password="pass",
            from_email="from@example.com",
            to_emails=["to@example.com"],
        )
        assert config.smtp_host == "smtp.example.com"
        assert config.username == "user"
        assert config.password == "pass"
        assert config.from_email == "from@example.com"
        assert config.to_emails == ["to@example.com"]
        assert config.smtp_port == 587
        assert config.use_tls is True


class TestEmailNotificationAdapter:
    """Tests for EmailNotificationAdapter."""

    @pytest.fixture
    def config(self) -> EmailNotificationConfig:
        """Create email notification config."""
        return EmailNotificationConfig(
            smtp_host="smtp.example.com",
            username="user",
            password="pass",
            from_email="from@example.com",
            to_emails=["to@example.com"],
        )

    @pytest.fixture
    def adapter(self, config: EmailNotificationConfig) -> EmailNotificationAdapter:
        """Create email notification adapter."""
        return EmailNotificationAdapter(config)

    @pytest.fixture
    def sample_enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary="Resumo executivo.",
            strategic_themes=("Tema 1", "Tema 2"),
            category_enrichments=(
                CategoryEnrichment(
                    category_name="Lightning",
                    overview="Visão geral do Lightning.",
                    key_themes=(),
                    business_impact="",
                    adoption_guidance="",
                    risk_assessment="",
                    feature_enrichments=(),
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            migration_checklist=("Verificar deploy",),
            generated_at="2026-05-01T10:00:00",
        )

    def test_init_sets_properties(
        self, adapter: EmailNotificationAdapter, config: EmailNotificationConfig
    ) -> None:
        """Should initialize with correct properties."""
        assert adapter.config is config

    def test_name_property(self, adapter: EmailNotificationAdapter) -> None:
        """Adapter name should be correct."""
        assert adapter.name == "email_notification"

    def test_format_email_body(
        self, adapter: EmailNotificationAdapter, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """_format_email_body should format enrichment into email text."""
        body = adapter._format_email_body(sample_enrichment)

        assert "Release Notes: summer_26" in body
        assert "=" * 50 in body
        assert "Resumo executivo." in body
        assert "Temas Estratégicos:" in body
        assert "  • Tema 1" in body
        assert "  • Tema 2" in body
        assert "Categorias:" in body
        assert "  Lightning: Visão geral do Lightning." in body
        assert "Checklist de Migração:" in body
        assert "  ☐ Verificar deploy" in body

    @pytest.mark.asyncio
    async def test_send_email_success(self, adapter: EmailNotificationAdapter) -> None:
        """_send_email should return True on success."""
        with patch("smtplib.SMTP") as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            result = await adapter._send_email("Subject", "Body")

        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_failure(self, adapter: EmailNotificationAdapter) -> None:
        """_send_email should return False on exception."""
        with patch("smtplib.SMTP", side_effect=Exception("SMTP error")):
            result = await adapter._send_email("Subject", "Body")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_with_subject(self, adapter: EmailNotificationAdapter) -> None:
        """send should use provided subject."""
        with patch.object(adapter, "_send_email", return_value=True) as mock_send:
            result = await adapter.send("Message", subject="Custom Subject")

        assert result is True
        mock_send.assert_called_once_with("Custom Subject", "Message")

    @pytest.mark.asyncio
    async def test_send_default_subject(self, adapter: EmailNotificationAdapter) -> None:
        """send should use default subject when not provided."""
        with patch.object(adapter, "_send_email", return_value=True) as mock_send:
            result = await adapter.send("Message")

        assert result is True
        mock_send.assert_called_once_with("Salesforce WebDev Notification", "Message")


class TestCompositeNotificationAdapter:
    """Tests for CompositeNotificationAdapter."""

    @pytest.fixture
    def mock_adapters(self) -> list[MagicMock]:
        """Create mock adapters."""
        adapter1 = MagicMock()
        adapter1.name = "adapter1"
        adapter1.execute = AsyncMock()
        adapter1.send = AsyncMock(return_value=True)

        adapter2 = MagicMock()
        adapter2.name = "adapter2"
        adapter2.execute = AsyncMock()
        adapter2.send = AsyncMock(return_value=False)

        return [adapter1, adapter2]

    @pytest.fixture
    def composite_adapter(self, mock_adapters: list[MagicMock]) -> CompositeNotificationAdapter:
        """Create composite notification adapter."""
        return CompositeNotificationAdapter(mock_adapters)

    @pytest.fixture
    def sample_enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary="Resumo.",
            strategic_themes=(),
            category_enrichments=(),
            migration_checklist=(),
            generated_at="2026-05-01T10:00:00",
        )

    def test_init_sets_properties(
        self,
        composite_adapter: CompositeNotificationAdapter,
        mock_adapters: list[MagicMock],
    ) -> None:
        """Should initialize with correct properties."""
        assert composite_adapter.adapters == mock_adapters

    def test_name_property(self, composite_adapter: CompositeNotificationAdapter) -> None:
        """Adapter name should be correct."""
        assert composite_adapter.name == "composite_notification"

    @pytest.mark.asyncio
    async def test_execute_calls_all_adapters(
        self,
        composite_adapter: CompositeNotificationAdapter,
        mock_adapters: list[MagicMock],
        sample_enrichment: ReleaseEnrichment,
    ) -> None:
        """execute should call all adapters."""
        await composite_adapter.execute(sample_enrichment)

        for adapter in mock_adapters:
            adapter.execute.assert_called_once_with(sample_enrichment)

    @pytest.mark.asyncio
    async def test_execute_handles_adapter_errors(
        self,
        composite_adapter: CompositeNotificationAdapter,
        mock_adapters: list[MagicMock],
        sample_enrichment: ReleaseEnrichment,
    ) -> None:
        """execute should handle adapter errors gracefully."""
        mock_adapters[0].execute = AsyncMock(side_effect=Exception("Adapter 1 failed"))

        # Should not raise
        await composite_adapter.execute(sample_enrichment)

        mock_adapters[0].execute.assert_called_once()
        mock_adapters[1].execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_calls_all_adapters(
        self,
        composite_adapter: CompositeNotificationAdapter,
        mock_adapters: list[MagicMock],
    ) -> None:
        """send should call all adapters."""
        result = await composite_adapter.send("Test message")

        assert result is True  # At least one returned True
        for adapter in mock_adapters:
            adapter.send.assert_called_once_with("Test message")

    @pytest.mark.asyncio
    async def test_send_returns_false_when_all_fail(
        self,
        composite_adapter: CompositeNotificationAdapter,
        mock_adapters: list[MagicMock],
    ) -> None:
        """send should return False when all adapters return False."""
        mock_adapters[0].send = AsyncMock(return_value=False)
        mock_adapters[1].send = AsyncMock(return_value=False)

        result = await composite_adapter.send("Test message")

        assert result is False

    @pytest.mark.asyncio
    async def test_send_handles_adapter_errors(
        self,
        composite_adapter: CompositeNotificationAdapter,
        mock_adapters: list[MagicMock],
    ) -> None:
        """send should handle adapter errors gracefully."""
        mock_adapters[0].send = AsyncMock(side_effect=Exception("Adapter 1 failed"))
        mock_adapters[1].send = AsyncMock(return_value=True)

        result = await composite_adapter.send("Test message")

        assert result is True
