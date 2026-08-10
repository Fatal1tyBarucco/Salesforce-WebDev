"""Domain models and Pydantic schemas for the Auto-Healing Agent.

Defines strongly-typed request/response structures for webhook events,
LLM analysis outputs, and internal state management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# ── Enums ───────────────────────────────────────────────────────────


class WorkflowConclusion(str, Enum):
    """Possible conclusions for a GitHub Actions workflow run."""

    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"
    NEUTRAL = "neutral"
    SKIPPED = "skipped"
    STALE = "stale"


class HealingOutcome(str, Enum):
    """Possible outcomes of an auto-healing attempt."""

    PULL_REQUEST_CREATED = "pull_request_created"
    INCREMENTAL_FIX_COMMITTED = "incremental_fix_committed"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    ANALYSIS_FAILED = "analysis_failed"
    SKIPPED = "skipped"


# ── Webhook Payload Schemas ─────────────────────────────────────────


class WorkflowRunPayload(BaseModel):  # type: ignore[misc]
    """Schema for the ``workflow_run`` section of a GitHub webhook."""

    id: int = Field(description="Unique identifier for the workflow run")
    name: str = Field(default="", description="Display name of the workflow")
    head_branch: str = Field(default="", description="Branch that triggered the run")
    head_sha: str = Field(default="", description="Commit SHA at HEAD of the branch")
    conclusion: str | None = Field(
        default=None, description="Final status of the run (success, failure, etc.)"
    )
    action: str = Field(default="", description="Webhook action (completed, requested)")
    html_url: str = Field(default="", description="URL to the workflow run on GitHub")
    repository: dict[str, Any] = Field(default_factory=dict, description="Repository metadata")


class WebhookPayload(BaseModel):  # type: ignore[misc]
    """Top-level schema for a GitHub webhook payload."""

    action: str = Field(default="", description="Webhook action type")
    workflow_run: WorkflowRunPayload | None = Field(
        default=None, description="Workflow run details"
    )


# ── LLM Analysis Schemas ───────────────────────────────────────────


class RootCauseAnalysis(BaseModel):  # type: ignore[misc]
    """Structured output from the LLM root cause analysis."""

    root_cause_summary: str = Field(
        default="", description="One-paragraph summary of the failure root cause"
    )
    affected_file_path: str = Field(
        default="", description="Relative path to the file that needs correction"
    )
    corrected_code: str = Field(
        default="", description="Full corrected content of the affected file"
    )
    explanation: str = Field(
        default="", description="Technical explanation of what was changed and why"
    )


class IncrementalCorrection(BaseModel):  # type: ignore[misc]
    """Structured output from the LLM for subsequent fix attempts."""

    corrected_code: str = Field(default="", description="Incrementally corrected file content")
    analysis_of_previous_failure: str = Field(
        default="",
        description="Analysis of why the previous correction failed tests",
    )
    changes_description: str = Field(
        default="", description="Description of what was changed in this iteration"
    )


# ── Internal State ──────────────────────────────────────────────────


@dataclass
class HealingContext:
    """Internal state container for a single auto-healing workflow.

    Tracks the repository, branch, commit, and retry state for
    an active healing session.
    """

    repository_full_name: str = ""
    base_branch: str = "main"
    failed_commit_sha: str = ""
    failed_workflow_run_id: int = 0
    failed_workflow_name: str = ""
    failed_workflow_url: str = ""
    healing_branch_name: str = ""
    pull_request_number: int = 0
    attempt_count: int = 0
    max_attempts: int = 3
    failed_job_names: list[str] = field(default_factory=list)
    failed_step_names: list[str] = field(default_factory=list)
