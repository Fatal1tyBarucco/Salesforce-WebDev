"""Tests for src/infrastructure/github.py — 100% coverage target."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.github import (
    GitHubConfig,
    GitHubOperationsAdapter,
    GitHubProjectAdapter,
)


class TestGitHubConfig:
    """Tests for GitHubConfig."""

    def test_init_with_explicit_token(self) -> None:
        """Should initialize with explicit token."""
        config = GitHubConfig(repo="owner/repo", token="explicit_token")
        assert config.repo == "owner/repo"
        assert config.token == "explicit_token"
        assert config.api_base == "https://api.github.com"

    def test_init_uses_env_token(self) -> None:
        """Should use GITHUB_TOKEN from environment when not provided."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env_token"}):
            config = GitHubConfig(repo="owner/repo")
            assert config.token == "env_token"

    def test_init_without_token(self) -> None:
        """Should initialize with None token when no env var."""
        with patch.dict("os.environ", {}, clear=True):
            config = GitHubConfig(repo="owner/repo")
            assert config.token is None

    def test_post_init_sets_token(self) -> None:
        """__post_init__ should set token from env."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "post_init_token"}):
            config = GitHubConfig(repo="owner/repo", token=None)
            assert config.token == "post_init_token"


class TestGitHubOperationsAdapter:
    """Tests for GitHubOperationsAdapter."""

    @pytest.fixture
    def config(self) -> GitHubConfig:
        """Create GitHub config."""
        return GitHubConfig(repo="owner/repo", token="test_token")

    @pytest.fixture
    def adapter(self, config: GitHubConfig) -> GitHubOperationsAdapter:
        """Create GitHub operations adapter."""
        return GitHubOperationsAdapter(config)

    @pytest.fixture
    def mock_github_client(self) -> MagicMock:
        """Create mock GitHub client."""
        return MagicMock()

    @pytest.fixture
    def mock_repo(self) -> MagicMock:
        """Create mock repository."""
        return MagicMock()

    def test_init_sets_properties(
        self, adapter: GitHubOperationsAdapter, config: GitHubConfig
    ) -> None:
        """Should initialize with correct properties."""
        assert adapter.config is config
        assert adapter._client is None

    def test_get_client_creates_client(self, adapter: GitHubOperationsAdapter) -> None:
        """_get_client should create Github client."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_github.return_value = mock_client

            client = adapter._get_client()

            assert client is mock_client
            mock_github.assert_called_once_with("test_token")

    def test_get_client_caches_client(self, adapter: GitHubOperationsAdapter) -> None:
        """_get_client should cache the client."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_github.return_value = mock_client

            client1 = adapter._get_client()
            client2 = adapter._get_client()

            assert client1 is client2
            mock_github.assert_called_once()

    def test_get_client_raises_when_pygithub_not_installed(
        self, adapter: GitHubOperationsAdapter
    ) -> None:
        """Should raise RuntimeError when PyGithub not installed."""
        with patch("github.Github", side_effect=ImportError):
            with pytest.raises(RuntimeError, match="PyGithub not installed"):
                adapter._get_client()

    def test_get_repo(self, adapter: GitHubOperationsAdapter) -> None:
        """_get_repo should return repository object."""
        mock_client = MagicMock()
        mock_repo = MagicMock()
        mock_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_client):
            repo = adapter._get_repo()

            assert repo is mock_repo
            mock_client.get_repo.assert_called_once_with("owner/repo")

    @pytest.mark.asyncio
    async def test_create_issue(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """create_issue should create and return issue details."""
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.html_url = "https://github.com/owner/repo/issues/123"
        mock_issue.title = "Test Issue"
        mock_repo.create_issue.return_value = mock_issue
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.create_issue(
                title="Test Issue",
                body="Issue body",
                labels=["bug"],
                assignees=["user1"],
            )

        assert result == {
            "number": 123,
            "url": "https://github.com/owner/repo/issues/123",
            "title": "Test Issue",
        }
        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue",
            body="Issue body",
            labels=["bug"],
            assignees=["user1"],
        )

    @pytest.mark.asyncio
    async def test_create_issue_without_optional_params(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """create_issue should work without optional params."""
        mock_issue = MagicMock()
        mock_issue.number = 124
        mock_issue.html_url = "https://github.com/owner/repo/issues/124"
        mock_issue.title = "Test Issue 2"
        mock_repo.create_issue.return_value = mock_issue
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.create_issue(title="Test Issue 2", body="Body")

        assert result["number"] == 124
        mock_repo.create_issue.assert_called_once_with(
            title="Test Issue 2",
            body="Body",
            labels=[],
            assignees=[],
        )

    @pytest.mark.asyncio
    async def test_update_issue(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """update_issue should update existing issue."""
        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.html_url = "https://github.com/owner/repo/issues/123"
        mock_repo.get_issue.return_value = mock_issue
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.update_issue(123, title="Updated Title", body="Updated Body")

        assert result == {
            "number": 123,
            "url": "https://github.com/owner/repo/issues/123",
        }
        mock_issue.edit.assert_called_once_with(title="Updated Title", body="Updated Body")

    @pytest.mark.asyncio
    async def test_close_issue(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """close_issue should close issue with optional comment."""
        mock_issue = MagicMock()
        mock_repo.get_issue.return_value = mock_issue
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            await adapter.close_issue(123, comment="Closing this issue")

        mock_issue.create_comment.assert_called_once_with("Closing this issue")
        mock_issue.edit.assert_called_once_with(state="closed")

    @pytest.mark.asyncio
    async def test_close_issue_without_comment(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """close_issue should work without comment."""
        mock_issue = MagicMock()
        mock_repo.get_issue.return_value = mock_issue
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            await adapter.close_issue(123)

        mock_issue.create_comment.assert_not_called()
        mock_issue.edit.assert_called_once_with(state="closed")

    @pytest.mark.asyncio
    async def test_get_issue(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """get_issue should return issue details."""
        mock_label1 = MagicMock()
        mock_label1.name = "bug"
        mock_label2 = MagicMock()
        mock_label2.name = "high-priority"

        mock_issue = MagicMock()
        mock_issue.number = 123
        mock_issue.title = "Test Issue"
        mock_issue.body = "Issue body"
        mock_issue.state = "open"
        mock_issue.labels = [mock_label1, mock_label2]
        mock_issue.html_url = "https://github.com/owner/repo/issues/123"
        mock_repo.get_issue.return_value = mock_issue
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.get_issue(123)

        assert result == {
            "number": 123,
            "title": "Test Issue",
            "body": "Issue body",
            "state": "open",
            "labels": ["bug", "high-priority"],
            "url": "https://github.com/owner/repo/issues/123",
        }

    @pytest.mark.asyncio
    async def test_get_issue_returns_none_on_error(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """get_issue should return None on error."""
        mock_repo.get_issue.side_effect = Exception("Not found")
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.get_issue(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_pr(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """create_pr should create pull request."""
        mock_pr = MagicMock()
        mock_pr.number = 10
        mock_pr.html_url = "https://github.com/owner/repo/pull/10"
        mock_pr.title = "Test PR"
        mock_repo.create_pull.return_value = mock_pr
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.create_pr(
                title="Test PR",
                body="PR body",
                head="feature-branch",
                base="main",
                draft=True,
            )

        assert result == {
            "number": 10,
            "url": "https://github.com/owner/repo/pull/10",
            "title": "Test PR",
        }
        mock_repo.create_pull.assert_called_once_with(
            title="Test PR",
            body="PR body",
            head="feature-branch",
            base="main",
            draft=True,
        )

    @pytest.mark.asyncio
    async def test_merge_pr_mergeable(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """merge_pr should merge when mergeable."""
        mock_pr = MagicMock()
        mock_pr.mergeable = True
        mock_repo.get_pull.return_value = mock_pr
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.merge_pr(10, method="squash")

        assert result is True
        mock_pr.merge.assert_called_once_with(merge_method="squash")

    @pytest.mark.asyncio
    async def test_merge_pr_not_mergeable(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """merge_pr should return False when not mergeable."""
        mock_pr = MagicMock()
        mock_pr.mergeable = False
        mock_repo.get_pull.return_value = mock_pr
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.merge_pr(10)

        assert result is False
        mock_pr.merge.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_release(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """create_release should create GitHub release."""
        mock_release = MagicMock()
        mock_release.tag_name = "v1.0.0"
        mock_release.html_url = "https://github.com/owner/repo/releases/tag/v1.0.0"
        mock_release.title = "Release v1.0.0"
        mock_repo.create_git_release.return_value = mock_release
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.create_release(
                tag="v1.0.0",
                name="Release v1.0.0",
                body="Release notes",
                draft=False,
                prerelease=False,
            )

        assert result == {
            "tag": "v1.0.0",
            "url": "https://github.com/owner/repo/releases/tag/v1.0.0",
            "name": "Release v1.0.0",
        }
        mock_repo.create_git_release.assert_called_once_with(
            tag="v1.0.0",
            name="Release v1.0.0",
            message="Release notes",
            draft=False,
            prerelease=False,
        )

    @pytest.mark.asyncio
    async def test_update_badge(self, adapter: GitHubOperationsAdapter) -> None:
        """update_badge should generate shields.io URL."""
        url = await adapter.update_badge("version", "1.0.0", "green")
        assert "img.shields.io/badge/version-1.0.0-green" in url

    @pytest.mark.asyncio
    async def test_update_badge_encodes_spaces(self, adapter: GitHubOperationsAdapter) -> None:
        """update_badge should encode spaces."""
        url = await adapter.update_badge("my badge", "value with spaces", "blue")
        assert "%20" in url

    @pytest.mark.asyncio
    async def test_trigger_workflow(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """trigger_workflow should trigger GitHub Actions workflow."""
        mock_workflow = MagicMock()
        mock_run = MagicMock()
        mock_run.id = 456
        mock_run.html_url = "https://github.com/owner/repo/actions/runs/456"
        mock_workflow.create_dispatch.return_value = mock_run
        mock_repo.get_workflow.return_value = mock_workflow
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.trigger_workflow(
                workflow_id="ci.yml",
                ref="main",
                inputs={"env": "production"},
            )

        assert result == {
            "run_id": 456,
            "url": "https://github.com/owner/repo/actions/runs/456",
        }
        mock_workflow.create_dispatch.assert_called_once_with(
            ref="main", inputs={"env": "production"}
        )

    @pytest.mark.asyncio
    async def test_create_or_update_file_existing(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """create_or_update_file should update existing file."""
        mock_contents = MagicMock()
        mock_contents.sha = "abc123"
        mock_repo.get_contents.return_value = mock_contents

        # Mock the return value from update_file - it's a dict with "content" key containing the ContentFile object
        mock_content_file = MagicMock()
        mock_content_file.sha = "new_sha"
        mock_content_file.html_url = "https://github.com/owner/repo/blob/main/file.txt"

        mock_result = {"content": mock_content_file}
        mock_repo.update_file.return_value = mock_result
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.create_or_update_file(
                path="file.txt",
                content="New content",
                message="Update file",
                branch="main",
            )

        assert result == {
            "sha": "new_sha",
            "url": "https://github.com/owner/repo/blob/main/file.txt",
        }
        mock_repo.update_file.assert_called_once_with(
            path="file.txt",
            message="Update file",
            content="New content",
            sha="abc123",
            branch="main",
        )

    @pytest.mark.asyncio
    async def test_create_or_update_file_new(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """create_or_update_file should create new file when not exists."""
        mock_repo.get_contents.side_effect = Exception("Not found")

        mock_content_file = MagicMock()
        mock_content_file.sha = "new_sha"
        mock_content_file.html_url = "https://github.com/owner/repo/blob/main/new.txt"

        mock_result = {"content": mock_content_file}
        mock_repo.create_file.return_value = mock_result
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.create_or_update_file(
                path="new.txt",
                content="New file content",
                message="Create file",
            )

        assert result == {
            "sha": "new_sha",
            "url": "https://github.com/owner/repo/blob/main/new.txt",
        }
        mock_repo.create_file.assert_called_once_with(
            path="new.txt",
            message="Create file",
            content="New file content",
            branch="repo",  # fallback from repo name
        )

    @pytest.mark.asyncio
    async def test_get_file(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """get_file should return file content."""
        mock_contents = MagicMock()
        mock_contents.decoded_content = b"File content"
        mock_repo.get_contents.return_value = mock_contents
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.get_file("file.txt", branch="main")

        assert result == "File content"
        mock_repo.get_contents.assert_called_once_with("file.txt", ref="main")

    @pytest.mark.asyncio
    async def test_get_file_returns_none_on_error(
        self,
        adapter: GitHubOperationsAdapter,
        mock_github_client: MagicMock,
        mock_repo: MagicMock,
    ) -> None:
        """get_file should return None on error."""
        mock_repo.get_contents.side_effect = Exception("Not found")
        mock_github_client.get_repo.return_value = mock_repo

        with patch.object(adapter, "_get_client", return_value=mock_github_client):
            result = await adapter.get_file("nonexistent.txt")

        assert result is None

    @pytest.mark.asyncio
    async def test_add_issue_to_project_raises_not_implemented(
        self, adapter: GitHubOperationsAdapter
    ) -> None:
        """add_issue_to_project should raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Project v2 operations need GraphQL"):
            await adapter.add_issue_to_project(123, 1)

    @pytest.mark.asyncio
    async def test_update_project_item_status_raises_not_implemented(
        self, adapter: GitHubOperationsAdapter
    ) -> None:
        """update_project_item_status should raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Project v2 operations need GraphQL"):
            await adapter.update_project_item_status("item1", "done")


class TestGitHubProjectAdapter:
    """Tests for GitHubProjectAdapter."""

    @pytest.fixture
    def adapter(self) -> GitHubProjectAdapter:
        """Create GitHub project adapter."""
        return GitHubProjectAdapter(token="test_token")

    def test_init_sets_properties(self, adapter: GitHubProjectAdapter) -> None:
        """Should initialize with correct properties."""
        assert adapter.token == "test_token"
        assert adapter._endpoint == "https://api.github.com/graphql"

    def test_init_uses_env_token(self) -> None:
        """Should use GITHUB_TOKEN from environment when not provided."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env_token"}):
            adapter = GitHubProjectAdapter(token=None)
            assert adapter.token == "env_token"

    @pytest.mark.asyncio
    async def test_graphql_executes_query(self, adapter: GitHubProjectAdapter) -> None:
        """_graphql should execute GraphQL query."""

        # Create proper async context manager mocks
        class MockResponse:
            def __init__(self, data):
                self._data = data

            async def json(self):
                return self._data

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class MockPostContext:
            def __init__(self, data):
                self._data = data

            async def __aenter__(self):
                return MockResponse(self._data)

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def __init__(self, data):
                self._data = data

            def post(self, *args, **kwargs):
                return MockPostContext(self._data)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_session = MockSession({"data": {"result": "success"}})

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await adapter._graphql("query { test }", {"var": "value"})

        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_graphql_raises_on_errors(self, adapter: GitHubProjectAdapter) -> None:
        """_graphql should raise on GraphQL errors."""

        class MockResponse:
            def __init__(self, data):
                self._data = data

            async def json(self):
                return self._data

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        class MockPostContext:
            def __init__(self, data):
                self._data = data

            async def __aenter__(self):
                return MockResponse(self._data)

            async def __aexit__(self, *args):
                pass

        class MockSession:
            def __init__(self, data):
                self._data = data

            def post(self, *args, **kwargs):
                return MockPostContext(self._data)

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

        mock_session = MockSession({"errors": [{"message": "Error"}]})

        with patch("aiohttp.ClientSession", return_value=mock_session):
            with pytest.raises(RuntimeError, match="GraphQL errors"):
                await adapter._graphql("query { test }")

    @pytest.mark.asyncio
    async def test_get_project_items(self, adapter: GitHubProjectAdapter) -> None:
        """get_project_items should return project items."""
        mock_items = [{"id": "1", "content": {"number": 1, "title": "Issue 1", "state": "OPEN"}}]

        with patch.object(
            adapter, "_graphql", return_value={"node": {"items": {"nodes": mock_items}}}
        ):
            result = await adapter.get_project_items("project_id")

        assert result == mock_items

    @pytest.mark.asyncio
    async def test_get_project_items_returns_empty_on_missing_data(
        self, adapter: GitHubProjectAdapter
    ) -> None:
        """get_project_items should return empty list when data missing."""
        with patch.object(adapter, "_graphql", return_value={}):
            result = await adapter.get_project_items("project_id")

        assert result == []

    @pytest.mark.asyncio
    async def test_update_item_field(self, adapter: GitHubProjectAdapter) -> None:
        """update_item_field should update project item field."""
        with patch.object(adapter, "_graphql", return_value={"updateProjectV2ItemFieldValue": {}}):
            result = await adapter.update_item_field(
                project_id="proj1",
                item_id="item1",
                field_id="field1",
                value="done",
            )

        assert result is True

    @pytest.mark.asyncio
    async def test_update_item_field_returns_false_on_error(
        self, adapter: GitHubProjectAdapter
    ) -> None:
        """update_item_field should return False on error."""
        with patch.object(adapter, "_graphql", side_effect=Exception("Failed")):
            result = await adapter.update_item_field(
                project_id="proj1",
                item_id="item1",
                field_id="field1",
                value="done",
            )

        assert result is False
