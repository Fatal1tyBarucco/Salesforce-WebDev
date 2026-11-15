"""Tests for src/infrastructure/generation.py — 100% coverage target."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.infrastructure.generation import (
    GenerationAdapter,
    MarkdownGenerationAdapter,
    ReadmeGenerationAdapter,
)
from src.infrastructure.storage import StorageAdapter
from src.models.enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
    ReleaseEnrichment,
)
from src.models.release import ReleaseCategory, ReleaseMetadata


class MockStorageAdapter(StorageAdapter):
    """Mock storage adapter for testing."""

    def __init__(self) -> None:
        self._metadata: dict[str, ReleaseMetadata] = {}
        self._enrichments: dict[str, ReleaseEnrichment] = {}
        self._markdown: dict[tuple[str, str, str], str] = {}

    async def list_releases(self) -> list[str]:
        return list(self._metadata.keys())

    async def load_release_metadata(self, slug: str) -> ReleaseMetadata | None:
        return self._metadata.get(slug)

    async def load_enrichment(self, slug: str) -> ReleaseEnrichment | None:
        return self._enrichments.get(slug)

    async def load_markdown(self, slug: str, category: str, locale: str) -> str | None:
        return self._markdown.get((slug, category, locale))

    async def save_release_metadata(self, metadata: ReleaseMetadata) -> str:
        self._metadata[metadata.slug] = metadata
        return f"releases/{metadata.slug}/.meta.json"

    async def save_enrichment(self, enrichment: ReleaseEnrichment) -> str:
        self._enrichments[enrichment.release_slug] = enrichment
        return f"releases/{enrichment.release_slug}/.enrichment.json"

    async def save_markdown(self, slug: str, category: str, content: str, locale: str) -> str:
        self._markdown[(slug, category, locale)] = content
        return f"releases/{slug}/{category}.{locale}.md"


def _make_release_metadata() -> ReleaseMetadata:
    """Create a sample ReleaseMetadata for testing."""
    return ReleaseMetadata(
        release_id=262,
        slug="summer_26",
        name="Summer '26",
        version="262.0",
        date="2026-05-01",
        total_features=10,
        avg_confidence=0.85,
        generated_at="2026-05-01T10:00:00",
        categories=(
            ReleaseCategory(name="Lightning", count=5, features=("feat1", "feat2")),
            ReleaseCategory(name="Apex", count=5, features=("feat3", "feat4")),
        ),
    )


def _make_enrichment() -> ReleaseEnrichment:
    """Create a sample ReleaseEnrichment for testing."""
    return ReleaseEnrichment(
        release_slug="summer_26",
        locale="pt_BR",
        executive_summary="Resumo executivo de teste.",
        strategic_themes=["Tema 1", "Tema 2"],
        category_enrichments=(
            CategoryEnrichment(
                category_name="Lightning",
                overview="Visão geral do Lightning.",
                key_themes=["Tema Lightning 1"],
                business_impact="Alto impacto no negócio.",
                adoption_guidance="Adotar imediatamente.",
                risk_assessment="Baixo risco.",
                feature_enrichments=(
                    FeatureEnrichment(
                        feature_name="Lightning Feature 1",
                        summary="Resumo da feature.",
                        details="Detalhes completos.",
                        business_context="Contexto de negócio.",
                        technical_context="Contexto técnico.",
                        migration_notes="Notas de migração.",
                        related_features=["Outra feature"],
                    ),
                ),
            ),
            CategoryEnrichment(
                category_name="Apex",
                overview="Visão geral do Apex.",
                key_themes=["Tema Apex 1"],
                business_impact="Médio impacto.",
                adoption_guidance="Planejar adoção.",
                risk_assessment="Médio risco.",
                feature_enrichments=(
                    FeatureEnrichment(
                        feature_name="Apex Feature 1",
                        summary="Resumo da feature Apex.",
                        details="Detalhes Apex.",
                        business_context="Contexto de negócio Apex.",
                        technical_context="Contexto técnico Apex.",
                        migration_notes="Notas de migração Apex.",
                        related_features=[],
                    ),
                ),
            ),
        ),
    )


class TestGenerationAdapter:
    """Tests for the abstract GenerationAdapter base class."""

    @pytest.mark.asyncio
    async def test_abstract_execute_raises_not_implemented(self) -> None:
        """Abstract execute should raise NotImplementedError."""
        adapter = GenerationAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.execute(MagicMock())

    def test_name_property(self) -> None:
        """Base adapter name property."""
        adapter = GenerationAdapter()
        assert adapter.name == "generation_adapter"


class TestMarkdownGenerationAdapter:
    """Tests for MarkdownGenerationAdapter."""

    @pytest.fixture
    def storage(self) -> MockStorageAdapter:
        """Create mock storage with sample data."""
        storage = MockStorageAdapter()
        release = _make_release_metadata()
        storage._metadata["summer_26"] = release
        return storage

    @pytest.fixture
    def enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return _make_enrichment()

    @pytest.fixture
    def adapter(self, storage: MockStorageAdapter) -> MarkdownGenerationAdapter:
        """Create adapter with mock storage."""
        return MarkdownGenerationAdapter(storage)

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: MarkdownGenerationAdapter) -> None:
        """Adapter name should be markdown_generation."""
        assert adapter.name == "markdown_generation"

    @pytest.mark.asyncio
    async def test_execute_raises_when_metadata_missing(
        self, adapter: MarkdownGenerationAdapter, enrichment: ReleaseEnrichment
    ) -> None:
        """Execute should raise ValueError when release metadata not found."""
        # Remove metadata to simulate missing release
        adapter._storage._metadata.clear()

        with pytest.raises(ValueError, match="Release metadata not found"):
            await adapter.execute(enrichment)

    @pytest.mark.asyncio
    async def test_execute_generates_files_for_both_locales(
        self,
        adapter: MarkdownGenerationAdapter,
        enrichment: ReleaseEnrichment,
        storage: MockStorageAdapter,
    ) -> None:
        """Execute should generate markdown files for both pt_BR and en_US locales."""
        generated = await adapter.execute(enrichment)

        # Should generate: RELEASE_NOTES (2 locales) + 2 categories * 2 locales = 6 files
        assert len(generated) == 6

        # Check file paths
        for filepath in generated:
            assert filepath.startswith("releases/summer_26/")
            assert filepath.endswith(".md")

    @pytest.mark.asyncio
    async def test_execute_generates_release_notes_markdown(
        self,
        adapter: MarkdownGenerationAdapter,
        enrichment: ReleaseEnrichment,
        storage: MockStorageAdapter,
    ) -> None:
        """Execute should generate RELEASE_NOTES markdown for each locale."""
        await adapter.execute(enrichment)

        # Check RELEASE_NOTES files were saved
        for locale in ["pt_BR", "en_US"]:
            content = storage._markdown.get(("summer_26", "RELEASE_NOTES", locale))
            assert content is not None
            assert "Summer '26" in content
            assert "Resumo executivo de teste" in content or "Executive summary" in content

    @pytest.mark.asyncio
    async def test_execute_generates_category_markdown(
        self,
        adapter: MarkdownGenerationAdapter,
        enrichment: ReleaseEnrichment,
        storage: MockStorageAdapter,
    ) -> None:
        """Execute should generate per-category markdown for each locale."""
        await adapter.execute(enrichment)

        for locale in ["pt_BR", "en_US"]:
            for cat in ["Lightning", "Apex"]:
                content = storage._markdown.get(("summer_26", cat, locale))
                assert content is not None
                assert cat in content
                assert "Summer '26" in content

    @pytest.mark.asyncio
    async def test_generate_category_markdown_includes_all_sections(
        self, adapter: MarkdownGenerationAdapter
    ) -> None:
        """_generate_category_markdown should include all enrichment sections."""
        release = _make_release_metadata()
        cat_enrichment = _make_enrichment().category_enrichments[0]  # Lightning

        markdown = adapter._generate_category_markdown(release, cat_enrichment, "pt_BR")

        # Check all sections present
        assert "Lightning — Summer '26" in markdown
        assert "**Release:** Summer '26 (`summer_26`)" in markdown
        assert "**Categoria:** Lightning" in markdown
        assert "**Locale:** pt_BR" in markdown
        assert "## Visão Geral" in markdown
        assert "Visão geral do Lightning" in markdown
        assert "## Temas Principais" in markdown
        assert "Tema Lightning 1" in markdown
        assert "## Impacto de Negócio" in markdown
        assert "Alto impacto no negócio" in markdown
        assert "## Orientações de Adoção" in markdown
        assert "Adotar imediatamente" in markdown
        assert "## Avaliação de Risco" in markdown
        assert "Baixo risco" in markdown
        assert "## Features" in markdown
        assert "Lightning Feature 1" in markdown
        assert "**Resumo:** Resumo da feature" in markdown
        assert "**Detalhes:** Detalhes completos" in markdown
        assert "**Contexto de Negócio:** Contexto de negócio" in markdown
        assert "**Contexto Técnico:** Contexto técnico" in markdown
        assert "**Notas de Migração:** Notas de migração" in markdown
        assert "**Features Relacionadas:**" in markdown
        assert "- Outra feature" in markdown
        assert "---" in markdown
        assert "Gerado em" in markdown

    @pytest.mark.asyncio
    async def test_generate_category_markdown_handles_empty_optional_fields(
        self, adapter: MarkdownGenerationAdapter
    ) -> None:
        """_generate_category_markdown should handle missing optional fields gracefully."""
        from src.models.enrichment import CategoryEnrichment, FeatureEnrichment

        release = _make_release_metadata()
        cat_enrichment = CategoryEnrichment(
            category_name="Test",
            overview=None,
            key_themes=None,
            business_impact=None,
            adoption_guidance=None,
            risk_assessment=None,
            feature_enrichments=(
                FeatureEnrichment(
                    feature_name="Test Feature",
                    summary=None,
                    details=None,
                    business_context=None,
                    technical_context=None,
                    migration_notes=None,
                    related_features=None,
                ),
            ),
        )

        markdown = adapter._generate_category_markdown(release, cat_enrichment, "pt_BR")

        # Should not crash and should include the feature name
        assert "Test — Summer '26" in markdown
        assert "Test Feature" in markdown
        # Optional sections should be absent or empty
        assert "Visão geral não disponível" in markdown


class TestReadmeGenerationAdapter:
    """Tests for ReadmeGenerationAdapter."""

    @pytest.fixture
    def storage(self) -> MockStorageAdapter:
        """Create mock storage with sample data."""
        storage = MockStorageAdapter()
        release = _make_release_metadata()
        storage._metadata["summer_26"] = release
        return storage

    @pytest.fixture
    def enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return _make_enrichment()

    @pytest.fixture
    def adapter(self, storage: MockStorageAdapter) -> ReadmeGenerationAdapter:
        """Create adapter with mock storage."""
        return ReadmeGenerationAdapter(storage)

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: ReadmeGenerationAdapter) -> None:
        """Adapter name should be readme_generation."""
        assert adapter.name == "readme_generation"

    @pytest.mark.asyncio
    async def test_execute_returns_empty_when_metadata_missing(
        self,
        adapter: ReadmeGenerationAdapter,
        enrichment: ReleaseEnrichment,
        storage: MockStorageAdapter,
    ) -> None:
        """Execute should return empty list when release metadata not found."""
        storage._metadata.clear()
        result = await adapter.execute(enrichment)
        assert result == []

    @pytest.mark.asyncio
    async def test_execute_generates_readme_summary(
        self,
        adapter: ReadmeGenerationAdapter,
        enrichment: ReleaseEnrichment,
        storage: MockStorageAdapter,
    ) -> None:
        """Execute should generate README summary markdown."""
        result = await adapter.execute(enrichment)

        assert len(result) == 1
        filepath = result[0]
        assert filepath == "releases/summer_26/README_SUMMARY.pt_BR.md"

        content = storage._markdown.get(("summer_26", "README_SUMMARY", "pt_BR"))
        assert content is not None
        assert "Summer '26 — Release Notes Summary" in content
        assert "**Release ID:** 262" in content
        assert "**Slug:** summer_26" in content
        assert "## Resumo Executivo" in content
        assert "Resumo executivo de teste" in content
        assert "## Temas Estratégicos" in content
        assert "- Tema 1" in content
        assert "- Tema 2" in content
        assert "## Categorias" in content
        assert "### Lightning" in content
        assert "Visão geral do Lightning" in content

    @pytest.mark.asyncio
    async def test_execute_handles_empty_enrichment(
        self, adapter: ReadmeGenerationAdapter, storage: MockStorageAdapter
    ) -> None:
        """Execute should handle enrichment with empty optional fields."""
        from src.models.enrichment import CategoryEnrichment, ReleaseEnrichment

        empty_enrichment = ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary=None,
            strategic_themes=[],
            category_enrichments=(
                CategoryEnrichment(
                    category_name="Test",
                    overview="Overview",
                    key_themes=[],
                    business_impact=None,
                    adoption_guidance=None,
                    risk_assessment=None,
                    feature_enrichments=[],
                ),
            ),
        )

        result = await adapter.execute(empty_enrichment)

        assert len(result) == 1
        content = storage._markdown.get(("summer_26", "README_SUMMARY", "pt_BR"))
        assert content is not None
        assert "Resumo não disponível" in content
