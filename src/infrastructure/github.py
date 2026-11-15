"""GitHub operations infrastructure — GitHub API adapter.

Implements GitHub operations: issues, PRs, releases, badges, workflows.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """GitHub adapter configuration."""

    repo: str  # "owner/repo"
    token: str | None = None
    api_base: str = "https://api.github.com"

    def __post_init__(self) -> None:
        if self.token is None:
            self.token = os.getenv("GITHUB_TOKEN")


class GitHubOperationsAdapter:
    """GitHub operations adapter for issues, PRs, and repository management."""

    def __init__(self, config: GitHubConfig | None = None) -> None:
        self.config = config or GitHubConfig(repo="")
        self._client: Any = None

    def _get_client(self) -> Any:
        """Lazy-load GitHub client."""
        if self._client is None:
            try:
                from github import Github

                self._client = Github(self.config.token) if self.config.token else Github()
            except ImportError:
                raise RuntimeError("PyGithub not installed. Run: uv add PyGithub")
        return self._client

    def _get_repo(self) -> Any:
        """Get repository object."""
        client = self._get_client()
        return client.get_repo(self.config.repo)

    # Issue operations
    async def create_issue(
        self,
        title: str,
        body: str,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a GitHub issue."""
        repo = self._get_repo()
        issue = repo.create_issue(
            title=title,
            body=body,
            labels=labels or [],
            assignees=assignees or [],
        )
        return {
            "number": issue.number,
            "url": issue.html_url,
            "title": issue.title,
        }

    async def update_issue(self, number: int, **kwargs: Any) -> dict[str, Any]:
        """Update an existing issue."""
        repo = self._get_repo()
        issue = repo.get_issue(number)
        issue.edit(**kwargs)
        return {"number": issue.number, "url": issue.html_url}

    async def close_issue(self, number: int, comment: str | None = None) -> None:
        """Close an issue."""
        repo = self._get_repo()
        issue = repo.get_issue(number)
        if comment:
            issue.create_comment(comment)
        issue.edit(state="closed")

    async def get_issue(self, number: int) -> dict[str, Any] | None:
        """Get issue details."""
        try:
            repo = self._get_repo()
            issue = repo.get_issue(number)
            return {
                "number": issue.number,
                "title": issue.title,
                "body": issue.body,
                "state": issue.state,
                "labels": [label.name for label in issue.labels],
                "url": issue.html_url,
            }
        except Exception as e:
            logger.warning("Failed to get issue %d: %s", number, e)
            return None

    # PR operations
    async def create_pr(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        draft: bool = False,
    ) -> dict[str, Any]:
        """Create a pull request."""
        repo = self._get_repo()
        pr = repo.create_pull(
            title=title,
            body=body,
            head=head,
            base=base,
            draft=draft,
        )
        return {
            "number": pr.number,
            "url": pr.html_url,
            "title": pr.title,
        }

    async def merge_pr(self, number: int, method: str = "squash") -> bool:
        """Merge a pull request."""
        repo = self._get_repo()
        pr = repo.get_pull(number)
        if pr.mergeable:
            pr.merge(merge_method=method)
            return True
        return False

    # Release operations
    async def create_release(
        self,
        tag: str,
        name: str,
        body: str,
        draft: bool = False,
        prerelease: bool = False,
    ) -> dict[str, Any]:
        """Create a GitHub release."""
        repo = self._get_repo()
        release = repo.create_git_release(
            tag=tag,
            name=name,
            message=body,
            draft=draft,
            prerelease=prerelease,
        )
        return {
            "tag": release.tag_name,
            "url": release.html_url,
            "name": release.title,
        }

    # Badge operations
    async def update_badge(self, badge_name: str, value: str, color: str = "blue") -> str:
        """Generate shields.io badge URL."""
        # This generates a shields.io URL - actual badge update
        # would require updating README or a badge service
        encoded_value = value.replace(" ", "%20")
        return f"https://img.shields.io/badge/{badge_name}-{encoded_value}-{color}"

    # Workflow operations
    async def trigger_workflow(
        self,
        workflow_id: str,
        ref: str = "main",
        inputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Trigger a GitHub Actions workflow."""
        repo = self._get_repo()
        workflow = repo.get_workflow(workflow_id)
        run = workflow.create_dispatch(ref=ref, inputs=inputs or {})
        return {
            "run_id": run.id,
            "url": run.html_url,
        }

    # File operations
    async def create_or_update_file(
        self,
        path: str,
        content: str,
        message: str,
        branch: str | None = None,
    ) -> dict[str, Any]:
        """Create or update a file in the repository."""
        repo = self._get_repo()
        target_branch = branch or self.config.repo.split("/")[-1]  # fallback

        try:
            # Try to get existing file
            contents = repo.get_contents(path, ref=target_branch)
            result = repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=contents.sha,
                branch=target_branch,
            )
        except Exception:
            # File doesn't exist, create it
            result = repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=target_branch,
            )

        return {
            "sha": result["content"].sha if "content" in result else None,
            "url": result["content"].html_url if "content" in result else None,
        }

    async def get_file(self, path: str, branch: str | None = None) -> str | None:
        """Get file content from repository."""
        try:
            repo = self._get_repo()
            target_branch = branch or "main"
            contents = repo.get_contents(path, ref=target_branch)
            content_bytes: bytes = contents.decoded_content  # type: ignore[assignment]
            return content_bytes.decode("utf-8")
        except Exception as e:
            logger.warning("Failed to get file %s: %s", path, e)
            return None

    # Project operations (GitHub Projects v2)
    async def add_issue_to_project(
        self, issue_number: int, project_number: int
    ) -> dict[str, Any] | None:
        """Add an issue to a GitHub Project (v2)."""
        # Requires GraphQL API
        raise NotImplementedError("Project v2 operations need GraphQL")

    async def update_project_item_status(self, item_id: str, status: str) -> bool:
        """Update a project item status."""
        raise NotImplementedError("Project v2 operations need GraphQL")


class GitHubProjectAdapter:
    """GitHub Project v2 adapter using GraphQL."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self._endpoint = "https://api.github.com/graphql"

    async def _graphql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute GraphQL query."""
        import aiohttp

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self._endpoint,
                json={"query": query, "variables": variables or {}},
                headers=headers,
            ) as resp:
                data = await resp.json()
                if "errors" in data:
                    raise RuntimeError(f"GraphQL errors: {data['errors']}")
                return data.get("data", {})  # type: ignore[no-any-return]

    async def get_project_items(self, project_id: str) -> list[dict[str, Any]]:
        """Get all items in a project."""
        query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              items(first: 100) {
                nodes {
                  id
                  content {
                    ... on Issue {
                      number
                      title
                      state
                    }
                    ... on PullRequest {
                      number
                      title
                      state
                    }
                  }
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        name
                        field { ... on ProjectV2SingleSelectField { name } }
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        data: dict[str, Any] = await self._graphql(query, {"projectId": project_id})
        return data.get("node", {}).get("items", {}).get("nodes", [])  # type: ignore[no-any-return]

    async def update_item_field(
        self, project_id: str, item_id: str, field_id: str, value: str
    ) -> bool:
        """Update a project item field value."""
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { singleSelectOptionId: $value }
          }) {
            projectV2Item { id }
          }
        }
        """
        try:
            await self._graphql(
                mutation,
                {
                    "projectId": project_id,
                    "itemId": item_id,
                    "fieldId": field_id,
                    "value": value,
                },
            )
            return True
        except Exception as e:
            logger.error("Failed to update project item: %s", e)
            return False
