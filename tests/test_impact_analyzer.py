"""Tests for impact_analyzer module."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.impact_analyzer import ImpactAnalyzer
from src.feature_classifier import FeatureType, ImpactLevel


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

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        classify_results = [
            AsyncMock(feature_type=FeatureType.SECURITY, impact=ImpactLevel.HIGH),
            AsyncMock(feature_type=FeatureType.PERFORMANCE, impact=ImpactLevel.MEDIUM),
            AsyncMock(feature_type=FeatureType.NEW_FEATURE, impact=ImpactLevel.LOW),
            AsyncMock(feature_type=FeatureType.BREAKING_CHANGE, impact=ImpactLevel.HIGH),
        ]
        classify_idx = [0]

        async def classify_side_effect(*args: object, **kwargs: object) -> AsyncMock:
            result = classify_results[classify_idx[0] % len(classify_results)]
            classify_idx[0] += 1
            return result

        mock_classify.side_effect = classify_side_effect
        mock_generate.return_value = '{"migration_actions": ["Update schema"], "risk_score": 0.7, "justification": "High risk"}'

        report = asyncio.run(analyzer.analyze("summer_26"))

    assert report is not None
    assert report.release_slug == "summer_26"
    assert report.total_features == 4
    assert len(report.breaking_changes) == 1
    assert len(report.security_fixes) == 1
    assert report.risk_score == 0.7


def test_analyze_returns_none_for_missing(tmp_path: Path) -> None:
    """impact_analyzer: analyze returns None for missing release."""
    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    assert asyncio.run(analyzer.analyze("nonexistent")) is None


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

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.BREAKING_CHANGE, impact=ImpactLevel.HIGH
        )
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.8, "justification": "High risk"}'
        )

        report = asyncio.run(analyzer.analyze("risk"))

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

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.BREAKING_CHANGE, impact=ImpactLevel.HIGH
        )
        mock_generate.return_value = '{"migration_actions": ["Action 1", "Action 2"], "risk_score": 0.6, "justification": "..."}'

        report = asyncio.run(analyzer.analyze("migration"))

    assert report is not None
    assert len(report.migration_actions) > 0


def test_analyze_executive_summary(tmp_path: Path) -> None:
    """impact_analyzer: executive summary is generated."""
    release_dir = tmp_path / "summary"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n" "- Important feature with long description\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.NEW_FEATURE, impact=ImpactLevel.LOW
        )
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.1, "justification": "Low risk"}'
        )

        report = asyncio.run(analyzer.analyze("summary"))

    assert report is not None
    assert len(report.executive_summary) > 0
    assert "summary" in report.executive_summary.lower() or "Impact" in report.executive_summary


# Remove obsolete tests


def test_analyze_handles_empty_release(tmp_path: Path) -> None:
    """impact_analyzer: analyze returns None for empty release."""
    release_dir = tmp_path / "empty"
    release_dir.mkdir()
    (release_dir / "empty.md").write_text("# Empty\n\nNo features here.\n")

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = asyncio.run(analyzer.analyze("empty"))

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

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        classify_results = [
            AsyncMock(feature_type=FeatureType.SECURITY, impact=ImpactLevel.HIGH),
            AsyncMock(feature_type=FeatureType.SECURITY, impact=ImpactLevel.MEDIUM),
            AsyncMock(feature_type=FeatureType.PERFORMANCE, impact=ImpactLevel.LOW),
            AsyncMock(feature_type=FeatureType.BUG_FIX, impact=ImpactLevel.LOW),
        ]
        classify_idx2 = [0]

        async def classify_side_effect2(*args: object, **kwargs: object) -> AsyncMock:
            result = classify_results[classify_idx2[0] % len(classify_results)]
            classify_idx2[0] += 1
            return result

        mock_classify.side_effect = classify_side_effect2
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.4, "justification": "..."}'
        )

        report = asyncio.run(analyzer.analyze("areas"))

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

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.BREAKING_CHANGE, impact=ImpactLevel.HIGH
        )
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.9, "justification": "..."}'
        )

        report = asyncio.run(analyzer.analyze("risk_range"))

    assert report is not None
    assert 0.0 <= report.risk_score <= 1.0


def test_analyze_migration_actions_empty(tmp_path: Path) -> None:
    """impact_analyzer: migration actions for non-breaking release."""
    release_dir = tmp_path / "no_migration"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n" "- Bug fix for login\n" "- Improvement for dashboard\n"
    )

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.BUG_FIX, impact=ImpactLevel.LOW
        )
        mock_generate.return_value = '{"migration_actions": ["No migration required"], "risk_score": 0.1, "justification": "..."}'

        report = asyncio.run(analyzer.analyze("no_migration"))

    assert report is not None
    assert len(report.migration_actions) > 0
    assert any("No migration" in a for a in report.migration_actions)


def test_analyze_skips_dotfiles(tmp_path: Path) -> None:
    """impact_analyzer: skips dotfiles in release directory."""
    release_dir = tmp_path / "dotfiles"
    release_dir.mkdir()
    (release_dir / ".hidden.md").write_text("# Hidden\n\n- Hidden feature\n")
    (release_dir / "visible.md").write_text("# Visible\n\n- Important security feature for auth\n")

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.SECURITY, impact=ImpactLevel.HIGH
        )
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.5, "justification": "..."}'
        )

        report = asyncio.run(analyzer.analyze("dotfiles"))

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

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.SECURITY, impact=ImpactLevel.MEDIUM
        )
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.3, "justification": "..."}'
        )

        report = asyncio.run(analyzer.analyze("tables"))

    assert report is not None
    assert report.total_features == 2


def test_analyze_zero_features(tmp_path: Path) -> None:
    """impact_analyzer: handles release with zero extractable features."""
    release_dir = tmp_path / "zero"
    release_dir.mkdir()
    (release_dir / "empty.md").write_text("# Empty Release\n\nThis release has no features.\n")

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))
    report = asyncio.run(analyzer.analyze("zero"))

    assert report is None


def test_analyze_critical_risk_level(tmp_path: Path) -> None:
    """impact_analyzer: critical risk level for high-risk release."""
    release_dir = tmp_path / "critical"
    release_dir.mkdir()
    features = "\n".join([f"- Breaking change: Remove feature {i}" for i in range(25)])
    (release_dir / "features.md").write_text(f"# Features\n\n{features}")

    analyzer = ImpactAnalyzer(base_dir=str(tmp_path))

    with (
        patch.object(
            analyzer._classifier, "classify_text", new_callable=AsyncMock
        ) as mock_classify,
        patch.object(analyzer._llm, "generate_text", new_callable=AsyncMock) as mock_generate,
    ):

        mock_classify.return_value = AsyncMock(
            feature_type=FeatureType.BREAKING_CHANGE, impact=ImpactLevel.HIGH
        )
        mock_generate.return_value = (
            '{"migration_actions": [], "risk_score": 0.8, "justification": "CRITICAL risk"}'
        )

        report = asyncio.run(analyzer.analyze("critical"))

    assert report is not None
    assert report.risk_score >= 0.7
    assert "CRITICAL" in report.executive_summary


# Remove obsolete tests
