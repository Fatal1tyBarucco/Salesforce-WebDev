"""Deterministic Git/GitHub change collector; this module never calls an LLM."""

from __future__ import annotations

import fnmatch
import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)
MAX_DIFF_CHARS = 20_000
MAX_DIFF_FILES = 40
MAX_PR_BODY_CHARS = 4_000
DEFAULT_IGNORES = (
    "*.lock",
    "package-lock.json",
    "docs/.last-processed-ref",
    "docs/.ai-logs/**",
    "docs/ai-generated/**",
    "*.md",
)
IGNORE_GLOBS = list(DEFAULT_IGNORES)
CONVENTIONAL_RE = re.compile(
    r"^(?:feat|fix|build|chore|ci|docs|perf|refactor|revert|style|test)(?:\([^)]*\))?!?:"
    r"|^BREAKING CHANGE:",
    re.IGNORECASE,
)


def run_cmd(cmd: list[str]) -> str:
    """Run a bounded subprocess and return stdout; report failures without leaking data."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.warning("Command failed (%s): %s", cmd[0] if cmd else "unknown", type(exc).__name__)
        return ""
    if result.returncode:
        logger.debug("Command exited with status %s: %s", result.returncode, cmd[0])
        return ""
    return result.stdout


def _ignore_patterns() -> list[str]:
    patterns = list(DEFAULT_IGNORES)
    ignore_file = Path(".github/ai-docs-ignore")
    if ignore_file.exists():
        patterns.extend(
            line.strip()
            for line in ignore_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    return patterns


def _is_ignored(path: str, patterns: list[str]) -> bool:
    return any(
        fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(Path(path).name, pattern)
        for pattern in patterns
    )


def collect_changes(since_ref: str = "HEAD~10") -> dict[str, Any]:
    """Collect commits, stats, bounded full diffs, and merged PR metadata."""
    if not since_ref or since_ref.startswith("-"):
        raise ValueError("since_ref must be a non-empty Git ref, not an option.")
    if not run_cmd(["git", "rev-parse", "--verify", f"{since_ref}^{{commit}}"]):
        raise ValueError(f"since_ref does not resolve to a Git commit: {since_ref}")
    commits_output = run_cmd(
        ["git", "log", f"{since_ref}..HEAD", "--format=%H%x09%s%x09%b%x1e", "--no-decorate"]
    )
    changed_paths_output = run_cmd(["git", "diff", "--name-only", "-z", f"{since_ref}..HEAD"])
    patterns = _ignore_patterns()
    changed_paths = [
        path
        for path in changed_paths_output.split("\0")
        if path and not _is_ignored(path, patterns)
    ]
    diff_stat = (
        run_cmd(["git", "diff", "--stat", f"{since_ref}..HEAD", "--", *changed_paths])
        if changed_paths
        else ""
    )

    commit_rows: list[dict[str, str]] = []
    for record in commits_output.split("\x1e"):
        record = record.strip("\n")
        if not record.strip():
            continue
        commit_hash, hash_separator, rest = record.partition("\t")
        subject, subject_separator, body = rest.partition("\t")
        if hash_separator:
            commit_rows.append(
                {
                    "sha": commit_hash,
                    "subject": subject.strip(),
                    "body": body.strip() if subject_separator else "",
                }
            )
        else:
            commit_rows.append({"sha": "", "subject": record.strip(), "body": ""})
    commits = [row["subject"] for row in commit_rows]
    conventional = [
        f"{row['subject']}\n{row['body']}".strip()
        for row in commit_rows
        if CONVENTIONAL_RE.search(row["subject"])
        or re.search(r"^BREAKING CHANGE:", row["body"], re.MULTILINE)
    ]

    diff_snippets: list[str] = []
    for path in changed_paths[:MAX_DIFF_FILES]:
        diff = run_cmd(["git", "diff", f"{since_ref}..HEAD", "--", path])
        if diff:
            diff_snippets.append(f"--- {path}\n{diff[:MAX_DIFF_CHARS]}")

    return {
        "commits": commits,
        "commit_details": commit_rows,
        "git_diff_stat": diff_stat[:MAX_DIFF_CHARS],
        "changed_files": changed_paths[:MAX_DIFF_FILES],
        "diff_snippets": diff_snippets,
        "conventional_commits": conventional,
        "merged_prs": _collect_merged_prs({row["sha"] for row in commit_rows if row["sha"]}),
        "since_ref": since_ref,
        "to_ref": "HEAD",
    }


def _collect_merged_prs(commit_hashes: set[str] | None = None) -> list[dict[str, Any]]:
    output = run_cmd(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "merged",
            "--limit",
            "1000",
            "--json",
            "title,body,labels,number,mergedAt,mergeCommit,closingIssuesReferences",
        ]
    )
    if not output:
        return []
    try:
        prs = json.loads(output)
    except json.JSONDecodeError:
        logger.warning("gh returned invalid PR JSON; skipping PR metadata.")
        return []
    if not isinstance(prs, list):
        return []
    normalized: list[dict[str, Any]] = []
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        if commit_hashes is not None:
            merge_commit = pr.get("mergeCommit")
            merge_sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
            if merge_sha not in commit_hashes:
                continue
        body = pr.get("body")
        if isinstance(body, str):
            pr["body"] = body[:MAX_PR_BODY_CHARS]
        normalized.append(pr)
    return normalized
