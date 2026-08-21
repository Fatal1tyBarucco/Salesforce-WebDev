"""API module providing REST endpoints and authentication for Salesforce WebDev automation."""

from __future__ import annotations

import json
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel

from .config import RELEASES_DIR

app = FastAPI(
    title="Salesforce WebDev API",
    description="API service for Salesforce web development automation and triage.",
    version="1.0.0",
)

API_KEY_ENV_VAR = "API_SECRET_KEY"
DEFAULT_API_KEY = "default-dev-key"
_API_KEY = os.getenv("API_KEY", "")
_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class TriageRequest(BaseModel):
    title: str
    description: str
    labels: list[str] = []


class TriageResponse(BaseModel):
    status: str
    category: str
    priority: str
    suggested_action: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """Validate the incoming API key header against environment configuration."""
    expected_key = os.getenv(API_KEY_ENV_VAR, DEFAULT_API_KEY)
    if not x_api_key or x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return x_api_key


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Public health check endpoint."""
    return {"status": "ok", "service": "salesforce-webdev-api"}


@app.post("/v1/triage", response_model=TriageResponse)
def triage_issue(
    payload: TriageRequest,
    api_key: str = Depends(verify_api_key),
) -> TriageResponse:
    """Triage an incoming issue using automated classification rules."""
    title_lower = payload.title.lower()
    if "bug" in title_lower or "error" in title_lower:
        category = "bug"
        priority = "high"
        suggested_action = "Assign to engineering on-call"
    elif "feature" in title_lower or "enhancement" in title_lower:
        category = "feature"
        priority = "medium"
        suggested_action = "Add to product backlog"
    else:
        category = "general"
        priority = "low"
        suggested_action = "Review during weekly triage"

    return TriageResponse(
        status="processed",
        category=category,
        priority=priority,
        suggested_action=suggested_action,
    )


@app.post("/v1/search")
def natural_language_search(
    payload: SearchRequest,
    api_key: str = Depends(verify_api_key),
) -> Dict[str, Any]:
    """Execute a natural language search query across release notes."""
    return {
        "query": payload.query,
        "results": [],
        "count": 0,
    }


# ---------------------------------------------------------------------------
# Lightweight HTTP Server API Handler & GraphQL Engine for Internal Testing
# ---------------------------------------------------------------------------


def _load_all_metas() -> list[dict[str, Any]]:
    releases_path = Path(RELEASES_DIR)
    if not releases_path.exists() or not releases_path.is_dir():
        return []

    metas = []
    for d in releases_path.iterdir():
        if d.is_dir():
            meta_file = d / ".meta.json"
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    metas.append(meta)
                except Exception:
                    continue
    return metas


def _validate_slug(slug: str) -> bool:
    if not slug or not _SLUG_RE.fullmatch(slug):
        return False
    from .config import KNOWN_RELEASES

    known_slugs = {r.slug for r in KNOWN_RELEASES}
    for m in _load_all_metas():
        if "slug" in m:
            known_slugs.add(m["slug"])
    return slug in known_slugs


def _find_meta(slug: str) -> dict[str, Any] | None:
    if not _validate_slug(slug):
        return None
    try:
        base_dir = Path(RELEASES_DIR).resolve(strict=True)
    except Exception:
        return None
    try:
        resolved_meta_path = (base_dir / slug / ".meta.json").resolve(strict=False)
        resolved_meta_path.relative_to(base_dir)
    except ValueError:
        return None
    except Exception:
        return None
    if not resolved_meta_path.exists():
        return None
    try:
        return json.loads(resolved_meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _parse_category_features(slug: str, category: str) -> list[dict[str, Any]]:
    if not _validate_slug(slug):
        return []
    base_dir = Path(RELEASES_DIR).resolve()
    release_dir = (base_dir / slug).resolve()
    try:
        release_dir.relative_to(base_dir)
    except ValueError:
        return []
    if not release_dir.is_dir():
        return []
    features: list[dict[str, Any]] = []
    try:
        for md_file in release_dir.glob("*.md"):
            if md_file.name.startswith("."):
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError:
                return []
            lines = content.splitlines()
            current_cat = None
            for line in lines:
                line_str = line.strip()
                if line_str.startswith("## "):
                    current_cat = line_str[3:].strip()
                if current_cat and category.lower() in current_cat.lower():
                    if line_str.startswith("* **") or line_str.startswith("- **"):
                        end_idx = line_str.find("**", 4)
                        if end_idx != -1:
                            feat_name = line_str[4:end_idx].strip()
                            if feat_name:
                                features.append({"name": feat_name, "category": current_cat})
                    elif "\t" in line_str:
                        parts = line_str.split("\t")
                        if len(parts[0].strip()) > 2:
                            features.append({"name": parts[0].strip(), "category": current_cat})
                    elif (
                        len(line_str) > 10
                        and not line_str.startswith("#")
                        and not line_str.startswith("|")
                    ):
                        features.append({"name": line_str, "category": current_cat})
    except OSError:
        return []
    return features


def _build_diff(current: dict[str, Any], previous: dict[str, Any]) -> dict[str, Any]:
    curr_total = current.get("total_features", 0)
    prev_total = previous.get("total_features", 0)
    return {
        "current": current.get("name", ""),
        "previous": previous.get("name", ""),
        "total_delta": curr_total - prev_total,
        "current_total": curr_total,
        "previous_total": prev_total,
    }


def _generate_openapi_spec() -> dict[str, Any]:
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Salesforce WebDev API",
            "version": "1.0.0",
            "description": "API service for Salesforce web development automation and triage.",
        },
        "paths": {
            "/health": {"get": {"summary": "Health check"}},
            "/releases": {"get": {"summary": "List releases"}},
            "/graphql": {"post": {"summary": "GraphQL endpoint"}},
        },
    }


def _gql_lex(query: str) -> list[str]:
    cleaned = query.replace("{", " { ").replace("}", " } ").replace(":", " : ")
    return [t for t in cleaned.split() if t]


def _select_graphql_fields(item: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    res: dict[str, Any] = {}
    mapping = {
        "name": "name",
        "slug": "slug",
        "releaseId": "release_id",
        "totalFeatures": "total_features",
        "categories": "categories",
    }
    for field in fields:
        dict_key = mapping.get(field, field)
        if dict_key in item:
            res[field] = item[dict_key]
    return res


def _execute_graphql(query: str) -> dict[str, Any]:
    tokens = _gql_lex(query)
    metas = _load_all_metas()
    if "releases" in tokens:
        fields = []
        in_releases = False
        for t in tokens:
            if t == "releases":
                in_releases = True
                continue
            if in_releases:
                if t in ("{", "}"):
                    continue
                fields.append(t)
        if not fields:
            fields = ["name", "slug", "totalFeatures"]
        data_releases = [_select_graphql_fields(m, fields) for m in metas]
        return {"data": {"releases": data_releases}}
    return {"data": {}}


class APIHandler(BaseHTTPRequestHandler):
    """Custom HTTP Handler for internal API routes and tests."""

    def _check_auth(self) -> bool:
        if not _API_KEY:
            return True
        path = self.path.split("?")[0]
        if path in ("/health", "/ready", "/metrics", "/openapi.json"):
            return True
        api_key = self.headers.get("X-API-Key", "")
        auth_header = self.headers.get("Authorization", "")
        bearer_key = ""
        if auth_header.startswith("Bearer "):
            bearer_key = auth_header[7:].strip()
        if api_key == _API_KEY or bearer_key == _API_KEY:
            return True
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"detail": "Unauthorized"}).encode("utf-8"))
        return False

    def do_GET(self) -> None:
        if not self._check_auth():
            return
        path = self.path.split("?")[0]
        if path in ("/health", "/ready"):
            self._send_json({"status": "ok"})
        elif path == "/metrics":
            self._send_response_data(200, "text/plain", b"pipeline_runs_total 1\n")
        elif path == "/openapi.json":
            self._send_json(_generate_openapi_spec())
        elif path == "/releases":
            self._send_json(_load_all_metas())
        elif path.startswith("/releases/"):
            parts = [p for p in path.split("/") if p]
            if len(parts) == 2:
                slug = parts[1]
                meta = _find_meta(slug)
                if meta:
                    self._send_json(meta)
                else:
                    self._send_response_data(
                        404, "application/json", json.dumps({"detail": "Not found"}).encode()
                    )
            elif len(parts) == 4 and parts[2] == "categories":
                slug, cat = parts[1], parts[3]
                features = _parse_category_features(slug, cat)
                self._send_json(features)
            else:
                self._send_response_data(
                    404, "application/json", json.dumps({"detail": "Not found"}).encode()
                )
        else:
            self._send_response_data(
                404, "application/json", json.dumps({"detail": "Not found"}).encode()
            )

    def do_POST(self) -> None:
        if not self._check_auth():
            return
        path = self.path.split("?")[0]
        if path == "/graphql":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""
            try:
                data = json.loads(body.decode("utf-8")) if body else {}
            except Exception:
                data = {}
            query = data.get("query", "")
            result = _execute_graphql(query)
            self._send_json(result)
        else:
            self._send_response_data(
                404, "application/json", json.dumps({"detail": "Not found"}).encode()
            )

    def _send_json(self, data: Any, status_code: int = 200) -> None:
        self._send_response_data(status_code, "application/json", json.dumps(data).encode("utf-8"))

    def _send_response_data(self, status_code: int, content_type: str, body: bytes) -> None:
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


def start_api_server(host: str = "127.0.0.1", port: int = 8080) -> HTTPServer:
    server = HTTPServer((host, port), APIHandler)
    return server
