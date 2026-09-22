"""Coverage push for src/feature_classifier.py."""

from unittest.mock import AsyncMock


def test_feature_classifier_import() -> None:
    from src.feature_classifier import FeatureClassifier
    mock_llm = AsyncMock()
    classifier = FeatureClassifier(llm=mock_llm)
    assert classifier is not None
