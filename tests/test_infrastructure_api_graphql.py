"""Tests for src/infrastructure/api/graphql.py — coverage target."""

from __future__ import annotations

from collections.abc import Callable

import pytest

import src.infrastructure.api as api_package
from src.infrastructure.api import graphql as graphql_module
from src.infrastructure.api.graphql import (
    CategoryFeaturesType,
    DiffType,
    Query,
    ReleaseType,
    schema,
)
from src.infrastructure.storage import FileSystemStorageAdapter
from src.models.release import ReleaseCategory, ReleaseMetadata


def _metadata(
    slug: str,
    *,
    release_id: int = 60,
    total_features: int = 10,
    categories: tuple[ReleaseCategory, ...] | None = None,
) -> ReleaseMetadata:
    """Build a ReleaseMetadata with GraphQL-relevant fields populated."""
    if categories is None:
        categories = (
            ReleaseCategory(name="Apex", count=5, features=("feat-a", "feat-b")),
            ReleaseCategory(name="Flow", count=5, features=("feat-c",)),
        )
    return ReleaseMetadata(
        release_id=release_id,
        slug=slug,
        name=slug.replace("_", " ").title(),
        version="60.0",
        date="2026-06-01",
        total_features=total_features,
        avg_confidence=0.9,
        generated_at="2026-05-01T10:00:00",
        categories=categories,
    )


class FakeStorage:
    """In-memory stand-in for StorageAdapter used by the GraphQL resolvers."""

    def __init__(self, releases: dict[str, ReleaseMetadata | None]) -> None:
        self._releases = releases

    async def list_releases(self) -> list[str]:
        return list(self._releases)

    async def load_release_metadata(self, slug: str) -> ReleaseMetadata | None:
        return self._releases.get(slug)


@pytest.fixture
def install_storage(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[dict[str, ReleaseMetadata | None]], FakeStorage]:
    """Patch ``graphql.get_storage`` so resolvers use a controllable fake."""

    def _install(releases: dict[str, ReleaseMetadata | None]) -> FakeStorage:
        fake = FakeStorage(releases)

        async def _get_storage() -> FakeStorage:
            return fake

        monkeypatch.setattr(graphql_module, "get_storage", _get_storage)
        return fake

    return _install


class TestGetStorage:
    """Tests for the storage dependency provider."""

    @pytest.mark.asyncio
    async def test_get_storage_returns_filesystem_adapter(self) -> None:
        """Real provider should build a FileSystemStorageAdapter."""
        storage = await graphql_module.get_storage()
        assert isinstance(storage, FileSystemStorageAdapter)


class TestReleasesResolver:
    """Tests for Query.releases."""

    @pytest.mark.asyncio
    async def test_releases_maps_all_metadata(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Should map every stored release into a ReleaseType."""
        install_storage(
            {
                "summer_26": _metadata("summer_26"),
                "spring_26": _metadata("spring_26", release_id=59, total_features=8),
            }
        )

        result = await Query().releases()

        assert len(result) == 2
        first = result[0]
        assert isinstance(first, ReleaseType)
        assert first.slug == "summer_26"
        assert first.release_id == 60
        assert first.total_features == 10
        assert first.avg_confidence == 0.9
        assert [c.name for c in first.categories] == ["Apex", "Flow"]
        assert first.categories[0].features == ["feat-a", "feat-b"]

    @pytest.mark.asyncio
    async def test_releases_empty_store(self, install_storage: Callable[..., FakeStorage]) -> None:
        """Empty store should yield an empty list."""
        install_storage({})

        assert await Query().releases() == []

    @pytest.mark.asyncio
    async def test_releases_skips_missing_metadata(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Slugs without metadata should be skipped."""
        install_storage({"summer_26": _metadata("summer_26"), "ghost_26": None})

        result = await Query().releases()

        assert [r.slug for r in result] == ["summer_26"]

    @pytest.mark.asyncio
    async def test_releases_release_without_categories(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """A release with no categories should map to an empty category list."""
        install_storage({"bare_26": _metadata("bare_26", categories=())})

        result = await Query().releases()

        assert len(result) == 1
        assert result[0].categories == []


class TestReleaseResolver:
    """Tests for Query.release."""

    @pytest.mark.asyncio
    async def test_release_found(self, install_storage: Callable[..., FakeStorage]) -> None:
        """Existing slug should return a fully mapped ReleaseType."""
        install_storage({"summer_26": _metadata("summer_26")})

        result = await Query().release(slug="summer_26")

        assert result is not None
        assert isinstance(result, ReleaseType)
        assert result.slug == "summer_26"
        assert result.name == "Summer 26"
        assert len(result.categories) == 2

    @pytest.mark.asyncio
    async def test_release_missing(self, install_storage: Callable[..., FakeStorage]) -> None:
        """Unknown slug should return None."""
        install_storage({})

        assert await Query().release(slug="nope") is None


class TestDiffResolver:
    """Tests for Query.diff."""

    @pytest.mark.asyncio
    async def test_diff_computes_category_deltas(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Should compare category counts between two releases."""
        current = _metadata(
            "summer_26",
            total_features=20,
            categories=(
                ReleaseCategory(name="Apex", count=8, features=("f1",)),
                ReleaseCategory(name="Flow", count=12, features=("f2",)),
            ),
        )
        previous = _metadata(
            "spring_26",
            release_id=59,
            total_features=15,
            categories=(
                ReleaseCategory(name="Apex", count=5, features=("f1",)),
                ReleaseCategory(name="Einstein", count=10, features=("f3",)),
            ),
        )
        install_storage({"summer_26": current, "spring_26": previous})

        result = await Query().diff(current="summer_26", previous="spring_26")

        assert isinstance(result, DiffType)
        assert result.total_delta == 5
        changes = {c.category: c.delta for c in result.changes}
        assert changes == {"Apex": 3, "Einstein": -10, "Flow": 12}

    @pytest.mark.asyncio
    async def test_diff_no_categories_on_either_side(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Releases without categories should produce zero changes."""
        install_storage(
            {
                "summer_26": _metadata("summer_26", categories=()),
                "spring_26": _metadata("spring_26", release_id=59, categories=()),
            }
        )

        result = await Query().diff(current="summer_26", previous="spring_26")

        assert result is not None
        assert result.changes == []
        assert result.total_delta == 0

    @pytest.mark.asyncio
    async def test_diff_missing_current(self, install_storage: Callable[..., FakeStorage]) -> None:
        """Missing current release should return None."""
        install_storage({"spring_26": _metadata("spring_26", release_id=59)})

        assert await Query().diff(current="ghost", previous="spring_26") is None

    @pytest.mark.asyncio
    async def test_diff_missing_previous(self, install_storage: Callable[..., FakeStorage]) -> None:
        """Missing previous release should return None."""
        install_storage({"summer_26": _metadata("summer_26")})

        assert await Query().diff(current="summer_26", previous="ghost") is None


class TestCategoryFeaturesResolver:
    """Tests for Query.category_features."""

    @pytest.mark.asyncio
    async def test_category_features_found(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Existing category should return its feature list."""
        install_storage({"summer_26": _metadata("summer_26")})

        result = await Query().category_features(slug="summer_26", category="Apex")

        assert isinstance(result, CategoryFeaturesType)
        assert result.category == "Apex"
        assert result.features == ["feat-a", "feat-b"]

    @pytest.mark.asyncio
    async def test_category_features_unknown_category(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Unknown category should return None."""
        install_storage({"summer_26": _metadata("summer_26")})

        assert await Query().category_features(slug="summer_26", category="Nope") is None

    @pytest.mark.asyncio
    async def test_category_features_missing_release(
        self, install_storage: Callable[..., FakeStorage]
    ) -> None:
        """Missing release should return None."""
        install_storage({})

        assert await Query().category_features(slug="ghost", category="Apex") is None


class TestSchemaAndExports:
    """Tests for the module-level schema and lazy package exports."""

    def test_schema_exposes_query_fields(self) -> None:
        """Strawberry schema should expose the documented root fields."""
        assert schema.query is Query
        sdl = schema.as_str()
        assert "type Query {" in sdl
        assert "releases: [ReleaseType!]!" in sdl
        assert "release(slug: String!): ReleaseType" in sdl
        assert "diff(current: String!, previous: String!): DiffType" in sdl
        assert "categoryFeatures(slug: String!, category: String!)" in sdl

    def test_graphql_router_lazy_export(self) -> None:
        """Package should expose graphql_router via PEP 562 __getattr__."""
        from src.infrastructure.api import graphql_router

        assert graphql_router is graphql_module.graphql_router
        assert type(graphql_router).__name__ == "GraphQLRouter"

    def test_unknown_package_attribute_raises(self) -> None:
        """Unknown attributes should raise AttributeError from __getattr__."""
        with pytest.raises(AttributeError, match="nope"):
            _ = api_package.nope
