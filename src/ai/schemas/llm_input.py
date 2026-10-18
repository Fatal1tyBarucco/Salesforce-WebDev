"""Schema for LLM input (raw context to classify)."""
<<<<<<< HEAD

from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


=======
from __future__ import annotations
from pydantic import BaseModel, Field

>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
class RawContext(BaseModel):
    git_commits: list[str] = Field(default_factory=list, description="Commit messages")
    git_diff_stat: str = Field("", description="git diff --stat output")
    diff_snippets: list[str] = Field(default_factory=list, description="Truncated file diffs")
    conventional_commits: list[str] = Field(default_factory=list)
<<<<<<< HEAD
    merged_prs: list[dict[str, Any]] = Field(
        default_factory=list, description="PR metadata from gh cli"
    )
=======
    merged_prs: list[dict] = Field(default_factory=list, description="PR metadata from gh cli")
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
    since_ref: str = Field("", description="Base ref")
    to_ref: str = Field("HEAD", description="Head ref")
