"""Stub ledger linker module for backward compatibility."""

from __future__ import annotations

from typing import Any


class FeatureLinker:
    """Stub feature linker."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def link(self, *args: Any, **kwargs: Any) -> list[Any]:
        return []


def _tokenize_name(name: str) -> list[str]:
    """Tokenize a feature name."""
    return name.lower().split()


def _jaccard(set1: set[str], set2: set[str]) -> float:
    """Calculate Jaccard similarity."""
    if not set1 and not set2:
        return 1.0
    if not set1 or not set2:
        return 0.0
    return len(set1 & set2) / len(set1 | set2)
