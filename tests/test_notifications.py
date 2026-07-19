"""Tests for src/notifications.py — 100% coverage."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

from src.notifications import (
    NotificationProfile,
    NotificationResult,
    ReleaseDigest,
    _format_discord_embed,
    _format_email_html,
    _format_slack_blocks,
    _load_profiles,
    _load_release_meta,
    _load_unsubscribed,
    build_digest,
    is_subscribed,
    send_discord,
    send_email,
    send_notifications,
    send_slack,
    unsubscribe,
)


def make_digest() -> ReleaseDigest:
    return ReleaseDigest(
        release_name="Summer '26",
        release_slug="summer_26",
        total_features=100,
        categories=[{"name": "Security", "count": 30}, {"name": "Sales", "count": 70}],
        generated_at="2025-01-01T00:00:00Z",
    )


def make_profile(**kwargs) -> NotificationProfile:
    defaults = {"name": "Test", "email": "test@example.com"}
    defaults.update(kwargs)
    return NotificationProfile(**defaults)


class TestLoadReleaseMeta:
    def test_no_file(self, tmp_path: Path) -> None:
        with patch("src.notifications.RELEASES_DIR", str(tmp_path)):
            assert _load_release_meta("nope") is None

    def test_valid_meta(self, tmp_path: Path) -> None:
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(json.dumps({"name": "Summer '26"}))
        with patch("src.notifications.RELEASES_DIR", str(tmp_path)):
            meta = _load_release_meta("summer_26")
            assert meta is not None
            assert meta["name"] == "Summer '26"

    def test_invalid_json(self, tmp_path: Path) -> None:
        d = tmp_path / "bad"
        d.mkdir()
        (d / ".meta.json").write_text("not json{")
        with patch("src.notifications.RELEASES_DIR", str(tmp_path)):
            assert _load_release_meta("bad") is None


class TestBuildDigest:
    def test_returns_none(self, tmp_path: Path) -> None:
        with patch("src.notifications._load_release_meta", return_value=None):
            assert build_digest("nope") is None

    def test_builds_digest(self, tmp_path: Path) -> None:
        meta = {"name": "R1", "total_features": 10, "categories": [{"name": "A", "count": 10}], "generated_at": ""}
        with patch("src.notifications._load_release_meta", return_value=meta):
            d = build_digest("r1")
            assert d is not None
            assert d.release_name == "R1"
            assert d.total_features == 10


class TestFormatEmailHtml:
    def test_format(self) -> None:
        digest = make_digest()
        profile = make_profile(categories=["Security"])
        html_out = _format_email_html(digest, profile)
        assert "Summer '26" in html_out
        assert "Security" in html_out
        assert "background:#eff6ff" in html_out

    def test_no_categories_filter(self) -> None:
        digest = make_digest()
        profile = make_profile(categories=[])
        html_out = _format_email_html(digest, profile)
        assert "Todas" in html_out


class TestFormatSlackBlocks:
    def test_format(self) -> None:
        digest = make_digest()
        profile = make_profile()
        result = _format_slack_blocks(digest, profile)
        assert "blocks" in result
        assert len(result["blocks"]) == 3

    def test_truncates_categories(self) -> None:
        digest = make_digest()
        digest.categories = [{"name": f"C{i}", "count": i} for i in range(20)]
        profile = make_profile()
        result = _format_slack_blocks(digest, profile)
        text = result["blocks"][2]["text"]["text"]
        assert "mais 5" in text


class TestFormatDiscordEmbed:
    def test_format(self) -> None:
        digest = make_digest()
        profile = make_profile()
        result = _format_discord_embed(digest, profile)
        assert "embeds" in result
        assert len(result["embeds"][0]["fields"]) == 2

    def test_truncates_fields(self) -> None:
        digest = make_digest()
        digest.categories = [{"name": f"C{i}", "count": i} for i in range(30)]
        profile = make_profile()
        result = _format_discord_embed(digest, profile)
        assert len(result["embeds"][0]["fields"]) == 25


class TestSendEmail:
    def test_no_email(self) -> None:
        profile = make_profile(email="")
        result = send_email(make_digest(), profile)
        assert result.success is False

    def test_success(self) -> None:
        profile = make_profile()
        mock_server = MagicMock()
        with patch("src.notifications.smtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
            mock_smtp.return_value.__exit__ = MagicMock(return_value=False)
            result = send_email(make_digest(), profile, smtp_user="u", smtp_pass="p")
            assert result.success is True

    def test_smtp_error(self) -> None:
        import smtplib

        profile = make_profile()
        with patch("src.notifications.smtplib.SMTP", side_effect=smtplib.SMTPException("fail")):
            result = send_email(make_digest(), profile)
            assert result.success is False
            assert "fail" in result.error


class TestSendSlack:
    def test_no_webhook(self) -> None:
        profile = make_profile(slack_webhook="")
        result = send_slack(make_digest(), profile)
        assert result.success is False

    def test_success(self) -> None:
        profile = make_profile(slack_webhook="https://hooks.slack.com/test")
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("src.notifications.urlopen", return_value=mock_resp):
            result = send_slack(make_digest(), profile)
            assert result.success is True

    def test_http_error(self) -> None:
        profile = make_profile(slack_webhook="https://hooks.slack.com/test")
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("src.notifications.urlopen", return_value=mock_resp):
            result = send_slack(make_digest(), profile)
            assert result.success is False

    def test_url_error(self) -> None:
        from urllib.error import URLError

        profile = make_profile(slack_webhook="https://hooks.slack.com/test")
        with patch("src.notifications.urlopen", side_effect=URLError("timeout")):
            result = send_slack(make_digest(), profile)
            assert result.success is False


class TestSendDiscord:
    def test_no_webhook(self) -> None:
        profile = make_profile(discord_webhook="")
        result = send_discord(make_digest(), profile)
        assert result.success is False

    def test_success(self) -> None:
        profile = make_profile(discord_webhook="https://discord.com/api/webhooks/test")
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("src.notifications.urlopen", return_value=mock_resp):
            result = send_discord(make_digest(), profile)
            assert result.success is True

    def test_http_error(self) -> None:
        profile = make_profile(discord_webhook="https://discord.com/api/webhooks/test")
        mock_resp = MagicMock()
        mock_resp.status = 400
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("src.notifications.urlopen", return_value=mock_resp):
            result = send_discord(make_digest(), profile)
            assert result.success is False

    def test_url_error(self) -> None:
        from urllib.error import URLError

        profile = make_profile(discord_webhook="https://discord.com/api/webhooks/test")
        with patch("src.notifications.urlopen", side_effect=URLError("fail")):
            result = send_discord(make_digest(), profile)
            assert result.success is False


class TestLoadProfiles:
    def test_no_file(self, tmp_path: Path) -> None:
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert _load_profiles() == []

    def test_valid(self, tmp_path: Path) -> None:
        d = tmp_path
        (d / "profiles.json").write_text(json.dumps([{"name": "P1", "email": "a@b.com"}]))
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            profiles = _load_profiles()
            assert len(profiles) == 1
            assert profiles[0].name == "P1"

    def test_invalid_json(self, tmp_path: Path) -> None:
        (tmp_path / "profiles.json").write_text("bad{")
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert _load_profiles() == []


class TestLoadUnsubscribed:
    def test_no_file(self, tmp_path: Path) -> None:
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert _load_unsubscribed() == set()

    def test_valid(self, tmp_path: Path) -> None:
        (tmp_path / "unsubscribe.json").write_text(json.dumps(["a@b.com"]))
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert _load_unsubscribed() == {"a@b.com"}

    def test_invalid_json(self, tmp_path: Path) -> None:
        (tmp_path / "unsubscribe.json").write_text("bad{")
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert _load_unsubscribed() == set()


class TestUnsubscribe:
    def test_new_email(self, tmp_path: Path) -> None:
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert unsubscribe("new@test.com") is True
            assert "new@test.com" in _load_unsubscribed()

    def test_os_error(self, tmp_path: Path) -> None:
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            with patch("pathlib.Path.write_text", side_effect=OSError("perm")):
                assert unsubscribe("fail@test.com") is False


class TestIsSubscribed:
    def test_subscribed(self, tmp_path: Path) -> None:
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert is_subscribed("ok@test.com") is True

    def test_unsubscribed(self, tmp_path: Path) -> None:
        (tmp_path / "unsubscribe.json").write_text(json.dumps(["out@test.com"]))
        with patch("src.notifications.NOTIFICATIONS_DIR", str(tmp_path)):
            assert is_subscribed("out@test.com") is False


class TestSendNotifications:
    def test_loads_default_profiles(self) -> None:
        digest = make_digest()
        with patch("src.notifications.build_digest", return_value=digest):
            with patch("src.notifications._load_profiles", return_value=[]):
                with patch("src.notifications._load_unsubscribed", return_value=set()):
                    results = send_notifications("s")
                    assert results == []

    def test_no_digest(self, tmp_path: Path) -> None:
        with patch("src.notifications.build_digest", return_value=None):
            assert send_notifications("nope") == []

    def test_disabled_profile_skipped(self) -> None:
        digest = make_digest()
        profile = make_profile(enabled=False)
        with patch("src.notifications.build_digest", return_value=digest):
            with patch("src.notifications._load_unsubscribed", return_value=set()):
                assert send_notifications("s", profiles=[profile]) == []

    def test_category_filter_no_match(self) -> None:
        digest = make_digest()
        profile = make_profile(categories=["NonExistent"])
        with patch("src.notifications.build_digest", return_value=digest):
            with patch("src.notifications._load_unsubscribed", return_value=set()):
                assert send_notifications("s", profiles=[profile]) == []

    def test_unsubscribed_email_skipped(self) -> None:
        digest = make_digest()
        profile = make_profile()
        with patch("src.notifications.build_digest", return_value=digest):
            with patch("src.notifications._load_unsubscribed", return_value={"test@example.com"}):
                assert send_notifications("s", profiles=[profile]) == []

    def test_sends_email_slack_discord(self) -> None:
        digest = make_digest()
        profile = make_profile(slack_webhook="https://s", discord_webhook="https://d")
        with patch("src.notifications.build_digest", return_value=digest):
            with patch("src.notifications._load_unsubscribed", return_value=set()):
                with patch("src.notifications.send_email", return_value=NotificationResult("email", True)):
                    with patch("src.notifications.send_slack", return_value=NotificationResult("slack", True)):
                        with patch("src.notifications.send_discord", return_value=NotificationResult("discord", True)):
                            results = send_notifications("s", profiles=[profile])
                            assert len(results) == 3
