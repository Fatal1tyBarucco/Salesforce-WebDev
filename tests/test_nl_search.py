"""Tests for nl_search module."""

from pathlib import Path

from src.nl_search import NLSearchEngine


def test_index_release(tmp_path: Path) -> None:
    """nl_search: index_release indexes release content."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "agentforce.md").write_text(
        "# Agentforce\n\n## Agentforce Features\n\n"
        "- New agent capability for customer service\n"
        "- Improved workflow automation\n"
    )

    engine = NLSearchEngine(base_dir=str(tmp_path))
    count = engine.index_release("summer_26")

    assert count == 1


def test_index_release_returns_zero_for_missing(tmp_path: Path) -> None:
    """nl_search: index_release returns 0 for missing release."""
    engine = NLSearchEngine(base_dir=str(tmp_path))
    assert engine.index_release("nonexistent") == 0


def test_index_all(tmp_path: Path) -> None:
    """nl_search: index_all indexes all releases."""
    for name in ["summer_26", "winter_26"]:
        release_dir = tmp_path / name
        release_dir.mkdir()
        (release_dir / "features.md").write_text(f"# {name}\n\n- Feature for {name}\n")

    engine = NLSearchEngine(base_dir=str(tmp_path))
    count = engine.index_all()

    assert count == 2


def test_search_returns_results(tmp_path: Path) -> None:
    """nl_search: search returns relevant results."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "agentforce.md").write_text(
        "# Agentforce\n\n## Agentforce Features\n\n"
        "- New agent capability for customer service\n"
        "- Improved workflow automation\n"
    )

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("agent capability")

    assert results.total_results > 0
    assert results.results[0].category == "Agentforce Features"


def test_search_returns_empty_for_no_match(tmp_path: Path) -> None:
    """nl_search: search returns empty for no match."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "features.md").write_text("# Features\n\n- Security improvement\n")

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("xyznonexistent")

    assert results.total_results == 0


def test_search_respects_max_results(tmp_path: Path) -> None:
    """nl_search: search respects max_results limit."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    features = "\n".join([f"- Feature {i}: Important capability for testing" for i in range(20)])
    (release_dir / "features.md").write_text(f"# Features\n\n{features}")

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("feature", max_results=5)

    assert results.total_results <= 5


def test_search_snippet_extraction(tmp_path: Path) -> None:
    """nl_search: search extracts relevant snippets."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- This is a long feature description about security improvements "
        "that should be extracted as a snippet when searching for security\n"
    )

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("security")

    assert results.total_results > 0
    assert "security" in results.results[0].text_snippet.lower()


def test_search_ranks_by_relevance(tmp_path: Path) -> None:
    """nl_search: search ranks results by relevance."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "agentforce.md").write_text(
        "# Agentforce\n\n## Agentforce Features\n\n" "- Agent capability for customer service\n"
    )
    (release_dir / "security.md").write_text(
        "# Security\n\n## Security Features\n\n" "- Security patch for authentication\n"
    )

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("agent")

    assert results.total_results > 0
    assert results.results[0].category == "Agentforce Features"


def test_search_empty_query(tmp_path: Path) -> None:
    """nl_search: search handles empty query."""
    engine = NLSearchEngine(base_dir=str(tmp_path))
    results = engine.search("")

    assert results.total_results == 0


def test_search_skips_dotfiles(tmp_path: Path) -> None:
    """nl_search: skips dotfiles during indexing."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / ".hidden.md").write_text("# Hidden\n\n- Hidden feature\n")
    (release_dir / "visible.md").write_text("# Visible\n\n- Important visible feature\n")

    engine = NLSearchEngine(base_dir=str(tmp_path))
    count = engine.index_release("summer_26")

    assert count == 1


def test_search_case_insensitive(tmp_path: Path) -> None:
    """nl_search: search is case insensitive."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "features.md").write_text("# Features\n\n- SECURITY improvement for auth\n")

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("security")

    assert results.total_results > 0


def test_search_multiple_releases(tmp_path: Path) -> None:
    """nl_search: search across multiple releases."""
    for name in ["summer_26", "winter_26"]:
        release_dir = tmp_path / name
        release_dir.mkdir()
        (release_dir / "features.md").write_text(f"# {name}\n\n- Feature for {name}\n")

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_all()

    results = engine.search("feature")

    assert results.total_results == 2


def test_search_snippet_with_context(tmp_path: Path) -> None:
    """nl_search: snippet includes context around match."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n" + "- " + "word " * 50 + "security " + "word " * 50 + "\n"
    )

    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine.index_release("summer_26")

    results = engine.search("security")

    assert results.total_results > 0
    assert "..." in results.results[0].text_snippet


def test_search_empty_index(tmp_path: Path) -> None:
    """nl_search: search handles empty index."""
    engine = NLSearchEngine(base_dir=str(tmp_path))
    results = engine.search("test")

    assert results.total_results == 0
    assert results.search_time_ms >= 0


def test_build_idf_empty(tmp_path: Path) -> None:
    """nl_search: build_idf handles empty document list."""
    engine = NLSearchEngine(base_dir=str(tmp_path))
    engine._build_idf()

    assert engine._idf == {}


def test_tokenize_query_filters_stopwords() -> None:
    """nl_search: tokenize_query filters stopwords."""
    engine = NLSearchEngine()
    terms = engine._tokenize_query("the quick brown fox")

    assert "the" not in terms
    assert "quick" in terms
    assert "brown" in terms
    assert "fox" in terms


def test_score_document_empty_term_count(tmp_path: Path) -> None:
    """nl_search: score_document handles empty term count."""
    from src.nl_search import _IndexedDocument

    engine = NLSearchEngine(base_dir=str(tmp_path))
    doc = _IndexedDocument(
        release_slug="test",
        file_name="test.md",
        category="Test",
        content="test content",
        terms={},
        term_count=0,
    )

    score, matched = engine._score_document(doc, {"test"})
    assert score == 0.0
    assert matched == []


def test_extract_snippet_no_match(tmp_path: Path) -> None:
    """nl_search: extract_snippet returns first N chars when no match."""
    engine = NLSearchEngine(base_dir=str(tmp_path))
    content = "A" * 300

    snippet = engine._extract_snippet(content, {"xyz"})

    assert snippet.startswith("A")
    assert snippet.endswith("...")
    assert len(snippet) < len(content)
