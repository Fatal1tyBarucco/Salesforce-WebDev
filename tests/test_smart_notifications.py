"""Tests for smart_notifications module."""

from pathlib import Path

from src.smart_notifications import (
    SmartNotificationEngine,
    UserPreferences,
    Notification,
    NotificationPriority,
)


def test_filter_notifications_by_interest():
    """smart_notifications: filters by user interests."""
    engine = SmartNotificationEngine()
    user = UserPreferences(user_id="test", interests=["security"])

    notifications = [
        Notification("Security fix", "XSS vulnerability patched", NotificationPriority.HIGH, "security", "summer_26", 0.9, []),
        Notification("New feature", "Added analytics dashboard", NotificationPriority.NORMAL, "new_feature", "summer_26", 0.5, []),
    ]

    filtered = engine.filter_notifications(notifications, user)

    assert len(filtered) == 1
    assert filtered[0].category == "security"


def test_filter_notifications_by_priority():
    """smart_notifications: filters by minimum priority."""
    engine = SmartNotificationEngine()
    user = UserPreferences(user_id="test", min_priority=NotificationPriority.HIGH)

    notifications = [
        Notification("Urgent fix", "Critical bug", NotificationPriority.URGENT, "bug_fix", "summer_26", 0.9, []),
        Notification("Minor update", "Cosmetic change", NotificationPriority.LOW, "general", "summer_26", 0.3, []),
    ]

    filtered = engine.filter_notifications(notifications, user)

    assert len(filtered) == 1
    assert filtered[0].priority == NotificationPriority.URGENT


def test_filter_notifications_by_category():
    """smart_notifications: filters by category."""
    engine = SmartNotificationEngine()
    user = UserPreferences(user_id="test", categories=["security", "performance"])

    notifications = [
        Notification("Security fix", "XSS patch", NotificationPriority.HIGH, "security", "summer_26", 0.9, []),
        Notification("Bug fix", "Login error", NotificationPriority.NORMAL, "bug_fix", "summer_26", 0.5, []),
    ]

    filtered = engine.filter_notifications(notifications, user)

    assert len(filtered) == 1
    assert filtered[0].category == "security"


def test_generate_digest(tmp_path: Path) -> None:
    """smart_notifications: generate digest aggregates notifications."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    user = UserPreferences(user_id="test", interests=["security"])

    notifications = [
        Notification("Security fix", "XSS patch", NotificationPriority.URGENT, "security", "summer_26", 0.9, []),
        Notification("Security fix", "Auth patch", NotificationPriority.HIGH, "security", "summer_26", 0.8, []),
    ]

    digest = engine.generate_digest(notifications, user)

    assert digest.user_id == "test"
    assert digest.total_count == 2
    assert digest.urgent_count == 1
    assert digest.high_count == 1
    assert len(digest.summary_text) > 0


def test_classify_notification():
    """smart_notifications: classifies notification content."""
    engine = SmartNotificationEngine()

    notif = engine.classify_notification(
        title="Critical security vulnerability",
        body="Found CVE in authentication module",
        release_slug="summer_26",
    )

    assert notif.priority == NotificationPriority.URGENT
    assert notif.category == "security"
    assert notif.relevance_score > 0.7


def test_generate_from_release(tmp_path: Path) -> None:
    """smart_notifications: generates notifications from release."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "security.md").write_text(
        "# Security\n\n## Security Features\n\n"
        "- Security patch for XSS vulnerability\n"
        "- Performance improvement for queries\n"
    )

    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = engine.generate_from_release("summer_26")

    assert len(notifications) > 0
    assert all(n.source_release == "summer_26" for n in notifications)


def test_generate_from_release_returns_empty_for_missing(tmp_path: Path) -> None:
    """smart_notifications: returns empty for missing release."""
    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = engine.generate_from_release("nonexistent")

    assert notifications == []


def test_notification_priority_comparison():
    """smart_notifications: priority ordering works correctly."""
    engine = SmartNotificationEngine()
    user = UserPreferences(user_id="test", min_priority=NotificationPriority.NORMAL)

    notifications = [
        Notification("Low", "Minor", NotificationPriority.LOW, "general", "summer_26", 0.3, []),
        Notification("Normal", "Update", NotificationPriority.NORMAL, "general", "summer_26", 0.5, []),
        Notification("High", "Important", NotificationPriority.HIGH, "general", "summer_26", 0.7, []),
    ]

    filtered = engine.filter_notifications(notifications, user)

    assert len(filtered) == 2
    assert filtered[0].priority == NotificationPriority.HIGH
    assert filtered[1].priority == NotificationPriority.NORMAL


def test_empty_interests_matches_all():
    """smart_notifications: empty interests match all notifications."""
    engine = SmartNotificationEngine()
    user = UserPreferences(user_id="test", interests=[])

    notifications = [
        Notification("Anything", "Content", NotificationPriority.NORMAL, "general", "summer_26", 0.5, []),
    ]

    filtered = engine.filter_notifications(notifications, user)

    assert len(filtered) == 1


def test_digest_empty_notifications():
    """smart_notifications: digest handles empty notifications."""
    engine = SmartNotificationEngine()
    user = UserPreferences(user_id="test")

    digest = engine.generate_digest([], user)

    assert digest.total_count == 0
    assert "No new notifications" in digest.summary_text


def test_generate_from_release_skips_dotfiles(tmp_path: Path) -> None:
    """smart_notifications: skips dotfiles in release directory."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / ".hidden.md").write_text(
        "# Hidden\n\n- Hidden feature\n"
    )
    (release_dir / "visible.md").write_text(
        "# Visible\n\n- Important security feature for auth\n"
    )

    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = engine.generate_from_release("summer_26")

    assert len(notifications) == 1


def test_classify_notification_performance():
    """smart_notifications: classifies performance notifications."""
    engine = SmartNotificationEngine()

    notif = engine.classify_notification(
        title="Performance improvement",
        body="Optimized query execution speed",
        release_slug="summer_26",
    )

    assert notif.category == "performance"
    assert notif.priority == NotificationPriority.NORMAL


def test_classify_notification_bug_fix():
    """smart_notifications: classifies bug fix notifications."""
    engine = SmartNotificationEngine()

    notif = engine.classify_notification(
        title="Bug fix for login page",
        body="Fixed error in form validation",
        release_slug="summer_26",
    )

    assert notif.category == "bug_fix"
    assert notif.priority == NotificationPriority.HIGH


def test_classify_notification_new_feature():
    """smart_notifications: classifies new feature notifications."""
    engine = SmartNotificationEngine()

    notif = engine.classify_notification(
        title="New feature: Analytics",
        body="Added analytics dashboard",
        release_slug="summer_26",
    )

    assert notif.category == "new_feature"
    assert notif.priority == NotificationPriority.NORMAL


def test_classify_notification_low_priority():
    """smart_notifications: classifies low priority notifications."""
    engine = SmartNotificationEngine()

    notif = engine.classify_notification(
        title="Minor cosmetic update",
        body="Low priority change",
        release_slug="summer_26",
    )

    assert notif.priority == NotificationPriority.LOW


def test_extract_key_features_limits_count(tmp_path: Path) -> None:
    """smart_notifications: limits key features to 5."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    features = "\n".join([f"- Feature {i}: Important description" for i in range(10)])
    (release_dir / "features.md").write_text(f"# Features\n\n{features}")

    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = engine.generate_from_release("summer_26")

    assert len(notifications) <= 5


def test_relevance_score_capping():
    """smart_notifications: relevance score capped at 1.0."""
    engine = SmartNotificationEngine()

    notif = engine.classify_notification(
        title="Critical security vulnerability breaking change",
        body="Urgent security fix",
        release_slug="summer_26",
    )

    assert notif.relevance_score <= 1.0


def test_extract_category_h2_heading(tmp_path: Path) -> None:
    """smart_notifications: extracts category from ## heading."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "## Agentforce Features\n\n- Important feature\n"
    )

    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = engine.generate_from_release("summer_26")

    assert len(notifications) > 0
    assert notifications[0].category == "Agentforce Features"


def test_extract_category_fallback(tmp_path: Path) -> None:
    """smart_notifications: uses filename as fallback category."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "my_features.md").write_text(
        "- Feature without heading\n"
    )

    engine = SmartNotificationEngine(base_dir=str(tmp_path))
    notifications = engine.generate_from_release("summer_26")

    assert len(notifications) > 0
    assert "My Features" in notifications[0].category
