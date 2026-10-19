"""Validated natural-language document deltas returned by the LLM."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GeneratedDocuments(BaseModel):
    """A complete set of documentation deltas, generated before any file is written."""

    model_config = ConfigDict(extra="forbid", strict=True)

    release_notes: str = Field(min_length=1)
    changelog_entry: str = Field(min_length=1)
    leadership_summary: str = Field(min_length=1)
    roadmap_suggestions: str = Field(min_length=1)
