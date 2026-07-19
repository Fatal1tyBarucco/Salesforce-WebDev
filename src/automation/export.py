"""JSON/CSV export for release data."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def _get_releases_dir() -> Path:
    from ..config import RELEASES_DIR

    return Path(RELEASES_DIR)


async def export_release_json(load_meta_fn: Any, slug: str) -> str:
    """Export release data as formatted JSON."""
    meta = load_meta_fn(slug)
    return json.dumps(meta if meta else {}, ensure_ascii=False, indent=2)


async def export_release_csv(load_meta_fn: Any, slug: str) -> str:
    """Export release feature data as CSV."""
    meta = load_meta_fn(slug)
    if not meta:
        return ""

    lines = ["category,feature,available_users,available_admins,requires_config,contact_sf"]
    release_dir = _get_releases_dir() / slug

    for cat_info in meta.get("categories", []):
        cat_name = cat_info["name"]
        slug_name = re.sub(r"[^a-z0-9]+", "_", cat_name.lower()).strip("_")
        md_file = release_dir / f"{slug_name}.md"

        if not md_file.exists():
            continue

        content = md_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if not line.startswith("|") or line.startswith("| :") or "Recurso" in line:
                continue
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 5:
                name = cells[0].replace("**", "").replace(" ⚠️", "")
                users = "Yes" if "✅" in cells[1] else "No"
                admins = "Yes" if "✅" in cells[2] else "No"
                config = "Yes" if "✅" in cells[3] else "No"
                contact = "Yes" if "✅" in cells[4] else "No"
                lines.append(
                    f"{cat_name.replace(',', ';')},{name.replace(',', ';')},{users},{admins},{config},{contact}"
                )

    return "\n".join(lines)


async def export_all_releases(
    load_meta_fn: Any, output_dir: str = "exports"
) -> dict[str, list[str]]:
    """Export all releases as both JSON and CSV files."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    results: dict[str, list[str]] = {}
    releases_dir = _get_releases_dir()

    if not releases_dir.exists():
        return results

    dirs_with_meta = []
    for d in releases_dir.iterdir():
        if not d.is_dir() or d.name == "exports":
            continue
        if not (d / ".meta.json").exists():
            continue
        meta = load_meta_fn(d.name)
        release_id = meta.get("release_id", 0) if meta else 0
        dirs_with_meta.append((d, release_id))

    dirs_with_meta.sort(key=lambda x: x[1], reverse=True)

    for d, _ in dirs_with_meta:
        json_content = await export_release_json(load_meta_fn, d.name)
        json_path = out / f"{d.name}.json"
        json_path.write_text(json_content, encoding="utf-8")

        csv_content = await export_release_csv(load_meta_fn, d.name)
        csv_path = out / f"{d.name}.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        results[d.name] = [str(json_path), str(csv_path)]

    return results
