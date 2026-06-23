"""Tests for issue_triage module."""

from unittest.mock import MagicMock, patch

from src.issue_triage import IssueCategory, IssueTriager, Priority, TriageResult


def test_triage_bug_report():
    """issue_triage: classifies bug reports."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Bug: Login fails with error",
        body="Getting exception when trying to log in. Error: Authentication failed.",
    )

    assert result.category == IssueCategory.BUG
    assert result.priority in (Priority.HIGH, Priority.CRITICAL)
    assert "bug" in result.suggested_labels


def test_triage_feature_request():
    """issue_triage: classifies feature requests."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Feature request: Add export to CSV",
        body="It would be nice to have a CSV export feature for the dashboard.",
    )

    assert result.category == IssueCategory.FEATURE_REQUEST
    assert "enhancement" in result.suggested_labels


def test_triage_security_issue():
    """issue_triage: classifies security issues."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Security vulnerability in authentication",
        body="Found a CVE vulnerability in the auth module that allows unauthorized access.",
    )

    assert result.category == IssueCategory.SECURITY
    assert "security" in result.suggested_labels
    assert result.priority in (Priority.CRITICAL, Priority.HIGH)


def test_triage_performance_issue():
    """issue_triage: classifies performance issues."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Performance degradation in scraper",
        body="The scraper is now much slower, taking 10x longer than before.",
    )

    assert result.category == IssueCategory.PERFORMANCE
    assert "performance" in result.suggested_labels


def test_triage_question():
    """issue_triage: classifies questions."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="How do I configure the pipeline?",
        body="I need help setting up the release notes pipeline. What are the steps?",
    )

    assert result.category == IssueCategory.QUESTION
    assert result.priority == Priority.LOW


def test_triage_critical_priority():
    """issue_triage: marks production issues as critical."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Production outage",
        body="The production server is down and users cannot access the application.",
    )

    assert result.priority == Priority.CRITICAL


def test_triage_suggests_assignee():
    """issue_triage: suggests assignee based on module keywords."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Scraper fails on new page structure",
        body="The scraper module fails to extract content from the new page layout. See src/scraper.py line 100.",
    )

    assert result.suggested_assignee is not None


def test_triage_generates_reasoning():
    """issue_triage: generates human-readable reasoning."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Bug in parser",
        body="The parser crashes when encountering empty tables.",
    )

    assert len(result.reasoning) > 0
    assert "bug" in result.reasoning.lower() or "BUG" in result.reasoning


def test_triage_other_category():
    """issue_triage: classifies unrecognized issues as OTHER."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Random title",
        body="Some random text without any keywords.",
    )

    assert result.category == IssueCategory.OTHER


def test_triage_confidence_range():
    """issue_triage: confidence is between 0 and 1."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Test issue",
        body="Test body text.",
    )

    assert 0.0 <= result.confidence <= 1.0


def test_triage_github_issue_with_mock():
    """issue_triage: triage_github_issue parses gh output."""
    triager = IssueTriager(repo="owner/repo")

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = '{"title":"Bug","body":"Login fails","labels":[{"name":"bug"}]}'

    with patch("src.issue_triage.subprocess.run", return_value=mock_result):
        result = triager.triage_github_issue(123)

        assert result is not None
        assert result.issue_number == 123
        assert result.category == IssueCategory.BUG


def test_triage_github_issue_returns_none_without_repo():
    """issue_triage: triage_github_issue returns None without repo."""
    triager = IssueTriager()
    assert triager.triage_github_issue(123) is None


def test_triage_github_issue_returns_none_on_failure():
    """issue_triage: triage_github_issue returns None on subprocess failure."""
    triager = IssueTriager(repo="owner/repo")

    mock_result = MagicMock()
    mock_result.returncode = 1

    with patch("src.issue_triage.subprocess.run", return_value=mock_result):
        assert triager.triage_github_issue(123) is None


def test_triage_github_issue_returns_none_on_timeout():
    """issue_triage: triage_github_issue returns None on timeout."""
    import subprocess as sp

    triager = IssueTriager(repo="owner/repo")

    with patch(
        "src.issue_triage.subprocess.run", side_effect=sp.TimeoutExpired(cmd="gh", timeout=10)
    ):
        assert triager.triage_github_issue(123) is None


def test_triage_github_issue_returns_none_on_invalid_json():
    """issue_triage: triage_github_issue returns None on invalid JSON."""
    triager = IssueTriager(repo="owner/repo")

    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "not json"

    with patch("src.issue_triage.subprocess.run", return_value=mock_result):
        assert triager.triage_github_issue(123) is None


def test_apply_triage_returns_false_without_repo():
    """issue_triage: apply_triage returns False without repo."""
    triager = IssueTriager()
    result = TriageResult(
        issue_number=123,
        title="Test",
        priority=Priority.MEDIUM,
        category=IssueCategory.BUG,
        suggested_labels=["bug"],
        suggested_assignee=None,
        confidence=0.5,
        reasoning="Test",
    )
    assert triager.apply_triage(result) is False


def test_apply_triage_returns_false_without_issue_number():
    """issue_triage: apply_triage returns False without issue number."""
    triager = IssueTriager(repo="owner/repo")
    result = TriageResult(
        issue_number=0,
        title="Test",
        priority=Priority.MEDIUM,
        category=IssueCategory.BUG,
        suggested_labels=["bug"],
        suggested_assignee=None,
        confidence=0.5,
        reasoning="Test",
    )
    assert triager.apply_triage(result) is False


def test_apply_triage_success():
    """issue_triage: apply_triage calls gh commands."""
    triager = IssueTriager(repo="owner/repo")
    result = TriageResult(
        issue_number=123,
        title="Test",
        priority=Priority.MEDIUM,
        category=IssueCategory.BUG,
        suggested_labels=["bug"],
        suggested_assignee=None,
        confidence=0.5,
        reasoning="Test reasoning",
    )

    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("src.issue_triage.subprocess.run", return_value=mock_result):
        assert triager.apply_triage(result) is True


def test_apply_triage_handles_timeout():
    """issue_triage: apply_triage returns False on timeout."""
    import subprocess as sp

    triager = IssueTriager(repo="owner/repo")
    result = TriageResult(
        issue_number=123,
        title="Test",
        priority=Priority.MEDIUM,
        category=IssueCategory.BUG,
        suggested_labels=["bug"],
        suggested_assignee=None,
        confidence=0.5,
        reasoning="Test",
    )

    with patch(
        "src.issue_triage.subprocess.run", side_effect=sp.TimeoutExpired(cmd="gh", timeout=10)
    ):
        assert triager.apply_triage(result) is False


def test_triage_with_labels():
    """issue_triage: uses existing labels for priority."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Issue",
        body="Some issue",
        labels=["critical", "urgent"],
    )

    assert result.priority == Priority.CRITICAL


def test_triage_high_label():
    """issue_triage: uses high label for priority."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Issue",
        body="Some issue",
        labels=["high"],
    )

    assert result.priority == Priority.HIGH


def test_triage_low_label():
    """issue_triage: uses low label for priority."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="Issue",
        body="Some issue",
        labels=["low"],
    )

    assert result.priority == Priority.LOW


def test_triage_api_module_label():
    """issue_triage: suggests API module label."""
    triager = IssueTriager()
    result = triager.triage_issue(
        title="API endpoint returns 500",
        body="The /api/releases endpoint is returning internal server error.",
    )

    assert "module:api" in result.suggested_labels
