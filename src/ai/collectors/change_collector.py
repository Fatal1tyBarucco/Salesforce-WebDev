"""Deterministic change collector — no LLM used; provides raw context to LLM."""
from __future__ import annotations
import subprocess
import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

IGNORE_GLOBS = [
    ".lock",
    "package-lock.json",
    "uv.lock",
    ".gitignore",
    ".github/ai-docs-ignore",
    "docs/.last-processed-ref",
    "NOTIFICATION_DIGEST.md",
    "DIFF_REPORT.md",
    "*.md",  # pipeline output; exclude from context
]

def run_cmd(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else result.stderr
    except Exception as exc:
        logger.warning("Command %s failed: %s", cmd, exc)
        return ""

def collect_changes(since_ref: str = "HEAD~10") -> dict[str, Any]:
    """Gather deterministic context since `since_ref`."""
    commits_raw = run_cmd(["git", "log", f"{since_ref}..HEAD", "--pretty=format:%H %s"])
    diffs_stat = run_cmd(["git", "diff", "--stat", since_ref])
    conventional = [line for line in commits_raw.splitlines() if re.search(r"^(feat|fix|BREAKING|refactor|docs|test|chore)\(", line)]
    # PR metadata from gh cli (if available in CI)
    pr_output = run_cmd(["gh", "pr", "list", "--state", "merged", "--json", "title,body,labels,number"])
    pr_merged = []
    try:
        import json
        if pr_output:
            pr_merged = json.loads(pr_output)[:10]
    except Exception:
        pass
    # Diff snippets (truncated)
    snippets = []
    for line in diffs_stat.splitlines():
        if any(g in line for g in IGNORE_GLOBS):
            continue
        snippets.append(line[:2000])
    return {
        "commits": [c for c in commits_raw.splitlines() if c.strip()],
        "git_diff_stat": diffs_stat,
        "diff_snippets": snippets[:50],
        "conventional_commits": conventional,
        "merged_prs": pr_merged,
        "since_ref": since_ref,
        "to_ref": "HEAD",
    }
