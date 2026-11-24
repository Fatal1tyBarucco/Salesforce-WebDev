"""Stub ledger models module for backward compatibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LifecycleStatus(str, Enum):
    """Feature lifecycle status."""

    ACTIVE = "active"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class LinkageMethod(str, Enum):
    """Method used for feature linkage."""

    EXACT = "exact"
    FUZZY = "fuzzy"
    SEMANTIC = "semantic"


@dataclass
class FeatureSnapshot:
    """Snapshot of a feature at a point in time."""

    feature_id: str
    title: str
    category: str
    release: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: LifecycleStatus = LifecycleStatus.ACTIVE


@dataclass
class FeatureEvolution:
    """Evolution of a feature across releases."""

    feature_id: str
    snapshots: list[FeatureSnapshot] = field(default_factory=list)
    current_state: str = "active"


@dataclass
class LedgerDiff:
    """Difference between two ledger states."""

    added: list[FeatureSnapshot] = field(default_factory=list)
    removed: list[FeatureSnapshot] = field(default_factory=list)
    changed: list[FeatureSnapshot] = field(default_factory=list)


@dataclass
class FeatureHistoryEntry:
    """Entry in feature history."""

    feature_id: str
    title: str
    release: str
    action: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FeatureLink:
    """Link between two features."""

    source_id: str
    target_id: str
    method: LinkageMethod
    confidence: float


@dataclass
class LedgerStats:
    """Statistics for the ledger."""

    total_features: int = 0
    total_links: int = 0
    active_features: int = 0
    deprecated_features: int = 0
