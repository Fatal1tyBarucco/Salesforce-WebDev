"""Impact Propagation Engine — Core Service.

Orchestrates graph building, blast radius computation, and migration report
generation using LLM inference with heuristic fallback and caching.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Self, Literal, cast

from src.cache_manager import CacheManager
from src.circuit_breaker import CircuitBreaker
from src.config import RELEASES_DIR
from src.llm_service import LLMService
from .graph_builder import DependencyGraphBuilder
from .heuristic_fallback import DependencyHeuristicFallback
from .models import (
    BlastRadiusNode,
    BlastRadiusResponse,
    DependencyGraphResponse,
    MigrationReportResponse,
    MigrationStep,
)

logger = logging.getLogger(__name__)

DEFAULT_MAX_DEPTH = 3
DEFAULT_CACHE_TTL = 86400


class ImpactPropagationEngine:
    """Engine de propagação de impacto e grafo de dependências."""

    def __init__(
        self,
        llm: LLMService | None = None,
        cache: CacheManager | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> None:
        self._llm = llm or LLMService()
        self._cache = cache or CacheManager(
            cache_dir=Path("cache/impact_propagation"), ttl_seconds=DEFAULT_CACHE_TTL
        )
        self._max_depth = max_depth
        self._breaker = CircuitBreaker(threshold=3, cooldown=120.0)
        self._graph_builder = DependencyGraphBuilder(llm=self._llm, breaker=self._breaker)
        self._heuristic = DependencyHeuristicFallback()

    async def build_graph_for_release(self, release_slug: str) -> DependencyGraphResponse:
        """Constrói ou recupera grafo de dependências para uma release."""
        cache_key = f"graph:{release_slug}"
        cached = self._cache.get(cache_key, namespace="propagation_graph")
        if cached is not None:
            return DependencyGraphResponse.model_validate(cached)

        # Construção com fallback
        try:
            graph = await self._graph_builder.build(release_slug)
            source = "llm"
        except Exception as err:
            logger.warning(
                "LLM graph build failed for %s: %s; using heuristic",
                release_slug,
                err,
            )
            graph = self._heuristic.build(release_slug)
            source = "heuristic"

        # Persistência em arquivo (artefato de release)
        release_dir = Path(RELEASES_DIR) / release_slug
        release_dir.mkdir(parents=True, exist_ok=True)
        graph_path = release_dir / ".dependency_graph.json"
        graph_path.write_text(json.dumps(graph.model_dump(), ensure_ascii=False), encoding="utf-8")

        # Cache
        self._cache.set(cache_key, graph.model_dump(), namespace="propagation_graph")
        return DependencyGraphResponse(
            release_slug=release_slug,
            nodes=graph.nodes,
            edges=graph.edges,
            graph_statistics=graph.graph_statistics,
            source=cast(Literal["llm", "heuristic"], source),
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    async def compute_blast_radius(
        self,
        release_slug: str,
        feature_slug: str,
        max_depth: int | None = None,
    ) -> BlastRadiusResponse:
        """Computa blast radius transitivo a partir de uma feature."""
        depth = max_depth or self._max_depth
        cache_key = f"blast:{release_slug}:{feature_slug}:{depth}"
        cached = self._cache.get(cache_key, namespace="blast_radius")
        if cached is not None:
            data = BlastRadiusResponse.model_validate(cached)
            data.cache_hit = True
            return data

        graph = await self.build_graph_for_release(release_slug)
        nodes_affected = self._bfs_affected(graph.edges, feature_slug, max_depth=depth)
        total_score = sum(n.impact_score for n in nodes_affected)

        response = BlastRadiusResponse(
            source_feature=feature_slug,
            max_depth=depth,
            nodes_affected=len(nodes_affected),
            total_impact_score=round(total_score, 2),
            nodes=nodes_affected,
            computed_at=datetime.now(timezone.utc).isoformat(),
            cache_hit=False,
        )
        self._cache.set(cache_key, response.model_dump(), namespace="blast_radius")
        return response

    async def generate_migration_report(self, release_slug: str) -> MigrationReportResponse:
        """Gera relatório de migração ordenado por risco de propagação."""
        graph = await self.build_graph_for_release(release_slug)
        steps = self._order_migration_steps(graph)

        return MigrationReportResponse(
            release_slug=release_slug,
            release_name="",  # preenchido pelo caller se necessário
            total_features_mapped=len(graph.nodes),
            critical_path_length=max((len(s.dependency_chain) for s in steps), default=0),
            steps=steps,
            dependency_graph_summary=self._summarize_edges(graph.edges),
            generated_at=datetime.now(timezone.utc).isoformat(),
            fallback_used=graph.source == "heuristic",
        )

    # ── Helpers internos ───────────────────────────────────────────

    def _bfs_affected(
        self,
        edges: list[Any],
        source: str,
        max_depth: int,
    ) -> list[BlastRadiusNode]:
        """BFS transitivo a partir da feature origem, acumulando scores."""
        adj: dict[str, list[Any]] = defaultdict(list)
        for e in edges:
            adj[e.source_feature].append(e)

        visited: set[str] = set()
        results: list[BlastRadiusNode] = []

        queue: deque[tuple[str, int, list[str], float, list[str]]] = deque()
        queue.append((source, 0, [source], 1.0, []))

        while queue:
            node, depth, path, conf, affected_by = queue.popleft()
            if node in visited or depth > max_depth:
                continue
            visited.add(node)

            # Impact score decai com profundidade e confiança
            impact_score = conf / (1.0 + depth)

            if node != source:
                results.append(
                    BlastRadiusNode(
                        feature_slug=node,
                        depth=depth,
                        impact_score=round(impact_score, 3),
                        dependency_path=path.copy(),
                        affected_by=affected_by.copy(),
                    )
                )

            for edge in adj.get(node, []):
                new_path = path + [edge.target_feature]
                new_conf = conf * edge.confidence
                new_affected = affected_by + [node]
                queue.append((edge.target_feature, depth + 1, new_path, new_conf, new_affected))

        # Ordena por impacto decrescente
        results.sort(key=lambda n: n.impact_score, reverse=True)
        return results

    def _summarize_edges(self, edges: list[Any]) -> dict[str, int]:
        """Resumo de contagens por tipo de dependência."""
        summary: dict[str, int] = defaultdict(int)
        for e in edges:
            summary[e.dependency_type] += 1
        return dict(summary)

    def _order_migration_steps(self, graph: DependencyGraphResponse) -> list[MigrationStep]:
        """Ordenação topológica ponderada por risco (impacto × profundidade)."""
        adj: dict[str, list[Any]] = defaultdict(list)
        indegree: dict[str, int] = defaultdict(int)

        for e in graph.edges:
            adj[e.source_feature].append(e)
            indegree[e.target_feature] += 1
            if e.source_feature not in indegree:
                indegree[e.source_feature] = 0

        # Fila de nós com indegree 0 (sem dependências de entrada)
        queue: deque[str] = deque([n for n in graph.nodes if indegree.get(n, 0) == 0])

        steps: list[MigrationStep] = []
        order = 0

        while queue:
            node = queue.popleft()
            order += 1

            # Risco baseado em número de dependentes e tipo de aresta
            dependents = len(adj.get(node, []))
            edge_types = {e.dependency_type for e in adj.get(node, [])}
            risk = self._classify_risk(dependents, edge_types)

            steps.append(
                MigrationStep(
                    order=order,
                    feature_slug=node,
                    category="",  # poderia ser enriquecido via meta
                    risk_level=cast(Literal["critical", "high", "medium", "low"], risk),
                    action=self._suggest_action(node, risk),
                    dependency_chain=list(edge_types),
                )
            )

            for edge in adj.get(node, []):
                indegree[edge.target_feature] -= 1
                if indegree[edge.target_feature] == 0:
                    queue.append(edge.target_feature)

        return steps

    @staticmethod
    def _classify_risk(dependents: int, edge_types: set[str]) -> str:
        if dependents >= 3 or "breaking" in edge_types or "deprecated_api" in edge_types:
            return "critical"
        if dependents >= 2 or "api" in edge_types:
            return "high"
        if dependents == 1:
            return "medium"
        return "low"

    @staticmethod
    def _suggest_action(feature_slug: str, risk: str) -> str:
        actions = {
            "critical": f"Validar {feature_slug} em sandbox ANTES do upgrade — risco crítico de quebra",
            "high": f"Testar {feature_slug} em ambiente de staging — alto risco de regressão",
            "medium": f"Revisar {feature_slug} como parte do plano de validação padrão",
            "low": f"Verificar {feature_slug} — risco baixo, incluído em smoke test",
        }
        return actions.get(risk, f"Revisar {feature_slug}")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        return
