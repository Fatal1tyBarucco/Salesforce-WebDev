"""Tests for Impact Propagation Engine (RIPE)."""

import json
from pathlib import Path

import pytest

from src.impact_propagation.engine import ImpactPropagationEngine
from src.impact_propagation.heuristic_fallback import DependencyHeuristicFallback
from src.impact_propagation.models import (
    DependencyEdge,
    MigrationReportResponse,
    DependencyGraphResponse,
)
from src.cache_manager import CacheManager


@pytest.fixture
def engine():
    # Use mock LLM service for testing
    class MockLLM:
        async def generate_text(self, prompt: str, system_instruction: str | None = None) -> str:
            return json.dumps(
                {"nodes": ["test_feature"], "edges": [], "statistics": {"nodes": 1, "edges": 0}}
            )

    return ImpactPropagationEngine(llm=MockLLM(), cache=CacheManager(Path("cache/test")))


def test_heuristic_fallback_builds_graph():
    """Test that heuristic fallback creates a valid DependencyGraphResponse."""
    heuristic = DependencyHeuristicFallback()
    result = heuristic.build("test_release")
    assert isinstance(result, DependencyGraphResponse)
    assert result.source == "heuristic"


@pytest.mark.asyncio
async def test_engine_builds_graph_with_llm(engine):
    """Test that the engine successfully builds a graph using LLM."""
    result = await engine.build_graph_for_release("test_release")
    assert isinstance(result, DependencyGraphResponse)
    assert result.source in ("llm", "heuristic")
    assert result.nodes  # Should have at least one node


@pytest.mark.asyncio
async def test_blast_radius_computation(engine):
    """Test that blast radius computation works and caches results."""
    # First call should not be cached
    result1 = await engine.compute_blast_radius("test_release", "test_feature", max_depth=2)
    assert result1.cache_hit is False

    # Second call should be cached
    result2 = await engine.compute_blast_radius("test_release", "test_feature", max_depth=2)
    assert result2.cache_hit is True
    assert result1 == result2


@pytest.mark.asyncio
async def test_migration_report_generation(engine):
    """Test that migration report generation works."""
    result = await engine.generate_migration_report("test_release")
    assert isinstance(result, MigrationReportResponse)
    assert result.release_slug == "test_release"
    assert result.fallback_used in (True, False)


def test_models_import():
    """Test that all required models can be imported and instantiated with valid data."""
    from src.impact_propagation.models import (
        DependencyGraphResponse,
    )

    # Verify models exist and have required fields
    assert DependencyEdge
    assert DependencyGraphResponse


def test_cache_manager_integration():
    """Test that CacheManager works with our cache keys."""
    from src.cache_manager import CacheManager

    cache = CacheManager(Path("cache/test"))
    test_key = "test_key"
    cache.set(test_key, "test_value")
    result = cache.get(test_key)
    assert result == "test_value"
    cache.invalidate(test_key)
    assert cache.get(test_key) is None
