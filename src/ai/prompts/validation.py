"""Pydantic models for validating ALL AI outputs.

Every structured response from the LLM is parsed through these models
before being processed, ensuring type safety and data integrity.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EnrichmentFeatureOutput(BaseModel):
    """Validated output for a single enriched feature."""

    name: str = Field(..., min_length=1, description="Exact feature name as provided")
    description: str = Field(
        ...,
        min_length=10,
        description="Professional 1-2 sentence description of business value",
    )
    impact: Literal["alto", "médio", "baixo"] = Field(
        ..., description="Impact level: alto/médio/baixo"
    )
    audience: Literal["usuários", "admins", "ambos"] = Field(
        ..., description="Target audience: usuários/admins/ambos"
    )
    use_cases: list[str] = Field(default_factory=list, description="2-3 practical use cases")
    risks: list[str] = Field(default_factory=list, description="Potential risks or considerations")
    code_example: str = Field(default="", description="Optional code/configuration example")


class EnrichmentOutput(BaseModel):
    """Validated output for category enrichment from LLM."""

    introduction: str = Field(
        ...,
        min_length=10,
        description="2-3 sentence overview of category theme and key changes",
    )
    features: list[EnrichmentFeatureOutput] = Field(
        ..., min_length=1, description="Enriched features list"
    )


class ClassificationOutput(BaseModel):
    """Validated output for feature classification from LLM."""

    type: Literal[
        "security",
        "performance",
        "bug_fix",
        "new_feature",
        "improvement",
        "deprecation",
        "breaking_change",
        "integration",
        "ui_ux",
        "other",
    ] = Field(..., description="Feature classification type")
    impact: Literal["alto", "médio", "baixo"] = Field(..., description="Impact level")
    audience: Literal["usuários", "admins", "ambos"] = Field(..., description="Target audience")
    priority: Literal["crítica", "importante", "opcional"] = Field(
        ..., description="Adoption priority"
    )
    justification: str = Field(
        ...,
        min_length=5,
        max_length=300,
        description="1-sentence justification for the classification",
    )


class ReportOutput(BaseModel):
    """Validated output for AI-generated reports."""

    headline: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Catchy headline for the report",
    )
    highlights: list[str] = Field(..., min_length=1, max_length=5, description="3 key highlights")
    risk_areas: list[str] = Field(..., min_length=1, max_length=3, description="2 risk areas")
    recommendation: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="1 actionable recommendation",
    )
    trend: Literal["crescimento", "estável", "declínio"] = Field(
        ..., description="Overall trend direction"
    )


class ImpactPredictionOutput(BaseModel):
    """Validated output for impact predictions."""

    categories: list[str] = Field(..., description="Categories with highest predicted impact")
    predictions: list[str] = Field(..., description="Specific predictions for each category")
    risk_level: Literal["alto", "moderado", "baixo"] = Field(..., description="Overall risk level")
    preparation_suggestions: list[str] = Field(
        default_factory=list,
        description="Suggested preparation steps for teams",
    )
