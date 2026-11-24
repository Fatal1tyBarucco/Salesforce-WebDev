"""Stub export module for backward compatibility."""

from __future__ import annotations


async def export_release_json(slug: str) -> str:
    """Export release as JSON."""
    return ""


async def export_release_csv(slug: str) -> str:
    """Export release as CSV."""
    return ""


async def export_all_releases(output_dir: str = "exports") -> dict[str, list[str]]:
    """Export all releases."""
    return {}
