"""Impact Propagation & Dependency Graph Engine (RIPE).

Provides cross-release dependency inference, blast radius computation, and
migration intelligence for Salesforce release features.
"""

from .engine import ImpactPropagationEngine
from .graph_builder import DependencyGraphBuilder
from .heuristic_fallback import DependencyHeuristicFallback
from .models import (
    BlastRadiusNode,
    BlastRadiusResponse,
    DependencyEdge,
    DependencyGraphResponse,
    MigrationReportResponse,
    MigrationStep,
)

__all__ = [
    "BlastRadiusNode",
    "BlastRadiusResponse",
    "DependencyEdge",
    "DependencyGraphBuilder",
    "DependencyGraphResponse",
    "DependencyHeuristicFallback",
    "ImpactPropagationEngine",
    "MigrationReportResponse",
    "MigrationStep",
]
