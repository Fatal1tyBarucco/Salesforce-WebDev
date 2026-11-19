"""Trailhead cache hardening tests (ADR-011): envelope, TTL, lock, migration."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import patch

from src.cache_io import compute_checksum
from src.salesforce import _load_trailhead_cache, _save_trailhead_cache


def test_save_writes_envelope_with_checksum(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        _save_trailhead_cache({"A": ["url1"]})
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert raw["schema_version"] == 1
    assert raw["data"] == {"A": ["url1"]}
    assert raw["checksum"] == compute_checksum({"A": ["url1"]})
    assert raw["ttl"] > 0


def test_roundtrip_via_envelope(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        _save_trailhead_cache({"Security": ["https://x"]})
        assert _load_trailhead_cache() == {"Security": ["https://x"]}


def test_legacy_plain_dict_migrates(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    p.write_text(json.dumps({"Legacy": ["u1", "u2"]}), encoding="utf-8")
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        assert _load_trailhead_cache() == {"Legacy": ["u1", "u2"]}
        _save_trailhead_cache({"Legacy": ["u1", "u2"]})
    raw = json.loads(p.read_text(encoding="utf-8"))
    assert "schema_version" in raw  # rewritten as envelope


def test_expired_envelope_returns_empty(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    data = {"A": ["url1"]}
    envelope = {
        "schema_version": 1,
        "timestamp": time.time() - 999_999,
        "ttl": 10,
        "checksum": compute_checksum(data),
        "data": data,
    }
    p.write_text(json.dumps(envelope), encoding="utf-8")
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        assert _load_trailhead_cache() == {}


def test_tampered_checksum_quarantined(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    data = {"A": ["url1"]}
    envelope = {
        "schema_version": 1,
        "timestamp": time.time(),
        "ttl": 3600,
        "checksum": "0" * 64,
        "data": data,
    }
    p.write_text(json.dumps(envelope), encoding="utf-8")
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        assert _load_trailhead_cache() == {}
    assert list((tmp_path / "quarantine").iterdir())


def test_corrupt_json_quarantined(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    p.write_text("{bad", encoding="utf-8")
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        assert _load_trailhead_cache() == {}
    assert not p.exists()
    assert list((tmp_path / "quarantine").iterdir())


def test_non_list_values_filtered(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    p.write_text(json.dumps({"A": ["ok", 42], "B": "not-a-list"}), encoding="utf-8")
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        assert _load_trailhead_cache() == {"A": ["ok"]}


def test_no_temp_leftovers_after_save(tmp_path: Path) -> None:
    p = tmp_path / "trailhead_cache.json"
    with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
        _save_trailhead_cache({"A": ["u"]})
    names = [x.name for x in tmp_path.iterdir()]
    assert not any(n.startswith(".tmp-") for n in names)
