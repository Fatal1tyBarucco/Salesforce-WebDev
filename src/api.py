"""REST API server for release data.

Provides JSON and GraphQL endpoints for programmatic access to release metadata.
No external dependencies — uses stdlib http.server.

REST Endpoints:
    GET  /releases                         — list all releases
    GET  /releases/{slug}                  — full release details
    GET  /releases/{slug}/categories/{name} — category features
    GET  /diff/{current}/{previous}        — comparison between releases

GraphQL Endpoint:
    POST /graphql                          — flexible query interface

OpenAPI:
    GET  /openapi.json                     — OpenAPI 3.0 specification
"""

from __future__ import annotations

import json
import logging
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

from .config import RELEASES_DIR, KNOWN_RELEASES
from .models import ErrorResponse, ReleaseResponse

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


def _validate_slug(slug: str) -> bool:
    """Validate a slug to prevent path traversal and ensure it maps to a known release."""
    if not slug or not re.match(r"^[a-z0-9_]+$", slug):
        return False
    # Reject slugs that do not correspond to any known release.
    return any(release.slug == slug for release in KNOWN_RELEASES)


def _find_meta(slug: str) -> dict[str, Any] | None:
    """Find a release meta by slug."""
    if not _validate_slug(slug):
        return None
    base = Path(RELEASES_DIR).resolve()
    meta_path = (base / slug).resolve()
    if not meta_path.is_relative_to(base):
        return None
    meta_file = meta_path / ".meta.json"
    if not meta_file.exists():
        return None
    try:
        result: dict[str, Any] = json.loads(meta_file.read_text(encoding="utf-8"))
        return result
    except (json.JSONDecodeError, OSError):
        return None


def _parse_category_features(slug: str, category_name: str) -> list[dict[str, Any]]:
    """Parse features from a category markdown file."""
    if not _validate_slug(slug):
        return []
    base = Path(RELEASES_DIR).resolve()
    releases_dir = (base / slug).resolve()
    if not releases_dir.is_relative_to(base):
        return []
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


_GRAPHQL_FIELD_MAP: dict[str, str] = {
    "name": "name",
    "slug": "slug",
    "releaseId": "release_id",
    "release_id": "release_id",
    "totalFeatures": "total_features",
    "total_features": "total_features",
    "avgConfidence": "avg_confidence",
    "avg_confidence": "avg_confidence",
    "generatedAt": "generated_at",
    "generated_at": "generated_at",
    "categories": "categories",
    "totalDelta": "total_delta",
    "total_delta": "total_delta",
    "current": "current",
    "previous": "previous",
    "changes": "changes",
    "delta": "delta",
    "category": "category",
}

_GRAPHQL_KEYWORDS = frozenset(
    {
        "query",
        "mutation",
        "subscription",
        "fragment",
        "on",
        "true",
        "false",
        "null",
    }
)


def _select_graphql_fields(data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Select and map GraphQL field names to internal keys."""
    if not fields:
        return data
    return {f: data.get(_GRAPHQL_FIELD_MAP[f], None) for f in fields if f in _GRAPHQL_FIELD_MAP}


def _extract_requested_fields(query: str) -> list[str]:
    """Extract requested field names from a GraphQL query string."""
    inner_match = re.search(r"\{([^}]+)\}\s*$", query)
    if not inner_match:
        return []
    raw_fields = re.findall(r"\b([a-zA-Z]\w*)\b", inner_match.group(1))
    return list(dict.fromkeys(f for f in raw_fields if f not in _GRAPHQL_KEYWORDS))


def _graphql_handle_releases(fields: list[str]) -> dict[str, Any]:
    """Handle `{ releases { ... } }` query."""
    metas = _load_all_metas()
    return {"data": {"releases": [_select_graphql_fields(m, fields) for m in metas]}}


def _graphql_handle_release(slug: str, fields: list[str]) -> dict[str, Any]:
    """Handle `{ release(slug: "...") { ... } }` query."""
    meta = _find_meta(slug)
    if meta is None:
        return {"data": {"release": None}, "errors": [{"message": f"release '{slug}' not found"}]}
    return {"data": {"release": _select_graphql_fields(meta, fields)}}


def _graphql_handle_diff(
    current_slug: str, previous_slug: str, fields: list[str]
) -> dict[str, Any]:
    """Handle `{ diff(current: "...", previous: "...") { ... } }` query."""
    current_meta = _find_meta(current_slug)
    if current_meta is None:
        return {
            "data": {"diff": None},
            "errors": [{"message": f"release '{current_slug}' not found"}],
        }
    previous_meta = _find_meta(previous_slug)
    if previous_meta is None:
        return {
            "data": {"diff": None},
            "errors": [{"message": f"release '{previous_slug}' not found"}],
        }
    diff = _build_diff(current_meta, previous_meta)
    return {"data": {"diff": _select_graphql_fields(diff, fields)}}


def _execute_graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a simplified GraphQL query.

    Supports:
        { releases { name slug totalFeatures categories { name count } } }
        { release(slug: "summer_26") { name totalFeatures } }
        { diff(current: "summer_26", previous: "spring_26") { totalDelta } }
    """
    query = query.strip()

    # Strip outer braces and whitespace
    query = re.sub(r"^\s*\{\s*", "", query)
    query = re.sub(r"\s*\}\s*$", "", query)

    # Strip field selection braces for operation detection
    query_op = re.sub(r"\s*\{[^}]*\}\s*$", "", query).strip()

    # Detect query type
    releases_match = re.match(r"^releases\s*$", query_op)
    release_match = re.match(r'^release\s*\(\s*slug\s*:\s*"([^"]+)"\s*\)$', query_op)
    diff_match = re.match(
        r'^diff\s*\(\s*current\s*:\s*"([^"]+)"\s*,\s*previous\s*:\s*"([^"]+)"\s*\)$',
        query_op,
    )

    # Validate: only one top-level operation allowed
    op_count = sum(1 for m in [releases_match, release_match, diff_match] if m)
    if op_count == 0:
        return {
            "errors": [
                {
                    "message": 'Unknown query. Supported: releases, release(slug: "..."), diff(current: "...", previous: "...")'
                }
            ]
        }

    fields = _extract_requested_fields(query)

    if releases_match:
        return _graphql_handle_releases(fields)
    if release_match:
        return _graphql_handle_release(release_match.group(1), fields)
    if diff_match:
        return _graphql_handle_diff(diff_match.group(1), diff_match.group(2), fields)

    return {
        "errors": [
            {
                "message": "Unknown query. Supported: releases, release(slug), diff(current, previous)"
            }
        ]
    }


_OPENAPI_SPEC_PATH = Path(__file__).parent / "openapi_spec.json"


def _generate_openapi_spec() -> dict[str, Any]:
    """Load OpenAPI 3.0 specification from bundled JSON file."""
    spec: dict[str, Any] = json.loads(_OPENAPI_SPEC_PATH.read_text(encoding="utf-8"))
    return spec


class APIHandler(BaseHTTPRequestHandler):
    """HTTP handler for REST API, GraphQL, and OpenAPI endpoints."""

    def do_GET(self) -> None:
        path = self.path.rstrip("/")

        if path == "/openapi.json":
            self._respond(200, _generate_openapi_spec())
            return

        metas = _load_all_metas()

        if path == "/releases":
            try:
                validated = [ReleaseResponse.model_validate(m).model_dump() for m in metas]
            except Exception:
                validated = metas
            self._respond(200, {"releases": validated})

        elif path.startswith("/releases/") and path.count("/") == 2:
            slug = path.split("/")[2]
            meta = _find_meta(slug)
            if meta is None:
                self._respond(404, ErrorResponse(error=f"release '{slug}' not found").model_dump())
                return
            try:
                self._respond(200, ReleaseResponse.model_validate(meta).model_dump())
            except Exception:
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

    def do_POST(self) -> None:
        path = self.path.rstrip("/")
        if path != "/graphql":
            self._respond(404, {"error": "not found"})
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
        except (ValueError, TypeError):
            self._respond(400, {"error": "invalid Content-Length header"})
            return
        if content_length == 0:
            self._respond(400, {"error": "empty request body"})
            return

        try:
            body = self.rfile.read(content_length)
            data: dict[str, Any] = json.loads(body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._respond(400, {"error": "invalid JSON"})
            return

        query = data.get("query", "")
        if not query:
            self._respond(400, {"error": "missing 'query' field"})
            return

        variables = data.get("variables")
        result = _execute_graphql(query, variables)
        self._respond(200, result)

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
