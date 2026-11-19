"""Summary cache atomic-write tests (ADR-011 R1)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.config import ReleaseInfo
from src.main import generate_summary_cache

RELEASE = ReleaseInfo(name="Test '26", release_id=262, slug="test_26")


@pytest.fixture
def isolated_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    return tmp_path


async def test_fallback_summary_written_atomically(isolated_cwd: Path) -> None:
    release_dir = isolated_cwd / "releases" / "test_26"
    release_dir.mkdir(parents=True)
    meta = {
        "name": RELEASE.name,
        "total_features": 5,
        "categories": [{"name": "Automação", "count": 5}],
    }
    (release_dir / ".meta.json").write_text(json.dumps(meta), encoding="utf-8")
    await generate_summary_cache(RELEASE, [], llm=None)
    summary_path = release_dir / ".summary_cache.json"
    assert summary_path.exists()
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["fallback"] is True
    assert data["category_summaries"]["Automação"]
    names = [p.name for p in release_dir.iterdir()]
    assert not any(n.startswith(".tmp-") for n in names)
