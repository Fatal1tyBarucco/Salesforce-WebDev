"""Tests for feature_classifier module."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from src.feature_classifier import (
    FeatureClassifier,
    FeatureType,
    ImpactLevel,
)


def test_classify_text_security():
    """feature_classifier: classifies security features."""
    classifier = FeatureClassifier()

    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "high"},
            "FeatureType": {"value": "security"},
            "confidence": 0.9,
        }
        result = asyncio.run(
            classifier.classify_text("Security vulnerability fix for authentication")
        )

    assert result.impact == ImpactLevel.HIGH
    assert result.feature_type == FeatureType.SECURITY
    assert result.confidence > 0.5


def test_classify_text_performance():
    """feature_classifier: classifies performance features."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "medium"},
            "FeatureType": {"value": "performance"},
            "confidence": 0.8,
        }
        result = asyncio.run(
            classifier.classify_text("Performance optimization for query execution")
        )

    assert result.feature_type == FeatureType.PERFORMANCE


def test_classify_text_bug_fix():
    """feature_classifier: classifies bug fixes."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "low"},
            "FeatureType": {"value": "bug_fix"},
            "confidence": 0.7,
        }
        result = asyncio.run(classifier.classify_text("Bug fix for login error"))

    assert result.feature_type == FeatureType.BUG_FIX


def test_classify_text_new_feature():
    """feature_classifier: classifies new features."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "medium"},
            "FeatureType": {"value": "new_feature"},
            "confidence": 0.8,
        }
        result = asyncio.run(classifier.classify_text("New feature: AI-powered analytics"))

    assert result.feature_type == FeatureType.NEW_FEATURE


def test_classify_text_deprecation():
    """feature_classifier: classifies deprecations."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "high"},
            "FeatureType": {"value": "deprecation"},
            "confidence": 0.9,
        }
        result = asyncio.run(classifier.classify_text("Deprecated: Legacy API endpoint"))

    assert result.feature_type == FeatureType.DEPRECATION
    assert result.impact == ImpactLevel.HIGH


def test_classify_text_breaking_change():
    """feature_classifier: classifies breaking changes."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "high"},
            "FeatureType": {"value": "breaking_change"},
            "confidence": 0.95,
        }
        result = asyncio.run(classifier.classify_text("Breaking change: Schema migration required"))

    assert result.feature_type == FeatureType.BREAKING_CHANGE
    assert result.impact == ImpactLevel.HIGH


def test_classify_text_other():
    """feature_classifier: classifies unknown features as OTHER."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "low"},
            "FeatureType": {"value": "other"},
            "confidence": 0.2,
        }
        result = asyncio.run(classifier.classify_text("Random text without keywords"))

    assert result.feature_type == FeatureType.OTHER


def test_classify_release(tmp_path: Path) -> None:
    """feature_classifier: classifies all features in a release."""
    release_dir = tmp_path / "summer_26"
    release_dir.mkdir()
    (release_dir / "security.md").write_text(
        "# Security\n\n"
        "- Security patch for XSS vulnerability\n"
        "- Performance improvement for queries\n"
        "- Bug fix for login issue\n"
    )

    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.side_effect = [
            {
                "ImpactLevel": {"value": "high"},
                "FeatureType": {"value": "security"},
                "confidence": 0.9,
            },
            {
                "ImpactLevel": {"value": "medium"},
                "FeatureType": {"value": "performance"},
                "confidence": 0.8,
            },
            {
                "ImpactLevel": {"value": "low"},
                "FeatureType": {"value": "bug_fix"},
                "confidence": 0.7,
            },
        ]
        result = asyncio.run(classifier.classify_release("summer_26", base_dir=str(tmp_path)))

    assert result is not None
    assert result.total_features == 3
    assert result.release_slug == "summer_26"
    assert len(result.features) == 3


def test_classify_release_returns_none_for_missing(tmp_path: Path) -> None:
    """feature_classifier: returns None for missing release."""
    classifier = FeatureClassifier()
    assert asyncio.run(classifier.classify_release("nonexistent", base_dir=str(tmp_path))) is None


def test_classify_release_handles_tables(tmp_path: Path) -> None:
    """feature_classifier: classifies table row features."""
    release_dir = tmp_path / "tables"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "| RECURSO | ATIVADO |\n"
        "| --- | --- |\n"
        "| Security enhancement for auth | Yes |\n"
        "| New feature for analytics | No |\n"
    )

    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "medium"},
            "FeatureType": {"value": "security"},
            "confidence": 0.8,
        }
        result = asyncio.run(classifier.classify_release("tables", base_dir=str(tmp_path)))

    assert result is not None
    assert result.total_features == 2


def test_classification_result_stats(tmp_path: Path) -> None:
    """feature_classifier: stats are aggregated correctly."""
    release_dir = tmp_path / "stats"
    release_dir.mkdir()
    (release_dir / "features.md").write_text(
        "# Features\n\n"
        "- Security vulnerability fix for auth\n"
        "- Security encryption improvement\n"
        "- Performance query optimization\n"
    )

    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.side_effect = [
            {
                "ImpactLevel": {"value": "high"},
                "FeatureType": {"value": "security"},
                "confidence": 0.9,
            },
            {
                "ImpactLevel": {"value": "medium"},
                "FeatureType": {"value": "security"},
                "confidence": 0.8,
            },
            {
                "ImpactLevel": {"value": "low"},
                "FeatureType": {"value": "performance"},
                "confidence": 0.7,
            },
        ]
        result = asyncio.run(classifier.classify_release("stats", base_dir=str(tmp_path)))

    assert result is not None
    assert result.by_type.get("security", 0) == 2
    assert result.by_type.get("performance", 0) == 1


def test_classify_release_skips_dotfiles(tmp_path: Path) -> None:
    """feature_classifier: skips dotfiles in release directory."""
    release_dir = tmp_path / "dotfiles"
    release_dir.mkdir()
    (release_dir / ".hidden.md").write_text("# Hidden\n\n- Hidden feature\n")
    (release_dir / "visible.md").write_text("# Visible\n\n- Important security feature for auth\n")

    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "high"},
            "FeatureType": {"value": "security"},
            "confidence": 0.9,
        }
        result = asyncio.run(classifier.classify_release("dotfiles", base_dir=str(tmp_path)))

    assert result is not None
    assert result.total_features == 1


def test_classify_release_returns_none_for_empty(tmp_path: Path) -> None:
    """feature_classifier: returns None when no features found."""
    release_dir = tmp_path / "empty"
    release_dir.mkdir()
    (release_dir / "empty.md").write_text("# Empty\n\nNo features here.\n")

    classifier = FeatureClassifier()
    result = asyncio.run(classifier.classify_release("empty", base_dir=str(tmp_path)))

    assert result is None


def test_classify_text_invalid_impact():
    """feature_classifier: defaults to LOW when impact is invalid."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "invalid_impact"},
            "FeatureType": {"value": "security"},
            "confidence": 0.8,
        }
        result = asyncio.run(classifier.classify_text("Test feature"))
    assert result.impact == ImpactLevel.LOW


def test_classify_text_invalid_type():
    """feature_classifier: defaults to OTHER when type is invalid."""
    classifier = FeatureClassifier()
    with patch.object(classifier._llm, "classify_text", new_callable=AsyncMock) as mock_classify:
        mock_classify.return_value = {
            "ImpactLevel": {"value": "high"},
            "FeatureType": {"value": "invalid_type"},
            "confidence": 0.8,
        }
        result = asyncio.run(classifier.classify_text("Test feature"))
    assert result.feature_type == FeatureType.OTHER
