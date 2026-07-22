"""Heuristic feature classifier — fallback when LLM is unavailable.

Provides keyword-based classification that mirrors the LLM classifier's
interface without requiring an API call.  Used for graceful degradation
when the LLM service fails or exceeds budget.

Usage::

    from src.heuristic_classifier import HeuristicFeatureClassifier

    classifier = HeuristicFeatureClassifier()
    result = classifier.classify_text("New security feature for MFA")
    # {"impact": "high", "type": "security", "confidence": 0.7}
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Keyword → (impact, type) mapping
_KEYWORD_RULES: list[tuple[str, str, str, float]] = [
    # (pattern, impact, type, confidence)
    (r"(?i)\b(security|vulnerability|cve|auth|xss|injection)\b", "high", "security", 0.8),
    (r"(?i)\b(performance|latency|speed|optimization|cache)\b", "high", "performance", 0.7),
    (r"(?i)\b(deprecated|end.of.life|sunset|removal)\b", "high", "deprecation", 0.8),
    (r"(?i)\b(breaking|incompatible|migration|upgrade.required)\b", "high", "breaking_change", 0.8),
    (r"(?i)\b(bug|fix|patch|hotfix|issue)\b", "medium", "bug_fix", 0.6),
    (r"(?i)\b(new|add|introduce|launch|feature)\b", "medium", "new_feature", 0.6),
    (r"(?i)\b(improve|enhance|update|extend)\b", "medium", "improvement", 0.5),
    (r"(?i)\b(api|integration|webhook|endpoint|rest|graphql)\b", "medium", "integration", 0.6),
    (r"(?i)\b(ui|ux|interface|design|lightning|experience)\b", "low", "ui_ux", 0.5),
    (r"(?i)\b(agentforce|einstein|ai|llm|model)\b", "high", "new_feature", 0.7),
]


@dataclass
class HeuristicClassification:
    """Result from heuristic classification."""

    impact: str  # "high" | "medium" | "low"
    type: str  # feature type
    confidence: float  # 0.0-1.0


class HeuristicFeatureClassifier:
    """Keyword-based feature classifier for fallback scenarios.

    Implements the same interface as ``FeatureClassifier.classify_text``
    but returns a dict directly (no async, no LLM).
    """

    def classify_text(self, text: str) -> dict[str, object]:
        """Classify a feature text using keyword matching.

        Args:
            text: Feature description text.

        Returns:
            Dict with 'impact', 'type', and 'confidence' keys.
        """
        if not text or not text.strip():
            return {"impact": "low", "type": "other", "confidence": 0.1}

        best_match: HeuristicClassification | None = None
        best_confidence = 0.0

        for pattern, impact, feature_type, confidence in _KEYWORD_RULES:
            if re.search(pattern, text):
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = HeuristicClassification(
                        impact=impact, type=feature_type, confidence=confidence
                    )

        if best_match:
            return {
                "impact": best_match.impact,
                "type": best_match.type,
                "confidence": best_match.confidence,
            }

        # Default: medium impact, generic type
        return {"impact": "medium", "type": "other", "confidence": 0.3}
