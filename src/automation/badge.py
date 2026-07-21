"""Dynamic badge generation."""

from __future__ import annotations

import json
from pathlib import Path


def _get_releases_dir() -> Path:
    from ..config import RELEASES_DIR

    return Path(RELEASES_DIR)


def generate_dynamic_badge(release_name: str, total_features: int) -> str:
    """Generate a dynamic badge markdown for the latest release."""
    return f"![Latest Release](https://img.shields.io/badge/Última%20Release-{release_name.replace(' ', '%20')}-blue)"


def get_latest_release_badge() -> str:
    """Get the latest release name for badge display."""
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
