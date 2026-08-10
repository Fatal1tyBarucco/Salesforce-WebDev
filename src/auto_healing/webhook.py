"""FastAPI webhook application for the Auto-Healing CI/CD Agent.

Receives GitHub ``workflow_run`` webhook events, validates them, and
orchestrates the auto-healing flow: log retrieval → LLM analysis →
pull request creation → circuit-breaker retry logic.

Designed for deployment behind a reverse proxy with webhook secret
validation for security.
"""

from __future__ import annotations

import base64
import binascii
import logging
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from github import GithubException

from .agent_core import AgentCore
from .github_service import GitHubService
from .models import (
    HealingContext,
    HealingOutcome,
    RootCauseAnalysis,
    WebhookPayload,
)

# ── Logging Configuration ───────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── Environment Variables ───────────────────────────────────────────

GITHUB_ACCESS_TOKEN: str = os.environ.get("GITHUB_ACCESS_TOKEN", "")
GOOGLE_API_KEY: str = os.environ.get("GOOGLE_API_KEY", "")
GITHUB_WEBHOOK_SECRET: str = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
PRIMARY_BRANCH: str = os.environ.get("PRIMARY_BRANCH", "main")
AUTO_FIX_BRANCH_PREFIX: str = "auto-fix/"
REPOSITORY_CONTEXT: str = os.environ.get(
    "REPOSITORY_CONTEXT",
    "Python project using pytest, ruff, black, mypy. Coverage threshold: 95%.",
)

# ── Service Initialization ──────────────────────────────────────────

github_service: GitHubService | None = None
agent_core: AgentCore | None = None


def _initialize_services() -> tuple[GitHubService | None, AgentCore | None]:
    """Initialize GitHub and Agent services from environment variables.

    Returns:
        Tuple of (GitHubService, AgentCore), either may be None if
        the required environment variables are missing.
    """
    initialized_github_service: GitHubService | None = None
    initialized_agent_core: AgentCore | None = None

    if GITHUB_ACCESS_TOKEN:
        try:
            initialized_github_service = GitHubService(access_token=GITHUB_ACCESS_TOKEN)
            logger.info("GitHub service initialized successfully.")
        except ValueError as error:
            logger.error("Failed to initialize GitHub service: %s", error)
    else:
        logger.warning("GITHUB_ACCESS_TOKEN not set. GitHub service disabled.")

    if GOOGLE_API_KEY:
        try:
            initialized_agent_core = AgentCore(google_api_key=GOOGLE_API_KEY)
            logger.info("Agent core initialized successfully.")
        except ValueError as error:
            logger.error("Failed to initialize agent core: %s", error)
    else:
        logger.warning("GOOGLE_API_KEY not set. Agent core disabled.")

    return initialized_github_service, initialized_agent_core


@asynccontextmanager
async def lifespan(application: FastAPI) -> Any:
    """Application lifespan manager for startup/shutdown events.

    Args:
        application: The FastAPI application instance.
    """
    global github_service, agent_core
    github_service, agent_core = _initialize_services()
    logger.info("Auto-Healing Agent started.")
    yield
    logger.info("Auto-Healing Agent shutting down.")


# ── FastAPI Application ─────────────────────────────────────────────

app = FastAPI(
    title="Auto-Healing CI/CD Agent",
    description=(
        "Event-driven agent that intercepts GitHub Actions failures, "
        "diagnoses root causes via LLM, and submits corrective pull requests."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ── Health Check ────────────────────────────────────────────────────


@app.get("/health")  # type: ignore[untyped-decorator]
async def health_check() -> JSONResponse:
    """Health check endpoint for container orchestration.

    Returns:
        JSON response with service status information.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "github_service_available": github_service is not None,
            "agent_core_available": agent_core is not None,
        }
    )


# ── Webhook Endpoint ────────────────────────────────────────────────


@app.post("/webhook/workflow-run")  # type: ignore[untyped-decorator]
async def handle_workflow_run_webhook(request: Request) -> JSONResponse:
    """Receive and process GitHub workflow_run webhook events.

    Validates the webhook payload, filters for completed failures,
    and routes to the appropriate healing flow:
    - Primary branch failures → initiate new healing PR
    - auto-fix/* branch failures → incremental fix via circuit breaker

    Args:
        request: The incoming FastAPI request object.

    Returns:
        JSON response indicating the processing result.

    Raises:
        HTTPException: If the payload is invalid or services are unavailable.
    """
    # Parse the webhook payload
    try:
        raw_payload: dict[str, Any] = await request.json()
    except Exception as error:
        logger.error("Failed to parse webhook payload: %s", error)
        raise HTTPException(status_code=400, detail="Invalid JSON payload.") from error

    payload = WebhookPayload(**raw_payload)

    # Validate required fields
    if payload.workflow_run is None:
        logger.warning("Webhook received without workflow_run data. Skipping.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.SKIPPED.value,
                "reason": "No workflow_run data.",
            },
            status_code=200,
        )

    workflow_run = payload.workflow_run

    # Filter: only process completed failures
    if payload.action != "completed":
        logger.info(
            "Ignoring workflow action '%s' (not 'completed').",
            payload.action,
        )
        return JSONResponse(
            content={
                "outcome": HealingOutcome.SKIPPED.value,
                "reason": f"Action is '{payload.action}', not 'completed'.",
            },
            status_code=200,
        )

    if workflow_run.conclusion != "failure":
        logger.info(
            "Ignoring workflow conclusion '%s' (not 'failure').",
            workflow_run.conclusion,
        )
        return JSONResponse(
            content={
                "outcome": HealingOutcome.SKIPPED.value,
                "reason": f"Conclusion is '{workflow_run.conclusion}', not 'failure'.",
            },
            status_code=200,
        )

    # Validate services are available
    if github_service is None or agent_core is None:
        logger.error("Services not initialized. Cannot process webhook.")
        raise HTTPException(
            status_code=503,
            detail="Auto-healing services are not available.",
        )

    # Route to appropriate healing flow
    head_branch: str = workflow_run.head_branch or ""

    if head_branch.startswith(AUTO_FIX_BRANCH_PREFIX):
        logger.info(
            "Detected failure on auto-fix branch '%s'. Initiating retry flow.",
            head_branch,
        )
        return await _handle_auto_fix_branch_failure(
            workflow_run=workflow_run,
        )

    if head_branch == PRIMARY_BRANCH:
        logger.info(
            "Detected failure on primary branch '%s'. Initiating healing flow.",
            head_branch,
        )
        return await _handle_primary_branch_failure(
            workflow_run=workflow_run,
        )

    logger.info(
        "Ignoring failure on branch '%s' (not primary or auto-fix).",
        head_branch,
    )
    return JSONResponse(
        content={
            "outcome": HealingOutcome.SKIPPED.value,
            "reason": (
                f"Branch '{head_branch}' is not the primary branch " "or an auto-fix branch."
            ),
        },
        status_code=200,
    )


# ── Primary Branch Failure Handler ──────────────────────────────────


async def _handle_primary_branch_failure(
    workflow_run: Any,
) -> JSONResponse:
    """Handle a failure on the primary branch by creating a healing PR.

    Downloads the failure logs, performs LLM root cause analysis,
    and creates a corrective pull request on an auto-fix branch.

    Args:
        workflow_run: The workflow run data from the webhook.

    Returns:
        JSON response with the healing outcome.
    """
    if github_service is None or agent_core is None:
        logger.error("Services not initialized in handler.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Services not available.",
            },
            status_code=200,
        )

    repository_data = workflow_run.repository or {}
    repository_full_name: str = repository_data.get("full_name", "")

    if not repository_full_name:
        logger.error("Repository full_name is missing from webhook payload.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Repository name not found in payload.",
            },
            status_code=200,
        )

    workflow_run_id: int = workflow_run.id
    head_sha: str = workflow_run.head_sha or ""
    workflow_name: str = workflow_run.name or "Unknown Workflow"
    workflow_url: str = workflow_run.html_url or ""

    # Step 1: Retrieve failure logs
    logger.info("Retrieving logs for workflow run %d...", workflow_run_id)
    log_text = github_service.retrieve_failed_action_logs(
        repository_full_name=repository_full_name,
        workflow_run_id=workflow_run_id,
    )
    if log_text is None:
        logger.error("Failed to retrieve workflow logs.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Could not retrieve workflow logs.",
            },
            status_code=200,
        )

    # Step 2: Perform LLM root cause analysis
    logger.info("Performing root cause analysis...")
    analysis = agent_core.analyze_pipeline_failure(
        workflow_log_text=log_text,
        repository_context=REPOSITORY_CONTEXT,
    )
    if analysis is None:
        logger.error("LLM root cause analysis failed.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "LLM analysis returned no result.",
            },
            status_code=200,
        )

    # Step 3: Create healing context
    context = HealingContext(
        repository_full_name=repository_full_name,
        failed_commit_sha=head_sha,
        failed_workflow_run_id=workflow_run_id,
        failed_workflow_name=workflow_name,
        failed_workflow_url=workflow_url,
    )

    # Step 4: Create pull request with the fix
    logger.info(
        "Creating healing PR for file '%s'...",
        analysis.affected_file_path,
    )
    pull_request = github_service.execute_auto_healing_pull_request(
        context=context,
        file_path=analysis.affected_file_path,
        corrected_code=analysis.corrected_code,
        commit_message=f"fix: {analysis.root_cause_summary[:72]}",
        pull_request_title=(
            f"🔧 Auto-Heal: {workflow_name} — " f"{analysis.root_cause_summary[:60]}"
        ),
        pull_request_body=_build_pull_request_body(
            analysis=analysis,
            workflow_name=workflow_name,
            workflow_url=workflow_url,
            head_sha=head_sha,
        ),
    )

    if pull_request is None:
        logger.error("Failed to create healing pull request.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Could not create healing pull request.",
            },
            status_code=200,
        )

    logger.info(
        "Healing PR #%d created successfully: %s",
        pull_request.number,
        pull_request.html_url,
    )
    return JSONResponse(
        content={
            "outcome": HealingOutcome.PULL_REQUEST_CREATED.value,
            "pull_request_number": pull_request.number,
            "pull_request_url": pull_request.html_url,
            "affected_file": analysis.affected_file_path,
            "root_cause_summary": analysis.root_cause_summary,
        },
        status_code=200,
    )


# ── Auto-Fix Branch Failure Handler (Circuit Breaker) ───────────────


async def _handle_auto_fix_branch_failure(
    workflow_run: Any,
) -> JSONResponse:
    """Handle a failure on an auto-fix branch using circuit-breaker logic.

    Checks retry eligibility, retrieves the test failure log, generates
    an incremental fix, and commits it to the existing PR.

    Args:
        workflow_run: The workflow run data from the webhook.

    Returns:
        JSON response with the retry outcome.
    """
    if github_service is None or agent_core is None:
        logger.error("Services not initialized in handler.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Services not available.",
            },
            status_code=200,
        )

    repository_data = workflow_run.repository or {}
    repository_full_name: str = repository_data.get("full_name", "")

    if not repository_full_name:
        logger.error("Repository full_name is missing from webhook payload.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Repository name not found in payload.",
            },
            status_code=200,
        )

    workflow_run_id: int = workflow_run.id

    # Extract PR number from branch name (auto-fix/<run_id>)
    head_branch: str = workflow_run.head_branch or ""
    branch_parts = head_branch.split("/")
    if len(branch_parts) < 2:
        logger.error("Cannot extract run ID from branch name '%s'.", head_branch)
        return JSONResponse(
            content={
                "outcome": HealingOutcome.SKIPPED.value,
                "reason": f"Cannot parse branch name '{head_branch}'.",
            },
            status_code=200,
        )

    try:
        int(branch_parts[1])  # Validate numeric run ID
    except ValueError:
        logger.error("Cannot parse run ID from branch '%s'.", head_branch)
        return JSONResponse(
            content={
                "outcome": HealingOutcome.SKIPPED.value,
                "reason": f"Invalid run ID in branch '{head_branch}'.",
            },
            status_code=200,
        )

    # Find the PR associated with this auto-fix branch
    pull_request_number = _find_pull_request_for_branch(
        repository_full_name=repository_full_name,
        branch_name=head_branch,
    )
    if pull_request_number is None:
        logger.error(
            "Could not find open PR for branch '%s'.",
            head_branch,
        )
        return JSONResponse(
            content={
                "outcome": HealingOutcome.SKIPPED.value,
                "reason": f"No open PR found for branch '{head_branch}'.",
            },
            status_code=200,
        )

    # Check circuit breaker eligibility
    is_eligible = github_service.validate_retry_eligibility(
        repository_full_name=repository_full_name,
        pull_request_number=pull_request_number,
    )
    if not is_eligible:
        logger.warning(
            "Circuit breaker open for PR #%d. Aborting.",
            pull_request_number,
        )
        return JSONResponse(
            content={
                "outcome": HealingOutcome.CIRCUIT_BREAKER_OPEN.value,
                "pull_request_number": pull_request_number,
            },
            status_code=200,
        )

    # Retrieve the test failure logs
    log_text = github_service.retrieve_failed_action_logs(
        repository_full_name=repository_full_name,
        workflow_run_id=workflow_run_id,
    )
    if log_text is None:
        logger.error("Failed to retrieve test failure logs.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Could not retrieve test failure logs.",
            },
            status_code=200,
        )

    # Determine the file path from the PR
    file_path = _determine_file_path_from_pr(
        repository_full_name=repository_full_name,
        pull_request_number=pull_request_number,
    )
    if file_path is None:
        logger.error(
            "Could not determine file path from PR #%d.",
            pull_request_number,
        )
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Could not determine affected file path.",
            },
            status_code=200,
        )

    # Get current file content on the PR branch
    current_content = _get_file_content_on_branch(
        repository_full_name=repository_full_name,
        file_path=file_path,
        branch_name=head_branch,
    )
    if current_content is None:
        logger.error("Could not retrieve current file content.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Could not retrieve current file content.",
            },
            status_code=200,
        )

    # Generate incremental fix
    logger.info(
        "Generating incremental fix for PR #%d...",
        pull_request_number,
    )
    correction = agent_core.process_subsequent_correction(
        current_file_content=current_content,
        test_failure_log=log_text,
        file_path=file_path,
    )
    if correction is None:
        logger.error("LLM incremental correction failed.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "LLM could not generate incremental fix.",
            },
            status_code=200,
        )

    # Commit the incremental fix
    success = github_service.inject_incremental_fix_commit(
        repository_full_name=repository_full_name,
        pull_request_number=pull_request_number,
        file_path=file_path,
        corrected_code=correction.corrected_code,
        analysis_of_previous_failure=correction.analysis_of_previous_failure,
        changes_description=correction.changes_description,
        attempt_number=2,
    )

    if not success:
        logger.error("Failed to commit incremental fix.")
        return JSONResponse(
            content={
                "outcome": HealingOutcome.ANALYSIS_FAILED.value,
                "reason": "Could not commit incremental fix.",
            },
            status_code=200,
        )

    logger.info(
        "Incremental fix committed to PR #%d successfully.",
        pull_request_number,
    )
    return JSONResponse(
        content={
            "outcome": HealingOutcome.INCREMENTAL_FIX_COMMITTED.value,
            "pull_request_number": pull_request_number,
            "changes_description": correction.changes_description,
        },
        status_code=200,
    )


# ── Helper Functions ────────────────────────────────────────────────


def _build_pull_request_body(
    analysis: RootCauseAnalysis,
    workflow_name: str,
    workflow_url: str,
    head_sha: str,
) -> str:
    """Build the markdown body for an auto-healing pull request.

    Args:
        analysis: The root cause analysis from the LLM.
        workflow_name: Name of the failed workflow.
        workflow_url: URL to the failed workflow run.
        head_sha: The commit SHA that failed.

    Returns:
        Formatted markdown string for the PR body.
    """
    return (
        "## 🔧 Auto-Healing: CI/CD Pipeline Fix\n\n"
        f"**Failed Workflow:** [{workflow_name}]({workflow_url})\n"
        f"**Failed Commit:** `{head_sha[:8]}`\n"
        f"**Affected File:** `{analysis.affected_file_path}`\n\n"
        "### Root Cause Analysis\n"
        f"{analysis.root_cause_summary}\n\n"
        "### Changes Applied\n"
        f"{analysis.explanation}\n\n"
        "---\n"
        "_This pull request was generated automatically by the "
        "Auto-Healing CI/CD Agent. The fix will be validated by "
        "the agent-validation workflow before merging._\n\n"
        "Please review the changes carefully before approving."
    )


def _find_pull_request_for_branch(
    repository_full_name: str,
    branch_name: str,
) -> int | None:
    """Find an open pull request for a given branch name.

    Args:
        repository_full_name: Owner/repo format.
        branch_name: The head branch to search for.

    Returns:
        Pull request number if found, None otherwise.
    """
    if github_service is None:
        return None

    repository = github_service._get_repository(repository_full_name)
    if repository is None:
        return None

    try:
        pull_requests = repository.get_pulls(state="open", head=branch_name)
        for pull_request in pull_requests:
            if pull_request.head and pull_request.head.ref == branch_name:
                return pull_request.number  # type: ignore[no-any-return]
    except (GithubException, AttributeError, TypeError) as error:
        logger.error(
            "Failed to search for PRs on branch '%s': %s",
            branch_name,
            error,
        )

    return None


def _determine_file_path_from_pr(
    repository_full_name: str,
    pull_request_number: int,
) -> str | None:
    """Determine the primary file path modified in a pull request.

    Args:
        repository_full_name: Owner/repo format.
        pull_request_number: The pull request number to inspect.

    Returns:
        File path of the first modified Python file, or None.
    """
    if github_service is None:
        return None

    repository = github_service._get_repository(repository_full_name)
    if repository is None:
        return None

    try:
        pull_request = repository.get_pull(pull_request_number)
        if pull_request is None:
            return None

        files = pull_request.get_files()
        for file in files:
            if file.filename and file.filename.endswith(".py"):
                return file.filename  # type: ignore[no-any-return]
    except (GithubException, AttributeError, TypeError) as error:
        logger.error(
            "Failed to get files for PR #%d: %s",
            pull_request_number,
            error,
        )

    return None


def _get_file_content_on_branch(
    repository_full_name: str,
    file_path: str,
    branch_name: str,
) -> str | None:
    """Retrieve the content of a file at a specific branch.

    Args:
        repository_full_name: Owner/repo format.
        file_path: Relative path to the file.
        branch_name: The branch to read from.

    Returns:
        File content as string, or None on failure.
    """
    if github_service is None:
        return None

    repository = github_service._get_repository(repository_full_name)
    if repository is None:
        return None

    content_file = github_service._get_file_content_at_ref(
        repository=repository,
        file_path=file_path,
        ref=branch_name,
    )
    if content_file is None:
        return None

    try:
        if content_file.content is None:
            return None
        decoded_bytes = base64.b64decode(content_file.content)
        return decoded_bytes.decode("utf-8")
    except (ValueError, binascii.Error, UnicodeDecodeError) as error:
        logger.error("Failed to decode file content: %s", error)
        return None
