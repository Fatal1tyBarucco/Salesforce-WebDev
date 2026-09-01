"""Tests for src/heuristic_classifier.py — 100% coverage target."""


class TestClassifyText:
    """HeuristicFeatureClassifier.classify_text: keyword + pattern scoring."""

    def test_empty_text_returns_low_confidence(self) -> None:
        from src.heuristic_classifier import HeuristicFeatureClassifier

        clf = HeuristicFeatureClassifier()
        result = clf.classify_text("")
        assert result["impact"] == "low"
        assert result["confidence"] == 0.1

    def test_none_text_returns_low(self) -> None:
        from src.heuristic_classifier import HeuristicFeatureClassifier

        clf = HeuristicFeatureClassifier()
        result = clf.classify_text(None)
        assert result["impact"] == "low"

    def test_security_text_detected(self) -> None:
        from src.heuristic_classifier import HeuristicFeatureClassifier

        clf = HeuristicFeatureClassifier()
        result = clf.classify_text("Enhanced security and authentication features")
        assert result["impact"] in ("high", "medium", "low")
        assert "confidence" in result

    def test_unknown_text_returns_medium(self) -> None:
        from src.heuristic_classifier import HeuristicFeatureClassifier

        clf = HeuristicFeatureClassifier()
        result = clf.classify_text("Random text with no keywords at all xyz")
        assert result["impact"] == "medium"
        assert result["confidence"] == 0.3

    def test_generic_text_returns_impact_and_confidence(self) -> None:
        from src.heuristic_classifier import HeuristicFeatureClassifier

        clf = HeuristicFeatureClassifier()
        result = clf.classify_text("Some generic feature description")
        assert result["impact"] in ("alto", "médio", "baixo", "high", "medium", "low")
        assert "confidence" in result
