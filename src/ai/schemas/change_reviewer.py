"""Second-pass self-review of classification by the LLM."""
<<<<<<< HEAD

from __future__ import annotations
import json
import re
import logging
from pydantic import BaseModel, Field

from .change import ChangeClassification

logger = logging.getLogger(__name__)

=======
from __future__ import annotations
import json
import re
import logging
from pydantic import BaseModel, Field
from typing import Literal
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)

from .change import ChangeClassification

logger = logging.getLogger(__name__)

class SelfReviewResponse(BaseModel):
    valid: bool = Field(..., description="Whether classification is consistent")
    inconsistencies: list[str] = Field(default_factory=list)
    corrected_fields: dict[str, str] = Field(default_factory=dict)
    note: str = ""

<<<<<<< HEAD

SYSTEM_PROMPT = (
    "Você é um auditor de qualidade de IA responsável por validar "
    "respostas do LLM. Você deve revisar classificações e apontar inconsistências. "
    "RESPONDA COM JSON (sem markdown, sem code fences): "
    '{"valid": bool, "inconsistencies": list[str], "corrected_fields": dict[str, str], "note": str}'
)


def review_classification(classification: ChangeClassification) -> SelfReviewResponse:
    """Deterministic second-pass self-review (no LLM call).

    Audits structural consistency of the classification: low confidence,
    missing affected components and missing source references.
    """
    inconsistencies: list[str] = []
    for entry in classification.changes:
        if entry.confidence < 0.5:
            inconsistencies.append(f"{entry.title}: confiança baixa ({entry.confidence:.2f})")
        if not entry.affected_components:
            inconsistencies.append(f"{entry.title}: sem componentes afetados")
        if not entry.source_refs:
            inconsistencies.append(f"{entry.title}: sem referências de origem")
    if not classification.changes and not classification.review_needed:
        inconsistencies.append("Classificação vazia — nenhuma mudança processada")
    return SelfReviewResponse(
        valid=not inconsistencies,
        inconsistencies=inconsistencies,
        corrected_fields={},
        note="Revisão determinística (segunda passada, sem chamada de LLM).",
    )

=======
SYSTEM_PROMPT = (
    "Você é um auditor de qualidade de IA responsável por validar "
    "respostas do LLM. Você deve revisar classificações e apontar inconsistências. "
    "RESPONDA COM JSON (sem markdown, sem code fences): "
    '{"valid": bool, "inconsistencies": list[str], "corrected_fields": dict[str, str], "note": str}'
)

def review_classification(classification: ChangeClassification) -> SelfReviewResponse | None:
    user_prompt = (
        f"Classificação do LLM:\n"
        f"title={classification.title!r}\n"
        f"type={classification.type!r}\n"
        f"impact={classification.impact!r}\n"
        f"priority={classification.priority!r}\n"
        f"affected_components={classification.affected_components}\n"
        f"source_refs={classification.source_refs}\n"
        f"confidence={classification.confidence}"
    )
    data = _json_extract(user_prompt)
    if data is None:
        return None
    try:
        return SelfReviewResponse.model_validate(data)
    except Exception as exc:
        logger.warning("Self-review returned an invalid response: %s", exc)
        return None
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)

def _json_extract(text: str) -> dict[str, object] | None:
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
    try:
<<<<<<< HEAD
        data: object = json.loads(clean)
    except Exception as exc:
        logger.debug("Failed to parse self-review response: %s", exc)
        return None
    if isinstance(data, dict):
        return data
    return None
=======
        return json.loads(clean)
    except Exception as exc:
        logger.debug("Failed to parse self-review response: %s", exc)
        return None
>>>>>>> f3bb032 (feat(ai-docs): pipeline dinâmico de documentação por IA via GitHub Actions)
