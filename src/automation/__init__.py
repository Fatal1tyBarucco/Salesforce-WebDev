"""AI automation package — split from ai_automation.py for modularity.

Re-exports models and AIAutomationService for backward compatibility.
Module-level wrapper functions are in ``ai_automation.py``.
"""

from .models import (  # noqa: F401
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
from .notifications import USER_PROFILES as USER_PROFILES  # noqa: F401
from .service import AIAutomationService as AIAutomationService  # noqa: F401
