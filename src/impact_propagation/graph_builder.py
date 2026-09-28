"""Dependency Graph Builder.

Constroi grafos direcionados de dependências entre features de release usando
LLM (com CircuitBreaker) ou heuristic como fallback.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.config import RELEASES_DIR
from src.llm_service import LLMService
from src.circuit_breaker import CircuitBreaker
from .models import DependencyEdge, DependencyGraphResponse

logger = logging.getLogger(__name__)


class DependencyGraphBuilder:
    """Constrói grafo de dependências usando LLM (ou heuristic se indisponível)."""

    def __init__(self, llm: LLMService, breaker: CircuitBreaker) -> None:
        self._llm = llm
        self._breaker = breaker

    async def build(self, release_slug: str) -> DependencyGraphResponse:
        release_dir = Path(RELEASES_DIR) / release_slug
        meta_path = release_dir / ".meta.json"
        meta: dict[str, Any] = {}
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass

        # Extrai nomes de features a partir da meta / estrutura de markdown
        features = self._extract_feature_slugs(release_dir, meta)
        if not features:
            # Retorna grafo vazio ao invés de falhar
            return DependencyGraphResponse(
                release_slug=release_slug,
                nodes=[],
                edges=[],
                graph_statistics={"nodes": 0, "edges": 0},
                generated_at="",
                source="llm",
            )

        prompt = self._build_dependency_prompt(features, meta.get("name", release_slug))
        system = (
            "Você é um arquiteto Salesforce com conhecimento profundo de releases."
            " Analise features de release e infira dependências entre elas."
            " Responda APENAS um objeto JSON com nós e arestas; sem texto extra."
            " Prefixe entradas com nomes de features compatíveis com slug (sem espaços)."
        )

        if self._breaker.is_open:
            raise RuntimeError("Circuit breaker aberto para inferência de dependência")

        try:
            result = await self._llm.generate_text(prompt, system)
            self._breaker.record_success()
            parsed = json.loads(result)
            edges = [DependencyEdge(**e) for e in parsed.get("edges", [])]
            return DependencyGraphResponse(
                release_slug=release_slug,
                nodes=parsed.get("nodes", features),
                edges=edges,
                graph_statistics=parsed.get("statistics", {}),
                generated_at="",
                source="llm",
            )
        except Exception as err:
            self._breaker.record_failure()
            logger.warning("Falha no LLM para construção de grafo %s: %s", release_slug, err)
            raise

    @staticmethod
    def _build_dependency_prompt(features: list[str], release_name: str) -> str:
        # Retorna prompt conciso com todas as arestas explícitas
        joined = ", ".join(features)
        return (
            f"Release {release_name} contém features: {joined}. "
            "Analise cada feature em termos de dependências entre si "
            "(API, object, permissão, integração). "
            "Retorne JSON: "
            '{"nodes": [...], "edges": [{"source_feature","target_feature",'
            '"dependency_type","confidence"}], "statistics": {...}}. '
            "Confiança entre 0.0 e 1.0 (1.0 = certo). "
            "Tipos válidos: api, object, permission, integration, "
            "deprecated_api, version_constraint, extensible, breaking."
        )

    @staticmethod
    def _extract_feature_slugs(release_dir: Path, meta: dict[str, Any]) -> list[str]:
        cats = meta.get("categories", [])
        slugs: list[str] = []
        for cat in cats:
            name = cat.get("name", "")
            if isinstance(name, str) and name:
                slugs.append(name.replace(" ", "_").lower())
        return slugs if slugs else []
