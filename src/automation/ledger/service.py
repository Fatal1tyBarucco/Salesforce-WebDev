"""Stub ledger service module for backward compatibility."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def now_iso() -> str:
    """Current time in ISO format."""
    return datetime.now().isoformat()


class FeatureEvolutionLedgerService:
    """Stub feature evolution ledger service."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def process(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return {}

    async def get_evolution(self, feature_id: str) -> dict[str, Any] | None:
        return None
