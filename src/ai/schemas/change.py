"""Pydantic schema for change classification output from LLM."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class ChangeEntry(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    type: Literal["feature","bugfix","security","performance","breaking_change","documentation","refactor"]
    impact: Literal["high","medium","low"]
    impact_justification: str = Field(..., min_length=10, max_length=500)
    priority: Literal["P0","P1","P2","P3"]
    affected_components: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(..., min_length=1)
    confidence: float = Field(..., ge=0.0, le=1.0)
    needs_review: bool = False
    review_note: str = ""

class ChangeClassification(BaseModel):
    changes: list[ChangeEntry] = Field(default_factory=list)
    review_needed: list[ChangeEntry] = Field(default_factory=list)

    def populate_review_needed(self) -> None:
        self.review_needed = [c for c in self.changes if c.confidence < 0.5]
        self.changes = [c for c in self.changes if c.confidence >= 0.5]
        for entry in self.review_needed:
            entry.needs_review = True
            entry.review_note = "Baixa confiança — ser revisado pela equipe."
