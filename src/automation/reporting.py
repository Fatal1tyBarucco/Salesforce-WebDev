"""Stub reporting module for backward compatibility."""

from __future__ import annotations

from typing import Any


async def generate_ai_summary_report(current_slug: str, previous_slug: str) -> str:
    """Generate AI summary report."""
    return ""


async def generate_changelog() -> str:
    """Generate changelog."""
    return ""


async def generate_diff_report(current_slug: str, previous_slug: str) -> str:
    """Generate diff report."""
    return ""


async def _generate_legacy_ai_summary(current_slug: str, previous_slug: str) -> str:
    """Generate legacy AI summary."""
    return ""


async def generate_regression_report(current_slug: str, previous_slug: str) -> str:
    """Generate regression report."""
    return ""


async def generate_quality_report() -> str:
    """Generate quality report."""
    return ""


async def calculate_category_impact_scores() -> list[dict[str, Any]]:
    """Calculate category impact scores."""
    return []
