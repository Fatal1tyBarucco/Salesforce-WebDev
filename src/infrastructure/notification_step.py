"""Notification step adapter — bridges pipeline step to notification adapters."""

from __future__ import annotations

from typing import Any

from src.core.pipeline.steps import NotificationStep
from src.infrastructure.messaging import (
    CompositeNotificationAdapter,
    NotificationAdapter,
)
from src.models.enrichment import ReleaseEnrichment


class NotificationStepAdapter(NotificationStep):
    """Adapter that wraps a NotificationAdapter as a PipelineStep."""

    def __init__(self, adapter: NotificationAdapter) -> None:
        self._adapter = adapter

    @property
    def name(self) -> str:
        return f"notification_step_{self._adapter.name}"

    async def execute(self, enrichment: ReleaseEnrichment) -> None:
        """Execute notification via the wrapped adapter."""
        await self._adapter.execute(enrichment)


def create_notification_step(
    github_repo: str | None = None,
    github_token: str | None = None,
    slack_webhook: str | None = None,
    email_config: dict[str, Any] | None = None,
) -> NotificationStep:
    """Create a composite notification step with configured adapters."""

    adapters: list[NotificationAdapter] = []

    if github_repo:
        from src.infrastructure.messaging import (
            GitHubNotificationAdapter,
            GitHubNotificationConfig,
        )

        adapters.append(
            GitHubNotificationAdapter(
                GitHubNotificationConfig(repo=github_repo, token=github_token)
            )
        )

    if slack_webhook:
        from src.infrastructure.messaging import (
            SlackNotificationAdapter,
            SlackNotificationConfig,
        )

        adapters.append(
            SlackNotificationAdapter(SlackNotificationConfig(webhook_url=slack_webhook))
        )

    if email_config:
        from src.infrastructure.messaging import (
            EmailNotificationAdapter,
            EmailNotificationConfig,
        )

        adapters.append(EmailNotificationAdapter(EmailNotificationConfig(**email_config)))

    if not adapters:
        # Return a no-op step
        class NoopNotificationStep(NotificationStep):
            @property
            def name(self) -> str:
                return "noop_notification"

            async def execute(self, enrichment: ReleaseEnrichment) -> None:
                pass

        return NoopNotificationStep()

    composite = CompositeNotificationAdapter(adapters)
    return NotificationStepAdapter(composite)
