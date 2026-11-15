"""REST API routes — FastAPI router factory.

Creates the REST API endpoints for the Salesforce WebDev service.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from src.core.classification.service import (
    ClassificationConfig,
    ClassificationService,
    ClassificationStrategy,
)
from src.core.summarization.service import SummarizationService
from src.infrastructure.llm import HeuristicClassificationAdapter
from src.infrastructure.storage import FileSystemStorageAdapter, StorageAdapter
from src.models.api import (
    DiffResponse,
    FeatureCategory,
    FeatureClassificationRequest,
    FeatureClassificationResponse,
    ReleaseResponse,
)

logger = logging.getLogger(__name__)

# Dependency providers
_storage_adapter: StorageAdapter | None = None
_classification_service: ClassificationService | None = None
_summarization_service: SummarizationService | None = None


def get_storage() -> StorageAdapter:
    """Get storage adapter instance."""
    global _storage_adapter
    if _storage_adapter is None:
        _storage_adapter = FileSystemStorageAdapter()
    return _storage_adapter


def get_classification_service() -> ClassificationService:
    """Get classification service instance."""
    global _classification_service
    if _classification_service is None:
        heuristic = HeuristicClassificationAdapter()
        config = ClassificationConfig(strategy=ClassificationStrategy.HEURISTIC)
        _classification_service = ClassificationService(
            config=config,
            heuristic_adapter=heuristic,
        )
    return _classification_service


def get_summarization_service() -> SummarizationService:
    """Get summarization service instance."""
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service


# Request/Response models
class ReleaseListResponse(BaseModel):
    releases: list[ReleaseResponse]


class EnrichmentResponse(BaseModel):
    release_slug: str
    executive_summary: str
    strategic_themes: list[str]
    categories: list[dict[str, Any]]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str = "2.0.0"


# Create router
def create_rest_router() -> APIRouter:
    """Create and configure the REST API router."""
    router = APIRouter(prefix="/api/v1", tags=["Salesforce WebDev"])

    # Health check
    @router.get("/health", response_model=HealthResponse)  # type: ignore
    async def health_check() -> HealthResponse:
        return HealthResponse(status="ok", service="salesforce-webdev")

    # Release endpoints
    @router.get("/releases", response_model=ReleaseListResponse)  # type: ignore
    async def list_releases(
        storage: StorageAdapter = Depends(get_storage),  # noqa: B008
    ) -> ReleaseListResponse:
        """List all available releases."""
        slugs = await storage.list_releases()
        releases = []

        for slug in slugs:
            metadata = await storage.load_release_metadata(slug)
            if metadata:
                releases.append(
                    ReleaseResponse(
                        name=metadata.name,
                        slug=metadata.slug,
                        release_id=metadata.release_id,
                        total_features=metadata.total_features,
                        avg_confidence=metadata.avg_confidence,
                        generated_at=metadata.generated_at,
                        categories=[
                            FeatureCategory(name=c.name, count=c.count) for c in metadata.categories
                        ],
                    )
                )

        return ReleaseListResponse(releases=releases)

    # Diff endpoint - must come before /releases/{slug} to avoid path conflict
    @router.get("/releases/diff", response_model=DiffResponse)  # type: ignore
    async def get_diff(
        current: str = Query(..., description="Current release slug"),
        previous: str = Query(..., description="Previous release slug"),
        storage: StorageAdapter = Depends(get_storage),  # noqa: B008
    ) -> DiffResponse:
        """Get diff between two releases."""
        cur_meta = await storage.load_release_metadata(current)
        prev_meta = await storage.load_release_metadata(previous)

        if not cur_meta or not prev_meta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or both releases not found",
            )

        cur_cats = {c.name: c.count for c in cur_meta.categories}
        prev_cats = {c.name: c.count for c in prev_meta.categories}
        all_cats = sorted(set(cur_cats) | set(prev_cats))

        changes = [
            {"category": name, "delta": cur_cats.get(name, 0) - prev_cats.get(name, 0)}
            for name in all_cats
        ]

        return DiffResponse(
            current=cur_meta.name,
            previous=prev_meta.name,
            total_delta=cur_meta.total_features - prev_meta.total_features,
            categories=[],
            changes=changes,
        )

    @router.get("/releases/{slug}", response_model=ReleaseResponse)  # type: ignore
    async def get_release(
        slug: str,
        storage: StorageAdapter = Depends(get_storage),  # noqa: B008
    ) -> ReleaseResponse:
        """Get release metadata by slug."""
        metadata = await storage.load_release_metadata(slug)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Release '{slug}' not found",
            )

        return ReleaseResponse(
            name=metadata.name,
            slug=metadata.slug,
            release_id=metadata.release_id,
            total_features=metadata.total_features,
            avg_confidence=metadata.avg_confidence,
            generated_at=metadata.generated_at,
            categories=[FeatureCategory(name=c.name, count=c.count) for c in metadata.categories],
        )

    @router.get("/releases/{slug}/enrichment", response_model=EnrichmentResponse)  # type: ignore
    async def get_enrichment(
        slug: str,
        storage: StorageAdapter = Depends(get_storage),  # noqa: B008
    ) -> EnrichmentResponse:
        """Get AI enrichment for a release."""
        enrichment = await storage.load_enrichment(slug)
        if not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Enrichment for '{slug}' not found",
            )

        return EnrichmentResponse(
            release_slug=enrichment.release_slug,
            executive_summary=enrichment.executive_summary,
            strategic_themes=list(enrichment.strategic_themes),
            categories=[c.to_dict() for c in enrichment.category_enrichments],
        )

    @router.get("/releases/{slug}/markdown/{category}")  # type: ignore
    async def get_markdown(
        slug: str,
        category: str,
        locale: str = Query("pt_BR", pattern="^(pt_BR|en_US)$"),
        storage: StorageAdapter = Depends(get_storage),  # noqa: B008
    ) -> dict[str, str]:
        """Get markdown content for a category."""
        content = await storage.load_markdown(slug, category, locale)
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Markdown for '{category}' in '{locale}' not found",
            )

        return {"slug": slug, "category": category, "locale": locale, "content": content}

    # Classification endpoint
    @router.post("/classify", response_model=FeatureClassificationResponse)  # type: ignore
    async def classify_feature(
        request: FeatureClassificationRequest,
        service: ClassificationService = Depends(get_classification_service),  # noqa: B008
    ) -> FeatureClassificationResponse:
        """Classify a single feature text."""
        result = await service.classify_single(request.text)

        return FeatureClassificationResponse(
            impact=result.impact.value,
            type=result.feature_type.value,
            confidence=result.confidence,
        )

    # Summarization endpoint
    @router.post("/summarize")  # type: ignore
    async def summarize_release(
        release_slug: str = Query(..., description="Release slug to summarize"),
        storage: StorageAdapter = Depends(get_storage),  # noqa: B008
        service: SummarizationService = Depends(get_summarization_service),  # noqa: B008
    ) -> dict[str, str]:
        """Generate release notes summary."""
        metadata = await storage.load_release_metadata(release_slug)
        enrichment = await storage.load_enrichment(release_slug)

        if not metadata or not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Release or enrichment not found",
            )

        markdown = service.generate_release_notes_markdown(metadata, enrichment)
        return {"release_slug": release_slug, "markdown": markdown}

    return router


# For backward compatibility with existing code
app_router = create_rest_router()
