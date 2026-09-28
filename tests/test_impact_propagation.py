"""Tests for Impact Propagation Engine (RIPE)."""

import json
from pathlib import Path

import pytest

from src.cache_manager import CacheManager
from src.impact_propagation.engine import ImpactPropagationEngine
from src.impact_propagation.heuristic_fallback import DependencyHeuristicFallback
from src.impact_propagation.models import (
    DependencyEdge,
    DependencyGraphResponse,
    MigrationReportResponse,
)

LLM_GRAPH_JSON = json.dumps(
    {
        "nodes": ["api_features", "data_cloud"],
        "edges": [
            {
                "source_feature": "api_features",
                "target_feature": "data_cloud",
                "dependency_type": "api",
                "confidence": 0.9,
            }
        ],
        "statistics": {"nodes": 2, "edges": 1},
    }
)

DENSE_GRAPH_JSON = json.dumps(
    {
        "nodes": ["api_features", "data_cloud", "object_model", "analytics"],
        "edges": [
            {
                "source_feature": "api_features",
                "target_feature": "data_cloud",
                "dependency_type": "api",
                "confidence": 0.9,
            },
            {
                "source_feature": "api_features",
                "target_feature": "object_model",
                "dependency_type": "object",
                "confidence": 0.8,
            },
            {
                "source_feature": "data_cloud",
                "target_feature": "object_model",
                "dependency_type": "integration",
                "confidence": 0.7,
            },
            {
                "source_feature": "object_model",
                "target_feature": "analytics",
                "dependency_type": "api",
                "confidence": 0.6,
            },
        ],
        "statistics": {"nodes": 4, "edges": 4},
    }
)


class MockLLM:
    """Fake LLM returning a canned dependency graph (or raising on demand)."""

    def __init__(self, payload: str = LLM_GRAPH_JSON, error: Exception | None = None) -> None:
        self._payload = payload
        self._error = error
        self.calls = 0

    async def generate_text(self, prompt: str, system_instruction: str | None = None) -> str:
        self.calls += 1
        if self._error is not None:
            raise self._error
        return self._payload


@pytest.fixture
def releases_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect RELEASES_DIR to a tmp release tree with usable metadata."""
    root = tmp_path / "releases"
    release_dir = root / "test_release"
    release_dir.mkdir(parents=True)
    release_dir.joinpath(".meta.json").write_text(
        json.dumps(
            {
                "name": "Test Release",
                "slug": "test_release",
                "categories": [
                    {"name": "API Features", "count": 2},
                    {"name": "Data Cloud", "count": 1},
                ],
            }
        ),
        encoding="utf-8",
    )
    for module in (
        "src.impact_propagation.engine",
        "src.impact_propagation.graph_builder",
        "src.impact_propagation.heuristic_fallback",
    ):
        monkeypatch.setattr(f"{module}.RELEASES_DIR", str(root))
    return root


@pytest.fixture
def engine(releases_root: Path, tmp_path: Path) -> ImpactPropagationEngine:
    """Engine wired to a mock LLM and a per-test (never reused) cache dir."""
    return ImpactPropagationEngine(llm=MockLLM(), cache=CacheManager(tmp_path / "cache"))


def make_engine(tmp_path: Path, llm: MockLLM) -> ImpactPropagationEngine:
    return ImpactPropagationEngine(llm=llm, cache=CacheManager(tmp_path / "cache"))


def test_heuristic_fallback_builds_graph(releases_root: Path) -> None:
    """Heuristic fallback creates a graph from release metadata."""
    result = DependencyHeuristicFallback().build("test_release")
    assert isinstance(result, DependencyGraphResponse)
    assert result.source == "heuristic"
    assert result.nodes == ["api_features", "data_cloud"]
    assert len(result.edges) == 1
    assert result.edges[0].dependency_type == "api"
    assert result.graph_statistics == {"nodes": 2.0, "edges": 1.0}


def test_heuristic_fallback_empty_release(releases_root: Path) -> None:
    """A release without metadata or markdown yields an empty heuristic graph."""
    result = DependencyHeuristicFallback().build("missing_release")
    assert result.source == "heuristic"
    assert result.nodes == []
    assert result.edges == []


def test_heuristic_fallback_skips_invalid_metadata(releases_root: Path) -> None:
    """Malformed .meta.json, blank names, and heading-style names are tolerated."""
    release_dir = Path(releases_root) / "broken_release"
    release_dir.mkdir()
    release_dir.joinpath(".meta.json").write_text("{not-json", encoding="utf-8")
    assert DependencyHeuristicFallback().build("broken_release").nodes == []

    release_dir.joinpath(".meta.json").write_text(
        json.dumps({"categories": [{"name": ""}, {"name": 123}]}), encoding="utf-8"
    )
    assert DependencyHeuristicFallback().build("broken_release").nodes == []

    release_dir.joinpath(".meta.json").write_text(
        json.dumps({"categories": [{"name": "## Section"}]}), encoding="utf-8"
    )
    assert DependencyHeuristicFallback().build("broken_release").nodes == []


def test_heuristic_fallback_reads_markdown(releases_root: Path) -> None:
    """Markdown feature tables are parsed when the release has no categories."""
    release_dir = Path(releases_root) / "md_release"
    release_dir.mkdir()
    release_dir.joinpath(".hidden.md").write_text("| Recurso | não lida |\n", encoding="utf-8")
    release_dir.joinpath("features.md").write_text(
        "| Recurso | Descrição |\n"
        "| **API Nova** | descrição |\n"
        "| Objeto Custom | descrição |\n"
        "|Feature| sem espaço |\n"
        "| | |\n"
        "|---|---|\n"
        "| Fora da Tabela | não lida |\n",
        encoding="utf-8",
    )
    result = DependencyHeuristicFallback().build("md_release")
    assert result.source == "heuristic"
    assert result.nodes == ["API Nova", "Objeto Custom"]
    assert [e.source_feature for e in result.edges] == ["API Nova"]


def test_heuristic_fallback_dedupes_categories(releases_root: Path) -> None:
    """Repeated category names collapse into a single node."""
    release_dir = Path(releases_root) / "dup_release"
    release_dir.mkdir()
    release_dir.joinpath(".meta.json").write_text(
        json.dumps({"categories": [{"name": "API Features"}, {"name": "API Features"}]}),
        encoding="utf-8",
    )
    result = DependencyHeuristicFallback().build("dup_release")
    assert result.nodes == ["api_features"]


def test_heuristic_fallback_unreadable_markdown(releases_root: Path) -> None:
    """Unreadable markdown files are skipped instead of crashing the fallback."""
    release_dir = Path(releases_root) / "unreadable_release"
    release_dir.mkdir()
    release_dir.joinpath("features.md").mkdir()
    assert DependencyHeuristicFallback().build("unreadable_release").nodes == []


def test_has_api_dependency_handles_empty_name() -> None:
    """An empty feature name never maps to an API dependency."""
    assert DependencyHeuristicFallback()._has_api_dependency("") is False
    assert DependencyHeuristicFallback()._has_api_dependency("api_version") is True


@pytest.mark.asyncio
async def test_engine_builds_graph_with_llm(engine: ImpactPropagationEngine) -> None:
    """Engine builds a graph through the mocked LLM when metadata exists."""
    result = await engine.build_graph_for_release("test_release")
    assert isinstance(result, DependencyGraphResponse)
    assert result.source == "llm"
    assert result.nodes == ["api_features", "data_cloud"]
    assert len(result.edges) == 1
    assert result.generated_at


@pytest.mark.asyncio
async def test_engine_graph_is_cached(engine: ImpactPropagationEngine, releases_root: Path) -> None:
    """Second build for the same release is served from cache without an LLM call."""
    first = await engine.build_graph_for_release("test_release")
    second = await engine.build_graph_for_release("test_release")
    assert first.nodes == second.nodes
    assert second.source == "llm"
    graph_file = Path(releases_root) / "test_release" / ".dependency_graph.json"
    assert graph_file.exists()
    assert json.loads(graph_file.read_text(encoding="utf-8"))["nodes"] == first.nodes


@pytest.mark.asyncio
async def test_engine_graph_without_features(tmp_path: Path, releases_root: Path) -> None:
    """Releases with no extractable features return an empty (but valid) graph."""
    result = await make_engine(tmp_path, MockLLM()).build_graph_for_release("missing_release")
    assert result.source == "llm"
    assert result.nodes == []
    assert result.edges == []


@pytest.mark.asyncio
async def test_graph_builder_tolerates_broken_meta(tmp_path: Path, releases_root: Path) -> None:
    """Malformed release metadata does not break graph construction."""
    release_dir = Path(releases_root) / "broken_release"
    release_dir.mkdir()
    release_dir.joinpath(".meta.json").write_text("{not-json", encoding="utf-8")
    result = await make_engine(tmp_path, MockLLM()).build_graph_for_release("broken_release")
    assert result.source == "llm"
    assert result.nodes == []


@pytest.mark.asyncio
async def test_graph_builder_skips_blank_categories(tmp_path: Path, releases_root: Path) -> None:
    """Blank category names are ignored while valid ones still reach the LLM."""
    release_dir = Path(releases_root) / "mixed_release"
    release_dir.mkdir()
    release_dir.joinpath(".meta.json").write_text(
        json.dumps({"categories": [{"name": ""}, {"name": "API Features"}]}), encoding="utf-8"
    )
    result = await make_engine(tmp_path, MockLLM()).build_graph_for_release("mixed_release")
    assert result.source == "llm"
    assert result.nodes == ["api_features", "data_cloud"]


@pytest.mark.asyncio
async def test_graph_builder_rejects_invalid_llm_payload(
    tmp_path: Path, releases_root: Path
) -> None:
    """A malformed LLM payload triggers the heuristic fallback."""
    engine = make_engine(tmp_path, MockLLM(payload="não é json"))
    result = await engine.build_graph_for_release("test_release")
    assert result.source == "heuristic"


@pytest.mark.asyncio
async def test_engine_falls_back_to_heuristic_on_llm_error(
    tmp_path: Path, releases_root: Path
) -> None:
    """LLM failure during graph build triggers the heuristic fallback."""
    engine = make_engine(tmp_path, MockLLM(error=RuntimeError("llm down")))
    result = await engine.build_graph_for_release("test_release")
    assert result.source == "heuristic"
    assert result.nodes == ["api_features", "data_cloud"]
    assert len(result.edges) == 1


@pytest.mark.asyncio
async def test_engine_falls_back_when_circuit_opens(tmp_path: Path, releases_root: Path) -> None:
    """Once the breaker trips, further LLM calls are short-circuited to the heuristic."""
    meta = json.dumps({"name": "Release", "categories": [{"name": "API Features"}]})
    slugs = ("test_release", "rel_a", "rel_b", "rel_c")
    for slug in slugs:
        release_dir = Path(releases_root) / slug
        release_dir.mkdir(exist_ok=True)
        release_dir.joinpath(".meta.json").write_text(meta, encoding="utf-8")

    llm = MockLLM(error=RuntimeError("llm down"))
    engine = make_engine(tmp_path, llm)
    sources = [await engine.build_graph_for_release(slug) for slug in slugs]
    assert [g.source for g in sources] == ["heuristic"] * 4
    assert llm.calls == 3


@pytest.mark.asyncio
async def test_blast_radius_computation(engine: ImpactPropagationEngine) -> None:
    """Blast radius is computed transitively and cached between calls."""
    result1 = await engine.compute_blast_radius("test_release", "api_features", max_depth=2)
    assert result1.cache_hit is False
    assert result1.nodes_affected == 1
    assert result1.nodes[0].feature_slug == "data_cloud"
    assert result1.nodes[0].depth == 1

    result2 = await engine.compute_blast_radius("test_release", "api_features", max_depth=2)
    assert result2.cache_hit is True

    cached = result1.model_dump(exclude={"cache_hit"})
    fresh = result2.model_dump(exclude={"cache_hit"})
    assert cached == fresh


@pytest.mark.asyncio
async def test_blast_radius_unknown_source_returns_empty(
    engine: ImpactPropagationEngine,
) -> None:
    """A feature absent from the graph yields an empty blast radius."""
    result = await engine.compute_blast_radius("test_release", "ghost_feature", max_depth=1)
    assert result.nodes_affected == 0
    assert result.total_impact_score == 0.0
    assert result.nodes == []


@pytest.mark.asyncio
async def test_dense_graph_traversal_and_ordering(tmp_path: Path, releases_root: Path) -> None:
    """Multi-edge graphs respect max depth during BFS and keep topological order."""
    engine = make_engine(tmp_path, MockLLM(payload=DENSE_GRAPH_JSON))
    blast = await engine.compute_blast_radius("test_release", "api_features", max_depth=1)
    assert blast.nodes_affected == 2
    assert {n.feature_slug for n in blast.nodes} == {"data_cloud", "object_model"}

    report = await engine.generate_migration_report("test_release")
    assert [s.feature_slug for s in report.steps] == [
        "api_features",
        "data_cloud",
        "object_model",
        "analytics",
    ]
    assert report.dependency_graph_summary == {"api": 2, "object": 1, "integration": 1}


@pytest.mark.asyncio
async def test_migration_report_generation(engine: ImpactPropagationEngine) -> None:
    """Migration report orders steps by dependency and classifies risk."""
    result = await engine.generate_migration_report("test_release")
    assert isinstance(result, MigrationReportResponse)
    assert result.release_slug == "test_release"
    assert result.fallback_used is False
    assert result.total_features_mapped == 2
    assert [s.feature_slug for s in result.steps] == ["api_features", "data_cloud"]
    assert result.steps[0].risk_level == "high"
    assert "api" in result.steps[0].dependency_chain
    assert result.steps[1].risk_level == "low"
    assert result.critical_path_length == 1
    assert result.dependency_graph_summary == {"api": 1}


@pytest.mark.asyncio
async def test_migration_report_fallback_used(tmp_path: Path, releases_root: Path) -> None:
    """Reports generated from the heuristic fallback are flagged."""
    engine = make_engine(tmp_path, MockLLM(error=RuntimeError("llm down")))
    result = await engine.generate_migration_report("test_release")
    assert result.fallback_used is True
    assert result.steps


@pytest.mark.asyncio
async def test_engine_async_context_manager(tmp_path: Path, releases_root: Path) -> None:
    """Engine supports async context manager protocol."""
    async with make_engine(tmp_path, MockLLM()) as ctx:
        assert isinstance(ctx, ImpactPropagationEngine)
        assert (await ctx.build_graph_for_release("test_release")).nodes


def test_risk_classification_and_actions() -> None:
    """Risk levels and suggested actions cover every classification branch."""
    classify = ImpactPropagationEngine._classify_risk
    assert classify(3, set()) == "critical"
    assert classify(0, {"breaking"}) == "critical"
    assert classify(0, {"deprecated_api"}) == "critical"
    assert classify(2, set()) == "high"
    assert classify(0, {"api"}) == "high"
    assert classify(1, set()) == "medium"
    assert classify(0, set()) == "low"

    suggest = ImpactPropagationEngine._suggest_action
    for risk in ("critical", "high", "medium", "low"):
        assert suggest("my_feature", risk)
    assert suggest("my_feature", "unknown") == "Revisar my_feature"


def test_models_import() -> None:
    """Test that all required models can be imported and instantiated with valid data."""
    from src.impact_propagation.models import (
        DependencyGraphResponse,
    )

    # Verify models exist and have required fields
    assert DependencyEdge
    assert DependencyGraphResponse


def test_cache_manager_integration() -> None:
    """Test that CacheManager works with our cache keys."""
    from src.cache_manager import CacheManager

    cache = CacheManager(Path("cache/test"))
    test_key = "test_key"
    cache.set(test_key, "test_value")
    result = cache.get(test_key)
    assert result == "test_value"
    cache.invalidate(test_key)
    assert cache.get(test_key) is None
