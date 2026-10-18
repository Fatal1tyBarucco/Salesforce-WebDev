"""Second-pass self-review of classification by the LLM."""
from __future__ import annotations
import json
import re
import logging
from pydantic import BaseModel, Field
from typing import Literal

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

def _json_extract(text: str) -> dict[str, object] | None:
    clean = text.strip()
    if clean.startswith("```"):
        clean = re.sub(r"^```(?:json)?\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
    try:
        return json.loads(clean)
    except Exception as exc:
        logger.debug("Failed to parse self-review response: %s", exc)
        return None
