"""Messaging infrastructure — notification adapters.

Implements the NotificationStep contract for sending notifications
via GitHub, Slack, Email, Webhook, etc.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

from src.core.pipeline.steps import NotificationStep
from src.models.enrichment import ReleaseEnrichment

logger = logging.getLogger(__name__)


class NotificationAdapter(NotificationStep):
    """Abstract notification adapter interface."""

    @property
    def name(self) -> str:
        return "notification_adapter"

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        raise NotImplementedError

    async def send(self, message: str, **kwargs: Any) -> bool:
        raise NotImplementedError


@dataclass
class GitHubNotificationConfig:
    """Configuration for GitHub notifications."""

    repo: str
    token: str | None = None
    issue_template: str = "release_notes"
    create_issue: bool = True
    update_existing: bool = True


class GitHubNotificationAdapter(NotificationAdapter):
    """Send notifications via GitHub Issues."""

    def __init__(self, config: GitHubNotificationConfig) -> None:
        self.config = config
        self._gh_adapter: Any | None = None

    @property
    def name(self) -> str:
        return "github_notification"

    async def _get_adapter(self) -> Any:
        if self._gh_adapter is None:
            from .github import GitHubConfig, GitHubOperationsAdapter

            self._gh_adapter = GitHubOperationsAdapter(
                GitHubConfig(repo=self.config.repo, token=self.config.token)
            )
        return self._gh_adapter

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        """Send release notification as GitHub issue."""
        if not self.config.create_issue:
            return

        adapter = await self._get_adapter()

        title = f"📢 Release Notes: {enrichment.release_slug}"
        body = self._format_issue_body(enrichment)

        # Check for existing issue if update_existing
        if self.config.update_existing:
            existing = await self._find_existing_issue(adapter, enrichment.release_slug)
            if existing:
                await adapter.update_issue(existing["number"], body=body)
                logger.info("Updated existing issue for %s", enrichment.release_slug)
                return

        await adapter.create_issue(
            title=title,
            body=body,
            labels=["release-notes", "automated"],
        )
        logger.info("Created GitHub issue for %s", enrichment.release_slug)

    async def _find_existing_issue(self, adapter: Any, release_slug: str) -> dict[str, Any] | None:
        """Find existing issue for this release."""
        # This would need search API - simplified for now
        return None

    def _format_issue_body(self, enrichment: ReleaseEnrichment) -> str:
        """Format issue body from enrichment."""
        lines = [
            f"# Release Notes: {enrichment.release_slug}",
            "",
            enrichment.executive_summary or "Resumo não disponível.",
            "",
            "## Temas Estratégicos",
            "",
        ]

        for theme in enrichment.strategic_themes:
            lines.append(f"- {theme}")

        lines.extend(
            [
                "",
                "## Categorias",
                "",
            ]
        )

        for cat in enrichment.category_enrichments:
            lines.append(f"### {cat.category_name}")
            lines.append("")
            lines.append(cat.overview or "Sem visão geral.")
            lines.append("")

            if cat.key_themes:
                lines.append("**Temas:**")
                for theme in cat.key_themes:
                    lines.append(f"- {theme}")
                lines.append("")

        if enrichment.migration_checklist:
            lines.extend(
                [
                    "## Checklist de Migração",
                    "",
                ]
            )
            for item in enrichment.migration_checklist:
                lines.append(f"- [ ] {item}")
            lines.append("")

        lines.extend(
            [
                "---",
                "*Gerado automaticamente pelo pipeline Salesforce WebDev*",
            ]
        )

        return "\n".join(lines)

    async def send(self, message: str, **kwargs: Any) -> bool:
        """Send a generic message as GitHub issue comment."""
        # Not implemented for generic messages
        return False


@dataclass
class SlackNotificationConfig:
    """Configuration for Slack notifications."""

    webhook_url: str | None = None
    channel: str | None = None
    username: str = "Salesforce WebDev"
    icon_emoji: str = ":salesforce:"

    def __post_init__(self) -> None:
        if self.webhook_url is None:
            self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")


class SlackNotificationAdapter(NotificationAdapter):
    """Send notifications via Slack webhook."""

    def __init__(self, config: SlackNotificationConfig | None = None) -> None:
        self.config = config or SlackNotificationConfig()
        if self.config.webhook_url is None:
            self.config.webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    @property
    def name(self) -> str:
        return "slack_notification"

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        """Send release notification to Slack."""
        if not self.config.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return

        payload = self._format_slack_payload(enrichment)
        await self._send_webhook(payload)

    def _format_slack_payload(self, enrichment: ReleaseEnrichment) -> dict[str, Any]:
        """Format Slack message payload."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 Novo Release: {enrichment.release_slug}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": enrichment.executive_summary or "Resumo não disponível.",
                },
            },
            {"type": "divider"},
        ]

        if enrichment.strategic_themes:
            theme_text = "\n".join(f"• {t}" for t in enrichment.strategic_themes[:5])
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Temas Estratégicos:*\n{theme_text}",
                    },
                }
            )

        if enrichment.migration_checklist:
            checklist_text = "\n".join(f"☐ {item}" for item in enrichment.migration_checklist[:3])
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Ações Recomendadas:*\n{checklist_text}",
                    },
                }
            )

        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Gerado automaticamente pelo Salesforce WebDev",
                    }
                ],
            }
        )

        return {
            "channel": self.config.channel,
            "username": self.config.username,
            "icon_emoji": self.config.icon_emoji,
            "blocks": blocks,
        }

    async def _send_webhook(self, payload: dict[str, Any]) -> bool:
        """Send payload to Slack webhook."""
        import aiohttp

        webhook_url = self.config.webhook_url
        if not webhook_url:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        logger.info("Slack notification sent successfully")
                        return True
                    else:
                        logger.error("Slack webhook failed: %s", resp.status)
                        return False
        except Exception as e:
            logger.error("Slack notification error: %s", e)
            return False

    async def send(self, message: str, **kwargs: Any) -> bool:
        """Send a simple message to Slack."""
        webhook_url = self.config.webhook_url
        if not webhook_url:
            return False

        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    json={"text": message},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False


@dataclass
class EmailNotificationConfig:
    """Configuration for email notifications."""

    smtp_host: str
    username: str
    password: str
    from_email: str
    to_emails: list[str]
    smtp_port: int = 587
    use_tls: bool = True


class EmailNotificationAdapter(NotificationAdapter):
    """Send notifications via email (SMTP)."""

    def __init__(self, config: EmailNotificationConfig) -> None:
        self.config = config

    @property
    def name(self) -> str:
        return "email_notification"

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        """Send release notification via email."""
        subject = f"📢 Salesforce Release Notes: {enrichment.release_slug}"
        body = self._format_email_body(enrichment)
        await self._send_email(subject, body)

    def _format_email_body(self, enrichment: ReleaseEnrichment) -> str:
        """Format email body."""
        lines = [
            f"Release Notes: {enrichment.release_slug}",
            "=" * 50,
            "",
            enrichment.executive_summary or "Resumo não disponível.",
            "",
            "Temas Estratégicos:",
        ]

        for theme in enrichment.strategic_themes:
            lines.append(f"  • {theme}")

        lines.extend(["", "Categorias:", ""])

        for cat in enrichment.category_enrichments:
            lines.append(f"  {cat.category_name}: {cat.overview}")

        if enrichment.migration_checklist:
            lines.extend(["", "Checklist de Migração:", ""])
            for item in enrichment.migration_checklist:
                lines.append(f"  ☐ {item}")

        return "\n".join(lines)

    async def _send_email(self, subject: str, body: str) -> bool:
        """Send email via SMTP."""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        try:
            msg = MIMEMultipart()
            msg["From"] = self.config.from_email
            msg["To"] = ", ".join(self.config.to_emails)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)

            logger.info("Email notification sent to %s", self.config.to_emails)
            return True
        except Exception as e:
            logger.error("Email notification failed: %s", e)
            return False

    async def send(self, message: str, **kwargs: Any) -> bool:
        subject = kwargs.get("subject", "Salesforce WebDev Notification")
        return await self._send_email(subject, message)


class CompositeNotificationAdapter(NotificationAdapter):
    """Composite adapter that sends to multiple channels."""

    def __init__(self, adapters: list[NotificationAdapter]) -> None:
        self.adapters = adapters

    @property
    def name(self) -> str:
        return "composite_notification"

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        """Send to all adapters."""
        import asyncio

        results = await asyncio.gather(
            *[adapter.execute(enrichment) for adapter in self.adapters],
            return_exceptions=True,
        )

        for adapter, result in zip(self.adapters, results):
            if isinstance(result, Exception):
                logger.error("Notification adapter %s failed: %s", adapter.name, result)

    async def send(self, message: str, **kwargs: Any) -> bool:
        """Send to all adapters."""
        import asyncio

        results = await asyncio.gather(
            *[adapter.send(message, **kwargs) for adapter in self.adapters],
            return_exceptions=True,
        )

        return any(r is True for r in results if not isinstance(r, Exception))
