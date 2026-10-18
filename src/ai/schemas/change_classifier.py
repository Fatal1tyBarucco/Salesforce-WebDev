"""First-pass classification of LLM output."""
<<<<<<< HEAD

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
=======
from __future__ import annotations
import logging
from .change import ChangeEntry

logger = logging.getLogger(__name__)

def validate_and_annotate(entry: ChangeEntry) -> ChangeEntry:
    """Validate entry and annotate low-confidence items."""
    if entry.confidence < 0.5:
        entry.needs_review = True
        entry.review_note = "Baixa confiança — ser revisado pela equipe."
<<<<<<< HEAD
    return ChangeClassification(**entry.model_dump())
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
=======
    return entry
>>>>>>> 4279e73 (fix(ai-docs): corrige change_reviewer (import + logger), change_classifier (retorno), e prompts path)
