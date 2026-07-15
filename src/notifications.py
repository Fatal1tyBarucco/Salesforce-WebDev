"""Stakeholder notification system for release updates.

Provides email digest, Slack webhook, and Discord webhook notifications
after each release is processed. Configurable profiles determine which
categories trigger notifications.

No external dependencies — uses stdlib smtplib, urllib, json, html.
"""

from __future__ import annotations

import html
import json
import logging
import smtplib
import ssl
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from .config import RELEASES_DIR

logger = logging.getLogger(__name__)

NOTIFICATIONS_DIR = "notifications"
UNSUBSCRIBE_FILE = "unsubscribe.json"


@dataclass
class NotificationProfile:
    """Configuration for notification delivery."""

    name: str
    email: str = ""
    slack_webhook: str = ""
    discord_webhook: str = ""
    categories: list[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class NotificationResult:
    """Result of sending a notification."""

    channel: str  # "email" | "slack" | "discord"
    success: bool
    error: str = ""
    recipient: str = ""


@dataclass
class ReleaseDigest:
    """Digest of a release for notification."""

    release_name: str
    release_slug: str
    total_features: int
    categories: list[dict[str, Any]]
    generated_at: str


def _load_release_meta(slug: str) -> dict[str, Any] | None:
    """Load metadata for a release."""
    meta_path = Path(RELEASES_DIR) / slug / ".meta.json"
    if not meta_path.exists():
        return None
    try:
        result: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
        return result
    except json.JSONDecodeError, OSError:
        return None


def build_digest(slug: str) -> ReleaseDigest | None:
    """Build a notification digest from release metadata."""
    meta = _load_release_meta(slug)
    if meta is None:
        return None
    return ReleaseDigest(
        release_name=meta.get("name", slug),
        release_slug=slug,
        total_features=meta.get("total_features", 0),
        categories=meta.get("categories", []),
        generated_at=meta.get("generated_at", ""),
    )


def _format_email_html(digest: ReleaseDigest, profile: NotificationProfile) -> str:
    """Format release digest as HTML email body."""
    cat_rows = ""
    for cat in digest.categories:
        name = cat.get("name", "?")
        count = cat.get("count", 0)
        highlighted = ""
        if not profile.categories or name in profile.categories:
            highlighted = ' style="background:#eff6ff"'
        cat_rows += f"<tr{highlighted}><td>{html.escape(name)}</td><td>{count}</td></tr>\n"

    category_list = ", ".join(profile.categories) if profile.categories else "Todas"

    return f"""<!DOCTYPE html>
<html>
<body style="font-family:-apple-system,sans-serif;max-width:600px;margin:0 auto;padding:20px">
<h2 style="color:#1e40af">Salesforce Release Notes — {digest.release_name}</h2>
<p><strong>{digest.total_features}</strong> features em <strong>{len(digest.categories)}</strong> categorias</p>
<p style="font-size:12px;color:#666">Categorias monitoradas: {category_list}</p>
<table style="width:100%;border-collapse:collapse">
<tr style="background:#f1f5f9"><th style="text-align:left;padding:8px">Categoria</th><th style="text-align:left;padding:8px">Features</th></tr>
{cat_rows}
</table>
<p style="font-size:11px;color:#999;margin-top:20px">Gerado automaticamente pelo pipeline de Release Notes</p>
</body>
</html>"""


def _format_slack_blocks(digest: ReleaseDigest, profile: NotificationProfile) -> dict[str, Any]:
    """Format release digest as Slack Block Kit message."""
    cat_text = "\n".join(
        f"• *{c.get('name', '?')}*: {c.get('count', 0)} features" for c in digest.categories[:15]
    )
    if len(digest.categories) > 15:
        cat_text += f"\n... e mais {len(digest.categories) - 15} categorias"

    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🚀 {digest.release_name} — Release Notes"},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{digest.total_features}* features em *{len(digest.categories)}* categorias",
                },
            },
            {"type": "section", "text": {"type": "mrkdwn", "text": cat_text}},
        ]
    }


def _format_discord_embed(digest: ReleaseDigest, profile: NotificationProfile) -> dict[str, Any]:
    """Format release digest as Discord embed."""
    cat_fields = [
        {"name": c.get("name", "?"), "value": str(c.get("count", 0)), "inline": True}
        for c in digest.categories[:25]
    ]

    return {
        "embeds": [
            {
                "title": f"🚀 {digest.release_name} — Release Notes",
                "description": f"**{digest.total_features}** features em **{len(digest.categories)}** categorias",
                "color": 3447003,
                "fields": cat_fields,
            }
        ]
    }


def send_email(
    digest: ReleaseDigest,
    profile: NotificationProfile,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    smtp_user: str = "",
    smtp_pass: str = "",
) -> NotificationResult:
    """Send release digest via email."""
    if not profile.email:
        return NotificationResult("email", False, "no email address", "")

    html_body = _format_email_html(digest, profile)
    plain_body = f"{digest.release_name} — {digest.total_features} features\n\n" + "\n".join(
        f"• {c.get('name', '?')}: {c.get('count', 0)}" for c in digest.categories
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Salesforce {digest.release_name} — Release Notes"
    msg["From"] = smtp_user or profile.email
    msg["To"] = profile.email
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls(context=context)
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(msg["From"], [profile.email], msg.as_string())
        return NotificationResult("email", True, recipient=profile.email)
    except (smtplib.SMTPException, OSError) as e:
        logger.error("Email notification failed: %s", e)
        return NotificationResult("email", False, str(e), profile.email)


def send_slack(digest: ReleaseDigest, profile: NotificationProfile) -> NotificationResult:
    """Send release digest via Slack webhook."""
    if not profile.slack_webhook:
        return NotificationResult("slack", False, "no webhook URL", "")

    payload = _format_slack_blocks(digest, profile)
    data = json.dumps(payload).encode("utf-8")

    try:
        req = Request(
            profile.slack_webhook,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                return NotificationResult(
                    "slack", False, f"HTTP {resp.status}", profile.slack_webhook
                )
        return NotificationResult("slack", True, recipient=profile.slack_webhook)
    except (URLError, OSError) as e:
        logger.error("Slack notification failed: %s", e)
        return NotificationResult("slack", False, str(e), profile.slack_webhook)


def send_discord(digest: ReleaseDigest, profile: NotificationProfile) -> NotificationResult:
    """Send release digest via Discord webhook."""
    if not profile.discord_webhook:
        return NotificationResult("discord", False, "no webhook URL", "")

    payload = _format_discord_embed(digest, profile)
    data = json.dumps(payload).encode("utf-8")

    try:
        req = Request(
            profile.discord_webhook,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=10) as resp:
            if resp.status >= 400:
                return NotificationResult(
                    "discord", False, f"HTTP {resp.status}", profile.discord_webhook
                )
        return NotificationResult("discord", True, recipient=profile.discord_webhook)
    except (URLError, OSError) as e:
        logger.error("Discord notification failed: %s", e)
        return NotificationResult("discord", False, str(e), profile.discord_webhook)


def _load_profiles() -> list[NotificationProfile]:
    """Load notification profiles from config file."""
    profiles_path = Path(NOTIFICATIONS_DIR) / "profiles.json"
    if not profiles_path.exists():
        return []
    try:
        data: list[dict[str, Any]] = json.loads(profiles_path.read_text(encoding="utf-8"))
        return [
            NotificationProfile(
                name=p.get("name", ""),
                email=p.get("email", ""),
                slack_webhook=p.get("slack_webhook", ""),
                discord_webhook=p.get("discord_webhook", ""),
                categories=p.get("categories", []),
                enabled=p.get("enabled", True),
            )
            for p in data
        ]
    except json.JSONDecodeError, OSError:
        return []


def _load_unsubscribed() -> set[str]:
    """Load set of unsubscribed email addresses."""
    unsub_path = Path(NOTIFICATIONS_DIR) / UNSUBSCRIBE_FILE
    if not unsub_path.exists():
        return set()
    try:
        data: list[str] = json.loads(unsub_path.read_text(encoding="utf-8"))
        return set(data)
    except json.JSONDecodeError, OSError:
        return set()


def unsubscribe(email: str) -> bool:
    """Add an email to the unsubscribe list."""
    unsub_path = Path(NOTIFICATIONS_DIR) / UNSUBSCRIBE_FILE
    unsub_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _load_unsubscribed()
    existing.add(email)
    try:
        unsub_path.write_text(json.dumps(sorted(existing), indent=2), encoding="utf-8")
        return True
    except OSError:
        return False


def is_subscribed(email: str) -> bool:
    """Check if an email is subscribed."""
    return email not in _load_unsubscribed()


def send_notifications(
    slug: str,
    profiles: list[NotificationProfile] | None = None,
    smtp_host: str = "smtp.gmail.com",
    smtp_port: int = 587,
    smtp_user: str = "",
    smtp_pass: str = "",
) -> list[NotificationResult]:
    """Send notifications for a release to all matching profiles."""
    digest = build_digest(slug)
    if digest is None:
        return []

    if profiles is None:
        profiles = _load_profiles()

    unsubscribed = _load_unsubscribed()
    results: list[NotificationResult] = []

    for profile in profiles:
        if not profile.enabled:
            continue

        # Filter categories if profile has specific ones
        if profile.categories:
            filtered_categories = [
                c for c in digest.categories if c.get("name") in profile.categories
            ]
            if not filtered_categories:
                continue

        # Check email unsubscribe
        if profile.email and profile.email in unsubscribed:
            continue

        if profile.email:
            results.append(send_email(digest, profile, smtp_host, smtp_port, smtp_user, smtp_pass))
        if profile.slack_webhook:
            results.append(send_slack(digest, profile))
        if profile.discord_webhook:
            results.append(send_discord(digest, profile))

    return results
