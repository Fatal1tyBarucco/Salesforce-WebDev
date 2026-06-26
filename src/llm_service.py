"""LLM service abstraction for text generation."""

from __future__ import annotations

from typing import Optional


class LLMService:
    """Abstraction for LLM text generation."""

    async def generate_text(
        self, prompt: str, system_prompt: Optional[str] = None
    ) -> Optional[str]:
        """Generate text using the LLM. Override in subclasses."""
        return None
