"""Type stubs for google.genai.types.

Covers the subset used in this project:
  - GenerateContentConfig
"""

from __future__ import annotations

class GenerateContentConfig:
    """Configuration for content generation."""
    def __init__(
        self,
        *,
        system_instruction: str = ...,
        temperature: float = ...,
        max_output_tokens: int = ...,
        top_p: float = ...,
        top_k: int = ...,
        stop_sequences: list[str] | None = ...,
    ) -> None: ...
