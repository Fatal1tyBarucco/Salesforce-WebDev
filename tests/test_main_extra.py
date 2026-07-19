"""Tests for src/main.py — coverage for remaining paths."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from src.main import (
    _check,
    _find_existing_releases,
    _format_entry_table,
    _format_impact_report,
    _format_notification_digest,
    _generate_category_summary,
    _slugify_category,
)
from src.parser import FeatureImpactCategory, FeatureImpactEntry


class TestFindExistingReleases:
    def test_no_dir(self, tmp_path: Path) -> None:
        with patch("src.main.RELEASES_DIR", str(tmp_path / "nope")):
            assert _find_existing_releases() == set()

    def test_with_releases(self, tmp_path: Path) -> None:
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / "cat.md").write_text("## Cat\n\n- Feature\n")
        with patch("src.main.RELEASES_DIR", str(tmp_path)):
            assert "summer_26" in _find_existing_releases()

    def test_skips_files(self, tmp_path: Path) -> None:
        (tmp_path / "file.txt").write_text("hi")
        with patch("src.main.RELEASES_DIR", str(tmp_path)):
            assert _find_existing_releases() == set()


class TestFormatImpactReport:
    def test_with_breaking_and_security(self) -> None:
        report = MagicMock()
        report.total_features = 10
        report.breaking_changes = ["BC1", "BC2"]
        report.security_fixes = ["SF1"]
        report.risk_score = 7.5
        result = _format_impact_report(report, "Summer '26")
        assert "Breaking Changes" in result
        assert "Security Fixes" in result
        assert "7.5" in result

    def test_empty(self) -> None:
        report = MagicMock()
        report.total_features = 0
        report.breaking_changes = []
        report.security_fixes = []
        report.risk_score = 0
        result = _format_impact_report(report, "Test")
        assert "0" in result


class TestFormatNotificationDigest:
    def test_with_notifications(self) -> None:
        digest = MagicMock()
        digest.summary_text = "Summary"
        notif = MagicMock()
        notif.priority = MagicMock(value="high")
        notif.title = "Title"
        notif.body = "Body"
        digest.notifications = [notif]
        result = _format_notification_digest(digest)
        assert "Summary" in result
        assert "Title" in result

    def test_empty(self) -> None:
        digest = MagicMock()
        digest.summary_text = ""
        digest.notifications = []
        result = _format_notification_digest(digest)
        assert "Notification Digest" in result


class TestSlugifyCategory:
    def test_basic(self) -> None:
        assert _slugify_category("Sales & Service") == "sales_service"

    def test_portuguese(self) -> None:
        result = _slugify_category("Segurança & Identidade")
        assert "seguranca" in result


class TestCheck:
    def test_true(self) -> None:
        assert _check(True) == "✅"

    def test_false(self) -> None:
        assert _check(False) == "❌"


class TestFormatEntryTable:
    def test_basic(self) -> None:
        entry = FeatureImpactEntry(
            name="Test Feature",
            available_users=True,
            available_admins=False,
            requires_config=True,
            contact_sf=False,
            confidence=1.0,
        )
        result = _format_entry_table(entry)
        assert "Test Feature" in result
        assert "✅" in result
        assert "❌" in result

    def test_low_confidence(self) -> None:
        entry = FeatureImpactEntry(name="Low Conf", confidence=0.3)
        result = _format_entry_table(entry)
        assert "⚠️" in result

    def test_with_docs_url(self) -> None:
        entry = FeatureImpactEntry(name="With Link")
        result = _format_entry_table(entry, docs_url="https://docs.example.com")
        assert "🔗" in result


class TestGenerateCategorySummary:
    def test_empty(self) -> None:
        cat = FeatureImpactCategory(name="Empty")
        assert _generate_category_summary(cat) == ""

    def test_with_entries(self) -> None:
        cat = FeatureImpactCategory(name="C")
        cat.entries.append(FeatureImpactEntry(name="A", confidence=0.9))
        cat.entries.append(FeatureImpactEntry(name="B", confidence=0.5))
        result = _generate_category_summary(cat)
        assert "2 features" in result
        assert "1 with high confidence" in result
