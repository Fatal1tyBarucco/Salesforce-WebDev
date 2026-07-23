"""AI automation package — split from ai_automation.py for modularity.

Re-exports models and AIAutomationService for backward compatibility.
Module-level wrapper functions are in ``ai_automation.py``.
"""

from .models import (
    AISummary,
    CategoryImpactScore,
    ContentHash,
    DeduplicationResult,
    FilteredNotification,
    ImpactPrediction,
    QualityMetrics,
    Regression,
    ReleaseComparison,
    TriageResult,
    UserProfile,
)
from .notifications import USER_PROFILES
from .service import AIAutomationService

__all__ = [
    "AIAutomationService",
    "AISummary",
    "CategoryImpactScore",
    "ContentHash",
    "DeduplicationResult",
    "FilteredNotification",
    "ImpactPrediction",
    "QualityMetrics",
    "Regression",
    "ReleaseComparison",
    "TriageResult",
    "UserProfile",
    "USER_PROFILES",
]
