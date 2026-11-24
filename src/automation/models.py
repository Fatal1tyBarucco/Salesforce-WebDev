"""Stub models module for backward compatibility."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContentHash:
    """Content hash for deduplication."""

    path: str
    hash: str


@dataclass
class DeduplicationResult:
    """Result of content deduplication analysis."""

    release_slug: str
    unchanged_files: list[str]
    changed_files: list[str]
    new_files: list[str]
    deleted_files: list[str]


@dataclass
class Regression:
    """Regression detected between releases."""

    feature_id: str
    title: str
    severity: str
    description: str


@dataclass
class ReleaseComparison:
    """Comparison between two releases."""

    current: str
    previous: str
    added: list[str]
    removed: list[str]
    changed: list[str]
    stats: dict[str, int]
