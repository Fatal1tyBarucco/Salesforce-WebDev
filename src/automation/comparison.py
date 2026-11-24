"""Stub comparison module for backward compatibility."""

from __future__ import annotations

from typing import Any


def compare_releases(current_slug: str, previous_slug: str) -> dict[str, Any]:
    """Compare two releases."""
    return {
        "current": current_slug,
        "previous": previous_slug,
        "added": [],
        "removed": [],
        "changed": [],
        "stats": {},
    }


async def generate_comparison_report(current_slug: str, previous_slug: str) -> str:
    """Generate comparison report."""
    return ""


async def calculate_quality_metrics(slug: str) -> dict[str, Any] | None:
    """Calculate quality metrics."""
    return None


async def detect_regressions(current_slug: str, previous_slug: str) -> list[dict[str, Any]]:
    """Detect regressions."""
    return []


async def generate_quality_report() -> str:
    """Generate quality report."""
    return ""
