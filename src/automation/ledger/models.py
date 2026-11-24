"""Pydantic models para o Salesforce Feature Evolution Ledger (SFEL).

Todos os modelos usam Pydantic v2 com validação estrita.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# ── Enums ──────────────────────────────────────────────────────────────


class LifecycleStatus(str, Enum):
    """Estado do ciclo de vida de uma feature entre duas releases."""

    BORN = "born"
    ALIVE = "alive"
    RENAMED = "renamed"
    CATEGORY_CHANGED = "category_changed"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class LinkageMethod(str, Enum):
    """Como uma feature foi associada entre duas releases."""

    EXACT = "exact"
    FUZZY = "fuzzy"
    LLM = "llm"
    HEURISTIC = "heuristic"


# ── Tipos de dado ───────────────────────────────────────────────────────


class FeatureSnapshot(BaseModel):
    """Representação de uma feature em uma release específica."""

    name: str = Field(..., min_length=1, description="Nome normalizado da feature")
    release_slug: str = Field(..., min_length=1, description="Identificador da release")
    category: str = Field(..., min_length=1, description="Categoria da feature")
    snippet: str = Field(
        "",
        description="Trecho do markdown fonte (até 200 caracteres)",
    )
    feature_type: str = Field(
        "other",
        description="Tipo de classificação (security, performance, etc.)",
    )
    impact: str = Field(
        "low",
        description="Nível de impacto: high | medium | low",
    )
    first_seen: str = Field(..., description="Timestamp ISO da primeira indexação")
    last_seen: str = Field(..., description="Timestamp ISO da última indexação")


class FeatureLink(BaseModel):
    """Ligação entre uma feature na release A e a mesma feature na release B."""

    feature_a: FeatureSnapshot
    feature_b: FeatureSnapshot
    status: LifecycleStatus = Field(
        ...,
        description="Transição de ciclo de vida detectada",
    )
    linkage_method: LinkageMethod = Field(
        ...,
        description="Como o match foi realizado",
    )
    similarity_score: float = Field(
        1.0,
        ge=0.0,
        le=1.0,
        description="Similaridade Jaccard dos conjuntos de tokens dos nomes",
    )
    notes: str = Field(
        "",
        description="Explicação legível (gerada por LLM quando disponível)",
    )


class LedgerDiff(BaseModel):
    """Diff entre duas releases consecutivas em nível de feature."""

    current_slug: str = Field(..., min_length=1)
    previous_slug: str = Field(..., min_length=1)
    current_name: str = Field(..., description="Nome exibido da release atual")
    previous_name: str = Field(..., description="Nome exibido da release anterior")
    born: list[FeatureSnapshot] = Field(
        default_factory=list,
        description="Features presentes apenas na release atual",
    )
    alive: list[FeatureSnapshot] = Field(
        default_factory=list,
        description="Features presentes em ambas as releases (inalteradas)",
    )
    renamed: list[FeatureLink] = Field(
        default_factory=list,
        description="Features renomeadas entre as releases",
    )
    category_changed: list[FeatureLink] = Field(
        default_factory=list,
        description="Features que mudaram de categoria",
    )
    deprecated: list[FeatureSnapshot] = Field(
        default_factory=list,
        description="Features marcadas como deprecated na release atual",
    )
    removed: list[FeatureSnapshot] = Field(
        default_factory=list,
        description="Features presentes apenas na release anterior",
    )
    total_current_features: int = Field(0, ge=0)
    total_previous_features: int = Field(0, ge=0)
    generated_at: str = Field(
        "",
        description="Timestamp ISO da geração do ledger",
    )


class FeatureHistoryEntry(BaseModel):
    """Entrada no histórico completo de uma feature através de todas as releases."""

    feature_name: str = Field(..., min_length=1)
    entries: list[FeatureSnapshot] = Field(
        default_factory=list,
        description="Ordenadas por release_id crescente",
    )
    current_status: LifecycleStatus = Field(
        LifecycleStatus.ALIVE,
        description="Status na pair de releases mais recente",
    )
    total_releases_seen: int = Field(0, ge=0)
    removed_in: str | None = Field(
        None,
        description="Release slug onde a feature foi removida (se aplicável)",
    )


class LedgerStats(BaseModel):
    """Estatísticas agregadas do ledger entre duas releases."""

    current_slug: str
    previous_slug: str
    total_features_current: int = Field(0, ge=0)
    total_features_previous: int = Field(0, ge=0)
    born_count: int = Field(0, ge=0)
    alive_count: int = Field(0, ge=0)
    renamed_count: int = Field(0, ge=0)
    category_changed_count: int = Field(0, ge=0)
    deprecated_count: int = Field(0, ge=0)
    removed_count: int = Field(0, ge=0)
    linkage_method_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Contagem de links por LinkageMethod",
    )
    unlinked_previous: list[str] = Field(
        default_factory=list,
        description="Nomes de features anteriores sem match na release atual",
    )
    unlinked_current: list[str] = Field(
        default_factory=list,
        description="Nomes de features atuais sem match na release anterior",
    )
