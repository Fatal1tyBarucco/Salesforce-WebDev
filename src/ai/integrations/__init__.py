"""External integrations for Salesforce metadata analysis and Trailhead modules."""

from .salesforce import SalesforceAnalyzer
from .trailhead import TrailheadIntegration

__all__ = ["SalesforceAnalyzer", "TrailheadIntegration"]
