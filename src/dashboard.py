"""Interactive web dashboard for release exploration.

Generates a static HTML dashboard with JavaScript for:
- Feature search across all releases
- Category filter and drill-down
- Side-by-side release comparison
- Confidence heatmap visualization
- Export filtered results as CSV/JSON

No external dependencies — pure stdlib + inline JS.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import RELEASES_DIR

DASHBOARD_DIR = "analytics"


def _load_all_metas() -> list[dict[str, Any]]:
    """Load all .meta.json files sorted by release_id."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return []
    metas = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
                metas.append(meta)
            except json.JSONDecodeError, OSError:
                continue

    metas.sort(key=lambda m: m.get("release_id", 0))
    return metas


def _load_features(slug: str) -> list[dict[str, str]]:
    """Load features from all .md files in a release."""
    releases_dir = Path(RELEASES_DIR) / slug
    if not releases_dir.exists():
        return []

    features: list[dict[str, str]] = []
    for md_file in releases_dir.glob("*.md"):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue

        category = ""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## "):
                category = line[3:].strip()
                continue
            if not line or line.startswith("#") or line.startswith("|"):
                continue

            bullet_match = re.match(r"^\*\s+\*\*(.+?)\*\*\s*(?:—\s*_(.+)_)?$", line)
            if bullet_match:
                features.append(
                    {
                        "name": bullet_match.group(1).strip(),
                        "category": category,
                        "availability": (bullet_match.group(2) or "").strip(),
                        "release": slug,
                    }
                )
                continue
            if "\t" in line:
                parts = line.split("\t")
                name = parts[0].strip()
                if name and len(name) > 3:
                    features.append(
                        {
                            "name": name,
                            "category": category,
                            "availability": "",
                            "release": slug,
                        }
                    )
                continue
            if len(line) > 10:
                features.append(
                    {
                        "name": line,
                        "category": category,
                        "availability": "",
                        "release": slug,
                    }
                )

    return features


def _build_dashboard_data() -> dict[str, Any]:
    """Build all data needed for the dashboard."""
    metas = _load_all_metas()
    releases: list[dict[str, Any]] = []
    all_features: list[dict[str, str]] = []

    for meta in metas:
        slug = meta.get("slug", "")
        releases.append(
            {
                "name": meta.get("name", slug),
                "slug": slug,
                "release_id": meta.get("release_id", 0),
                "total_features": meta.get("total_features", 0),
                "avg_confidence": meta.get("avg_confidence", 0),
                "categories": meta.get("categories", []),
            }
        )
        features = _load_features(slug)
        all_features.extend(features)

    return {
        "releases": releases,
        "features": all_features,
        "total_releases": len(releases),
        "total_features": len(all_features),
    }


def generate_dashboard_html(data: dict[str, Any]) -> str:
    """Generate interactive HTML dashboard."""
    data_json = json.dumps(data, ensure_ascii=True)
    template_path = Path(__file__).parent / "dashboard_template.html"
    template = template_path.read_text(encoding="utf-8")
    return template.replace("{DATA_JSON}", data_json)


def generate_dashboard(output_dir: str = DASHBOARD_DIR) -> str | None:
    """Generate interactive dashboard. Returns output path or None if no data."""
    data = _build_dashboard_data()
    if not data["releases"]:
        return None
    html_content = generate_dashboard_html(data)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    output_file = out_path / "dashboard.html"
    output_file.write_text(html_content, encoding="utf-8")
    return str(output_file)
