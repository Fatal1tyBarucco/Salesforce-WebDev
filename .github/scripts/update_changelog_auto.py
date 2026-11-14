#!/usr/bin/env python3
"""Auto-update docs/changelog.md with high-impact commits only."""

from __future__ import annotations

import subprocess
from pathlib import Path

CHANGELOG = Path("docs/changelog.md")
MAX_COMMITS = 10
IMPACT_KEYWORDS = [
    "feat",
    "refactor",
    "upgrade",
    "pipeline",
    "docs",
    "ai-",
    "enhanced",
    "quality",
    "rebuild",
    "redesign",
]
SKIP_AUTHOR_MSG = ["github-actions[bot]", "docs(sync)", "chore(", "fix(", "update"]


def get_impact_commits():
    result = subprocess.run(
        ["git", "log", "--pretty=format:%h|%s", "--no-merges", "-i", "--all", f"-{MAX_COMMITS}"],
        capture_output=True,
        text=True,
    )
    commits = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 1)
        if len(parts) != 2:
            continue
        sha, msg = parts
        msg_lower = msg.lower()
        # Skip non-impact authors/messages
        if any(sk in msg for sk in SKIP_AUTHOR_MSG):
            continue
        if not any(kw in msg_lower for kw in IMPACT_KEYWORDS):
            continue
        commits.append((sha[:7], msg))
    return commits


def already_in_changelog(msg: str) -> bool:
    if not CHANGELOG.exists():
        return False
    content = CHANGELOG.read_text(encoding="utf-8")
    return msg in content


def append_to_changelog(commits):
    if not commits:
        return False

    new_entries = [f"- `{sha}` — {msg}\n" for sha, msg in commits if not already_in_changelog(msg)]
    if not new_entries:
        return False

    content = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else ""
    section = "## Atualizações automáticas (grande impacto)"
    if section in content:
        content = content.rstrip() + "\n" + "".join(new_entries)
    else:
        content = content.rstrip() + f"\n\n---\n\n{section}\n\n" + "".join(new_entries)

    CHANGELOG.write_text(content.rstrip() + "\n", encoding="utf-8")
    return True


if __name__ == "__main__":
    commits = get_impact_commits()
    modified = append_to_changelog(commits)
    if modified:
        print(
            f"Changelog atualizado: {len([c for c in commits if not already_in_changelog(c[1])])} novos itens."
        )
    else:
        print("Nenhuma nova atualização de grande impacto detectada.")
