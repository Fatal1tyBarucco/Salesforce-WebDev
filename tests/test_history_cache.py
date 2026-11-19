"""releases/history.json hardening tests (ADR-011): atomic, locked, tolerant."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

from src.config import ReleaseInfo
from src.release_docs import _update_release_history

RELEASE = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
OLDER = ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26")


def test_history_upsert_and_sort(tmp_path: Path) -> None:
    with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
        _update_release_history(OLDER, 100, 10)
        _update_release_history(RELEASE, 200, 20)
        _update_release_history(RELEASE, 250, 22)  # upsert, not duplicate
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert [h["slug"] for h in history] == ["summer_26", "spring_26"]
    assert history[0]["total_features"] == 250


def test_history_corrupt_quarantined_and_rebuilt(tmp_path: Path) -> None:
    (tmp_path / "history.json").write_text("{corrupt", encoding="utf-8")
    with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
        _update_release_history(RELEASE, 10, 2)  # must not raise
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert len(history) == 1
    assert list((tmp_path / "quarantine").iterdir())


def test_history_non_list_quarantined(tmp_path: Path) -> None:
    (tmp_path / "history.json").write_text('{"a": 1}', encoding="utf-8")
    with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
        _update_release_history(RELEASE, 10, 2)
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert isinstance(history, list)


def test_history_bad_entries_filtered(tmp_path: Path) -> None:
    (tmp_path / "history.json").write_text(
        json.dumps([{"slug": "ok", "release_id": 1}, "bad", 42]), encoding="utf-8"
    )
    with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
        _update_release_history(RELEASE, 10, 2)
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert all(isinstance(h, dict) for h in history)


def test_history_non_numeric_release_id_sorts_safely(tmp_path: Path) -> None:
    (tmp_path / "history.json").write_text(
        json.dumps([{"slug": "weird", "release_id": "abc"}]), encoding="utf-8"
    )
    with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
        _update_release_history(RELEASE, 10, 2)  # must not raise
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert len(history) == 2


def test_history_no_temp_leftovers(tmp_path: Path) -> None:
    with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
        _update_release_history(RELEASE, 10, 2)
    names = [p.name for p in tmp_path.iterdir()]
    assert not any(n.startswith(".tmp-") for n in names)


def _child_update(releases_dir_str: str, slug: str, release_id: int) -> None:
    from src.config import ReleaseInfo as RI

    with patch("src.release_docs.RELEASES_DIR", releases_dir_str):
        _update_release_history(RI(name=slug, release_id=release_id, slug=slug), 1, 1)
    os._exit(0)


def test_history_concurrent_updates_no_lost_entries(tmp_path: Path) -> None:
    pids: list[int] = []
    for i in range(4):
        pid = os.fork()
        if pid == 0:  # pragma: no cover — child branch
            try:
                _child_update(str(tmp_path), f"release_{i}", 250 + i * 2)
            except BaseException:
                os._exit(1)
        pids.append(pid)
    for pid in pids:
        _, status = os.waitpid(pid, 0)
        assert os.waitstatus_to_exitcode(status) == 0
    history = json.loads((tmp_path / "history.json").read_text(encoding="utf-8"))
    assert {h["slug"] for h in history} == {f"release_{i}" for i in range(4)}
