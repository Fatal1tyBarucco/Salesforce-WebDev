"""Review-based workflow for release notes pipeline.

Provides functions to create PRs instead of direct pushes, with
diff preview, label-based triage, and auto-merge support.

Uses gh CLI for all GitHub operations — no external dependencies.
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PRResult:
    """Result of creating a pull request."""

    success: bool
    pr_number: int = 0
    pr_url: str = ""
    branch: str = ""
    error: str = ""


@dataclass
class ChangeAnalysis:
    """Analysis of changes for labeling triage."""

    new_features: list[str]
    changed_categories: list[str]
    removed_features: list[str]
    total_additions: int
    total_deletions: int
    labels: list[str] = field(default_factory=list)


def _run_gh(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a gh CLI command and return the result."""
    cmd = ["gh"] + args
    logger.debug("Running: %s", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def get_current_branch() -> str:
    """Get the current git branch name."""
    git_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return git_result.stdout.strip()


def create_branch(name: str) -> bool:
    """Create and checkout a new branch."""
    try:
        subprocess.run(
            ["git", "checkout", "-b", name],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def commit_and_push(message: str, branch: str) -> bool:
    """Stage all changes, commit, and push to the branch."""
    try:
        subprocess.run(
            ["git", "add", "-A"],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["git", "push", "-u", "origin", branch],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        logger.error("Push failed: %s", e.stderr)
        return False


def analyze_changes() -> ChangeAnalysis:
    """Analyze staged/unstaged changes for labeling."""
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )

    new_features: list[str] = []
    changed_categories: list[str] = []
    removed_features: list[str] = []
    additions = 0
    deletions = 0

    for line in result.stdout.split("\n"):
        if "=>" in line:
            parts = line.split("=>")
            if len(parts) == 2:
                old = parts[0].strip().strip("{}")
                new = parts[1].strip().strip("{}")
                if old.endswith(".md") and new.endswith(".md"):
                    changed_categories.append(new.replace(".md", ""))
        elif "|" in line:
            parts = line.split("|")
            if len(parts) == 2:
                try:
                    nums = parts[1].strip().split()
                    if len(nums) >= 2:
                        additions += int(nums[0])
                        deletions += int(nums[1])
                except (ValueError, IndexError):
                    pass

    # Check for new release directories
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    for line in status_result.stdout.split("\n"):
        if line.startswith("A ") and ".meta.json" in line:
            slug = line.split("/")[-2] if "/" in line else "unknown"
            new_features.append(slug)
        elif line.startswith("D ") and ".md" in line:
            removed_features.append(line.strip())

    labels: list[str] = []
    if new_features:
        labels.append("new-release")
    if changed_categories:
        labels.append("category-update")
    if removed_features:
        labels.append("regression-alert")
    if additions > 100:
        labels.append("large-change")

    return ChangeAnalysis(
        new_features=new_features,
        changed_categories=changed_categories,
        removed_features=removed_features,
        total_additions=additions,
        total_deletions=deletions,
        labels=labels,
    )


def create_pr(
    title: str,
    body: str,
    branch: str,
    base: str = "main",
    labels: list[str] | None = None,
    auto_merge: bool = False,
) -> PRResult:
    """Create a pull request using gh CLI."""
    args = [
        "pr",
        "create",
        "--title",
        title,
        "--body",
        body,
        "--head",
        branch,
        "--base",
        base,
    ]

    if labels:
        args.extend(["--label", ",".join(labels)])

    result = _run_gh(args, check=False)
    if result.returncode != 0:
        return PRResult(success=False, error=result.stderr.strip())

    # Parse PR number and URL from output
    pr_url = result.stdout.strip()
    pr_number = 0
    if "/pull/" in pr_url:
        try:
            pr_number = int(pr_url.split("/pull/")[-1].split("/")[0].split("?")[0])
        except (ValueError, IndexError):
            pass

    if auto_merge and pr_number:
        merge_args = ["pr", "merge", str(pr_number), "--auto", "--squash"]
        _run_gh(merge_args, check=False)

    return PRResult(
        success=True,
        pr_number=pr_number,
        pr_url=pr_url,
        branch=branch,
    )


def generate_diff_preview() -> str:
    """Generate a markdown diff preview for the PR body."""
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )

    status_result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        check=False,
    )

    lines = ["## 📋 Resumo das Alterações\n"]

    if status_result.stdout.strip():
        lines.append("### Arquivos modificados\n")
        lines.append("```")
        lines.append(status_result.stdout.strip())
        lines.append("```\n")

    if result.stdout.strip():
        lines.append("### Estatísticas\n")
        lines.append("```")
        lines.append(result.stdout.strip())
        lines.append("```\n")

    analysis = analyze_changes()
    if analysis.labels:
        lines.append(f"### Labels: {', '.join(analysis.labels)}\n")

    if analysis.new_features:
        lines.append(f"### 🆕 Novas releases: {', '.join(analysis.new_features)}\n")

    if analysis.total_additions or analysis.total_deletions:
        lines.append(f"**+{analysis.total_additions}** / **-{analysis.total_deletions}** linhas\n")

    lines.append("---\n_Gerado automaticamente pelo pipeline de Release Notes_")

    return "\n".join(lines)


def submit_changes(
    release_slug: str = "",
    auto_merge: bool = False,
    target_branch: str = "develop",
) -> PRResult:
    """Full workflow: create branch, commit, push, open PR.

    By default targets 'develop' as a staging branch. After CI passes
    on develop, a separate PR can be opened from develop to main.
    This two-stage approach ensures main always stays clean.

    Args:
        release_slug: Slug of the release being processed.
        auto_merge: Enable auto-merge on the resulting PR.
        target_branch: Branch to push to and create PR against.
            Use 'develop' for staging, 'main' for direct PR.
    """
    from datetime import datetime, timezone

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d-%H%M")
    branch_name = f"release-notes/{release_slug or 'auto'}-{timestamp}"

    if not create_branch(branch_name):
        return PRResult(success=False, error="Failed to create branch")

    analysis = analyze_changes()
    diff_preview = generate_diff_preview()

    title = f"chore(release-notes): {release_slug or 'atualização automática'} — {timestamp}"
    body = diff_preview

    if not commit_and_push(
        f"chore(release-notes): {release_slug or 'update'} — {timestamp}", branch_name
    ):
        return PRResult(success=False, branch=branch_name, error="Failed to commit and push")

    pr_result = create_pr(
        title=title,
        body=body,
        branch=branch_name,
        base=target_branch,
        labels=analysis.labels,
        auto_merge=auto_merge,
    )

    # Switch back to target branch
    subprocess.run(["git", "checkout", target_branch], capture_output=True, text=True, check=False)

    return pr_result
