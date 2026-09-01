"""Type stubs for syrupy (snapshot testing library).

Provides type annotations for the SnapshotAssertion fixture used in tests.
"""

from __future__ import annotations

from typing import Any, TypeVar

T = TypeVar("T")

class SnapshotAssertion:
    """Type stub for the syrupy snapshot assertion object."""

    def __eq__(self, other: object) -> bool: ...

def snapshot(*args: Any, **kwargs: Any) -> SnapshotAssertion:
    """Fixture that provides a SnapshotAssertion for comparing against saved snapshots."""
    ...
