"""AI-powered GitHub issue triage.

Automatically labels, prioritizes, and routes GitHub issues
based on content analysis and keyword matching.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Issue priority level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(Enum):
    """Issue category."""

    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    QUESTION = "question"
    OTHER = "other"


@dataclass
class TriageResult:
    """Result of triaging an issue."""

    issue_number: int
    title: str
    priority: Priority
    category: IssueCategory
    suggested_labels: list[str]
    suggested_assignee: str | None
    confidence: float
    reasoning: str


# ---------------------------------------------------------------------------
# Keyword dictionaries for triage
# ---------------------------------------------------------------------------

BUG_KEYWORDS: frozenset[str] = frozenset(
    {
        "bug",
        "error",
        "crash",
        "fail",
        "broken",
        "issue",
        "problem",
        "exception",
        "traceback",
        "not working",
        "doesn't work",
        "regression",
    }
)

FEATURE_KEYWORDS: frozenset[str] = frozenset(
    {
        "feature",
        "request",
        "enhancement",
        "proposal",
        "idea",
        "suggestion",
        "would be nice",
        "can we add",
        "please add",
    }
)

SECURITY_KEYWORDS: frozenset[str] = frozenset(
    {
        "security",
        "vulnerability",
        "cve",
        "exploit",
        "xss",
        "injection",
        "authentication",
        "authorization",
        "data leak",
        "exposed",
    }
)

PERFORMANCE_KEYWORDS: frozenset[str] = frozenset(
    {
        "performance",
        "slow",
        "timeout",
        "latency",
        "memory",
        "cpu",
        "optimization",
        "bottleneck",
    }
)

DOCUMENTATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "documentation",
        "docs",
        "readme",
        "example",
        "tutorial",
        "how to",
        "guide",
        "missing info",
    }
)

QUESTION_KEYWORDS: frozenset[str] = frozenset(
    {
        "question",
        "how do i",
        "how to",
        "what is",
        "why",
        "help",
        "support",
        "clarification",
    }
)

CRITICAL_KEYWORDS: frozenset[str] = frozenset(
    {
        "critical",
        "urgent",
        "production",
        "down",
        "outage",
        "data loss",
        "security vulnerability",
        "breaking change",
    }
)

HIGH_KEYWORDS: frozenset[str] = frozenset(
    {
        "important",
        "blocking",
        "blocker",
        "regression",
        "broken",
        "error",
        "failure",
    }
)

# Module assignment based on file paths
MODULE_ASSIGNEES: dict[str, str] = {
    "src/scraper.py": "Fatal1tyBarucco",
    "src/parser.py": "Fatal1tyBarucco",
    "src/main.py": "Fatal1tyBarucco",
    "src/generator.py": "Fatal1tyBarucco",
    "src/api.py": "Fatal1tyBarucco",
    "src/ai_automation.py": "Fatal1tyBarucco",
    "src/salesforce.py": "Fatal1tyBarucco",
    "tests/": "Fatal1tyBarucco",
}


class IssueTriager:
    """Triages GitHub issues automatically."""

    def __init__(self, repo: str | None = None) -> None:
        self._repo = repo

    def triage_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
    ) -> TriageResult:
        """Triage a single issue.

        Args:
            title: Issue title.
            body: Issue body text.
            labels: Existing labels on the issue.

        Returns:
            TriageResult with classification and suggestions.
        """
        combined_text = f"{title} {body}".lower()

        # Determine category
        category, cat_confidence = self._classify_category(combined_text)

        # Determine priority
        priority, pri_confidence = self._classify_priority(combined_text, labels or [])

        # Generate label suggestions
        suggested_labels = self._suggest_labels(category, priority, combined_text)

        # Suggest assignee based on content
        assignee = self._suggest_assignee(combined_text)

        # Generate reasoning
        reasoning = self._generate_reasoning(category, priority, combined_text)

        confidence = (cat_confidence + pri_confidence) / 2

        return TriageResult(
            issue_number=0,
            title=title,
            priority=priority,
            category=category,
            suggested_labels=suggested_labels,
            suggested_assignee=assignee,
            confidence=confidence,
            reasoning=reasoning,
        )

    def triage_github_issue(self, issue_number: int) -> TriageResult | None:
        """Triage a GitHub issue by number.

        Args:
            issue_number: The GitHub issue number.

        Returns:
            TriageResult or None if issue not found.
        """
        if not self._repo:
            return None

        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "view",
                    str(issue_number),
                    "--repo",
                    self._repo,
                    "--json",
                    "title,body,labels",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return None

            data = json.loads(result.stdout)
            title = data.get("title", "")
            body = data.get("body", "")
            labels = [label.get("name", "") for label in data.get("labels", [])]

            triage = self.triage_issue(title, body, labels)
            triage.issue_number = issue_number
            return triage

        except subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError:
            return None

    def apply_triage(self, result: TriageResult) -> bool:
        """Apply triage results to a GitHub issue.

        Args:
            result: The TriageResult to apply.

        Returns:
            True if successful, False otherwise.
        """
        if not self._repo or result.issue_number == 0:
            return False

        try:
            # Add labels
            if result.suggested_labels:
                subprocess.run(
                    [
                        "gh",
                        "issue",
                        "edit",
                        str(result.issue_number),
                        "--repo",
                        self._repo,
                        "--add-label",
                        ",".join(result.suggested_labels),
                    ],
                    capture_output=True,
                    timeout=10,
                )

            # Add comment with reasoning
            comment = f"""## 🤖 AI Triage

**Priority:** {result.priority.value.upper()}
**Category:** {result.category.value}
**Confidence:** {result.confidence:.0%}

### Reasoning
{result.reasoning}

---
*Auto-generated by IssueTriager*"""

            subprocess.run(
                [
                    "gh",
                    "issue",
                    "comment",
                    str(result.issue_number),
                    "--repo",
                    self._repo,
                    "--body",
                    comment,
                ],
                capture_output=True,
                timeout=10,
            )

            return True

        except subprocess.TimeoutExpired, FileNotFoundError:
            return False

    def _classify_category(self, text: str) -> tuple[IssueCategory, float]:
        """Classify issue category."""
        scores: dict[IssueCategory, float] = {}

        for cat, keywords in [
            (IssueCategory.BUG, BUG_KEYWORDS),
            (IssueCategory.FEATURE_REQUEST, FEATURE_KEYWORDS),
            (IssueCategory.SECURITY, SECURITY_KEYWORDS),
            (IssueCategory.PERFORMANCE, PERFORMANCE_KEYWORDS),
            (IssueCategory.DOCUMENTATION, DOCUMENTATION_KEYWORDS),
            (IssueCategory.QUESTION, QUESTION_KEYWORDS),
        ]:
            matches = sum(1 for kw in keywords if kw in text)
            if matches > 0:
                scores[cat] = matches / len(keywords)

        if scores:
            best_cat = max(scores, key=lambda k: scores[k])
            return best_cat, min(1.0, 0.5 + scores[best_cat])

        return IssueCategory.OTHER, 0.2

    def _classify_priority(self, text: str, labels: list[str]) -> tuple[Priority, float]:
        """Classify issue priority."""
        labels_lower = [label.lower() for label in labels]

        # Check for critical indicators
        if any(kw in text for kw in CRITICAL_KEYWORDS):
            return Priority.CRITICAL, 0.9
        if "critical" in labels_lower or "urgent" in labels_lower:
            return Priority.CRITICAL, 0.95

        # Check for high priority
        if any(kw in text for kw in HIGH_KEYWORDS):
            return Priority.HIGH, 0.7
        if "high" in labels_lower or "important" in labels_lower:
            return Priority.HIGH, 0.8

        # Check for low priority
        if any(kw in text for kw in QUESTION_KEYWORDS):
            return Priority.LOW, 0.6
        if "question" in labels_lower or "low" in labels_lower:
            return Priority.LOW, 0.7

        return Priority.MEDIUM, 0.5

    def _suggest_labels(self, category: IssueCategory, priority: Priority, text: str) -> list[str]:
        """Suggest labels for the issue."""
        labels: list[str] = []

        # Category label
        label_map = {
            IssueCategory.BUG: "bug",
            IssueCategory.FEATURE_REQUEST: "enhancement",
            IssueCategory.SECURITY: "security",
            IssueCategory.PERFORMANCE: "performance",
            IssueCategory.DOCUMENTATION: "documentation",
            IssueCategory.QUESTION: "question",
        }
        if category in label_map:
            labels.append(label_map[category])

        # Priority label
        if priority in (Priority.CRITICAL, Priority.HIGH):
            labels.append("priority:high")

        # Module-specific labels
        if "scraper" in text or "playwright" in text:
            labels.append("module:scraper")
        if "parser" in text or "extract" in text:
            labels.append("module:parser")
        if "api" in text or "endpoint" in text:
            labels.append("module:api")
        if "test" in text:
            labels.append("module:tests")

        return labels

    def _suggest_assignee(self, text: str) -> str | None:
        """Suggest assignee based on content."""
        for path, assignee in MODULE_ASSIGNEES.items():
            if path.rstrip("/").lower() in text:
                return assignee
        return None

    def _generate_reasoning(self, category: IssueCategory, priority: Priority, text: str) -> str:
        """Generate human-readable reasoning."""
        reasons: list[str] = []

        reasons.append(f"Classified as **{category.value}** based on keyword analysis.")

        if priority == Priority.CRITICAL:
            reasons.append("Marked as **CRITICAL** due to production/security indicators.")
        elif priority == Priority.HIGH:
            reasons.append("Marked as **HIGH** priority due to blocking/regression indicators.")
        elif priority == Priority.LOW:
            reasons.append(
                "Marked as **LOW** priority — appears to be a question or documentation request."
            )

        return " ".join(reasons)
