"""Second-pass self-review of classification by the LLM."""

from __future__ import annotations
import json
import re
import logging
from pydantic import BaseModel, Field

from .change import ChangeClassification

logger = logging.getLogger(__name__)


class SelfReviewResponse(BaseModel):
    valid: bool = Field(..., description="Whether classification is consistent")
    inconsistencies: list[str] = Field(default_factory=list)
    corrected_fields: dict[str, str] = Field(default_factory=dict)
    note: str = ""


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


def _json_extract(text: str) -> dict[str, object] | None:
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
    try:
        data: object = json.loads(clean)
    except Exception as exc:
        logger.debug("Failed to parse self-review response: %s", exc)
        return None
    if isinstance(data, dict):
        return data
    return None
