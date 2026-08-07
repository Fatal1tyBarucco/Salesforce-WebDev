"""Prompt templates for AI-powered Salesforce release analysis."""

from .classification import (
    build_classification_system_prompt,
    build_classification_user_prompt,
    parse_classification_response,
)
from .enrichment import (
    build_enrichment_system_prompt,
    build_enrichment_user_prompt,
    build_release_context,
    parse_enrichment_response,
)
from .reporting import (
    build_ai_summary_prompt,
    build_changelog_prompt,
    build_diff_report_prompt,
    build_impact_prediction_prompt,
    build_regression_report_prompt,
    build_reporting_system_prompt,
    parse_report_response,
)
from .validation import (
    ClassificationOutput,
    EnrichmentFeatureOutput,
    EnrichmentOutput,
    ImpactPredictionOutput,
    ReportOutput,
)

__all__ = [
    "ClassificationOutput",
    "EnrichmentFeatureOutput",
    "EnrichmentOutput",
    "ImpactPredictionOutput",
    "ReportOutput",
    "build_ai_summary_prompt",
    "build_changelog_prompt",
    "build_classification_system_prompt",
    "build_classification_user_prompt",
    "build_diff_report_prompt",
    "build_enrichment_system_prompt",
    "build_enrichment_user_prompt",
    "build_impact_prediction_prompt",
    "build_regression_report_prompt",
    "build_release_context",
    "build_reporting_system_prompt",
    "parse_classification_response",
    "parse_enrichment_response",
    "parse_report_response",
]
