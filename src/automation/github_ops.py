"""Stub github_ops module for backward compatibility."""

from __future__ import annotations


async def create_github_issue(
    release_name: str, total_features: int, categories: int
) -> str | None:
    """Create GitHub issue."""
    return None
