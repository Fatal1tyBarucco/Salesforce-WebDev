"""Dynamic badge generation for releases.

Uses the AI generators/badges module for professional badge creation,
with fallback to simple shields.io URLs.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..ai.generators.badges import (
    category_header_badges,
    feature_count_badge,
    release_badge,
    release_meta_badges,
)


def _get_releases_dir() -> Path:
    from ..config import RELEASES_DIR

    return Path(RELEASES_DIR)


def generate_dynamic_badge(release_name: str, total_features: int) -> str:
    """Generate a dynamic badge markdown for the latest release.

    Args:
        release_name: Release name (e.g. "Summer '26").
        total_features: Total feature count.

    Returns:
        Markdown badge string.
    """
    release = release_badge(release_name)
    features = feature_count_badge(total_features)
    return f"{release.to_markdown()} {features.to_markdown()}"


def get_latest_release_badge() -> str:
    """Get the latest release name for badge display.

    Returns:
        Release name string or "N/A" if not found.
    """
    releases_dir = _get_releases_dir()
    if not releases_dir.exists():
        return "N/A"
    latest = None
    latest_id = -1
    for d in releases_dir.iterdir():
        meta_path = releases_dir / d.name / ".meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                if meta and meta.get("release_id", 0) > latest_id:
                    latest_id = meta.get("release_id", 0)
                    latest = meta.get("name", d.name)
            except (json.JSONDecodeError, OSError):
                continue
    return latest or "N/A"


def generate_release_header_badges(slug: str) -> str:
    """Generate a full badge row for a release header.

    Args:
        slug: Release slug (e.g. "summer_26").

    Returns:
        Markdown string with release metadata badges.
    """
    releases_dir = _get_releases_dir()
    meta_path = releases_dir / slug / ".meta.json"

    if not meta_path.exists():
        return ""

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    name = meta.get("name", slug)
    total = sum(c.get("count", 0) for c in meta.get("categories", []))
    cat_count = len(meta.get("categories", []))

    return release_meta_badges(name, total, cat_count)


def generate_category_badges(slug: str, category_name: str) -> str:
    """Generate badges for a specific category in a release.

    Args:
        slug: Release slug.
        category_name: Category name.

    Returns:
        Markdown string with category badges.
    """
    releases_dir = _get_releases_dir()
    meta_path = releases_dir / slug / ".meta.json"

    if not meta_path.exists():
        return ""

    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    for cat in meta.get("categories", []):
        if cat.get("name") == category_name:
            count = cat.get("count", 0)
            return category_header_badges(category_name, count)

    return ""
