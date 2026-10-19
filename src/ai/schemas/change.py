"""Pydantic schema for change classification output from LLM."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ChangeEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    type: Literal[
        "feature",
        "bugfix",
        "security",
        "performance",
        "breaking_change",
        "documentation",
        "refactor",
    ]
    impact: Literal["high", "medium", "low"]
    impact_justification: str = Field(..., min_length=10, max_length=500)
    priority: Literal["P0", "P1", "P2", "P3"]
    affected_components: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    needs_review: bool = False
    review_note: str = ""


class ChangeClassification(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    changes: list[ChangeEntry] = Field(default_factory=list)
    review_needed: list[ChangeEntry] = Field(default_factory=list)

    def populate_review_needed(self) -> None:
        low_confidence = [entry for entry in self.changes if entry.confidence < 0.5]
        self.changes = [entry for entry in self.changes if entry.confidence >= 0.5]
        candidates = [*self.review_needed, *low_confidence]
        unique: dict[tuple[str, tuple[str, ...]], ChangeEntry] = {}
        for entry in candidates:
            key = (entry.title, tuple(entry.source_refs))
            entry.needs_review = True
            if not entry.review_note:
                entry.review_note = "Baixa confiança ou sinalizada pelo classificador."
            unique[key] = entry
        self.review_needed = list(unique.values())
