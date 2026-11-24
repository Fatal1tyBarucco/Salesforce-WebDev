"""Stub notifications module for backward compatibility."""

from __future__ import annotations

from typing import Any


async def generate_filtered_notification(
    slug: str, profile_type: str, categories: list[dict[str, Any]]
) -> dict[str, Any]:
    """Generate filtered notification."""
    return {
        "slug": slug,
        "profile_type": profile_type,
        "features": [],
        "summary": "",
    }
