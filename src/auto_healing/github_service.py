"""GitHub integration service for the Auto-Healing Agent.

Provides all GitHub API interactions including: downloading workflow logs,
creating branches, updating files, opening pull requests, and implementing
the circuit-breaker retry logic for incremental fix commits.

Uses PyGithub for API access with comprehensive error handling and
null-safety checks on every external response.
"""

from __future__ import annotations

import io
import logging
import zipfile

from github import Github, GithubException
from github.ContentFile import ContentFile
from github.GitRef import GitRef
from github.PullRequest import PullRequest
from github.Repository import Repository

from .models import HealingContext

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────

AGENT_COMMIT_MESSAGE_PREFIX = "[auto-heal]"
MAX_CIRCUIT_BREAKER_ATTEMPTS: int = 3
CIRCUIT_BREAKER_COMMENT_TEMPLATE: str = (
    "## 🚫 Auto-Healing Circuit Breaker Triggered\n\n"
    "The auto-healing agent has exhausted **{attempt_count}** correction "
    "attempts for this pull request without achieving a passing test suite.\n\n"
    "**Failed workflow:** [{workflow_name}]({workflow_url})\n"
    "**Last failed commit:** `{commit_sha}`\n\n"
    "### Recommended Next Steps\n"
    "1. Review the agent's correction attempts above\n"
    "2. Manually diagnose the root cause\n"
    "3. Close this PR and apply the fix directly\n\n"
    "_This comment was generated automatically by the Auto-Healing Agent._"
)
INCREMENTAL_FIX_COMMENT_TEMPLATE: str = (
    "## 🔄 Incremental Fix — Attempt {attempt_number}\n\n"
    "**Analysis of previous failure:**\n{analysis}\n\n"
    "**Changes applied:**\n{changes}\n\n"
    "_Automated fix committed by the Auto-Healing Agent._"
)


# ── Service Class ───────────────────────────────────────────────────


class GitHubService:
    """Encapsulates all GitHub API operations for the auto-healing workflow.

    Provides methods for log retrieval, branch management, file updates,
    pull request creation, and circuit-breaker enforcement.

    Attributes:
        _github_client: Authenticated PyGithub client instance.
    """

    def __init__(self, access_token: str) -> None:
        """Initialize the GitHub service with an authenticated client.

        Args:
            access_token: A GitHub Personal Access Token with repo scope.

        Raises:
            ValueError: If the access_token is empty or None.
        """
        if not access_token:
            raise ValueError("GitHub access token must not be empty.")
        self._github_client: Github = Github(access_token)

    # ── Repository Access ───────────────────────────────────────────

    def _get_repository(self, repository_full_name: str) -> Repository | None:
        """Safely retrieve a repository object by full name.

        Args:
            repository_full_name: Owner/repo format (e.g., "owner/repo").

        Returns:
            Repository object if found, None otherwise.
        """
        try:
            repository: Repository = self._github_client.get_repo(repository_full_name)
            return repository
        except GithubException as error:
            logger.error(
                "Failed to access repository '%s': %s",
                repository_full_name,
                error,
            )
            return None

    # ── Log Retrieval ───────────────────────────────────────────────

    def retrieve_failed_action_logs(
        self,
        repository_full_name: str,
        workflow_run_id: int,
    ) -> str | None:
        """Download and extract logs from a failed GitHub Actions workflow run.

        Downloads the log archive (ZIP), extracts all log files, and
        concatenates them into a single string for LLM analysis.

        Args:
            repository_full_name: Owner/repo format (e.g., "owner/repo").
            workflow_run_id: The numeric ID of the workflow run.

        Returns:
            Concatenated log text if successful, None on any failure.
        """
        repository = self._get_repository(repository_full_name)
        if repository is None:
            return None

        try:
            workflow_run = repository.get_workflow_run(workflow_run_id)
        except GithubException as error:
            logger.error(
                "Failed to retrieve workflow run %d: %s",
                workflow_run_id,
                error,
            )
            return None

        if workflow_run is None:
            logger.error("Workflow run %d returned None.", workflow_run_id)
            return None

        try:
            log_bytes: bytes = workflow_run.logs()  # type: ignore[attr-defined]
        except GithubException as error:
            logger.error(
                "Failed to download logs for workflow run %d: %s",
                workflow_run_id,
                error,
            )
            return None

        if not log_bytes:
            logger.error("Log archive is empty for workflow run %d.", workflow_run_id)
            return None

        return self._extract_logs_from_zip_archive(log_bytes)

    def _extract_logs_from_zip_archive(self, zip_bytes: bytes) -> str | None:
        """Extract and concatenate log files from a ZIP archive.

        Args:
            zip_bytes: Raw bytes of the ZIP archive.

        Returns:
            Concatenated log content, or None if extraction fails.
        """
        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
                log_entries: list[str] = []
                for file_info in archive.infolist():
                    if file_info.file_size == 0:
                        continue
                    with archive.open(file_info) as log_file:
                        raw_content: bytes = log_file.read()
                        decoded_content: str = raw_content.decode("utf-8", errors="replace")
                        log_entries.append(f"=== {file_info.filename} ===\n{decoded_content}\n")
                if not log_entries:
                    logger.warning("ZIP archive contained no readable log files.")
                    return None
                return "\n".join(log_entries)
        except (zipfile.BadZipFile, OSError) as error:
            logger.error("Failed to extract ZIP archive: %s", error)
            return None

    # ── Branch Management ───────────────────────────────────────────

    def _create_healing_branch(
        self,
        repository: Repository,
        branch_name: str,
        base_branch: str,
    ) -> GitRef | None:
        """Create a new branch from the HEAD of the base branch.

        Args:
            repository: The GitHub repository object.
            branch_name: Name for the new branch (e.g., "auto-fix/12345").
            base_branch: Name of the source branch (e.g., "main").

        Returns:
            GitRef object if created successfully, None otherwise.
        """
        try:
            base_ref = repository.get_git_ref(f"heads/{base_branch}")
        except GithubException as error:
            logger.error(
                "Failed to get base branch ref '%s': %s",
                base_branch,
                error,
            )
            return None

        if base_ref is None or base_ref.object is None:
            logger.error("Base branch ref '%s' returned None.", base_branch)
            return None

        base_sha: str = base_ref.object.sha
        if not base_sha:
            logger.error("Base branch SHA is empty for '%s'.", base_branch)
            return None

        try:
            new_ref = repository.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_sha,
            )
            logger.info(
                "Created healing branch '%s' from '%s' (SHA: %s).",
                branch_name,
                base_branch,
                base_sha[:8],
            )
            return new_ref
        except GithubException as error:
            logger.error(
                "Failed to create branch '%s': %s",
                branch_name,
                error,
            )
            return None

    # ── File Operations ─────────────────────────────────────────────

    def _get_file_content_at_ref(
        self,
        repository: Repository,
        file_path: str,
        ref: str,
    ) -> ContentFile | None:
        """Retrieve a file's content at a specific git reference.

        Args:
            repository: The GitHub repository object.
            file_path: Relative path to the file in the repository.
            ref: Git reference (branch name, SHA, etc.).

        Returns:
            ContentFile object if found, None otherwise.
        """
        try:
            content_file = repository.get_contents(file_path, ref=ref)
            if isinstance(content_file, list):
                logger.error("Path '%s' is a directory, not a file.", file_path)
                return None
            return content_file
        except GithubException as error:
            logger.error(
                "Failed to get file '%s' at ref '%s': %s",
                file_path,
                ref,
                error,
            )
            return None

    # ── Pull Request Creation ───────────────────────────────────────

    def execute_auto_healing_pull_request(
        self,
        context: HealingContext,
        file_path: str,
        corrected_code: str,
        commit_message: str,
        pull_request_title: str,
        pull_request_body: str,
    ) -> PullRequest | None:
        """Create a complete auto-healing pull request.

        Performs the full Git Flow: creates a healing branch, retrieves
        the file at the failed commit, updates it with corrected code,
        and opens a pull request.

        Args:
            context: The healing session context.
            file_path: Relative path to the file to correct.
            corrected_code: Full corrected file content.
            commit_message: Commit message for the fix.
            pull_request_title: Title for the pull request.
            pull_request_body: Body/description for the pull request.

        Returns:
            PullRequest object if successful, None on any failure.
        """
        repository = self._get_repository(context.repository_full_name)
        if repository is None:
            return None

        # Create the healing branch
        branch_name = f"auto-fix/{context.failed_workflow_run_id}"
        healing_branch = self._create_healing_branch(
            repository=repository,
            branch_name=branch_name,
            base_branch=context.base_branch,
        )
        if healing_branch is None:
            return None

        # Retrieve the file at the failed commit
        content_file = self._get_file_content_at_ref(
            repository=repository,
            file_path=file_path,
            ref=context.failed_commit_sha,
        )
        if content_file is None:
            return None

        if content_file.sha is None:
            logger.error("File SHA is None for '%s'.", file_path)
            return None

        # Update the file on the healing branch
        try:
            repository.update_file(
                path=file_path,
                message=f"{AGENT_COMMIT_MESSAGE_PREFIX} {commit_message}",
                content=corrected_code,
                sha=content_file.sha,
                branch=branch_name,
            )
            logger.info("Updated file '%s' on branch '%s'.", file_path, branch_name)
        except GithubException as error:
            logger.error(
                "Failed to update file '%s' on branch '%s': %s",
                file_path,
                branch_name,
                error,
            )
            return None

        # Open the pull request
        try:
            pull_request = repository.create_pull(
                title=pull_request_title,
                body=pull_request_body,
                head=branch_name,
                base=context.base_branch,
            )
            logger.info(
                "Opened pull request #%d: %s",
                pull_request.number,
                pull_request.html_url,
            )
            context.pull_request_number = pull_request.number
            context.healing_branch_name = branch_name
            context.attempt_count = 1
            return pull_request
        except GithubException as error:
            logger.error(
                "Failed to create pull request from branch '%s': %s",
                branch_name,
                error,
            )
            return None

    # ── Circuit Breaker ─────────────────────────────────────────────

    def validate_retry_eligibility(
        self,
        repository_full_name: str,
        pull_request_number: int,
    ) -> bool:
        """Check if a pull request is still eligible for auto-healing retries.

        Counts commits authored by the agent on the pull request branch.
        If the count exceeds MAX_CIRCUIT_BREAKER_ATTEMPTS, adds a warning
        comment and returns False.

        Args:
            repository_full_name: Owner/repo format.
            pull_request_number: The pull request number to check.

        Returns:
            True if retries are still allowed, False if circuit breaker is open.
        """
        repository = self._get_repository(repository_full_name)
        if repository is None:
            return False

        try:
            pull_request = repository.get_pull(pull_request_number)
        except GithubException as error:
            logger.error(
                "Failed to retrieve PR #%d: %s",
                pull_request_number,
                error,
            )
            return False

        if pull_request is None:
            logger.error("PR #%d returned None.", pull_request_number)
            return False

        # Count agent commits on the PR
        agent_commit_count: int = 0
        try:
            commits = pull_request.get_commits()
            for commit in commits:
                if commit.commit is None:
                    continue
                message = commit.commit.message or ""
                if message.startswith(AGENT_COMMIT_MESSAGE_PREFIX):
                    agent_commit_count += 1
        except GithubException as error:
            logger.error(
                "Failed to retrieve commits for PR #%d: %s",
                pull_request_number,
                error,
            )
            return False

        logger.info(
            "PR #%d has %d agent commits (limit: %d).",
            pull_request_number,
            agent_commit_count,
            MAX_CIRCUIT_BREAKER_ATTEMPTS,
        )

        if agent_commit_count >= MAX_CIRCUIT_BREAKER_ATTEMPTS:
            self._add_circuit_breaker_comment(
                repository=repository,
                pull_request=pull_request,
                attempt_count=agent_commit_count,
            )
            return False

        return True

    def _add_circuit_breaker_comment(
        self,
        repository: Repository,
        pull_request: PullRequest,
        attempt_count: int,
    ) -> None:
        """Add a circuit-breaker warning comment to a pull request.

        Args:
            repository: The GitHub repository object.
            pull_request: The pull request to comment on.
            attempt_count: Number of attempts that were made.
        """
        comment_body = CIRCUIT_BREAKER_COMMENT_TEMPLATE.format(
            attempt_count=attempt_count,
            workflow_name="CI Pipeline",
            workflow_url="",
            commit_sha="latest",
        )
        try:
            pull_request.create_issue_comment(comment_body)
            logger.warning(
                "Circuit breaker triggered on PR #%d after %d attempts.",
                pull_request.number,
                attempt_count,
            )
        except GithubException as error:
            logger.error(
                "Failed to add circuit breaker comment to PR #%d: %s",
                pull_request.number,
                error,
            )

    # ── Incremental Fix ─────────────────────────────────────────────

    def inject_incremental_fix_commit(
        self,
        repository_full_name: str,
        pull_request_number: int,
        file_path: str,
        corrected_code: str,
        analysis_of_previous_failure: str,
        changes_description: str,
        attempt_number: int,
    ) -> bool:
        """Commit an incremental fix to an existing auto-healing pull request.

        Retrieves the current file on the PR branch, updates it with new
        corrected code, and adds a documentation comment to the PR.

        Args:
            repository_full_name: Owner/repo format.
            pull_request_number: The pull request to update.
            file_path: Relative path to the file being corrected.
            corrected_code: New corrected file content.
            analysis_of_previous_failure: Why the previous fix failed.
            changes_description: What was changed in this iteration.
            attempt_number: Current attempt number (for documentation).

        Returns:
            True if the commit was successful, False otherwise.
        """
        repository = self._get_repository(repository_full_name)
        if repository is None:
            return False

        try:
            pull_request = repository.get_pull(pull_request_number)
        except GithubException as error:
            logger.error(
                "Failed to retrieve PR #%d: %s",
                pull_request_number,
                error,
            )
            return False

        if pull_request is None:
            logger.error("PR #%d returned None.", pull_request_number)
            return False

        head_sha = pull_request.head.sha if pull_request.head else None
        if not head_sha:
            logger.error("PR #%d head SHA is None.", pull_request_number)
            return False

        # Retrieve the current file on the PR branch
        content_file = self._get_file_content_at_ref(
            repository=repository,
            file_path=file_path,
            ref=head_sha,
        )
        if content_file is None or content_file.sha is None:
            return False

        # Determine the branch name from the PR head
        branch_name = pull_request.head.ref if pull_request.head else None
        if not branch_name:
            logger.error("PR #%d head ref is None.", pull_request_number)
            return False

        # Commit the updated file
        try:
            repository.update_file(
                path=file_path,
                message=(
                    f"{AGENT_COMMIT_MESSAGE_PREFIX} incremental fix attempt #{attempt_number}"
                ),
                content=corrected_code,
                sha=content_file.sha,
                branch=branch_name,
            )
            logger.info(
                "Committed incremental fix #%d to PR #%d on branch '%s'.",
                attempt_number,
                pull_request_number,
                branch_name,
            )
        except GithubException as error:
            logger.error(
                "Failed to commit incremental fix to PR #%d: %s",
                pull_request_number,
                error,
            )
            return False

        # Add documentation comment to the PR
        comment_body = INCREMENTAL_FIX_COMMENT_TEMPLATE.format(
            attempt_number=attempt_number,
            analysis=analysis_of_previous_failure,
            changes=changes_description,
        )
        try:
            pull_request.create_issue_comment(comment_body)
        except GithubException as error:
            logger.warning(
                "Failed to add documentation comment to PR #%d: %s",
                pull_request_number,
                error,
            )

        return True
