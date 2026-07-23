"""Tests for release_summarizer module."""

import asyncio
import json
from pathlib import Path

from src.release_summarizer import ReleaseSummarizer


def test_summarizer_returns_summary(tmp_path: Path) -> None:
    """release_summarizer: summarize returns summary for valid release."""
    release_dir = tmp_path / "summer_26" / "pt_BR"
    release_dir.mkdir(parents=True)
    (tmp_path / "summer_26" / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Summer '26",
                "total_features": 3,
                "categories": [
                    {"name": "Agentforce", "count": 2},
                    {"name": "Security", "count": 1},
                ],
            }
        )
    )
    (release_dir / "agentforce.md").write_text(
        "## Agentforce\n\n| Recurso | Usuários | Admins | Config | Contato | Docs |\n"
        "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
        "| **Feature A** | ✅ | ❌ | ❌ | ❌ | |\n"
        "| **Feature B** | ✅ | ❌ | ❌ | ❌ | |\n"
    )
    (release_dir / "security.md").write_text(
        "## Segurança\n\n| Recurso | Usuários | Admins | Config | Contato | Docs |\n"
        "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
        "| **Feature D** | ✅ | ❌ | ❌ | ❌ | |\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = asyncio.run(summarizer.summarize("summer_26"))

    assert summary is not None
    assert summary.release_slug == "summer_26"
    assert summary.total_features == 3
    assert len(summary.top_categories) > 0
    assert len(summary.executive_summary) > 0


def test_summarizer_returns_none_for_missing(tmp_path: Path) -> None:
    """release_summarizer: summarize returns None for missing release."""
    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    assert asyncio.run(summarizer.summarize("nonexistent")) is None


def test_summarizer_extracts_category_names(tmp_path: Path) -> None:
    """release_summarizer: category names extracted from headings."""
    release_dir = tmp_path / "winter_26" / "pt_BR"
    release_dir.mkdir(parents=True)
    (tmp_path / "winter_26" / ".meta.json").write_text(
        json.dumps(
            {
                "name": "Winter '26",
                "total_features": 2,
                "categories": [{"name": "Agentforce", "count": 2}],
            }
        )
    )
    (release_dir / "agentforce.md").write_text(
        "## Agentforce Features\n\n"
        "| Recurso | Usuários | Admins | Config | Contato | Docs |\n"
        "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
        "| **Feature A** | ✅ | ❌ | ❌ | ❌ | |\n"
        "| **Feature B** | ✅ | ❌ | ❌ | ❌ | |\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = asyncio.run(summarizer.summarize("winter_26"))

    assert summary is not None
    cat_names = [c.name for c in summary.top_categories]
    assert any("agentforce" in c.lower() for c in cat_names)


def test_summarizer_handles_empty_release(tmp_path: Path) -> None:
    """release_summarizer: handles release with no features."""
    release_dir = tmp_path / "empty_release" / "pt_BR"
    release_dir.mkdir(parents=True)
    (release_dir / "empty.md").write_text(
        "# Empty Release\n\nThis release contains no significant features or changes.\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = asyncio.run(summarizer.summarize("empty_release"))

    assert summary is not None
    assert summary.total_features == 0


def test_summarizer_handles_table_features(tmp_path: Path) -> None:
    """release_summarizer: counts table row features."""
    release_dir = tmp_path / "tables" / "pt_BR"
    release_dir.mkdir(parents=True)
    (release_dir / "features.md").write_text(
        "## Features\n\n"
        "| Recurso | Usuários | Admins | Config | Contato | Docs |\n"
        "| :--- | :---: | :---: | :---: | :---: | :---: |\n"
        "| **Feature A** | ✅ | ❌ | ❌ | ❌ | |\n"
        "| **Feature B** | ✅ | ❌ | ❌ | ❌ | |\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = asyncio.run(summarizer.summarize("tables"))

    assert summary is not None
    assert summary.total_features == 2


def test_summarizer_handles_dotfiles(tmp_path: Path) -> None:
    """release_summarizer: skips dotfiles in release directory."""
    release_dir = tmp_path / "dotfiles" / "pt_BR"
    release_dir.mkdir(parents=True)
    (release_dir / ".hidden.md").write_text(
        "## Hidden\n\n| Recurso | Usuários |\n| :--- | :---: |\n| **H1** | ✅ |\n"
    )
    (release_dir / "visible.md").write_text(
        "## Visible\n\n| Recurso | Usuários |\n| :--- | :---: |\n| **V1** | ✅ |\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = asyncio.run(summarizer.summarize("dotfiles"))

    assert summary is not None
    assert summary.total_features == 1


def test_summarizer_extracts_h2_category(tmp_path: Path) -> None:
    """release_summarizer: extracts category from ## heading."""
    release_dir = tmp_path / "h2category" / "pt_BR"
    release_dir.mkdir(parents=True)
    (release_dir / "features.md").write_text(
        "## Agentforce Features\n\n" "| Recurso | Usuários |\n| :--- | :---: |\n| **F1** | ✅ |\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = asyncio.run(summarizer.summarize("h2category"))

    assert summary is not None
    cat_names = [c.name for c in summary.top_categories]
    assert any("agentforce" in c.lower() for c in cat_names)


def test_load_meta_invalid_json(tmp_path: Path) -> None:
    """release_summarizer: handles invalid JSON in meta file."""
    release_dir = tmp_path / "invalid_meta"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text("not valid json {{{")

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    result = summarizer._load_meta(release_dir)
    assert result == {}


def test_to_markdown(tmp_path: Path) -> None:
    """release_summarizer: to_markdown generates valid markdown."""
    from src.release_summarizer import CategoryHighlight, ReleaseSummary

    summary = ReleaseSummary(
        release_slug="test",
        release_name="Test Release",
        total_features=10,
        total_categories=3,
        executive_summary="Test executive summary.",
        business_impact="Business impact paragraph.",
        strategic_themes=["AI-First", "Security"],
        top_categories=[
            CategoryHighlight("Agentforce", 5, 50.0, "Voice", "AI"),
        ],
        migration_notes="No notes.",
        confidence=0.9,
    )

    md = ReleaseSummarizer().to_markdown(summary)
    assert "Test Release" in md
    assert "10 recursos" in md
    assert "AI-First" in md
    assert "Business impact" in md
