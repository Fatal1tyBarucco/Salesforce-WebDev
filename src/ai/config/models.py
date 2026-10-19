"""Central model configuration for the AI documentation pipeline."""

from __future__ import annotations

import os

DEFAULT_OPENROUTER_FREE_MODEL = "openrouter/free"


def get_openrouter_free_model() -> str:
    """Return the configured OpenRouter free model identifier."""
    model = os.getenv("AI_DOCS_MODEL", DEFAULT_OPENROUTER_FREE_MODEL).strip()
    if model != "openrouter/free" and not model.endswith(":free"):
        raise ValueError("AI_DOCS_MODEL must be openrouter/free or an OpenRouter :free model.")
    return model
