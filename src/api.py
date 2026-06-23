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


def _validate_slug(slug: str) -> bool:
    """Validate a slug to prevent path traversal."""
    return bool(re.match(r"^[a-z0-9_]+$", slug))


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


def _execute_graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a simplified GraphQL query.

    Supports:
        { releases { name slug totalFeatures categories { name count } } }
        { release(slug: "summer_26") { name totalFeatures } }
        { diff(current: "summer_26", previous: "spring_26") { totalDelta } }
    """
    query = query.strip()
    variables = variables or {}

    # Simple parser: extract operation and fields
    # { releases { ... } } or { release(slug: "...") { ... } }

    # Detect query type
    releases_match = re.search(r"releases\s*\{", query)
    release_match = re.search(r'release\s*\(\s*slug\s*:\s*"([^"]+)"\s*\)\s*\{', query)
    diff_match = re.search(
        r'diff\s*\(\s*current\s*:\s*"([^"]+)"\s*,\s*previous\s*:\s*"([^"]+)"\s*\)\s*\{',
        query,
    )

    # Extract all field names from the query (flat extraction, ignores nesting)
    requested_fields = list(
        dict.fromkeys(re.findall(r"\b(\w+)\b", query.split("{", 2)[-1] if "{" in query else query))
    )
    # Remove GraphQL keywords
    graphql_keywords = {
        "query",
        "mutation",
        "subscription",
        "fragment",
        "on",
        "true",
        "false",
        "null",
    }
    requested_fields = [f for f in requested_fields if f not in graphql_keywords]

    def _select_fields(data: dict[str, Any], fields: list[str]) -> dict[str, Any]:
        if not fields:
            return data
        result: dict[str, Any] = {}
        field_map = {
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
        for field in fields:
            if field in field_map:
                result[field] = data.get(field_map[field], None)
        return result

    if releases_match:
        metas = _load_all_metas()
        results = [_select_fields(m, requested_fields) for m in metas]
        return {"data": {"releases": results}}

    if release_match:
        slug = release_match.group(1)
        meta = _find_meta(slug)
        if meta is None:
            return {
                "data": {"release": None},
                "errors": [{"message": f"release '{slug}' not found"}],
            }
        return {"data": {"release": _select_fields(meta, requested_fields)}}

    if diff_match:
        current_slug = diff_match.group(1)
        previous_slug = diff_match.group(2)
        current_meta = _find_meta(current_slug)
        previous_meta = _find_meta(previous_slug)
        if current_meta is None:
            return {
                "data": {"diff": None},
                "errors": [{"message": f"release '{current_slug}' not found"}],
            }
        if previous_meta is None:
            return {
                "data": {"diff": None},
                "errors": [{"message": f"release '{previous_slug}' not found"}],
            }
        diff = _build_diff(current_meta, previous_meta)
        return {"data": {"diff": _select_fields(diff, requested_fields)}}

    return {
        "errors": [
            {
                "message": "Unknown query. Supported: releases, release(slug), diff(current, previous)"
            }
        ]
    }


def _generate_openapi_spec() -> dict[str, Any]:
    """Generate OpenAPI 3.0 specification."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Salesforce Release Notes API",
            "description": "REST API for accessing Salesforce Release Notes data",
            "version": "3.0.0",
        },
        "servers": [{"url": "http://localhost:8081", "description": "Local development"}],
        "paths": {
            "/releases": {
                "get": {
                    "summary": "List all releases",
                    "operationId": "listReleases",
                    "responses": {
                        "200": {
                            "description": "List of releases",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "releases": {
                                                "type": "array",
                                                "items": {"$ref": "#/components/schemas/Release"},
                                            }
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/releases/{slug}": {
                "get": {
                    "summary": "Get release details",
                    "operationId": "getRelease",
                    "parameters": [
                        {
                            "name": "slug",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Release details",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Release"}
                                }
                            },
                        },
                        "404": {"description": "Release not found"},
                    },
                }
            },
            "/releases/{slug}/categories/{name}": {
                "get": {
                    "summary": "Get category features",
                    "operationId": "getCategoryFeatures",
                    "parameters": [
                        {
                            "name": "slug",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "name",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Category features",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/CategoryFeatures"}
                                }
                            },
                        },
                        "404": {"description": "Release or category not found"},
                    },
                }
            },
            "/diff/{current}/{previous}": {
                "get": {
                    "summary": "Compare two releases",
                    "operationId": "compareReleases",
                    "parameters": [
                        {
                            "name": "current",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "previous",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Release comparison",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Diff"}
                                }
                            },
                        },
                        "404": {"description": "Release not found"},
                    },
                }
            },
            "/graphql": {
                "post": {
                    "summary": "GraphQL query endpoint",
                    "operationId": "graphql",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {"type": "string"},
                                        "variables": {"type": "object"},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "GraphQL response",
                            "content": {"application/json": {"schema": {"type": "object"}}},
                        },
                    },
                }
            },
        },
        "components": {
            "schemas": {
                "Release": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "slug": {"type": "string"},
                        "release_id": {"type": "integer"},
                        "total_features": {"type": "integer"},
                        "avg_confidence": {"type": "number"},
                        "categories": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Category"},
                        },
                    },
                },
                "Category": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "count": {"type": "integer"}},
                },
                "CategoryFeatures": {
                    "type": "object",
                    "properties": {
                        "release": {"type": "string"},
                        "category": {"type": "string"},
                        "features": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Feature"},
                        },
                        "count": {"type": "integer"},
                    },
                },
                "Feature": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}, "availability": {"type": "string"}},
                },
                "Diff": {
                    "type": "object",
                    "properties": {
                        "current": {"type": "string"},
                        "previous": {"type": "string"},
                        "changes": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Change"},
                        },
                        "total_delta": {"type": "integer"},
                    },
                },
                "Change": {
                    "type": "object",
                    "properties": {
                        "category": {"type": "string"},
                        "previous": {"type": "integer"},
                        "current": {"type": "integer"},
                        "delta": {"type": "integer"},
                    },
                },
            }
        },
    }


class APIHandler(BaseHTTPRequestHandler):
    """HTTP handler for REST API, GraphQL, and OpenAPI endpoints."""

    def do_GET(self) -> None:
        path = self.path.rstrip("/")

        if path == "/openapi.json":
            self._respond(200, _generate_openapi_spec())
            return

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
