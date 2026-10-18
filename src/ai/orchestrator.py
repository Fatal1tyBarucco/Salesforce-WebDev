"""Orchestrator for AI-driven documentation pipeline (uses existing LLMService)."""
from __future__ import annotations
import logging
import os
from dataclasses import dataclass
from typing import Any
from .llm.client import ExistingLLMClient
from .collectors.change_collector import collect_changes

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    changes: list[dict]
    documents: list[str]
    errors: list[str]
    status: str = "completed"
    total_tokens: int = 0


class AIDocOrchestrator:
    """Coordinates: collect -> classify -> generate -> render -> publish."""

    def __init__(self, since_ref: str | None = None, publish_mode: str = "commit") -> None:
        self.since_ref = since_ref or self._last_ref()
        self.publish_mode = publish_mode  # "commit" or "pr"
        self.llm = ExistingLLMClient()

    def _last_ref(self) -> str:
        path = "docs/.last-processed-ref"
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
        return "HEAD~10"

    async def run(self) -> PipelineResult:
        logger.info("Starting AI-doc pipeline since_ref=%s", self.since_ref)
        try:
            raw = collect_changes(since_ref=self.since_ref)
            if not raw.get("commits"):
                logger.info("No relevant changes — no-op.")
                return PipelineResult(changes=[], documents=[], errors=[], status="no-op")
            # Classification via existing LLMService free-tier chain
            prompt = self._build_classify_prompt(raw)
            classified = self.llm.generate(prompt, schema=dict)
            # Render with existing generators (preserve layout)
            docs = self._render_documents(classified)
            # Persist ref
            with open("docs/.last-processed-ref", "w") as f:
                f.write(os.getenv("GITHUB_SHA", "HEAD"))
            return PipelineResult(changes=classified.get("changes", []), documents=docs, errors=[], status="completed")
        except Exception as exc:
            logger.error("Pipeline error: %s", exc)
            return PipelineResult(changes=[], documents=[], errors=[str(exc)], status="failed")

    def _build_classify_prompt(self, raw: dict) -> str:
        return (
            f"Você é arquiteto de software responsável por analisar mudanças.\n\n"
            f"Contexto (git log, diffs, PRs): {raw}\n\n"
            f"Classifique cada mudança: title, description (pt-BR), type (feature|bugfix|security|performance|breaking_change|documentation|refactor), "
            f"impact (high|medium|low), justification, priority (P0-P3), affected_components, source_refs, confidence (0-1).\n"
            f"Responda com JSON estrito."
        )

    def _render_documents(self, classified: dict | str) -> list[str]:
        if isinstance(classified, str):
            try:
                import json
                classified = json.loads(classified)
            except Exception:
                return ["<!-- erro: LLM retornou texto, não JSON -->"]
        from src.ai.generators.markdown import MarkdownGenerator
        from src.ai.generators.badges import impact_badge, type_badge, priority_badge
        data_dict: dict = {}
        if isinstance(classified, dict):
            data_dict = classified
        else:
            return ["<!-- erro: classificação não é dict -->"]
        changes = data_dict.get("changes", [])
        if not changes:
            return []
        # Feed structured output into existing visual generators
        table = MarkdownGenerator.impact_table(changes)
        dist = MarkdownGenerator.impact_distribution(
            sum(1 for c in changes if c.get("impact") == "high"),
            sum(1 for c in changes if c.get("impact") == "medium"),
            sum(1 for c in changes if c.get("impact") == "low"),
        )
        return [table, dist]
