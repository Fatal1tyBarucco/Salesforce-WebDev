"""Tests for release_summarizer module."""

import json
from pathlib import Path

from src.release_summarizer import ReleaseSummarizer


def test_summarizer_returns_summary(tmp_path: Path) -> None:
    """release_summarizer: summarize returns summary for valid release."""
    # Create release structure
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text(
        json.dumps({"release_name": "Summer '26", "total_features": 50})
    )
    (release_dir / "agentforce.md").write_text(
        "# Agentforce\n\n## Agentforce\n\n- Feature A: New agent capability\n"
        "- Feature B: Improved workflow\n- Feature C: Better integration\n"
    )
    (release_dir / "security.md").write_text(
        "# Security\n\n## Segurança\n\n- Feature D: Enhanced encryption\n"
        "- Feature E: New auth method\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("summer_26")

    assert summary is not None
    assert summary.release_slug == "summer_26"
    assert summary.total_features > 0
    assert len(summary.top_categories) > 0
    assert len(summary.key_highlights) > 0
    assert "recursos" in summary.summary_text.lower() or "features" in summary.summary_text.lower()


def test_summarizer_returns_none_for_missing(tmp_path: Path) -> None:
    """release_summarizer: summarize returns None for missing release."""
    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    assert summarizer.summarize("nonexistent") is None


def test_summarizer_extracts_category_names(tmp_path: Path) -> None:
    """release_summarizer: category names extracted from headings."""
    release_dir = tmp_path / "winter_26"
    release_dir.mkdir()
    (release_dir / "agentforce.md").write_text(
        "# Agentforce\n\n## Agentforce Features\n\n"
        "- New agent capability for automated customer service\n"
        "- Improved workflow automation with AI assistance\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("winter_26")

    assert summary is not None
    cat_names = [c[0] for c in summary.top_categories]
    assert any("agentforce" in c.lower() for c in cat_names)


def test_summarizer_handles_empty_release(tmp_path: Path) -> None:
    """release_summarizer: handles release with no features."""
    release_dir = tmp_path / "empty_release"
    release_dir.mkdir()
    (release_dir / "empty.md").write_text(
        "# Empty Release\n\nThis release contains no significant features or changes.\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("empty_release")

    # Should return a summary even with minimal content
    assert summary is not None
    assert summary.total_features == 0


def test_summarizer_confidence_scales_with_features(tmp_path: Path) -> None:
    """release_summarizer: confidence scales with feature count."""
    # Small release
    small_dir = tmp_path / "small"
    small_dir.mkdir()
    (small_dir / "small.md").write_text(
        "# Small Release\n\n- Feature 1: Important new capability\n"
    )

    # Large release
    large_dir = tmp_path / "large"
    large_dir.mkdir()
    features = "\n".join(
        [f"- Feature {i}: Detailed description of important feature {i}" for i in range(200)]
    )
    (large_dir / "large.md").write_text(f"# Large Release\n\n{features}")

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    small = summarizer.summarize("small")
    large = summarizer.summarize("large")

    assert small is not None
    assert large is not None
    assert large.confidence >= small.confidence


def test_summarizer_handles_invalid_meta(tmp_path: Path) -> None:
    """release_summarizer: handles invalid .meta.json gracefully."""
    release_dir = tmp_path / "invalid_meta"
    release_dir.mkdir()
    (release_dir / ".meta.json").write_text("not valid json {{{")
    (release_dir / "features.md").write_text(
        "# Features\n\n- Important feature with long description for testing\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("invalid_meta")

    assert summary is not None


def test_summarizer_handles_missing_meta(tmp_path: Path) -> None:
    """release_summarizer: handles missing .meta.json."""
    release_dir = tmp_path / "no_meta"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n- Important feature with long description for testing\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("no_meta")

    assert summary is not None


def test_summarizer_handles_table_features(tmp_path: Path) -> None:
    """release_summarizer: counts table row features."""
    release_dir = tmp_path / "tables"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "This is a detailed description of the features in this release.\n\n"
        "| RECURSO | ATIVADO |\n"
        "| --- | --- |\n"
        "| Feature A with detailed description | Yes |\n"
        "| Feature B with detailed description | No |\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("tables")

    assert summary is not None
    assert summary.total_features == 2


def test_summarizer_handles_blockquotes(tmp_path: Path) -> None:
    """release_summarizer: extracts sentences from blockquotes."""
    release_dir = tmp_path / "quotes"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n> This is an important quote with enough text to be extracted.\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("quotes")

    assert summary is not None
    assert len(summary.key_highlights) > 0


def test_summarizer_handles_mixed_case_keywords(tmp_path: Path) -> None:
    """release_summarizer: boosts category keywords regardless of case."""
    release_dir = tmp_path / "keywords"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Security improvement for authentication system\n"
        "- Performance optimization for database queries\n"
        "- Bug fix for login issue\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("keywords")

    assert summary is not None
    assert summary.total_features == 3


def test_summarizer_handles_dotfiles(tmp_path: Path) -> None:
    """release_summarizer: skips dotfiles in release directory."""
    release_dir = tmp_path / "dotfiles"
    release_dir.mkdir()
    (release_dir / ".hidden.md").write_text("# Hidden\n\n- Hidden feature\n")
    (release_dir / "visible.md").write_text(
        "# Visible Features\n\n- Important visible feature with description\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("dotfiles")

    assert summary is not None
    # Should only count visible features
    assert summary.total_features == 1


def test_summarizer_returns_none_for_short_sentences(tmp_path: Path) -> None:
    """release_summarizer: returns None when all sentences are too short."""
    release_dir = tmp_path / "short"
    release_dir.mkdir()
    (release_dir / "short.md").write_text("# Short\n\n- A\n- B\n- C\n")

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("short")

    assert summary is None


def test_summarizer_extracts_h2_category(tmp_path: Path) -> None:
    """release_summarizer: extracts category from ## heading."""
    release_dir = tmp_path / "h2category"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "## Agentforce Features\n\n" "- Important feature with long description for extraction\n"
    )

    summarizer = ReleaseSummarizer(base_dir=str(tmp_path))
    summary = summarizer.summarize("h2category")

    assert summary is not None
    cat_names = [c[0] for c in summary.top_categories]
    assert any("agentforce" in c.lower() for c in cat_names)
