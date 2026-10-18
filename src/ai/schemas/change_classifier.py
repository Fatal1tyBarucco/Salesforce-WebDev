"""First-pass classification of LLM output."""
from __future__ import annotations
import logging
from .change import ChangeEntry

logger = logging.getLogger(__name__)

def validate_and_annotate(entry: ChangeEntry) -> ChangeEntry:
    """Validate entry and annotate low-confidence items."""
    if entry.confidence < 0.5:
        entry.needs_review = True
        entry.review_note = "Baixa confiança — ser revisado pela equipe."
    return entry
