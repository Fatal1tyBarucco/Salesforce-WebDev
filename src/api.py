"""REST API server for release data.

Provides JSON endpoints for programmatic access to release metadata.
No external dependencies — uses stdlib http.server.

Endpoints:
    GET /releases                         — list all releases
    GET /releases/{slug}                  — full release details
    GET /releases/{slug}/categories/{name} — category features
    GET /diff/{current}/{previous}        — comparison between releases
"""

from __future__ import annotations

import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

from .config import RELEASES_DIR

logger = logging.getLogger(__name__)

API_PORT = 8081


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
            except (json.JSONDecodeError, OSError):
                continue
    metas.sort(key=lambda m: m.get("release_id", 0))
    return metas


def _find_meta(slug: str) -> dict[str, Any] | None:
    """Find a release meta by slug."""
    meta_path = Path(RELEASES_DIR) / slug / ".meta.json"
    if not meta_path.exists():
        return None
    try:
        result: dict[str, Any] = json.loads(meta_path.read_text(encoding="utf-8"))
        return result
    except (json.JSONDecodeError, OSError):
        return None


def _parse_category_features(slug: str, category_name: str) -> list[dict[str, Any]]:
    """Parse features from a category markdown file."""
    releases_dir = Path(RELEASES_DIR) / slug
    if not releases_dir.exists():
        return []

    # Find the matching .md file by category name
    target_file = None
    for md_file in releases_dir.glob("*.md"):
        if md_file.name.startswith("."):
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            first_line = content.split("\n", 1)[0].strip()
            if first_line.startswith("## "):
                file_category = first_line[3:].strip()
                if file_category.lower() == category_name.lower():
                    target_file = md_file
                    break
        except OSError:
            continue

    if target_file is None:
        return []

    features: list[dict[str, Any]] = []
    try:
        content = target_file.read_text(encoding="utf-8")
    except OSError:
        return []

    for line in content.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("|"):
            continue
        # Bullet point format: * **Feature name** — _Availability_
        bullet_match = re.match(r"^\*\s+\*\*(.+?)\*\*\s*(?:—\s*_(.+)_)?$", line)
        if bullet_match:
            name = bullet_match.group(1).strip()
            availability = bullet_match.group(2) or ""
            features.append({"name": name, "availability": availability.strip()})
            continue
        # Tab-separated format (raw feature impact data)
        if "\t" in line:
            parts = line.split("\t")
            name = parts[0].strip()
            if name:
                features.append({"name": name, "availability": ""})
            continue
        # Plain text line (long enough to be a feature)
        if len(line) > 10:
            features.append({"name": line, "availability": ""})

    return features


def _build_diff(current_meta: dict[str, Any], previous_meta: dict[str, Any]) -> dict[str, Any]:
    """Build a diff between two releases."""
    curr_cats = {c["name"]: c["count"] for c in current_meta.get("categories", [])}
    prev_cats = {c["name"]: c["count"] for c in previous_meta.get("categories", [])}

    all_names = sorted(set(curr_cats.keys()) | set(prev_cats.keys()))
    changes: list[dict[str, Any]] = []
    for name in all_names:
        prev_count = prev_cats.get(name, 0)
        curr_count = curr_cats.get(name, 0)
        delta = curr_count - prev_count
        changes.append(
            {
                "category": name,
                "previous": prev_count,
                "current": curr_count,
                "delta": delta,
            }
        )

    return {
        "current": current_meta.get("name", current_meta.get("slug", "?")),
        "previous": previous_meta.get("name", previous_meta.get("slug", "?")),
        "changes": changes,
        "total_delta": current_meta.get("total_features", 0)
        - previous_meta.get("total_features", 0),
    }


class APIHandler(BaseHTTPRequestHandler):
    """HTTP handler for REST API endpoints."""

    def do_GET(self) -> None:
        path = self.path.rstrip("/")
        metas = _load_all_metas()

        if path == "/releases":
            self._respond(200, {"releases": metas})

        elif path.startswith("/releases/") and path.count("/") == 2:
            slug = path.split("/")[2]
            meta = _find_meta(slug)
            if meta is None:
                self._respond(404, {"error": f"release '{slug}' not found"})
                return
            self._respond(200, meta)

        elif path.startswith("/releases/") and path.count("/") == 4:
            parts = path.split("/")
            slug = parts[2]
            category_name = parts[4]
            meta = _find_meta(slug)
            if meta is None:
                self._respond(404, {"error": f"release '{slug}' not found"})
                return
            features = _parse_category_features(slug, category_name)
            self._respond(
                200,
                {
                    "release": meta.get("name", slug),
                    "category": category_name,
                    "features": features,
                    "count": len(features),
                },
            )

        elif path.startswith("/diff/") and path.count("/") == 3:
            parts = path.split("/")
            current_slug = parts[2]
            previous_slug = parts[3]
            current_meta = _find_meta(current_slug)
            previous_meta = _find_meta(previous_slug)
            if current_meta is None:
                self._respond(404, {"error": f"release '{current_slug}' not found"})
                return
            if previous_meta is None:
                self._respond(404, {"error": f"release '{previous_slug}' not found"})
                return
            diff = _build_diff(current_meta, previous_meta)
            self._respond(200, diff)

        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, code: int, data: dict[str, Any] | list[Any]) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        logger.debug("API server: %s", format % args)


def start_api_server(port: int = API_PORT) -> HTTPServer:
    """Start REST API HTTP server in a background thread."""
    server = HTTPServer(("0.0.0.0", port), APIHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("REST API server started on port %d", port)
    return server
