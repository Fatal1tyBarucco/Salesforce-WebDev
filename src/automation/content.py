"""Stub content module for backward compatibility."""

from __future__ import annotations

from pathlib import Path
from typing import Any


async def analyze_content_changes(release_slug: str) -> dict[str, Any]:
    """Analyze content changes."""
    return {
        "release_slug": release_slug,
        "unchanged_files": [],
        "changed_files": [],
        "new_files": [],
        "deleted_files": [],
    }


async def generate_deduplication_report(release_slug: str) -> str:
    """Generate deduplication report."""
    return ""


async def get_content_hash(file_path: str) -> str | None:
    """Get content hash."""
    return None


async def is_content_unchanged(file_path: str, expected_hash: str) -> bool:
    """Check if content is unchanged."""
    return True


def load_content_cache(cache_path: Path) -> dict[str, Any]:
    """Load content cache."""
    return {}


def save_content_cache(cache_path: Path, cache: dict[str, Any]) -> None:
    """Save content cache."""
