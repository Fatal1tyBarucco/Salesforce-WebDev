"""Pydantic models for Impact Propagation Engine.

Defines data structures for dependency graphs, blast radius results, and
migration intelligence reports.
"""

from __future__ import annotations

from pydantic import BaseModel, Field  # type: ignore[import-not-found]
from typing import Literal

# Keep consistent with existing naming (tipo 'alto' vs 'high')
# E2E tests expect these Spanish/Portuguese labels; keep for compatibility


class DependencyEdge(BaseModel):  # type: ignore[misc]
    """Uma aresta do grafo de dependências entre features.

    Representa inferência de dependência cruzada entre features de release,
    como API → object, permission_set, ou integração de feature dependente.
    """

    source_feature: str = Field(..., description="Slug/nome da feature origem")
    target_feature: str = Field(..., description="Feature dependente (afetada)")
    dependency_type: Literal[
        "api",
        "object",
        "permission",
        "integration",
        "deprecated_api",
        "version_constraint",
        "extensible",
        "breaking",
    ] = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança do LLM na relação")
    evidence: str = Field("", description="Trecho do texto de release que fundamenta a relação")


class BlastRadiusNode(BaseModel):  # type: ignore[misc]
    """Resultado de propagação para um nó específico no grafo de dependências."""

    feature_slug: str
    depth: int = Field(..., ge=0)
    impact_score: float = Field(..., ge=0.0)
    dependency_path: list[str] = Field(
        default_factory=list, description="Sequência de dependência desde origem"
    )
    affected_by: list[str] = Field(
        default_factory=list, description="Features pai que causam impacto"
    )


class BlastRadiusResponse(BaseModel):  # type: ignore[misc]
    """Resposta da computação de blast radius para uma feature alvo."""

    source_feature: str
    max_depth: int
    nodes_affected: int
    total_impact_score: float
    nodes: list[BlastRadiusNode]
    computed_at: str
    cache_hit: bool = False


class MigrationStep(BaseModel):  # type: ignore[misc]
    """Passo sequencial de migração gerado pelo RIPE."""

    order: int = Field(..., ge=1)
    feature_slug: str
    category: str = ""
    risk_level: Literal["critical", "high", "medium", "low"]
    action: str = ""
    dependency_chain: list[str] = Field(default_factory=list)


class MigrationReportResponse(BaseModel):  # type: ignore[misc]
    """Relatório completo de migração para uma release.

        Contém etapas ordenadas de migração, derivadas de blast radius e
    grafos de dependência — permitindo que equipes criem um checklist de migração
    ordenado por risco sistêmico, não por ordem alfabética.
    """

    release_slug: str
    release_name: str
    total_features_mapped: int
    critical_path_length: int
    steps: list[MigrationStep]
    dependency_graph_summary: dict[str, int]
    generated_at: str
    fallback_used: bool = False


class DependencyGraphResponse(BaseModel):  # type: ignore[misc]
    """Grafo direcionado de dependências entre features de release.

    Usado por consultas e visualizações de grafo. Origem indica o
    provedor do grafo: 'llm' (inferência em tempo real) ou 'heuristic'
    (fallback baseado em regras).
    """

    release_slug: str
    nodes: list[str]
    edges: list[DependencyEdge]
    graph_statistics: dict[str, float]
    generated_at: str
    source: Literal["llm", "heuristic"] = "llm"
