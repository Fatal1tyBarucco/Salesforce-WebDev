"""Tests for API authentication (X-API-Key / Authorization: Bearer)."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch


from src.api import APIHandler


def _make_handler(
    path: str,
    method: str = "GET",
    body: bytes = b"",
    headers: dict[str, str] | None = None,
) -> APIHandler:
    """Create an APIHandler with mocked socket and optional headers."""
    request = MagicMock()
    request.makefile.return_value = BytesIO()

    handler = APIHandler(request, ("127.0.0.1", 12345), MagicMock())
    handler.path = path
    handler.wfile = BytesIO()
    handler.request_version = "HTTP/1.1"
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    handler.headers = headers or {"Content-Length": str(len(body))}
    handler.rfile = BytesIO(body)
    return handler


class TestAuthDisabled:
    """When API_KEY is not set, all requests should pass."""

    def test_no_auth_allows_get(self) -> None:
        with patch("src.api._API_KEY", ""):
            handler = _make_handler("/releases")
            assert handler._check_auth() is True

    def test_no_auth_allows_post(self) -> None:
        with patch("src.api._API_KEY", ""):
            handler = _make_handler("/graphql")
            assert handler._check_auth() is True


class TestAuthEnabled:
    """When API_KEY is set, protected endpoints require the key."""

    def test_missing_key_returns_401(self) -> None:
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler("/releases")
            result = handler._check_auth()
            assert result is False
            handler.send_response.assert_called_with(401)

    def test_wrong_key_returns_401(self) -> None:
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler(
                "/releases",
                headers={"X-API-Key": "wrong-key", "Content-Length": "0"},
            )
            result = handler._check_auth()
            assert result is False
            handler.send_response.assert_called_with(401)

    def test_valid_x_api_key(self) -> None:
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler(
                "/releases",
                headers={"X-API-Key": "secret-key", "Content-Length": "0"},
            )
            assert handler._check_auth() is True

    def test_valid_bearer_token(self) -> None:
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler(
                "/releases",
                headers={"Authorization": "Bearer secret-key", "Content-Length": "0"},
            )
            assert handler._check_auth() is True

    def test_bearer_with_extra_spaces(self) -> None:
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler(
                "/releases",
                headers={"Authorization": "Bearer   secret-key  ", "Content-Length": "0"},
            )
            assert handler._check_auth() is True

    def test_public_endpoints_skip_auth(self) -> None:
        """Health, ready, metrics, and openapi should not require auth."""
        with patch("src.api._API_KEY", "secret-key"):
            for path in ["/health", "/ready", "/metrics", "/openapi.json"]:
                handler = _make_handler(path)
                assert handler._check_auth() is True, f"Auth should be skipped for {path}"

    def test_graphql_requires_auth(self) -> None:
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler(
                "/graphql",
                body=json.dumps({"query": "{ releases { name } }"}).encode(),
            )
            result = handler._check_auth()
            assert result is False

    def test_do_get_blocked_without_auth(self, tmp_path: Path) -> None:
        """Full do_GET should return 401 when auth fails."""
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler("/releases")
            handler.do_GET()
            handler.send_response.assert_called_with(401)

    def test_do_post_blocked_without_auth(self) -> None:
        """Full do_POST should return 401 when auth fails."""
        with patch("src.api._API_KEY", "secret-key"):
            handler = _make_handler(
                "/graphql",
                body=json.dumps({"query": "{ releases { name } }"}).encode(),
            )
            handler.do_POST()
            handler.send_response.assert_called_with(401)

    def test_do_get_allowed_with_auth(self, tmp_path: Path) -> None:
        """Full do_GET should succeed with valid key."""
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(json.dumps({"name": "S", "release_id": 262}))
        with patch("src.api._API_KEY", "secret-key"), patch("src.api.RELEASES_DIR", str(tmp_path)):
            handler = _make_handler(
                "/releases",
                headers={"X-API-Key": "secret-key", "Content-Length": "0"},
            )
            handler.do_GET()
            handler.send_response.assert_called_with(200)
