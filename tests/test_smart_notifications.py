"""Tests for smart_notifications module."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.smart_notifications import (
    SmartNotificationEngine,
    UserPreferences,
    NotificationPriority,
    Notification,
    DeliveryChannel,
)


def test_filter_notifications_by_interest():
    """smart_notifications: filters by interest keywords."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    user = UserPreferences(user_id="test", interests=["security"], categories=[])
    notifications = [
        Notification(
            "Security update",
            "Body",
            NotificationPriority.HIGH,
            "security",
            "r1",
            0.9,
            [DeliveryChannel.CONSOLE],
        ),
        Notification(
            "Marketing feature",
            "Body",
            NotificationPriority.NORMAL,
            "marketing",
            "r1",
            0.5,
            [DeliveryChannel.CONSOLE],
        ),
    ]
    filtered = engine.filter_notifications(notifications, user)
    assert len(filtered) == 1
    assert filtered[0].title == "Security update"


def test_filter_notifications_by_priority():
    """smart_notifications: filters by minimum priority."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    user = UserPreferences(
        user_id="test", interests=[], categories=[], min_priority=NotificationPriority.HIGH
    )
    notifications = [
        Notification(
            "Urgent", "Body", NotificationPriority.URGENT, "a", "r1", 0.9, [DeliveryChannel.CONSOLE]
        ),
        Notification(
            "Low", "Body", NotificationPriority.LOW, "b", "r1", 0.3, [DeliveryChannel.CONSOLE]
        ),
    ]
    filtered = engine.filter_notifications(notifications, user)
    assert len(filtered) == 1
    assert filtered[0].title == "Urgent"


def test_filter_notifications_by_category():
    """smart_notifications: filters by category."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    user = UserPreferences(user_id="test", interests=[], categories=["security"])
    notifications = [
        Notification(
            "A",
            "Body",
            NotificationPriority.NORMAL,
            "security",
            "r1",
            0.5,
            [DeliveryChannel.CONSOLE],
        ),
        Notification(
            "B",
            "Body",
            NotificationPriority.NORMAL,
            "marketing",
            "r1",
            0.5,
            [DeliveryChannel.CONSOLE],
        ),
    ]
    filtered = engine.filter_notifications(notifications, user)
    assert len(filtered) == 1


def test_generate_digest(tmp_path: Path):
    """smart_notifications: generates digest from notifications."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    user = UserPreferences(user_id="test", interests=[], categories=[])
    notifications = [
        Notification(
            "Title",
            "Body",
            NotificationPriority.HIGH,
            "security",
            "r1",
            0.9,
            [DeliveryChannel.CONSOLE],
        ),
    ]

    with patch.object(engine, "_generate_summary", new_callable=AsyncMock) as mock_summary:
        mock_summary.return_value = "Summary text"
        digest = asyncio.run(engine.generate_digest(notifications, user))

    assert digest.total_count == 1
    assert digest.high_count == 1
    assert digest.summary_text == "Summary text"


def test_classify_notification():
    """smart_notifications: classifies notification content."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"priority": "HIGH", "category": "security", "relevance": 0.9}'

        notif = asyncio.run(engine.classify_notification("Title", "Body", "summer_26"))

    assert notif.priority == NotificationPriority.HIGH
    assert notif.category == "security"
    assert notif.relevance_score == 0.9


def test_generate_from_release(tmp_path: Path):
    """smart_notifications: generates notifications from release."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir(parents=True)
    (release_dir / "security.md").write_text(
        "# Security\n\n- Fix auth vulnerability in login flow\n- Improve encryption standards\n"
    )

    engine = SmartNotificationEngine(base_dir=str(tmp_path))

    with patch.object(engine, "classify_notification", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = Notification(
            "Fix auth vulnerability",
            "Body",
            NotificationPriority.HIGH,
            "security",
            "summer_26",
            0.9,
            [DeliveryChannel.CONSOLE],
        )
        notifications = asyncio.run(engine.generate_from_release("summer_26"))

    assert len(notifications) == 2
    assert all("security" in n.category.lower() for n in notifications)


def test_generate_from_release_returns_empty_for_missing(tmp_path: Path):
    """smart_notifications: returns empty for nonexistent release."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = asyncio.run(engine.generate_from_release("nonexistent"))
    assert notifications == []


def test_notification_priority_comparison():
    """smart_notifications: priority comparison works."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    user = UserPreferences(
        user_id="test", interests=[], categories=[], min_priority=NotificationPriority.NORMAL
    )
    notifications = [
        Notification(
            "A", "Body", NotificationPriority.URGENT, "a", "r1", 0.9, [DeliveryChannel.CONSOLE]
        ),
        Notification(
            "B", "Body", NotificationPriority.LOW, "b", "r1", 0.3, [DeliveryChannel.CONSOLE]
        ),
    ]
    filtered = engine.filter_notifications(notifications, user)
    assert len(filtered) == 1


def test_empty_interests_matches_all():
    """smart_notifications: empty interests match all notifications."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    user = UserPreferences(user_id="test", interests=[], categories=[])
    notifications = [
        Notification(
            "A", "Body", NotificationPriority.NORMAL, "a", "r1", 0.5, [DeliveryChannel.CONSOLE]
        ),
        Notification(
            "B", "Body", NotificationPriority.NORMAL, "b", "r1", 0.5, [DeliveryChannel.CONSOLE]
        ),
    ]
    filtered = engine.filter_notifications(notifications, user)
    assert len(filtered) == 2


def test_digest_empty_notifications(tmp_path: Path):
    """smart_notifications: digest handles empty notifications."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    user = UserPreferences(user_id="test", interests=[], categories=[])

    with patch.object(engine, "_generate_summary", new_callable=AsyncMock) as mock_summary:
        mock_summary.return_value = "No notifications."
        digest = asyncio.run(engine.generate_digest([], user))

    assert digest.total_count == 0
    assert digest.summary_text == "No notifications."


def test_generate_from_release_skips_dotfiles(tmp_path: Path):
    """smart_notifications: skips dotfiles in release directory."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir(parents=True)
    (release_dir / ".hidden.md").write_text("# Hidden\n\n- Hidden feature\n")
    (release_dir / "visible.md").write_text("# Visible\n\n- Important feature\n")

    engine = SmartNotificationEngine(base_dir=str(tmp_path))

    with patch.object(engine, "classify_notification", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = Notification(
            "Feature",
            "Body",
            NotificationPriority.NORMAL,
            "general",
            "summer_26",
            0.5,
            [DeliveryChannel.CONSOLE],
        )
        notifications = asyncio.run(engine.generate_from_release("summer_26"))

    assert len(notifications) == 1


def test_classify_notification_performance():
    """smart_notifications: classifies performance notification."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = (
            '{"priority": "NORMAL", "category": "performance", "relevance": 0.6}'
        )
        notif = asyncio.run(engine.classify_notification("Performance fix", "Body", "r1"))

    assert notif.priority == NotificationPriority.NORMAL
    assert notif.category == "performance"


def test_classify_notification_bug_fix():
    """smart_notifications: classifies bug fix notification."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"priority": "HIGH", "category": "bug", "relevance": 0.8}'
        notif = asyncio.run(engine.classify_notification("Bug fix", "Body", "r1"))

    assert notif.category == "bug"


def test_classify_notification_new_feature():
    """smart_notifications: classifies new feature notification."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"priority": "NORMAL", "category": "feature", "relevance": 0.7}'
        notif = asyncio.run(engine.classify_notification("New feature", "Body", "r1"))

    assert notif.category == "feature"


def test_classify_notification_low_priority():
    """smart_notifications: classifies low priority notification."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"priority": "LOW", "category": "docs", "relevance": 0.3}'
        notif = asyncio.run(engine.classify_notification("Documentation update", "Body", "r1"))

    assert notif.priority == NotificationPriority.LOW


def test_extract_key_features_limits_count():
    """smart_notifications: extracts key features with limit."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    content = "# Features\n" + "\n".join(
        [f"- Feature {i}: Detailed description of feature {i}" for i in range(10)]
    )
    features = engine._extract_key_features(content)
    assert len(features) == 5


def test_relevance_score_capping(tmp_path: Path):
    """smart_notifications: relevance score capped at 1.0."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"priority": "HIGH", "category": "security", "relevance": 1.5}'
        notif = asyncio.run(engine.classify_notification("Title", "Body", "r1"))

    assert notif.relevance_score <= 1.0


def test_extract_category_h2_heading():
    """smart_notifications: extracts category from h2 heading."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    content = "## Security Updates\n\n- Feature\n"
    cat = engine._extract_category(content, "fallback")
    assert "Security" in cat


def test_extract_category_fallback():
    """smart_notifications: falls back to file stem when no heading found."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")
    content = "Just some text without headings\n"
    cat = engine._extract_category(content, "my_category")
    assert "My Category" in cat


def test_classify_notification_invalid_json():
    """smart_notifications: handles invalid JSON from LLM gracefully."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "not valid json at all"
        notif = asyncio.run(engine.classify_notification("Title", "Body", "r1"))

    assert notif.priority == NotificationPriority.NORMAL
    assert notif.category == "general"


def test_classify_notification_invalid_priority():
    """smart_notifications: handles invalid priority from LLM gracefully."""
    engine = SmartNotificationEngine(base_dir="/tmp/nonexistent")

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = '{"priority": "INVALID", "category": "security", "relevance": 0.5}'
        notif = asyncio.run(engine.classify_notification("Title", "Body", "r1"))

    assert notif.priority == NotificationPriority.NORMAL


def test_generate_summary_with_notifications(tmp_path: Path):
    """smart_notifications: _generate_summary produces summary for notifications."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = [
        Notification(
            "Urgent",
            "Body",
            NotificationPriority.URGENT,
            "security",
            "r1",
            0.9,
            [DeliveryChannel.CONSOLE],
        ),
        Notification(
            "High",
            "Body",
            NotificationPriority.HIGH,
            "marketing",
            "r1",
            0.7,
            [DeliveryChannel.CONSOLE],
        ),
    ]

    with patch.object(engine._llm, "generate_text", new_callable=AsyncMock) as mock_llm:
        mock_llm.return_value = "You have 2 urgent notifications."
        summary = asyncio.run(engine._generate_summary(notifications, 1, 1))

    assert "urgent" in summary.lower() or "notification" in summary.lower()
