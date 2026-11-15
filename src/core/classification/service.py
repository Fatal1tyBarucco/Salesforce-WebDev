"""Classification domain service — orchestrates feature classification.

This service defines the classification strategy interface and coordinates
between LLM and heuristic classifiers. No external dependencies.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.models.classification import (
    ClassificationResult,
    ClassifiedFeature,
    FeatureType,
    ImpactLevel,
)
from src.models.feature import FeatureCategory

logger = logging.getLogger(__name__)


class ClassificationStrategy(Enum):
    """Classification strategy to use."""

    LLM = "llm"
    HEURISTIC = "heuristic"
    HYBRID = "hybrid"  # Try LLM first, fall back to heuristic


@dataclass(frozen=True)
class ClassificationConfig:
    """Classification configuration — immutable value object."""

    strategy: ClassificationStrategy = ClassificationStrategy.HYBRID
    confidence_threshold: float = 0.5
    batch_size: int = 10
    timeout_seconds: int = 60


class ClassificationAdapter(ABC):
    """Abstract adapter for classification implementations.

    The domain service depends on this interface. Concrete implementations
    (LLM, heuristic) live in the infrastructure layer.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name for logging."""
        ...

    @abstractmethod
    async def classify(
        self, features: list[str], categories: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Classify a batch of feature texts.

        Returns a list of dicts with keys: impact, type, confidence,
        audience, priority, justification.
        """
        ...


class ClassificationService:
    """Domain service for classifying features.

    Coordinates between different classification strategies and
    provides a unified interface for the pipeline.
    """

    def __init__(
        self,
        config: ClassificationConfig | None = None,
        llm_adapter: ClassificationAdapter | None = None,
        heuristic_adapter: ClassificationAdapter | None = None,
    ) -> None:
        self.config = config or ClassificationConfig()
        self._llm_adapter = llm_adapter
        self._heuristic_adapter = heuristic_adapter

    async def classify_features(self, categories: list[FeatureCategory]) -> ClassificationResult:
        """Classify all features in the given categories.

        Args:
            categories: List of feature categories to classify.

        Returns:
            ClassificationResult with all classified features.
        """
        # Extract all feature texts
        feature_texts: list[str] = []
        for cat in categories:
            for feature in cat.features:
                text = feature.raw_text or feature.name
                if text:
                    feature_texts.append(text)

        if not feature_texts:
            return ClassificationResult(
                release_slug="",
                total_features=0,
                by_impact={},
                by_type={},
                features=(),
            )

        # Classify based on strategy
        if self.config.strategy == ClassificationStrategy.LLM:
            results = await self._classify_with_llm(feature_texts)
        elif self.config.strategy == ClassificationStrategy.HEURISTIC:
            results = await self._classify_with_heuristic(feature_texts)
        else:  # HYBRID
            results = await self._classify_hybrid(feature_texts)

        # Build classified features
        classified: list[ClassifiedFeature] = []
        for text, result in zip(feature_texts, results):
            classified.append(self._build_classified_feature(text, result))

        # Aggregate stats
        by_impact: dict[str, int] = {}
        by_type: dict[str, int] = {}
        for feat in classified:
            by_impact[feat.impact.value] = by_impact.get(feat.impact.value, 0) + 1
            by_type[feat.feature_type.value] = by_type.get(feat.feature_type.value, 0) + 1

        return ClassificationResult(
            release_slug=categories[0].locale if categories else "",
            total_features=len(classified),
            by_impact=by_impact,
            by_type=by_type,
            features=tuple(classified),
        )

    async def classify_single(self, text: str) -> ClassifiedFeature:
        """Classify a single feature text."""
        if self.config.strategy == ClassificationStrategy.LLM:
            results = await self._classify_with_llm([text])
        elif self.config.strategy == ClassificationStrategy.HEURISTIC:
            results = await self._classify_with_heuristic([text])
        else:
            results = await self._classify_hybrid([text])

        return self._build_classified_feature(text, results[0] if results else {})

    async def _classify_with_llm(self, texts: list[str]) -> list[dict[str, Any]]:
        """Classify using LLM adapter."""
        if not self._llm_adapter:
            logger.warning("LLM adapter not available, falling back to heuristic")
            return await self._classify_with_heuristic(texts)

        categories = [
            "ImpactLevel: high, medium, low",
            "FeatureType: security, performance, bug_fix, new_feature, improvement, deprecation, breaking_change, integration, ui_ux, other",
        ]

        results = []
        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i : i + self.config.batch_size]
            batch_results = await self._llm_adapter.classify(batch, categories)
            results.extend(batch_results)

        return results

    async def _classify_with_heuristic(self, texts: list[str]) -> list[dict[str, Any]]:
        """Classify using heuristic adapter."""
        if not self._heuristic_adapter:
            logger.warning("Heuristic adapter not available, using defaults")
            return [self._default_classification() for _ in texts]

        return await self._heuristic_adapter.classify(texts)

    async def _classify_hybrid(self, texts: list[str]) -> list[dict[str, Any]]:
        """Try LLM first, fall back to heuristic on failure."""
        try:
            return await self._classify_with_llm(texts)
        except Exception as e:
            logger.warning("LLM classification failed: %s, falling back to heuristic", e)
            return await self._classify_with_heuristic(texts)

    def _build_classified_feature(self, text: str, result: dict[str, Any]) -> ClassifiedFeature:
        """Build a ClassifiedFeature from classification result."""
        from src.models.classification import Audience, Priority

        impact_val = result.get("impact", "low")
        type_val = result.get("type", "other")
        confidence = result.get("confidence", 0.2)

        # Map Portuguese impact values
        impact_map_pt = {"alto": "high", "médio": "medium", "baixo": "low"}
        impact_en = impact_map_pt.get(impact_val, impact_val)

        try:
            impact = ImpactLevel(impact_en)
        except ValueError:
            impact = ImpactLevel.LOW

        try:
            ftype = FeatureType(type_val)
        except ValueError:
            ftype = FeatureType.OTHER

        audience = None
        if result.get("audience"):
            try:
                audience = Audience(result["audience"])
            except ValueError:
                pass

        priority = None
        if result.get("priority"):
            try:
                priority = Priority(result["priority"])
            except ValueError:
                pass

        justification = result.get("justification", "")

        return ClassifiedFeature(
            name=text.strip(),
            impact=impact,
            feature_type=ftype,
            confidence=float(confidence),
            keywords_matched=tuple(result.get("keywords_matched", [])),
            audience=audience,
            priority=priority,
            justification=justification,
        )

    def _default_classification(self) -> dict[str, Any]:
        """Default classification when all adapters fail."""
        return {
            "impact": "medium",
            "type": "other",
            "confidence": 0.1,
            "audience": "",
            "priority": "",
            "justification": "Default classification (adapters unavailable)",
        }
