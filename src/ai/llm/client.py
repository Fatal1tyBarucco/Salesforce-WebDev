"""LLM client abstraction — delegates to existing LLMService (free tier chain)."""
<<<<<<< HEAD

=======
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
from __future__ import annotations
import logging
import json
import re
<<<<<<< HEAD
from typing import Any, Protocol
=======
from typing import Protocol
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)

# Use the project's existing LLMService (free tier: OpenRouter -> OpenCode -> Gemini)
try:
    from src.llm_service import LLMService
except ImportError:
<<<<<<< HEAD
    import sys
    import pathlib

=======
    import sys, pathlib
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
    root = pathlib.Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(root))
    from src.llm_service import LLMService

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Protocol for clients that use the existing free-tier provider chain."""
<<<<<<< HEAD

    def generate(self, prompt: str, schema: type | None = None) -> dict[str, Any] | str: ...
=======
    def generate(self, prompt: str, schema: type | None = None) -> dict | str:
        ...
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)


class ExistingLLMClient:
    """Client that wraps the project's existing LLMService (free-tier chain)."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
    ) -> None:
        self.service = LLMService(
            api_key=None,
            model_name=model,
            provider=provider,
        )
        self.provider = self.service.provider
        self.model = self.service.model_name
        logger.info(
            "LLMClient initialized: provider=%s, model=%s",
            self.provider,
            self.model,
        )

    def generate(
        self,
        prompt: str,
        schema: type | None = None,
<<<<<<< HEAD
    ) -> dict[str, Any] | str:
=======
    ) -> dict | str:
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        try:
            raw = self.service.generate_completion(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000,
            )
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            raise
        if schema is not None and isinstance(raw, str):
            try:
                clean = raw.strip()
                if clean.startswith("```"):
                    clean = re.sub(r"^```(?:json)?\s*", "", clean)
                    clean = re.sub(r"\s*```$", "", clean)
                data = json.loads(clean)
<<<<<<< HEAD
                if isinstance(data, dict):
                    if isinstance(schema, type) and hasattr(schema, "model_validate"):
                        validated = schema.model_validate(data)
                        if isinstance(validated, dict):
                            return validated
                    return data
                return raw
            except Exception as exc:
                logger.warning("Schema validation failed after LLM response: %s", exc)
=======
                if isinstance(schema, type) and hasattr(schema, "model_validate"):
                    return schema.model_validate(data)
                return data  # type: ignore[no-any-return]
            except Exception as exc:
                logger.warning(
                    "Schema validation failed after LLM response: %s", exc
                )
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
                return raw
        return raw
