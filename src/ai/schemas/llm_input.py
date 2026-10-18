"""Schema for LLM input (raw context to classify)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RawContext(BaseModel):
    git_commits: list[str] = Field(default_factory=list, description="Commit messages")
    git_diff_stat: str = Field("", description="git diff --stat output")
    diff_snippets: list[str] = Field(default_factory=list, description="Truncated file diffs")
    conventional_commits: list[str] = Field(default_factory=list)
    merged_prs: list[dict[str, Any]] = Field(
        default_factory=list, description="PR metadata from gh cli"
    )
    since_ref: str = Field("", description="Base ref")
    to_ref: str = Field("HEAD", description="Head ref")
