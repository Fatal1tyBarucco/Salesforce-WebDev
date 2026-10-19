"""Central model configuration for the AI documentation pipeline."""

from __future__ import annotations

import os

DEFAULT_OPENROUTER_FREE_MODEL = "google/gemma-4-31b-it:free"


def get_openrouter_free_model() -> str:
    """Return the configured OpenRouter model, rejecting non-free identifiers."""
    model = os.getenv("AI_DOCS_MODEL", DEFAULT_OPENROUTER_FREE_MODEL).strip()
    if not model.endswith(":free"):
        raise ValueError("AI_DOCS_MODEL must identify an OpenRouter :free model.")
    return model
