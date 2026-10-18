#!/usr/bin/env python3
"""Auto-update docs/changelog.md with high-impact commits only."""
from __future__ import annotations
import subprocess
import re
from pathlib import Path

CHANGELOG = Path("docs/changelog.md")
MAX_COMMITS = 10
IMPACT_KEYWORDS = ["feat", "refactor", "upgrade", "pipeline", "docs", "ai-", "enhanced", "quality", "rebuild", "redesign"]
SKIP_AUTHOR_MSG = ["github-actions[bot]", "docs(sync)", "chore(", "fix(", "update"]

def get_impact_commits():
    result = subprocess.run(
        ["git", "log", "--pretty=format:%h|%s", "--no-merges", "-i", "--all", f"-{MAX_COMMITS}"],
        capture_output=True, text=True,
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
    lines = ["\n---\n\n## Atualizações automáticas (grande impacto)\n"]
    added = False
    for sha, msg in commits:
        if already_in_changelog(msg):
            continue
        lines.append(f"- `{sha}` — {msg}\n")
        added = True
    if added:
        with open(CHANGELOG, "a", encoding="utf-8") as f:
            f.writelines(lines)
    return added

if __name__ == "__main__":
    commits = get_impact_commits()
    modified = append_to_changelog(commits)
    if modified:
        print(f"Changelog atualizado: {len([c for c in commits if not already_in_changelog(c[1])])} novos itens.")
    else:
        print("Nenhuma nova atualização de grande impacto detectada.")
