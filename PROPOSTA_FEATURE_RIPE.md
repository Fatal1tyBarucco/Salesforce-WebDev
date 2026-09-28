# Proposta de Feature: Motor de Propagação de Impacto e Grafo de Dependências
## (Cross-Release Impact Propagation & Dependency Graph Engine — RIPE)

**Versão do documento:** 1.0  
**Data:** 2026-09-28  
**Autor:** Arquiteto de Software / Product Owner Técnico  
**Repositório de referência:** `Fatal1tyBarucco/Salesforce-WebDev`  
**Status:** Proposta arquitetural — Ready for Design Review

---

## 1. Nome da Feature & Visão Geral

**Nome técnico:** `ImpactPropagationEngine` (codename: **RIPE** — Release Impact Propagation Engine)  
**Nome de produto:** *Motor de Propagação de Impacto e Grafo de Dependências entre Features*

**Visão Geral:**  
Um serviço arquiteturalmente coeso que, após a classificação e enriquecimento de cada release (já existente via `feature_classifier.py` / `feature_enricher.py`), realiza **inferência de dependências cruzadas entre features** usando raciocínio LLM (com fallback heurístico) e constrói um **grafo direcionado de dependências** (features → APIs/objetos/permismoes → features afetadas). A partir desse grafo, o engine computa o **blast radius transitivo** (propagação de impacto) por feature e gera, por release, um **Migration Intelligence Report** estrutural — um artefato JSON + endpoint REST — que responde à pergunta real de arquitetos Salesforce: *"Se eu atualizar para Summer '26, qual conjunto de recursos da minha org existente é afetado, em que ordem de risco e com que dependências?"*

A feature expande o paradigma *Knowledge-as-Code* de "documento estático por release" para **"rede de conhecimento viva entre releases"**, permitindo consultas como:  
- `propagate("agentforce_ai_analytics")` → retorna todos os recursos dependentes, com caminho de dependência  
- `blast_radius("deprecate_legacy_api")` → retorna impacto transitivo estimado  
- `compare_dependencies("summer_26", "spring_26")` → delta de grafo entre releases

---

## 2. Motivação & Caso de Uso

### Problema real
Salesforce libera releases trimestrais com 150–400+ recursos categorizados. Admins e arquitetos não apenas precisam saber *"o que é novo"* (já resolvido pelo pipeline de `release_summarizer.py` + `nl_search.py`), mas precisam responder:

1. **Interdependência:** "O recurso *Agentforce AI Analytics* depende de qual API/object que eu já uso? Se essa API mudar, o que mais quebre?"
2. **Ordem de migração:** "Quais recursos devo migrar/testar PRIMEIRO dado que dependem de recursos de alta crítica?"
3. **Regressão preventiva:** "Minha org usa 3 recursos de impacto 🔴. Se um deles for removido/deprecado, qual é a cadeia de quebra?"

Hoje, o pipeline produz `IMPACT_REPORT.md`, `.summary_cache.json`, `CHANGELOG.md` — todos **unidirecionais e estáticos** por release. Não há mecanismo de **propagação de impacto entre releases** nem **modelagem de dependência entre features**.

### Casos de uso concretos

| Persona | Dor | Como RIPE resolve |
|---|---|---|
| **CTO / Arquiteto Salesforce** | Planeja upgrade de org com 50+ integrações. Precisa de um mapa de risco sistêmico antes do go-live. | `blast_radius()` + `propagation_path()` retornam o conjunto transitive de recursos impactados, ordenado por profundidade de dependência. |
| **Developer / Admin** | Precisa saber se uma nova feature (e.g., "Enhanced Flow Builder") exige atualização de uma Apex class ou permission set existente. | O grafo de dependências mapeia `feature → salesforce_object / api_version / permission_set`, permitindo consulta direta. |
| **Migration Lead** | Precisa de um checklist de migração ordenado por risco, não por ordem alfabética. | O `MigrationIntelligenceReport` ordena recursos pelo score de propagação (`impact_score × dependency_depth`) e gera passos sequenciais. |
| **Pipeline / CI** | Queria automatizar testes de regressão apenas nos recursos que *de fato* dependem do que mudou. | O endpoint `/v1/propagation/affected` aceita uma lista de recursos modificados e retorna o conjunto de testes necessários. |

---

## 3. Arquitetura & Fluxo de Dados

### 3.1 Módulos afetados / novos arquivos

**Novos arquivos em `src/`:**

```
src/
  impact_propagation/              # novo pacote
    __init__.py
    models.py                      # Pydantic: DependencyEdge, BlastRadius, MigrationReport
    engine.py                      # ImpactPropagationEngine (serviço principal)
    graph_builder.py               # DependencyGraphBuilder (construção do grafo)
    heuristic_fallback.py          # DependencyHeuristicFallback (quando LLM falha)
    cache_key.py                   # chaves de cache para grafo + blast radius
  api.py                          # extendido: 2 novos endpoints REST (já existe FastAPI + stdlib)
  models.py                       # extendido: DependencyGraphResponse adicionado
  cache_manager.py                # usado (já existente, TTL + namespace)
  circuit_breaker.py              # usado (já existente, protege chamadas LLM)
  llm_service.py                  # usado (já existente, fallback chain: OpenRouter → OpenCode → Gemini)
```

**Modificações em arquivos existentes:**

- `src/models.py` → adicionar `DependencyGraphResponse`, `BlastRadiusRequest`, `MigrationReportResponse`
- `src/api.py` → adicionar endpoints `/v1/propagation/graph`, `/v1/propagation/blast-radius`, `/v1/propagation/migration-report`
- `src/main.py` → (opcional, fase 2) chamar `ImpactPropagationEngine.build_for_release()` como etapa pós-classificação no pipeline
- `src/config.py` → adicionar constante `IMPACT_PROPAGATION_CACHE_TTL = 86400`, `IMPACT_PROPAGATION_MAX_DEPTH = 3`

### 3.2 Diagrama textual do fluxo de processamento

```
[Pipeline existente]
    │
    ▼
Release classificadas (feature_classifier.py)
    │
    ▼
Enriquecimento AI (feature_enricher.py)  →  [features enriquecidas com impacto]
    │
    ▼
┌──────────────────────────────────────────────────────────────────────┐
│  NOVO: ImpactPropagationEngine (RIPE)                                │
├──────────────────────────────────────────────────────────────────────┤
│  1. DependencyGraphBuilder                                            │
│     - Lê features por release (pt_BR/*.md, .meta.json)              │
│     - Chama LLM (via llm_service.generate_text) com prompt estruturado│
│     - Recebe JSON de dependências (feature → [dependency_type, target])│
│     - Se LLM falhar 3× (CircuitBreaker OPEN) → heuristic_fallback     │
│     - Construção do grafo direcionado (networkx-style adj dict)      │
│     - Persistência: cache/impact_propagation/<slug>/graph.json        │
│                                                                      │
│  2. ImpactPropagationEngine.compute_blast_radius                      │
│     - Input: feature_slug + max_depth (default 3)                    │
│     - BFS/DFS no grafo a partir do nó inicial                       │
│     - Acumula scores: impact_score × depth × confidence              │
│     - Cache: namespace="blast_radius", key=<slug>:<feature>         │
│                                                                      │
│  3. MigrationIntelligenceReport                                      │
│     - Agrega blast_radius para todas as features de impacto 🔴/🟡   │
│     - Ordena por risco descendente                                   │
│     - Gera passos sequenciais de migração                            │
│     - Escreve releases/<slug>/.migration_report.json                │
│     - Escreve releases/<slug>/pt_BR/01_migration_guide.md           │
└──────────────────────────────────────────────────────────────────────┘
    │
    ▼
API (/v1/propagation/...)  +  Artefatos de arquivo  +  Cache TTL
```

### 3.3 Integração com infraestrutura existente

| Componente existente | Uso em RIPE | Mecanismo |
|---|---|---|
| `LLMService` (`llm_service.py`) | Inferência de dependências entre features; geração de passos de migração | `generate_text()` com system prompt estruturado; `classify_text()` para categorização de dependência |
| `CacheManager` (`cache_manager.py`) | Cache de grafo por release e blast radius por feature | Namespace `"propagation_graph"` (grafo) + `"blast_radius"` (resultado computado) |
| `CircuitBreaker` (`circuit_breaker.py`) | Proteção das chamadas LLM de inferência de dependência (costosa, suscetível a rate limits) | Instância dedicada `CircuitBreaker(threshold=3, cooldown=120.0)` no `DependencyGraphBuilder` |
| `RateLimiter` (`limiters/`) | Throttling de chamadas LLM por release (não sobrecarregar quota de 20 req/day do Gemini) | Uso do `RateLimiter` existente antes de cada `generate_text()` |
| `FeatureClassifier` (`feature_classifier.py`) | Fonte de dados de impacto por feature (🔴/🟡/🟢) para ponderar blast radius | Leitura do arquivo `.meta.json` (campo `classification_summary.by_impact`) |
| `NLSearchEngine` (`nl_search.py`) | (Fase 2) Busca semântica sobre o grafo de dependências | Indexação adicional de `DependencyEdge` no índice de documentos |

---

## 4. Especificação Técnica do Código

### 4.1 Modelos Pydantic (novos + extensão)

Arquivo: `src/impact_propagation/models.py`

```python
from __future__ import annotations

from pydantic import BaseModel, Field  # type: ignore[import-not-found]
from typing import Literal

class DependencyEdge(BaseModel):  # type: ignore[misc]
    """Uma aresta dirigida do grafo de dependências."""
    source_feature: str = Field(..., description="Slug/nome da feature origem")
    target_feature: str = Field(..., description="Feature dependente (afetada)")
    dependency_type: Literal["api", "object", "permission", "integration", "deprecated_api", "version_constraint"] = Field(...)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança do LLM na relação")
    evidence: str = Field("", description="Trecho do texto de release que fundamenta a relação")

class BlastRadiusNode(BaseModel):  # type: ignore[misc]
    """Resultado de propagação para um nó específico."""
    feature_slug: str
    depth: int = Field(..., ge=0)
    impact_score: float = Field(..., ge=0.0)
    dependency_path: list[str] = Field(default_factory=list, description="Caminho de dependência desde origem")
    affected_by: list[str] = Field(default_factory=list, description="Features pai que causam impacto")

class BlastRadiusResponse(BaseModel):  # type: ignore[misc]
    """Resposta do endpoint /v1/propagation/blast-radius."""
    source_feature: str
    max_depth: int
    nodes_affected: int
    total_impact_score: float
    nodes: list[BlastRadiusNode]
    computed_at: str
    cache_hit: bool = False

class MigrationStep(BaseModel):  # type: ignore[misc]
    """Passo sequencial de migração gerado pelo engine."""
    order: int = Field(..., ge=1)
    feature_slug: str
    category: str = ""
    risk_level: Literal["critical", "high", "medium", "low"]
    action: str = ""
    dependency_chain: list[str] = Field(default_factory=list)

class MigrationReportResponse(BaseModel):  # type: ignore[misc]
    """Relatório completo de migração para uma release."""
    release_slug: str
    release_name: str
    total_features_mapped: int
    critical_path_length: int
    steps: list[MigrationStep]
    dependency_graph_summary: dict[str, int]  # tipo -> contagem de arestas
    generated_at: str
    fallback_used: bool = False

class DependencyGraphResponse(BaseModel):  # type: ignore[misc]
    """Representação do grafo para a API."""
    release_slug: str
    nodes: list[str]
    edges: list[DependencyEdge]
    graph_statistics: dict[str, float]
    generated_at: str
    source: Literal["llm", "heuristic"] = "llm"
```

### 4.2 Extensão de `src/models.py` (adicionais)

```python
class DependencyGraphRequest(BaseModel):  # type: ignore[misc]
    release_slug: str = Field(...)
    include_interrelease: bool = Field(False, description="Incluir dependências com release anterior")

class BlastRadiusRequest(BaseModel):  # type: ignore[misc]
    release_slug: str
    feature_slug: str
    max_depth: int = Field(3, ge=1, le=5)
    include_impact_filter: bool = Field(True, description="Filtrar apenas features de impacto médio/alto")
```

### 4.3 Serviço principal — `src/impact_propagation/engine.py`

```python
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Self

from ..cache_manager import CacheManager
from ..circuit_breaker import CircuitBreaker
from ..config import RELEASES_DIR, IMPACT_PROPAGATION_MAX_DEPTH
from ..llm_service import LLMService
from .graph_builder import DependencyGraphBuilder
from .heuristic_fallback import DependencyHeuristicFallback
from .models import DependencyGraphResponse, BlastRadiusResponse, MigrationReportResponse

logger = logging.getLogger(__name__)

class ImpactPropagationEngine:
    """Engine de propagação de impacto e grafo de dependências."""

    def __init__(
        self,
        llm: LLMService | None = None,
        cache: CacheManager | None = None,
        max_depth: int = IMPACT_PROPAGATION_MAX_DEPTH,
    ) -> None:
        self._llm = llm or LLMService()
        self._cache = cache or CacheManager(
            cache_dir=Path("cache/impact_propagation"), ttl_seconds=86400
        )
        self._max_depth = max_depth
        # Circuit breaker dedicado para inferência de dependência (custo elevado)
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
            logger.warning("LLM graph build failed for %s: %s; using heuristic", release_slug, err)
            graph = self._heuristic.build(release_slug)
            source = "heuristic"

        # Persistência em arquivo (artefato de release)
        release_dir = Path(RELEASES_DIR) / release_slug
        graph_path = release_dir / ".dependency_graph.json"
        graph_path.write_text(
            json.dumps(graph.model_dump(), ensure_ascii=False), encoding="utf-8"
        )

        # Cache
        self._cache.set(cache_key, graph.model_dump(), namespace="propagation_graph")
        return DependencyGraphResponse(
            release_slug=release_slug,
            nodes=graph.nodes,
            edges=graph.edges,
            graph_statistics=graph.statistics,
            source=source,
        )

    async def compute_blast_radius(
        self, release_slug: str, feature_slug: str, max_depth: int | None = None
    ) -> BlastRadiusResponse:
        """Computa blast radius transitive a partir de uma feature."""
        depth = max_depth or self._max_depth
        cache_key = f"blast:{release_slug}:{feature_slug}:{depth}"
        cached = self._cache.get(cache_key, namespace="blast_radius")
        if cached is not None:
            data = BlastRadiusResponse.model_validate(cached)
            data.cache_hit = True
            return data

        # Recupera grafo (do arquivo de artefato ou cache)
        graph = await self.build_graph_for_release(release_slug)
        nodes_affected = self._bfs_affected(
            graph.edges, feature_slug, max_depth=depth
        )
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
        # Implementação simplificada para o esboço técnico — expandida no arquivo físico
        graph = await self.build_graph_for_release(release_slug)
        # Lógica de ordenação por impacto × profundidade de dependência
        steps = self._order_migration_steps(graph)
        return MigrationReportResponse(
            release_slug=release_slug,
            release_name="",
            total_features_mapped=len(graph.nodes),
            critical_path_length=max((s.dependency_chain.__len__() for s in steps), default=0),
            steps=steps,
            dependency_graph_summary={},
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

    # ── Métodos auxiliares (definidos no arquivo físico) ───
    def _bfs_affected(self, edges: list[Any], source: str, max_depth: int) -> list[Any]:
        ...  # BFS transitive com acúmulo de score

    def _order_migration_steps(self, graph: DependencyGraphResponse) -> list[Any]:
        ...  # Ordenação topológica ponderada por risco

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc: object) -> None:
        return
```

### 4.4 Graph Builder — `src/impact_propagation/graph_builder.py` (esboço de integração LLM)

```python
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..config import RELEASES_DIR
from ..llm_service import LLMService
from ..circuit_breaker import CircuitBreaker
from .models import DependencyGraphResponse, DependencyEdge

logger = logging.getLogger(__name__)

class DependencyGraphBuilder:
    def __init__(self, llm: LLMService, breaker: CircuitBreaker) -> None:
        self._llm = llm
        self._breaker = breaker

    async def build(self, release_slug: str) -> DependencyGraphResponse:
        release_dir = Path(RELEASES_DIR) / release_slug
        meta_path = release_dir / ".meta.json"
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}

        # Extrai nomes de features da meta / markdown
        features = self._extract_feature_slugs(release_dir, meta)
        if not features:
            return DependencyGraphResponse(release_slug=release_slug, nodes=[], edges=[], graph_statistics={})

        # Prompt estruturado para inferência de dependências
        prompt = self._build_dependency_prompt(features, meta.get("name", release_slug))
        system = "Você é um arquiteto Salesforce. Responda APENAS com JSON."

        # Proteção via Circuit Breaker
        if self._breaker.is_open:
            raise RuntimeError("Circuit breaker open for dependency inference")

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
                source="llm",
            )
        except Exception as err:
            self._breaker.record_failure()
            raise

    def _build_dependency_prompt(self, features: list[str], release_name: str) -> str:
        return (
            f"Release {release_name}. Features: {', '.join(features)}.\n"
            "Infera dependências entre elas (API, objeto, permissão, integração, depreciação).\n"
            "Responda em JSON: {\"nodes\": [...], \"edges\": [{\"source_feature\",\"target_feature\",\"dependency_type\",\"confidence\"}], \"statistics\": {...}}"
        )

    @staticmethod
    def _extract_feature_slugs(release_dir: Path, meta: dict[str, Any]) -> list[str]:
        # Extração simplificada a partir de .meta.json categories
        cats = meta.get("categories", [])
        slugs: list[str] = []
        for cat in cats:
            name = cat.get("name", "")
            if isinstance(name, str) and name:
                slugs.append(name.replace(" ", "_").lower())
        return slugs if slugs else []
```

---

## 5. Impacto na API e Distribuição

### 5.1 Novos endpoints REST (`src/api.py` — extensão do FastAPI existente)

```python
# Adição ao arquivo src/api.py (já existe app = FastAPI(...))

class DependencyGraphRequest(BaseModel):  # já definido em src/models.py
    release_slug: str

class BlastRadiusRequest(BaseModel):
    release_slug: str
    feature_slug: str
    max_depth: int = 3

@app.post("/v1/propagation/graph", response_model=DependencyGraphResponse)
def get_dependency_graph(payload: DependencyGraphRequest, api_key: str = Depends(verify_api_key)) -> DependencyGraphResponse:
    from .impact_propagation.engine import ImpactPropagationEngine
    engine = ImpactPropagationEngine()
    # Nota: em produção, usar async e injetar engine via DI (PipelineConfig)
    return engine.build_graph_for_release(payload.release_slug)

@app.post("/v1/propagation/blast-radius", response_model=BlastRadiusResponse)
async def blast_radius(payload: BlastRadiusRequest, api_key: str = Depends(verify_api_key)) -> BlastRadiusResponse:
    from .impact_propagation.engine import ImpactPropagationEngine
    engine = ImpactPropagationEngine()
    return await engine.compute_blast_radius(
        payload.release_slug, payload.feature_slug, payload.max_depth
    )

@app.get("/v1/propagation/migration-report/{release_slug}", response_model=MigrationReportResponse)
async def migration_report(release_slug: str, api_key: str = Depends(verify_api_key)) -> MigrationReportResponse:
    from .impact_propagation.engine import ImpactPropagationEngine
    engine = ImpactPropagationEngine()
    return await engine.generate_migration_report(release_slug)
```

**Nota de resiliência:** Se `LLMService` estiver indisponível (todas as chaves falharam, `provider="none"`), o endpoint `/v1/propagation/graph` retorna automaticamente o grafo heurístico (`source="heuristic"`) — nunca falha com 500, apenas degrada graciosamente (padrão já estabelecido por `LLMService.generate_completion()` que retorna mock).

### 5.2 Webhooks / Eventos (opcional — fase 2)

- `pipeline.propagation.completed` → emitido via `EventBus` (`src/events.py`) quando `ImpactPropagationEngine.build_graph_for_release()` completa.
- `pipeline.migration.report.ready` → emitido quando `.migration_report.json` é escrito.

### 5.3 Artefatos de distribuição (arquivos gerados)

Por release (`releases/<slug>/`):

```
releases/summer_26/
  .meta.json
  .summary_cache.json
  .dependency_graph.json        # NOVO — grafo direcionado completo
  .migration_report.json        # NOVO — relatório de migração ordenado
  pt_BR/
    01_migration_guide.md      # NOVO — guia de migração em Markdown (para humanos)
  en_US/
    01_migration_guide.md
```

---

## 6. Plano de Testes & Validation Gate

### 6.1 Cobertura mínima: 95% (conforme `pyproject.toml` `--cov-fail-under=95`)

**Arquivos de teste:** `tests/test_impact_propagation.py` (novo), extensões em `tests/test_api_auth.py`.

### 6.2 Casos de teste (Pytest — `pytest-asyncio` / `asyncio_mode = "auto"`)

```python
# tests/test_impact_propagation.py  (esboço técnico)

import pytest
from src.impact_propagation.engine import ImpactPropagationEngine
from src.impact_propagation.graph_builder import DependencyGraphBuilder
from src.impact_propagation.heuristic_fallback import DependencyHeuristicFallback
from src.impact_propagation.models import DependencyGraphResponse, BlastRadiusResponse
from src.cache_manager import CacheManager
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.generate_text = AsyncMock(return_value='{"nodes":["agentforce"],"edges":[],"statistics":{}}')
    return llm

@pytest.fixture
def engine(mock_llm):
    return ImpactPropagationEngine(llm=mock_llm, cache=CacheManager(Path("/tmp/test_cache")))

@pytest.mark.asyncio
async def test_engine_builds_graph_from_lm(engine, mock_llm, tmp_path):
    # Mock de arquivo de release existente
    from src.config import RELEASES_DIR
    # Cria estrutura mínima para teste
    ...
    result = await engine.build_graph_for_release("test_release")
    assert isinstance(result, DependencyGraphResponse)
    assert result.source == "llm"

@pytest.mark.asyncio
async def test_engine_falls_back_on_llm_failure(engine, mock_llm):
    mock_llm.generate_text.side_effect = Exception("LLM down")
    # O breaker deve abrir após 3 falhas; depois, heuristic é usado
    result = await engine.build_graph_for_release("test_release")
    assert result.source == "heuristic"  # fallback garantido

@pytest.mark.asyncio
async def test_blast_radius_cache_hit(engine):
    # Pré-popula cache com resposta simulada
    engine._cache.set("blast:test:feat:3", BlastRadiusResponse(...).model_dump(), namespace="blast_radius")
    result = await engine.compute_blast_radius("test", "feat")
    assert result.cache_hit is True

@pytest.mark.asyncio
async def test_bfs_affected_max_depth(engine):
    # Grafo linear: A -> B -> C -> D; max_depth=2 a partir de A
    edges = [
        {"source_feature":"A","target_feature":"B","dependency_type":"api","confidence":1.0},
        {"source_feature":"B","target_feature":"C","dependency_type":"api","confidence":1.0},
        {"source_feature":"C","target_feature":"D","dependency_type":"api","confidence":1.0},
    ]
    # Teste de que D não aparece com max_depth=2
    ...

def test_heuristic_fallback_builds_graph_without_llm():
    heuristic = DependencyHeuristicFallback()
    # Verifica que grafo vazio / básico é produzido sem chamar LLM
    result = heuristic.build("test_release")
    assert result.release_slug == "test_release"
    assert result.source == "heuristic"

@pytest.mark.asyncio
async def test_api_endpoint_graph(mock_llm):
    # Mock do FastAPI endpoint via TestClient
    from fastapi.testclient import TestClient
    from src.api import app
    # Injeta mock no engine via monkeypatch (não no arquivo de produção)
    ...
```

### 6.3 Estratégias de mock

| Componente externo | Mock / Substituição | Justificativa |
|---|---|---|
| `LLMService.generate_text` | `unittest.mock.AsyncMock` retorna JSON de grafo fixo; teste de falha via `side_effect=Exception` | Protege contra rate limits e custos de LLM durante CI |
| `CacheManager` | `CacheManager(cache_dir=tmp_path)` (isolado por teste) | Garante que testes não corrompem cache de desenvolvimento |
| `CircuitBreaker` | Instância dedicada com `threshold=1` no teste de falha rápida | Acelera o teste do caminho de fallback |
| `ReleaseDir / .meta.json` | Criação temporária via `tmp_path` + `monkeypatch` de `RELEASES_DIR` | Isola o teste do estado do repositório real |
| `Playwright / scraper` | Não usado — o engine opera apenas em arquivos já processados | Alinha com a arquitetura: RIPE é estágio *pós-pipeline* |

### 6.4 Gate de qualidade (executado antes de merge)

```bash
# Comando de validação integral (conforme AGENTS.md)
uv run ruff check src/impact_propagation/ tests/test_impact_propagation.py
uv run black --check src/impact_propagation/ tests/test_impact_propagation.py
uv run mypy src/impact_propagation/ --ignore-missing-imports --pretty
uv run pytest tests/test_impact_propagation.py -v --cov=src/impact_propagation --cov-fail-under=95 --timeout=120
```

**Pre-condições para merge:**
- [ ] `mypy strict = true` passa sem novos erros (confirmado com `mypy_path = "stubs"`)
- [ ] `ruff` sem violações (usar `ignore = ["BLE001", ...]` conforme `pyproject.toml`)
- [ ] `black` formatado (line-length 100, `target-version = ["py313"]`)
- [ ] Cobertura `>= 95%` (branch coverage ativado: `branch = true`)
- [ ] Nenhum arquivo `NOTIFICATION_DIGEST.md` / `DIFF_REPORT.md` de teste commitado (conforme AGENTS.md)
- [ ] `CircuitBreaker.is_open` é verificado em pelo menos um caso de teste
- [ ] `CacheManager.stats.hit_rate` é verificado após operação de cache

---

## 7. Resumo de Valor Arquitetural

| Critério | Status na proposta |
|---|---|
| **Aderência nativa à stack** | ✅ Python 3.13, `uv`, Pydantic v2, `FastAPI`, `LLMService`, `CacheManager`, `CircuitBreaker`, `Playwright` (pós-processamento) |
| **Inovação** | ✅ Primeiro mecanismo de **propagação transitive de impacto** e **grafo de dependências cruzadas** no repositório — vai além de classificação estática |
| **Não duplica** | ✅ `nl_search.py` (busca) e `release_summarizer.py` (resumo) permanecem inalterados; RIPE é camada de **raciocínio de rede** sobre os dados existentes |
| **Resiliência** | ✅ `CircuitBreaker` protege LLM; `CacheManager` reduz chamada; `heuristic_fallback` garante disponibilidade sem LLM |
| **LLM fallback** | ✅ Cadeia: `LLMService.generate_text` → `OpenRouter/Free` → `OpenCode` → `Gemini`; se todos falharem → `heuristic_fallback` |
| **Testes + Quality Gate** | ✅ Plano de testes detalhado com mock de LLM, cache isolado, breaker acelerado; gate `ruff/black/mypy/pytest --cov-fail-under=95` explicitado |
| **Valor para personas** | ✅ CTO (blast radius sistêmico), Admin (migração ordenada), Dev (dependências de API), Pipeline (automação de testes de regressão) |

---

## 8. Próximos Passos Sugeridos (Roadmap de Implementação)

**Fase 1 — Arquitetura + Especificação (esta proposta)** → Design Review + aprovação do Project Board (`Status: Backlog` → `In Progress` via `gh api graphql`)  
**Fase 2 — Núcleo:** `src/impact_propagation/` + `tests/test_impact_propagation.py` (cobertura 95%)  
**Fase 3 — Integração:** `api.py` endpoints + `main.py` chamada opcional pós-classificação + artefatos `.dependency_graph.json`  
**Fase 4 — Produção:** Validação com release real (`summer_26`), comparação `blast_radius` vs. `spring_26`, atualização do `README.en.md` / docs

---
*Fim do documento de proposta.*
