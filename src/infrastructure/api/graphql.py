"""GraphQL API schema and resolvers.

Provides a GraphQL endpoint for flexible querying of release data.
"""

from __future__ import annotations

import logging

import strawberry
from strawberry.fastapi import GraphQLRouter

from src.infrastructure.storage import FileSystemStorageAdapter, StorageAdapter

logger = logging.getLogger(__name__)


# Strawberry types
@strawberry.type
class FeatureCategoryType:
    name: str
    count: int
    features: list[str]


@strawberry.type
class ReleaseType:
    release_id: int
    slug: str
    name: str
    version: str
    date: str
    total_features: int
    avg_confidence: float
    generated_at: str
    categories: list[FeatureCategoryType]


@strawberry.type
class ChangeType:
    category: str
    delta: int


@strawberry.type
class DiffType:
    total_delta: int
    changes: list[ChangeType]


@strawberry.type
class CategoryFeaturesType:
    category: str
    features: list[str]


# Dependency
async def get_storage() -> StorageAdapter:
    return FileSystemStorageAdapter()


# Resolvers
@strawberry.type
class Query:
    @strawberry.field  # type: ignore
    async def releases(self) -> list[ReleaseType]:
        """List all releases."""
        storage = await get_storage()
        slugs = await storage.list_releases()
        result = []

        for slug in slugs:
            metadata = await storage.load_release_metadata(slug)
            if metadata:
                result.append(
                    ReleaseType(  # type: ignore[call-arg]
                        release_id=metadata.release_id,
                        slug=metadata.slug,
                        name=metadata.name,
                        version=metadata.version,
                        date=metadata.date,
                        total_features=metadata.total_features,
                        avg_confidence=metadata.avg_confidence,
                        generated_at=metadata.generated_at,
                        categories=[
                            FeatureCategoryType(  # type: ignore[call-arg]
                                name=c.name,
                                count=c.count,
                                features=list(c.features),
                            )
                            for c in metadata.categories
                        ],
                    )
                )

        return result

    @strawberry.field  # type: ignore
    async def release(self, slug: str) -> ReleaseType | None:
        """Get a single release by slug."""
        storage = await get_storage()
        metadata = await storage.load_release_metadata(slug)
        if not metadata:
            return None

        return ReleaseType(  # type: ignore[call-arg]
            release_id=metadata.release_id,
            slug=metadata.slug,
            name=metadata.name,
            version=metadata.version,
            date=metadata.date,
            total_features=metadata.total_features,
            avg_confidence=metadata.avg_confidence,
            generated_at=metadata.generated_at,
            categories=[
                FeatureCategoryType(  # type: ignore[call-arg]
                    name=c.name,
                    count=c.count,
                    features=list(c.features),
                )
                for c in metadata.categories
            ],
        )

    @strawberry.field  # type: ignore
    async def diff(self, current: str, previous: str) -> DiffType | None:
        """Get diff between two releases."""
        storage = await get_storage()
        cur_meta = await storage.load_release_metadata(current)
        prev_meta = await storage.load_release_metadata(previous)

        if not cur_meta or not prev_meta:
            return None

        cur_cats = {c.name: c.count for c in cur_meta.categories}
        prev_cats = {c.name: c.count for c in prev_meta.categories}
        all_cats = sorted(set(cur_cats) | set(prev_cats))

        changes = [
            ChangeType(  # type: ignore[call-arg]
                category=name,
                delta=cur_cats.get(name, 0) - prev_cats.get(name, 0),
            )
            for name in all_cats
        ]

        return DiffType(  # type: ignore[call-arg]
            total_delta=cur_meta.total_features - prev_meta.total_features,
            changes=changes,
        )

    @strawberry.field  # type: ignore
    async def category_features(self, slug: str, category: str) -> CategoryFeaturesType | None:
        """Get features for a specific category in a release."""
        storage = await get_storage()
        metadata = await storage.load_release_metadata(slug)
        if not metadata:
            return None

        cat = next((c for c in metadata.categories if c.name == category), None)
        if not cat:
            return None

        return CategoryFeaturesType(  # type: ignore[call-arg]
            category=category,
            features=list(cat.features),
        )


# Create schema
schema = strawberry.Schema(query=Query)

# Create GraphQL router
graphql_router = GraphQLRouter(schema, path="/graphql")
