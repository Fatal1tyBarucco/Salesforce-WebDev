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
            if not line or line.startswith(("#", "|")):
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


def _sanitize_value(value: Any) -> Any:
    """Recursively sanitize string values to prevent XSS.

    Escapes HTML special characters in all string values within
    dicts and lists, preventing injection into the dashboard template.
    """
    if isinstance(value, str):
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
    elif isinstance(value, dict):
        return {k: _sanitize_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    return value


def generate_dashboard_html(data: dict[str, Any]) -> str:
    """Generate interactive HTML dashboard with XSS-safe data.

    Only inlines minimal metadata (releases for selects), features loaded lazily
    from dashboard-data.json to avoid bloating HTML with ~20KB+ of feature data.
    """
    sanitized = _sanitize_value(data)
    # Only inline releases metadata (needed immediately for dropdowns)
    releases_data = {
        "releases": sanitized.get("releases", []),
        "total_releases": sanitized.get("total_releases", 0),
        "total_features": sanitized.get("total_features", 0),
    }
    releases_json = json.dumps(releases_data, ensure_ascii=True)
    template_path = Path(__file__).parent / "dashboard_template.html"
    template = template_path.read_text(encoding="utf-8")
    return template.replace("{DATA_JSON}", releases_json)


def generate_dashboard_data_json(
    data: dict[str, Any], output_dir: str = DASHBOARD_DIR
) -> str | None:
    """Generate separate JSON data file for lazy loading."""
    sanitized = _sanitize_value(data)
    data_json = json.dumps(sanitized, ensure_ascii=True)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    output_file = out_path / "dashboard-data.json"
    output_file.write_text(data_json, encoding="utf-8")
    return str(output_file)


def generate_dashboard(output_dir: str = DASHBOARD_DIR) -> str | None:
    """Generate interactive dashboard. Returns output path or None if no data."""
    data = _build_dashboard_data()
    if not data["releases"]:
        return None

    # Generate separate JSON data file for lazy loading
    generate_dashboard_data_json(data, output_dir)

    html_content = generate_dashboard_html(data)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # Copy combined CSS to output directory for self-contained dashboard
    css_src = Path(__file__).parent / "design-system" / "dashboard-combined.css"
    css_dst_dir = out_path / "design-system"
    css_dst_dir.mkdir(parents=True, exist_ok=True)
    css_dst = css_dst_dir / "dashboard-combined.css"
    if css_src.exists():
        css_dst.write_text(css_src.read_text(encoding="utf-8"), encoding="utf-8")

    output_file = out_path / "dashboard.html"
    output_file.write_text(html_content, encoding="utf-8")
    return str(output_file)
