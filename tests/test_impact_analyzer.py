"""Tests for impact_analyzer module."""

from pathlib import Path

from src.impact_analyzer import ImpactAnalyzer, ImpactReport


def test_analyze_returns_report(tmp_path: Path) -> None:
    """impact_analyzer: analyze returns report for valid release."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Security vulnerability fix for authentication\n"
        "- Performance improvement for queries\n"
        "- New feature for analytics\n"
        "- Breaking change: Schema migration required\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("summer_26")

    assert report is not None
    assert report.release_slug == "summer_26"
    assert report.total_features == 4
    assert len(report.breaking_changes) == 1
    assert len(report.security_fixes) == 1
    assert report.risk_score > 0


def test_analyze_returns_none_for_missing(tmp_path: Path) -> None:
    """impact_analyzer: analyze returns None for missing release."""
    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    assert analyzer.analyze("nonexistent") is None


def test_analyze_calculates_risk_score(tmp_path: Path) -> None:
    """impact_analyzer: risk score is calculated correctly."""
    release_dir = tmp_path / "risk"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Breaking change: API v1 removed\n"
        "- Security fix for XSS vulnerability\n"
        "- Critical production issue resolved\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("risk")

    assert report is not None
    assert 0.0 <= report.risk_score <= 1.0
    assert report.high_impact_count > 0


def test_analyze_generates_migration_actions(tmp_path: Path) -> None:
    """impact_analyzer: migration actions are generated."""
    release_dir = tmp_path / "migration"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Breaking change: Remove legacy API\n"
        "- Breaking change: Update authentication flow\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("migration")

    assert report is not None
    assert len(report.migration_actions) > 0


def test_analyze_executive_summary(tmp_path: Path) -> None:
    """impact_analyzer: executive summary is generated."""
    release_dir = tmp_path / "summary"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Important feature with long description\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("summary")

    assert report is not None
    assert len(report.executive_summary) > 0
    assert "summary" in report.executive_summary.lower() or "Impact" in report.executive_summary


def test_compare_releases(tmp_path: Path) -> None:
    """impact_analyzer: compare_releases returns comparison."""
    # Create current release
    current_dir = tmp_path / "summer_26"
    current_dir.mkdir()
    (current_dir / "features.md").write_text(
        "# Features\n\n- Breaking change: New API\n- Security fix\n"
    )

    # Create previous release
    prev_dir = tmp_path / "winter_26"
    prev_dir.mkdir()
    (prev_dir / "features.md").write_text(
        "# Features\n\n- Bug fix for login\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    comparison = analyzer.compare_releases("summer_26", "winter_26")

    assert comparison is not None
    assert comparison["current"] == "summer_26"
    assert comparison["previous"] == "winter_26"
    assert comparison["feature_delta"] != 0


def test_compare_releases_returns_none_for_missing(tmp_path: Path) -> None:
    """impact_analyzer: compare_releases returns None for missing release."""
    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    assert analyzer.compare_releases("summer_26", "winter_26") is None


def test_analyze_handles_empty_release(tmp_path: Path) -> None:
    """impact_analyzer: analyze returns None for empty release."""
    release_dir = tmp_path / "empty"
    release_dir.mkdir()
    (release_dir / "empty.md").write_text("# Empty\n\nNo features here.\n")

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("empty")

    assert report is None


def test_analyze_classifies_areas(tmp_path: Path) -> None:
    """impact_analyzer: areas are classified correctly."""
    release_dir = tmp_path / "areas"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Security patch for auth\n"
        "- Security encryption improvement\n"
        "- Performance query optimization\n"
        "- Bug fix for login\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("areas")

    assert report is not None
    assert len(report.areas) > 0
    area_names = [a.name for a in report.areas]
    assert "security" in area_names


def test_analyze_risk_score_ranges(tmp_path: Path) -> None:
    """impact_analyzer: risk score is in valid range."""
    release_dir = tmp_path / "risk_range"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Critical breaking change\n"
        "- Another critical change\n"
        "- More breaking changes\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("risk_range")

    assert report is not None
    assert 0.0 <= report.risk_score <= 1.0


def test_analyze_migration_actions_empty(tmp_path: Path) -> None:
    """impact_analyzer: migration actions for non-breaking release."""
    release_dir = tmp_path / "no_migration"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Bug fix for login\n"
        "- Improvement for dashboard\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("no_migration")

    assert report is not None
    assert len(report.migration_actions) > 0
    assert any("No migration" in a for a in report.migration_actions)


def test_analyze_skips_dotfiles(tmp_path: Path) -> None:
    """impact_analyzer: skips dotfiles in release directory."""
    release_dir = tmp_path / "dotfiles"
    release_dir.mkdir()
    (release_dir / ".hidden.md").write_text(
        "# Hidden\n\n- Hidden feature\n"
    )
    (release_dir / "visible.md").write_text(
        "# Visible\n\n- Important security feature for auth\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("dotfiles")

    assert report is not None
    assert report.total_features == 1


def test_analyze_table_features(tmp_path: Path) -> None:
    """impact_analyzer: extracts features from tables."""
    release_dir = tmp_path / "tables"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "| RECURSO | ATIVADO |\n"
        "| --- | --- |\n"
        "| Security enhancement | Yes |\n"
        "| Performance improvement | No |\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("tables")

    assert report is not None
    assert report.total_features == 2


def test_analyze_zero_features(tmp_path: Path) -> None:
    """impact_analyzer: handles release with zero extractable features."""
    release_dir = tmp_path / "zero"
    release_dir.mkdir()
    (release_dir / "empty.md").write_text(
        "# Empty Release\n\nThis release has no features.\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("zero")

    assert report is None


def test_analyze_critical_risk_level(tmp_path: Path) -> None:
    """impact_analyzer: critical risk level for high-risk release."""
    release_dir = tmp_path / "critical"
    release_dir.mkdir()
    features = "\n".join(
        [f"- Breaking change: Remove feature {i}" for i in range(25)]
    )
    (release_dir / "features.md").write_text(f"# Features\n\n{features}")

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = analyzer.analyze("critical")

    assert report is not None
    assert report.risk_score >= 0.7
    assert "CRITICAL" in report.executive_summary
