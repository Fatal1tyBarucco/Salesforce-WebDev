"""Tests for src/workflow.py — 100% coverage."""

import subprocess
from unittest.mock import patch

from src.workflow import (
    PRResult,
    ChangeAnalysis,
    _run_gh,
    analyze_changes,
    commit_and_push,
    create_branch,
    create_pr,
    generate_diff_preview,
    get_current_branch,
    submit_changes,
)


class TestPRResult:
    """Tests for PRResult dataclass."""

    def test_defaults(self) -> None:
        r = PRResult(success=True)
        assert r.success is True
        assert r.pr_number == 0
        assert r.pr_url == ""
        assert r.branch == ""
        assert r.error == ""

    def test_with_values(self) -> None:
        r = PRResult(
            success=False,
            pr_number=42,
            pr_url="https://github.com/pull/42",
            branch="dev",
            error="err",
        )
        assert r.pr_number == 42


class TestChangeAnalysis:
    """Tests for ChangeAnalysis dataclass."""

    def test_defaults(self) -> None:
        c = ChangeAnalysis(
            new_features=[],
            changed_categories=[],
            removed_features=[],
            total_additions=0,
            total_deletions=0,
        )
        assert c.labels == []


class TestRunGh:
    """Tests for _run_gh."""

    def test_success(self) -> None:
        mock_result = subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")
        with patch("src.workflow.subprocess.run", return_value=mock_result):
            result = _run_gh(["issue", "list"])
            assert result.stdout == "ok"

    def test_with_check_false(self) -> None:
        mock_result = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="err")
        with patch("src.workflow.subprocess.run", return_value=mock_result):
            result = _run_gh(["bad"], check=False)
            assert result.returncode == 1


class TestGetCurrentBranch:
    """Tests for get_current_branch."""

    def test_returns_branch(self) -> None:
        mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="main\n", stderr="")
        with patch("src.workflow.subprocess.run", return_value=mock):
            assert get_current_branch() == "main"


class TestCreateBranch:
    """Tests for create_branch."""

    def test_success(self) -> None:
        mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("src.workflow.subprocess.run", return_value=mock):
            assert create_branch("test-branch") is True

    def test_failure(self) -> None:
        with patch(
            "src.workflow.subprocess.run", side_effect=subprocess.CalledProcessError(1, "git")
        ):
            assert create_branch("bad-branch") is False


class TestCommitAndPush:
    """Tests for commit_and_push."""

    def test_success(self) -> None:
        mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("src.workflow.subprocess.run", return_value=mock):
            assert commit_and_push("msg", "branch") is True

    def test_failure(self) -> None:
        with patch(
            "src.workflow.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git", stderr="err"),
        ):
            assert commit_and_push("msg", "branch") is False


class TestAnalyzeChanges:
    """Tests for analyze_changes."""

    def test_with_new_release(self) -> None:
        diff_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=" releases/summer_26/.meta.json | 10 +\n", stderr=""
        )
        status_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="A  releases/summer_26/.meta.json\n", stderr=""
        )
        with patch("src.workflow.subprocess.run", side_effect=[diff_mock, status_mock]):
            result = analyze_changes()
            assert "summer_26" in result.new_features
            assert "new-release" in result.labels

    def test_with_rename(self) -> None:
        diff_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=" {old.md} => {new.md}\n", stderr=""
        )
        status_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("src.workflow.subprocess.run", side_effect=[diff_mock, status_mock]):
            result = analyze_changes()
            assert "category-update" in result.labels

    def test_with_removed_files(self) -> None:
        diff_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        status_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="D  releases/old/file.md\n", stderr=""
        )
        with patch("src.workflow.subprocess.run", side_effect=[diff_mock, status_mock]):
            result = analyze_changes()
            assert "regression-alert" in result.labels

    def test_large_change(self) -> None:
        diff_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=" file.md | 200 +++++++\n", stderr=""
        )
        status_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("src.workflow.subprocess.run", side_effect=[diff_mock, status_mock]):
            result = analyze_changes()
            assert "large-change" in result.labels

    def test_empty_changes(self) -> None:
        diff_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        status_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("src.workflow.subprocess.run", side_effect=[diff_mock, status_mock]):
            result = analyze_changes()
            assert result.labels == []

    def test_parse_error_in_diff(self) -> None:
        """Handles ValueError/ IndexError in diff parsing."""
        diff_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=" file.md | not_a_number\n", stderr=""
        )
        status_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        with patch("src.workflow.subprocess.run", side_effect=[diff_mock, status_mock]):
            result = analyze_changes()
            assert result.total_additions == 0


class TestCreatePr:
    """Tests for create_pr."""

    def test_success(self) -> None:
        mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="https://github.com/org/repo/pull/42\n", stderr=""
        )
        with patch("src.workflow._run_gh", return_value=mock):
            result = create_pr("title", "body", "branch")
            assert result.success is True
            assert result.pr_number == 42

    def test_failure(self) -> None:
        mock = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="error creating PR"
        )
        with patch("src.workflow._run_gh", return_value=mock):
            result = create_pr("title", "body", "branch")
            assert result.success is False
            assert "error" in result.error

    def test_with_labels(self) -> None:
        mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="https://github.com/pull/1\n", stderr=""
        )
        with patch("src.workflow._run_gh", return_value=mock) as mock_gh:
            create_pr("t", "b", "br", labels=["new-release"])
            call_args = mock_gh.call_args[0][0]
            assert "--label" in call_args

    def test_auto_merge(self) -> None:
        mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="https://github.com/pull/99\n", stderr=""
        )
        with patch("src.workflow._run_gh", return_value=mock) as mock_gh:
            create_pr("t", "b", "br", auto_merge=True)
            assert mock_gh.call_count == 2  # create + merge

    def test_pr_number_parse_failure(self) -> None:
        """Handles invalid PR number in URL with /pull/ but non-numeric."""
        mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="https://github.com/org/repo/pull/notanumber\n", stderr=""
        )
        with patch("src.workflow._run_gh", return_value=mock):
            result = create_pr("t", "b", "br")
            assert result.success is True
            assert result.pr_number == 0


class TestGenerateDiffPreview:
    """Tests for generate_diff_preview."""

    def test_generates_preview(self) -> None:
        diff_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=" file.md | 5 +++\n", stderr=""
        )
        status_mock = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="M file.md\n", stderr=""
        )
        # analyze_changes subprocess calls — with additions > 0
        analyze_diff = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=" file.md | 150 +++++\n", stderr=""
        )
        analyze_status = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="A  releases/new/.meta.json\n", stderr=""
        )

        with patch(
            "src.workflow.subprocess.run",
            side_effect=[diff_mock, status_mock, analyze_diff, analyze_status],
        ):
            result = generate_diff_preview()
            assert "Resumo" in result
            assert "Labels" in result or "releases" in result.lower()


class TestSubmitChanges:
    """Tests for submit_changes."""

    def test_full_workflow(self) -> None:
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
        pr_mock = PRResult(success=True, pr_number=1, pr_url="https://github.com/pull/1")
        checkout_mock = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        with (
            patch("src.workflow.create_branch", return_value=True),
            patch("src.workflow.analyze_changes", return_value=ChangeAnalysis([], [], [], 0, 0)),
            patch("src.workflow.generate_diff_preview", return_value="preview"),
            patch("src.workflow.commit_and_push", return_value=True),
            patch("src.workflow.create_pr", return_value=pr_mock),
            patch("src.workflow.subprocess.run", return_value=checkout_mock),
        ):
            result = submit_changes("summer_26")
            assert result.success is True

    def test_branch_creation_failure(self) -> None:
        with patch("src.workflow.create_branch", return_value=False):
            result = submit_changes("test")
            assert result.success is False
            assert "branch" in result.error.lower()

    def test_commit_failure(self) -> None:
        with (
            patch("src.workflow.create_branch", return_value=True),
            patch("src.workflow.analyze_changes", return_value=ChangeAnalysis([], [], [], 0, 0)),
            patch("src.workflow.generate_diff_preview", return_value="preview"),
            patch("src.workflow.commit_and_push", return_value=False),
        ):
            result = submit_changes("test")
            assert result.success is False
            assert "commit" in result.error.lower()
