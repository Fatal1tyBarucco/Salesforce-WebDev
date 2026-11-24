"""Health endpoint cache observability tests (ADR-011 R6)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.health import _get_health_data


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_health_includes_cache_stats(isolated_cwd: Path) -> None:
    cache_dir = isolated_cwd / "cache"
    cache_dir.mkdir()
    payload = {
        "schema_version": 1,
        "stats": {"hits": 5, "misses": 2, "hit_rate": 5 / 7},
    }
    (cache_dir / "stats.json").write_text(json.dumps(payload), encoding="utf-8")
    data = _get_health_data()
    cache = data["cache"]
    assert isinstance(cache, dict)
    assert cache["hits"] == 5


def test_health_cache_missing_degrades(isolated_cwd: Path) -> None:
    data = _get_health_data()
    assert data["cache"] == {}


def test_health_cache_corrupt_degrades(isolated_cwd: Path) -> None:
    cache_dir = isolated_cwd / "cache"
    cache_dir.mkdir()
    (cache_dir / "stats.json").write_text("{bad", encoding="utf-8")
    data = _get_health_data()
    assert data["cache"] == {}


def test_health_cache_wrong_shape_degrades(isolated_cwd: Path) -> None:
    cache_dir = isolated_cwd / "cache"
    cache_dir.mkdir()
    (cache_dir / "stats.json").write_text('{"stats": [1,2]}', encoding="utf-8")
    data = _get_health_data()
    assert data["cache"] == {}
