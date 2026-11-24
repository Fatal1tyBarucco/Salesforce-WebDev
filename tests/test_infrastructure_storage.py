"""Tests for src/infrastructure/storage.py — 100% coverage target."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.storage import (
    FileSystemStorageAdapter,
    GitHubStorageAdapter,
    StorageAdapter,
)
from src.models.enrichment import (
    CategoryEnrichment,
    FeatureEnrichment,
    ReleaseEnrichment,
)
from src.models.release import ReleaseMetadata


class TestStorageAdapter:
    """Tests for the abstract StorageAdapter base class."""

    @pytest.mark.asyncio
    async def test_abstract_methods_raise_not_implemented(self) -> None:
        """All abstract methods should raise NotImplementedError."""
        adapter = StorageAdapter()

        with pytest.raises(NotImplementedError):
            await adapter.save_release_metadata(MagicMock())

        with pytest.raises(NotImplementedError):
            await adapter.load_release_metadata("test")

        with pytest.raises(NotImplementedError):
            await adapter.save_enrichment(MagicMock())

        with pytest.raises(NotImplementedError):
            await adapter.load_enrichment("test")

        with pytest.raises(NotImplementedError):
            await adapter.save_markdown("slug", "cat", "content", "pt_BR")

        with pytest.raises(NotImplementedError):
            await adapter.load_markdown("slug", "cat", "pt_BR")

        with pytest.raises(NotImplementedError):
            await adapter.list_releases()


class TestFileSystemStorageAdapter:
    """Tests for FileSystemStorageAdapter."""

    @pytest.fixture
    def temp_dir(self) -> str:
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def adapter(self, temp_dir: str) -> FileSystemStorageAdapter:
        """Create filesystem storage adapter."""
        return FileSystemStorageAdapter(base_dir=temp_dir)

    @pytest.fixture
    def sample_release(self) -> ReleaseMetadata:
        """Create sample release metadata."""
        return ReleaseMetadata(
            release_id=60,
            slug="summer_26",
            name="Summer '26",
            version="60.0",
            date="2026-06-01",
        )

    @pytest.fixture
    def sample_enrichment(self) -> ReleaseEnrichment:
        """Create sample enrichment."""
        return ReleaseEnrichment(
            release_slug="summer_26",
            locale="pt_BR",
            executive_summary="Resumo executivo.",
            strategic_themes=("Tema 1", "Tema 2"),
            category_enrichments=(
                CategoryEnrichment(
                    category_name="Lightning",
                    overview="Visão geral do Lightning.",
                    key_themes=("Tema Lightning",),
                    business_impact="Alto impacto",
                    adoption_guidance="Adotar agora",
                    risk_assessment="Baixo risco",
                    feature_enrichments=(
                        FeatureEnrichment(
                            feature_name="Lightning Feature",
                            summary="Resumo da feature",
                            details="Detalhes completos",
                            business_context="Contexto negócio",
                            technical_context="Contexto técnico",
                            migration_notes="Notas migração",
                            related_features=("Outra feature",),
                            tags=("tag1",),
                            confidence=0.9,
                            locale="pt_BR",
                            generated_at="2026-05-01T10:00:00",
                        ),
                    ),
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            migration_checklist=("Verificar deploy", "Testar funcionalidade"),
            generated_at="2026-05-01T10:00:00",
        )

    @pytest.mark.asyncio
    async def test_init_creates_base_directory(self, temp_dir: str) -> None:
        """Should create base directory on initialization."""
        new_dir = Path(temp_dir) / "new_releases"
        _ = FileSystemStorageAdapter(base_dir=str(new_dir))

        assert new_dir.exists()

    @pytest.mark.asyncio
    async def test_save_and_load_release_metadata(
        self,
        adapter: FileSystemStorageAdapter,
        sample_release: ReleaseMetadata,
    ) -> None:
        """Should save and load release metadata."""
        await adapter.save_release_metadata(sample_release)

        loaded = await adapter.load_release_metadata("summer_26")

        assert loaded is not None
        assert loaded.slug == "summer_26"
        assert loaded.name == "Summer '26"
        assert loaded.version == "60.0"
        assert loaded.date == "2026-06-01"
        assert loaded.release_id == 60

    @pytest.mark.asyncio
    async def test_load_nonexistent_release_metadata(
        self, adapter: FileSystemStorageAdapter
    ) -> None:
        """Should return None for nonexistent release."""
        loaded = await adapter.load_release_metadata("nonexistent")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_load_release_metadata_handles_corrupted_json(
        self, adapter: FileSystemStorageAdapter
    ) -> None:
        """Should handle corrupted JSON gracefully."""
        # Create corrupted metadata file
        release_dir = Path(adapter.base_dir) / "corrupted"
        release_dir.mkdir(parents=True)
        meta_path = release_dir / ".meta.json"
        meta_path.write_text("{ invalid json", encoding="utf-8")

        loaded = await adapter.load_release_metadata("corrupted")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_save_and_load_enrichment(
        self,
        adapter: FileSystemStorageAdapter,
        sample_enrichment: ReleaseEnrichment,
    ) -> None:
        """Should save and load enrichment."""
        await adapter.save_enrichment(sample_enrichment)

        loaded = await adapter.load_enrichment("summer_26")

        assert loaded is not None
        assert loaded.release_slug == "summer_26"
        assert loaded.locale == "pt_BR"
        assert loaded.executive_summary == "Resumo executivo."
        assert loaded.strategic_themes == ("Tema 1", "Tema 2")
        assert len(loaded.category_enrichments) == 1
        assert loaded.category_enrichments[0].category_name == "Lightning"
        assert loaded.migration_checklist == (
            "Verificar deploy",
            "Testar funcionalidade",
        )

    @pytest.mark.asyncio
    async def test_load_nonexistent_enrichment(self, adapter: FileSystemStorageAdapter) -> None:
        """Should return None for nonexistent enrichment."""
        loaded = await adapter.load_enrichment("nonexistent")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_load_enrichment_handles_corrupted_json(
        self, adapter: FileSystemStorageAdapter
    ) -> None:
        """Should handle corrupted enrichment JSON gracefully."""
        release_dir = Path(adapter.base_dir) / "corrupted"
        release_dir.mkdir(parents=True)
        enrichment_path = release_dir / ".enrichment.json"
        enrichment_path.write_text("{ invalid json", encoding="utf-8")

        loaded = await adapter.load_enrichment("corrupted")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_save_and_load_markdown(self, adapter: FileSystemStorageAdapter) -> None:
        """Should save and load markdown files."""
        content = "# Lightning\n\nNova feature do Lightning."
        category = "Lightning"
        locale = "pt_BR"

        path = await adapter.save_markdown("summer_26", category, content, locale)

        assert Path(path).exists()
        assert "Lightning.pt_BR.md" in path

        loaded = await adapter.load_markdown("summer_26", category, locale)
        assert loaded == content

    @pytest.mark.asyncio
    async def test_load_nonexistent_markdown(self, adapter: FileSystemStorageAdapter) -> None:
        """Should return None for nonexistent markdown."""
        loaded = await adapter.load_markdown("summer_26", "NonExistent", "pt_BR")
        assert loaded is None

    @pytest.mark.asyncio
    async def test_save_markdown_sanitizes_category_name(
        self, adapter: FileSystemStorageAdapter
    ) -> None:
        """Should sanitize category name in filename."""
        content = "Test content"
        category = "Category/With Spaces & Symbols"
        locale = "pt_BR"

        path = await adapter.save_markdown("summer_26", category, content, locale)

        # Should replace spaces, slashes with underscores (but keeps &)
        assert "Category_With_Spaces_&_Symbols.pt_BR.md" in path

    @pytest.mark.asyncio
    async def test_list_releases(
        self, adapter: FileSystemStorageAdapter, sample_release: ReleaseMetadata
    ) -> None:
        """Should list all release slugs."""
        # Save multiple releases
        await adapter.save_release_metadata(sample_release)

        release2 = ReleaseMetadata(
            release_id=61,
            slug="winter_26",
            name="Winter '26",
            version="61.0",
            date="2026-10-01",
        )
        await adapter.save_release_metadata(release2)

        slugs = await adapter.list_releases()

        assert "summer_26" in slugs
        assert "winter_26" in slugs
        assert len(slugs) == 2
        assert slugs == sorted(slugs)

    @pytest.mark.asyncio
    async def test_list_releases_empty_directory(self, adapter: FileSystemStorageAdapter) -> None:
        """Should return empty list for empty directory."""
        slugs = await adapter.list_releases()
        assert slugs == []

    @pytest.mark.asyncio
    async def test_list_releases_ignores_non_release_dirs(
        self, adapter: FileSystemStorageAdapter, sample_release: ReleaseMetadata
    ) -> None:
        """Should ignore directories without .meta.json."""
        await adapter.save_release_metadata(sample_release)

        # Create a directory without .meta.json
        (Path(adapter.base_dir) / "not_a_release").mkdir()

        slugs = await adapter.list_releases()
        assert slugs == ["summer_26"]

    @pytest.mark.asyncio
    async def test_delete_release(
        self, adapter: FileSystemStorageAdapter, sample_release: ReleaseMetadata
    ) -> None:
        """Should delete release directory."""
        await adapter.save_release_metadata(sample_release)
        assert await adapter.load_release_metadata("summer_26") is not None

        result = await adapter.delete_release("summer_26")

        assert result is True
        assert await adapter.load_release_metadata("summer_26") is None
        assert not (Path(adapter.base_dir) / "summer_26").exists()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_release(self, adapter: FileSystemStorageAdapter) -> None:
        """Should return False for nonexistent release."""
        result = await adapter.delete_release("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_release_dir_path(self, adapter: FileSystemStorageAdapter) -> None:
        """_release_dir should return correct path."""
        path = adapter._release_dir("test_slug")
        assert path == Path(adapter.base_dir) / "test_slug"

    @pytest.mark.asyncio
    async def test_meta_path(self, adapter: FileSystemStorageAdapter) -> None:
        """_meta_path should return correct path."""
        path = adapter._meta_path("test_slug")
        assert path == Path(adapter.base_dir) / "test_slug" / ".meta.json"

    @pytest.mark.asyncio
    async def test_enrichment_path(self, adapter: FileSystemStorageAdapter) -> None:
        """_enrichment_path should return correct path."""
        path = adapter._enrichment_path("test_slug")
        assert path == Path(adapter.base_dir) / "test_slug" / ".enrichment.json"

    @pytest.mark.asyncio
    async def test_markdown_path(self, adapter: FileSystemStorageAdapter) -> None:
        """_markdown_path should return correct path."""
        path = adapter._markdown_path("test_slug", "Category", "pt_BR")
        assert path == Path(adapter.base_dir) / "test_slug" / "Category.pt_BR.md"


class TestGitHubStorageAdapter:
    """Tests for GitHubStorageAdapter."""

    @pytest.fixture
    def adapter(self) -> GitHubStorageAdapter:
        """Create GitHub storage adapter."""
        return GitHubStorageAdapter(
            repo="owner/repo",
            token="test_token",
            branch="main",
            base_path="releases",
        )

    def test_init_sets_properties(self, adapter: GitHubStorageAdapter) -> None:
        """Should initialize with correct properties."""
        assert adapter.repo == "owner/repo"
        assert adapter.token == "test_token"
        assert adapter.branch == "main"
        assert adapter.base_path == "releases"
        assert adapter._client is None

    def test_init_uses_env_token_when_not_provided(self) -> None:
        """Should use GITHUB_TOKEN from environment when not provided."""
        with patch.dict("os.environ", {"GITHUB_TOKEN": "env_token"}):
            adapter = GitHubStorageAdapter(repo="owner/repo")
            assert adapter.token == "env_token"

    def test_get_client_creates_github_client(self, adapter: GitHubStorageAdapter) -> None:
        """_get_client should create Github client."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_github.return_value = mock_client

            # _get_client is sync, not async
            client = adapter._get_client()

            assert client is mock_client
            mock_github.assert_called_once_with("test_token")

    def test_get_client_caches_client(self, adapter: GitHubStorageAdapter) -> None:
        """_get_client should cache the client."""
        with patch("github.Github") as mock_github:
            mock_client = MagicMock()
            mock_github.return_value = mock_client

            client1 = adapter._get_client()
            client2 = adapter._get_client()

            assert client1 is client2
            mock_github.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_release_metadata_raises_not_implemented(
        self, adapter: GitHubStorageAdapter
    ) -> None:
        """save_release_metadata should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await adapter.save_release_metadata(MagicMock())

    @pytest.mark.asyncio
    async def test_load_release_metadata_raises_not_implemented(
        self, adapter: GitHubStorageAdapter
    ) -> None:
        """load_release_metadata should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await adapter.load_release_metadata("test")

    @pytest.mark.asyncio
    async def test_save_enrichment_raises_not_implemented(
        self, adapter: GitHubStorageAdapter
    ) -> None:
        """save_enrichment should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await adapter.save_enrichment(MagicMock())

    @pytest.mark.asyncio
    async def test_load_enrichment_raises_not_implemented(
        self, adapter: GitHubStorageAdapter
    ) -> None:
        """load_enrichment should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await adapter.load_enrichment("test")

    @pytest.mark.asyncio
    async def test_save_markdown_raises_not_implemented(
        self, adapter: GitHubStorageAdapter
    ) -> None:
        """save_markdown should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await adapter.save_markdown("slug", "cat", "content", "pt_BR")

    @pytest.mark.asyncio
    async def test_list_releases_raises_not_implemented(
        self, adapter: GitHubStorageAdapter
    ) -> None:
        """list_releases should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            await adapter.list_releases()
