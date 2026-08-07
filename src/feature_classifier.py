"""AI-powered feature classifier.

Automatically classifies release features by impact level and type using a resilient LLM service.

Refactored (Phase 1): uses structured prompts with security analyst persona,
Pydantic-validated outputs, and business context with justification.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .ai.prompts.classification import (
    build_classification_system_prompt,
    parse_classification_response,
)
from .config import RELEASES_DIR
from .llm_service import LLMService

logger = logging.getLogger(__name__)


class ImpactLevel(Enum):
    """Feature impact level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FeatureType(Enum):
    """Feature classification type."""

    SECURITY = "security"
    PERFORMANCE = "performance"
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    IMPROVEMENT = "improvement"
    DEPRECATION = "deprecation"
    BREAKING_CHANGE = "breaking_change"
    INTEGRATION = "integration"
    UI_UX = "ui_ux"
    OTHER = "other"


@dataclass
class ClassifiedFeature:
    """A feature with its classification."""

    name: str
    impact: ImpactLevel
    feature_type: FeatureType
    confidence: float
    keywords_matched: list[str] = field(default_factory=list)
    audience: str = ""  # "usuários", "admins", "ambos"
    priority: str = ""  # "crítica", "importante", "opcional"
    justification: str = ""  # 1-sentence justification


@dataclass
class ClassificationResult:
    """Result of classifying all features in a release."""

    release_slug: str
    total_features: int
    by_impact: dict[str, int]
    by_type: dict[str, int]
    features: list[ClassifiedFeature]


class FeatureClassifier:
    """Classifies features by impact and type using an LLM."""

    def __init__(self, llm: LLMService | None = None) -> None:
        self._llm = llm or LLMService()

    async def classify_text(self, text: str) -> ClassifiedFeature:
        """Classify a single feature text using the LLM.

        Uses structured prompts with security analyst persona and
        validates output with Pydantic before returning.

        Args:
            text: The feature description text.

        Returns:
            ClassifiedFeature with impact, type, confidence, and justification.
        """
        categories = [
            "ImpactLevel: high, medium, low",
            "FeatureType: security, performance, bug_fix, new_feature, improvement, deprecation, breaking_change, integration, ui_ux, other",
        ]

        system_prompt = build_classification_system_prompt()

        result = await self._llm.classify_text(text, categories, system_prompt=system_prompt)

        # Try to parse with Pydantic validation first
        justification = ""
        audience = ""
        priority = ""

        if isinstance(result, dict):
            # Extract raw response for Pydantic validation
            raw_response = json.dumps(result)
            validated = parse_classification_response(raw_response)
            if validated:
                impact_val = validated.impact
                type_val = validated.type
                confidence = 0.85
                justification = validated.justification
                audience = validated.audience
                priority = validated.priority
            else:
                # Fallback to legacy parsing
                impact_val = result.get("ImpactLevel", {}).get("value", "low")
                type_val = result.get("FeatureType", {}).get("value", "other")
                confidence = result.get("confidence", 0.2)
        else:
            impact_val = "low"
            type_val = "other"
            confidence = 0.2

        # Map Portuguese impact values to English for enum
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

        return ClassifiedFeature(
            name=text.strip(),
            impact=impact,
            feature_type=ftype,
            confidence=float(confidence),
            keywords_matched=[],
            audience=audience,
            priority=priority,
            justification=justification,
        )

    async def classify_release(
        self, release_slug: str, base_dir: str = RELEASES_DIR
    ) -> ClassificationResult | None:
        """Classify all features in a release.

        Args:
            release_slug: The release directory name.
            base_dir: Base directory containing releases.

        Returns:
            ClassificationResult or None if release not found.
        """
        release_dir = Path(base_dir) / release_slug
        if not release_dir.is_dir():
            return None

        feature_texts: list[str] = []

        for md_file in sorted(release_dir.glob("*.md")):
            if md_file.name.startswith("."):
                continue
            content = md_file.read_text(encoding="utf-8")
            feature_texts.extend(self._extract_feature_texts(content))

        if not feature_texts:
            return None

        # Classify all features in parallel
        all_features = await asyncio.gather(*(self.classify_text(text) for text in feature_texts))

        # Aggregate stats
        by_impact: dict[str, int] = {}
        by_type: dict[str, int] = {}

        for feat in all_features:
            by_impact[feat.impact.value] = by_impact.get(feat.impact.value, 0) + 1
            by_type[feat.feature_type.value] = by_type.get(feat.feature_type.value, 0) + 1

        return ClassificationResult(
            release_slug=release_slug,
            total_features=len(all_features),
            by_impact=by_impact,
            by_type=by_type,
            features=list(all_features),
        )

    def _extract_feature_texts(self, content: str) -> list[str]:
        """Extract feature texts from markdown content."""
        features: list[str] = []

        for line in content.split("\n"):
            line = line.strip()
            # Bullet points
            if line.startswith("- ") or line.startswith("* "):
                text = line[2:].strip()
                if len(text) > 5:
                    features.append(text)
            # Table rows (skip headers)
            elif "|" in line and "RECURSO" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 2 and len(parts[0]) > 3:
                    features.append(parts[0])

        return features
