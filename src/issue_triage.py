"""AI-powered GitHub issue triage.

Automatically labels, prioritizes, and routes GitHub issues
based on content analysis and keyword matching.
"""

from __future__ import annotations

import json
from typing import Any
import subprocess
from dataclasses import dataclass
from enum import Enum

from .llm_service import LLMService


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
        self._llm = LLMService()

    async def triage_issue(
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
        combined_text = f"Title: {title}\nBody: {body}"

        # 1. Use LLM for category and priority classification
        categories = [cat.value for cat in IssueCategory]
        priorities = [pri.value for pri in Priority]

        system_prompt = (
            "You are a GitHub Issue Triage expert. Analyze the issue and return a JSON object "
            "with the following keys: 'category' (one of the provided categories), "
            "'priority' (one of the provided priorities), 'confidence' (0.0-1.0), "
            "and 'reasoning' (a concise explanation). "
            'Example output: {"category": "bug", "priority": "high", "confidence": 0.9, "reasoning": "..."}'
        )

        user_prompt = (
            f"Categories: {categories}\nPriorities: {priorities}\n\n"
            f"Issue content:\n{combined_text}"
        )

        llm_result = await self._llm.generate_text(user_prompt, system_prompt)

        if not llm_result:
            parsed: dict[str, Any] = {}
        else:
            import json

            try:
                start_idx = llm_result.find("{")
                end_idx = llm_result.rfind("}") + 1
                parsed = json.loads(llm_result[start_idx:end_idx]) if start_idx != -1 else {}
            except (ValueError, IndexError):
                parsed = {}

        # Fallbacks
        try:
            category = IssueCategory(parsed.get("category", "other"))
        except ValueError:
            category = IssueCategory.OTHER

        try:
            priority = Priority(parsed.get("priority", "medium"))
        except ValueError:
            priority = Priority.MEDIUM

        confidence = float(parsed.get("confidence", 0.5))
        reasoning = parsed.get("reasoning", "Classified based on general content analysis.")

        # Generate label suggestions and assignee based on metadata
        suggested_labels = self._suggest_labels(category, priority, combined_text.lower())
        assignee = self._suggest_assignee(combined_text.lower())

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

    async def triage_github_issue(self, issue_number: int) -> TriageResult | None:
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

            triage = await self.triage_issue(title, body, labels)
            triage.issue_number = issue_number
            return triage

        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
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

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

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
