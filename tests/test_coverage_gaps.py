"""Coverage tests for src modules to reach 100% coverage."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from src.main import (
    _format_impact_report,
    _format_notification_digest,
)

# ============================================================
# GraphQL Tests - Fixes for KeyError: 'data'
# ============================================================


def test_api_graphql_releases(tmp_path: Path) -> None:
    """api: GraphQL releases query returns all releases."""
    from src.api import _execute_graphql

    d = tmp_path / "summer_26"
    d.mkdir()
    (d / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 100,
                "categories": [{"name": "A", "count": 50}],
            }
        )
    )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql("{ releases { name slug totalFeatures } }")
        assert "data" in result
        assert len(result["data"]["releases"]) == 1
        assert result["data"]["releases"][0]["name"] == "Summer '26"
        assert result["data"]["releases"][0]["totalFeatures"] == 100


def test_api_graphql_releases_with_categories(tmp_path: Path) -> None:
    """api: GraphQL releases query includes categories."""
    from src.api import _execute_graphql

    d = tmp_path / "summer_26"
    d.mkdir()
    (d / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 100,
                "categories": [{"name": "A", "count": 50}],
            }
        )
    )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql("{ releases { name categories } }")
        assert "data" in result
        cats = result["data"]["releases"][0]["categories"]
        assert len(cats) == 1
        assert cats[0]["name"] == "A"


def test_api_graphql_release_by_slug(tmp_path: Path) -> None:
    """api: GraphQL release(slug) query returns single release."""
    from src.api import _execute_graphql

    d = tmp_path / "summer_26"
    d.mkdir()
    (d / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 100,
            }
        )
    )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql('{ release(slug: "summer_26") { name releaseId } }')
        assert "data" in result
        assert result["data"]["release"]["name"] == "Summer '26"
        assert result["data"]["release"]["releaseId"] == 262


def test_api_graphql_release_not_found(tmp_path: Path) -> None:
    """api: GraphQL release(slug) returns error for missing slug."""
    from src.api import _execute_graphql

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql('{ release(slug: "nope") { name } }')
        assert "data" in result
        assert result["data"]["release"] is None
        assert "errors" in result


def test_api_graphql_diff(tmp_path: Path) -> None:
    """api: GraphQL diff query returns comparison."""
    from src.api import _execute_graphql

    for slug, rid, feats in [("spring_26", 260, 80), ("summer_26", 262, 100)]:
        d = tmp_path / slug
        d.mkdir()
        (d / ".meta.json").write_text(
            json.dumps(
                {
                    "name": slug.replace("_", " ").title(),
                    "slug": slug,
                    "release_id": rid,
                    "total_features": feats,
                    "categories": [{"name": "A", "count": feats}],
                }
            )
        )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql(
            '{ diff(current: "summer_26", previous: "spring_26") { totalDelta current } }'
        )
        assert "data" in result
        assert result["data"]["diff"]["totalDelta"] == 20
        assert result["data"]["diff"]["current"] == "Summer 26"


def test_api_handler_post_graphql(tmp_path: Path) -> None:
    """api: POST /graphql executes query."""
    from src.api import APIHandler

    d = tmp_path / "summer_26"
    d.mkdir()
    (d / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 100,
                "categories": [],
            }
        )
    )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        handler = APIHandler.__new__(APIHandler)
        handler.path = "/graphql"
        handler.headers = {"Content-Length": "50"}
        query_json = json.dumps({"query": "{ releases { name } }"})
        handler.rfile = MagicMock()
        handler.rfile.read.return_value = query_json.encode()

        responses: list[tuple[int, Any]] = []

        def fake_respond(code: int, data: Any) -> None:
            responses.append((code, data))

        handler._respond = fake_respond  # type: ignore[assignment]
        handler.do_POST()
        assert responses[0][0] == 200
        assert "data" in responses[0][1]
        assert len(responses[0][1]["data"]["releases"]) == 1


def test_api_graphql_releases_no_fields(tmp_path: Path) -> None:
    """api: GraphQL releases query with no fields returns all data."""
    from src.api import _execute_graphql

    d = tmp_path / "summer_26"
    d.mkdir()
    (d / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 100,
                "categories": [],
            }
        )
    )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql("{ releases { } }")
        assert "data" in result
        assert len(result["data"]["releases"]) == 1
        assert "name" in result["data"]["releases"][0]


def test_api_graphql_diff_previous_not_found(tmp_path: Path) -> None:
    """api: GraphQL diff returns error when previous release not found."""
    from src.api import _execute_graphql

    d = tmp_path / "summer_26"
    d.mkdir()
    (d / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "slug": "summer_26",
                "release_id": 262,
                "total_features": 100,
            }
        )
    )

    with patch("src.api.RELEASES_DIR", str(tmp_path)):
        result = _execute_graphql('{ diff(current: "summer_26", previous: "nope") { totalDelta } }')
        assert "data" in result
        assert result["data"]["diff"] is None
        assert "errors" in result


# ============================================================
# Notification Digest Mock Attribute Fixes
# ============================================================


def test_format_notification_digest_with_notifications() -> None:
    """_format_notification_digest handles notifications list with priority.value."""
    digest = MagicMock()
    digest.summary_text = "3 new features in Summer '26"

    notif1 = MagicMock()
    notif1.priority = MagicMock(value="high")
    notif1.title = "Breaking Change"
    notif1.body = "API v1 removed"

    notif2 = MagicMock()
    notif2.priority = MagicMock(value="normal")
    notif2.title = "Enhancement"
    notif2.body = ""

    digest.notifications = [notif1, notif2]

    result = _format_notification_digest(digest)
    assert "3 new features" in result
    assert "Breaking Change" in result
    assert "API v1 removed" in result
    assert "Enhancement" in result


def test_impact_analysis_failure_in_pipeline() -> None:
    """Pipeline handles impact analysis with proper attributes."""
    report = MagicMock()
    report.total_features = 10
    report.breaking_changes = []
    report.security_fixes = []
    report.risk_score = 3.5

    result = _format_impact_report(report, "Test")
    assert "# Impact Report: Test" in result
    assert "10" in result


def test_notification_digest_failure_in_pipeline() -> None:
    """Notification digest formatting handles all attributes correctly."""
    digest = MagicMock()
    digest.summary_text = "Test summary"
    digest.notifications = []

    result = _format_notification_digest(digest)
    assert "# Notification Digest" in result
    assert "Test summary" in result
