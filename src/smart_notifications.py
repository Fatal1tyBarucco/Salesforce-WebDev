"""AI-powered smart notifications.

Filters and prioritizes notifications based on user interests,
generates personalized digests, and supports multiple delivery channels.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .config import RELEASES_DIR
from .feature_classifier import FeatureClassifier


class NotificationPriority(Enum):
    """Notification priority level."""

    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class DeliveryChannel(Enum):
    """Notification delivery channel."""

    EMAIL = "email"
    SLACK = "slack"
    DISCORD = "discord"
    WEBHOOK = "webhook"
    CONSOLE = "console"


@dataclass
class UserPreferences:
    """User notification preferences."""

    user_id: str
    interests: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    min_priority: NotificationPriority = NotificationPriority.NORMAL
    channels: list[DeliveryChannel] = field(default_factory=lambda: [DeliveryChannel.CONSOLE])
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8


@dataclass
class Notification:
    """A single notification."""

    title: str
    body: str
    priority: NotificationPriority
    category: str
    source_release: str
    relevance_score: float
    channels: list[DeliveryChannel]


@dataclass
class NotificationDigest:
    """Aggregated notification digest."""

    user_id: str
    notifications: list[Notification]
    total_count: int
    urgent_count: int
    high_count: int
    summary_text: str


class SmartNotificationEngine:
    """Filters and prioritizes notifications based on user interests."""

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir = Path(base_dir)
        self._classifier = FeatureClassifier()

    def filter_notifications(
        self,
        notifications: list[Notification],
        user: UserPreferences,
    ) -> list[Notification]:
        """Filter notifications based on user preferences.

        Args:
            notifications: List of notifications to filter.
            user: User preferences for filtering.

        Returns:
            Filtered and prioritized notifications.
        """
        filtered: list[Notification] = []

        for notif in notifications:
            # Check priority threshold
            if not self._meets_priority_threshold(notif.priority, user.min_priority):
                continue

            # Check interest match
            if not self._matches_interests(notif, user.interests):
                continue

            # Check category match
            if user.categories and notif.category not in user.categories:
                continue

            filtered.append(notif)

        # Sort by priority and relevance
        filtered.sort(key=lambda n: (n.priority.value, -n.relevance_score))

        return filtered

    def generate_digest(
        self,
        notifications: list[Notification],
        user: UserPreferences,
    ) -> NotificationDigest:
        """Generate a personalized notification digest.

        Args:
            notifications: List of notifications to include.
            user: User preferences.

        Returns:
            NotificationDigest with aggregated information.
        """
        filtered = self.filter_notifications(notifications, user)

        urgent_count = sum(1 for n in filtered if n.priority == NotificationPriority.URGENT)
        high_count = sum(1 for n in filtered if n.priority == NotificationPriority.HIGH)

        summary = self._generate_summary(filtered, urgent_count, high_count)

        return NotificationDigest(
            user_id=user.user_id,
            notifications=filtered,
            total_count=len(filtered),
            urgent_count=urgent_count,
            high_count=high_count,
            summary_text=summary,
        )

    def classify_notification(
        self,
        title: str,
        body: str,
        release_slug: str,
    ) -> Notification:
        """Classify and create a notification from content.

        Args:
            title: Notification title.
            body: Notification body.
            release_slug: Source release.

        Returns:
            Classified Notification.
        """
        combined = f"{title} {body}".lower()

        # Determine priority
        priority = self._classify_priority(combined)

        # Determine category
        category = self._classify_category(combined)

        # Calculate relevance score
        relevance = self._calculate_relevance(combined)

        return Notification(
            title=title,
            body=body,
            priority=priority,
            category=category,
            source_release=release_slug,
            relevance_score=relevance,
            channels=[DeliveryChannel.CONSOLE],
        )

    def generate_from_release(self, release_slug: str) -> list[Notification]:
        """Generate notifications from a release.

        Args:
            release_slug: The release directory name.

        Returns:
            List of notifications for the release.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return []

        notifications: list[Notification] = []

        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue

            content = md_file.read_text(encoding="utf-8")
            category = self._extract_category(content, md_file.stem)

            # Extract key features
            features = self._extract_key_features(content)

            for feature in features:
                notif = self.classify_notification(
                    title=feature,
                    body=f"New in {category}: {feature}",
                    release_slug=release_slug,
                )
                notif.category = category
                notifications.append(notif)

        return notifications

    def _meets_priority_threshold(
        self, notif_priority: NotificationPriority, min_priority: NotificationPriority
    ) -> bool:
        """Check if notification meets minimum priority threshold."""
        priority_order = {
            NotificationPriority.LOW: 0,
            NotificationPriority.NORMAL: 1,
            NotificationPriority.HIGH: 2,
            NotificationPriority.URGENT: 3,
        }
        return priority_order[notif_priority] >= priority_order[min_priority]

    def _matches_interests(self, notif: Notification, interests: list[str]) -> bool:
        """Check if notification matches user interests."""
        if not interests:
            return True

        combined = f"{notif.title} {notif.body} {notif.category}".lower()
        return any(interest.lower() in combined for interest in interests)

    def _classify_priority(self, text: str) -> NotificationPriority:
        """Classify notification priority."""
        if any(kw in text for kw in ["critical", "urgent", "security vulnerability", "breaking"]):
            return NotificationPriority.URGENT
        if any(kw in text for kw in ["important", "high", "regression", "bug fix"]):
            return NotificationPriority.HIGH
        if any(kw in text for kw in ["low", "minor", "cosmetic"]):
            return NotificationPriority.LOW
        return NotificationPriority.NORMAL

    def _classify_category(self, text: str) -> str:
        """Classify notification category."""
        if any(kw in text for kw in ["security", "vulnerability", "auth"]):
            return "security"
        if any(kw in text for kw in ["performance", "speed", "optimization"]):
            return "performance"
        if any(kw in text for kw in ["bug", "fix", "error"]):
            return "bug_fix"
        if any(kw in text for kw in ["feature", "new", "add"]):
            return "new_feature"
        return "general"

    def _calculate_relevance(self, text: str) -> float:
        """Calculate relevance score."""
        score = 0.5

        if any(kw in text for kw in ["security", "critical", "urgent"]):
            score += 0.3
        if any(kw in text for kw in ["breaking", "migration"]):
            score += 0.2
        if any(kw in text for kw in ["new feature", "improvement"]):
            score += 0.1

        return min(1.0, score)

    def _extract_category(self, content: str, fallback: str) -> str:
        """Extract category from markdown heading."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 🔗"):
                return line[3:].strip()
            if line.startswith("# ") and "Release" not in line:
                return line[2:].strip()
        return fallback.replace("_", " ").title()

    def _extract_key_features(self, content: str) -> list[str]:
        """Extract key features from markdown content."""
        features: list[str] = []
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                text = line[2:].strip()
                if len(text) > 10:
                    features.append(text)
        return features[:5]  # Limit to top 5 features

    def _generate_summary(
        self,
        notifications: list[Notification],
        urgent_count: int,
        high_count: int,
    ) -> str:
        """Generate digest summary text."""
        if not notifications:
            return "No new notifications matching your interests."

        lines = ["## 📬 Notification Digest"]

        if urgent_count > 0:
            lines.append(
                f"\n🚨 **{urgent_count} urgent** notification(s) require immediate attention."
            )

        if high_count > 0:
            lines.append(f"⚠️ **{high_count} high-priority** notification(s).")

        lines.append(f"\n📋 **{len(notifications)} total** notifications matching your interests.")

        # Group by category
        by_category: dict[str, int] = {}
        for notif in notifications:
            by_category[notif.category] = by_category.get(notif.category, 0) + 1

        if by_category:
            lines.append("\n### By Category")
            for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- {cat}: {count}")

        return "\n".join(lines)
