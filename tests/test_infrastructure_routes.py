"""Tests for src/infrastructure/api/routes.py — 100% coverage target."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.infrastructure.api.routes import (
    EnrichmentResponse,
    HealthResponse,
    ReleaseListResponse,
    ReleaseResponse,
    create_rest_router,
    get_classification_service,
    get_storage,
    get_summarization_service,
)
from src.models.api import FeatureCategory
from src.models.enrichment import CategoryEnrichment, ReleaseEnrichment
from src.models.release import ReleaseMetadata


class TestDependencyProviders:
    """Tests for dependency provider functions."""

    def setup_method(self) -> None:
        """Reset global instances before each test."""
        import src.infrastructure.api.routes as routes_module

        routes_module._storage_adapter = None
        routes_module._classification_service = None
        routes_module._summarization_service = None

    @pytest.mark.asyncio
    async def test_get_storage_creates_instance(self) -> None:
        """Should create FileSystemStorageAdapter on first call."""
        storage = get_storage()
        assert storage is not None
        # Second call should return same instance
        storage2 = get_storage()
        assert storage is storage2

    @pytest.mark.asyncio
    async def test_get_classification_service_creates_instance(self) -> None:
        """Should create ClassificationService on first call."""
        service = get_classification_service()
        assert service is not None
        # Second call should return same instance
        service2 = get_classification_service()
        assert service is service2

    @pytest.mark.asyncio
    async def test_get_summarization_service_creates_instance(self) -> None:
        """Should create SummarizationService on first call."""
        service = get_summarization_service()
        assert service is not None
        # Second call should return same instance
        service2 = get_summarization_service()
        assert service is service2


class TestResponseModels:
    """Tests for response model classes."""

    def test_health_response(self) -> None:
        """HealthResponse should have correct fields."""
        resp = HealthResponse(status="ok", service="test", version="1.0.0")
        assert resp.status == "ok"
        assert resp.service == "test"
        assert resp.version == "1.0.0"

    def test_release_list_response(self) -> None:
        """ReleaseListResponse should accept list of releases."""
        releases = [
            ReleaseResponse(
                name="Summer '26",
                slug="summer_26",
                release_id=60,
                total_features=10,
                avg_confidence=0.9,
                generated_at="2026-05-01T10:00:00",
                categories=[FeatureCategory(name="Lightning", count=5)],
            )
        ]
        resp = ReleaseListResponse(releases=releases)
        assert len(resp.releases) == 1
        assert resp.releases[0].slug == "summer_26"

    def test_enrichment_response(self) -> None:
        """EnrichmentResponse should have correct fields."""
        resp = EnrichmentResponse(
            release_slug="summer_26",
            executive_summary="Summary",
            strategic_themes=["Theme 1"],
            categories=[{"category_name": "Lightning"}],
        )
        assert resp.release_slug == "summer_26"
        assert resp.executive_summary == "Summary"
        assert resp.strategic_themes == ["Theme 1"]
        assert resp.categories == [{"category_name": "Lightning"}]


class TestCreateRestRouter:
    """Tests for create_rest_router function."""

    @pytest.fixture
    def mock_storage(self) -> AsyncMock:
        """Create mock storage adapter."""
        storage = AsyncMock()
        storage.list_releases = AsyncMock(return_value=["summer_26", "winter_26"])
        storage.load_release_metadata = AsyncMock(return_value=None)
        storage.load_enrichment = AsyncMock(return_value=None)
        storage.load_markdown = AsyncMock(return_value=None)
        return storage

    @pytest.fixture
    def mock_classification_service(self) -> AsyncMock:
        """Create mock classification service."""
        service = AsyncMock()
        service.classify_single = AsyncMock()
        return service

    @pytest.fixture
    def mock_summarization_service(self) -> AsyncMock:
        """Create mock summarization service."""
        service = AsyncMock()
        service.generate_release_notes_markdown = AsyncMock(return_value="# Release Notes")
        return service

    @pytest.fixture
    def client(
        self,
        mock_storage: AsyncMock,
        mock_classification_service: AsyncMock,
        mock_summarization_service: AsyncMock,
    ) -> TestClient:
        """Create test client with mocked dependencies."""
        import src.infrastructure.api.routes as routes_module

        # Override dependencies
        routes_module._storage_adapter = mock_storage
        routes_module._classification_service = mock_classification_service
        routes_module._summarization_service = mock_summarization_service

        router = create_rest_router()
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def sample_release_metadata(self) -> ReleaseMetadata:
        """Create sample release metadata."""
        return ReleaseMetadata(
            release_id=60,
            slug="summer_26",
            name="Summer '26",
            version="60.0",
            date="2026-06-01",
            total_features=10,
            avg_confidence=0.9,
            generated_at="2026-05-01T10:00:00",
            categories=[
                FeatureCategory(name="Lightning", count=5),
                FeatureCategory(name="Apex", count=5),
            ],
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
                    overview="Visão geral",
                    key_themes=("Tema",),
                    business_impact="Alto",
                    adoption_guidance="Adotar",
                    risk_assessment="Baixo",
                    feature_enrichments=(),
                    locale="pt_BR",
                    generated_at="2026-05-01T10:00:00",
                ),
            ),
            migration_checklist=("Item 1",),
            generated_at="2026-05-01T10:00:00",
        )

    def test_health_check(self, client: TestClient) -> None:
        """GET /health should return health status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "salesforce-webdev"

    def test_list_releases(
        self, client: TestClient, mock_storage: AsyncMock, sample_release_metadata: ReleaseMetadata
    ) -> None:
        """GET /releases should return list of releases."""
        mock_storage.list_releases.return_value = ["summer_26"]
        mock_storage.load_release_metadata.return_value = sample_release_metadata

        response = client.get("/api/v1/releases")
        assert response.status_code == 200
        data = response.json()
        assert len(data["releases"]) == 1
        assert data["releases"][0]["slug"] == "summer_26"
        assert data["releases"][0]["name"] == "Summer '26"

    def test_list_releases_empty(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases should return empty list when no releases."""
        mock_storage.list_releases.return_value = []

        response = client.get("/api/v1/releases")
        assert response.status_code == 200
        data = response.json()
        assert data["releases"] == []

    def test_get_release_found(
        self, client: TestClient, mock_storage: AsyncMock, sample_release_metadata: ReleaseMetadata
    ) -> None:
        """GET /releases/{slug} should return release when found."""
        mock_storage.load_release_metadata.return_value = sample_release_metadata

        response = client.get("/api/v1/releases/summer_26")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "summer_26"
        assert data["name"] == "Summer '26"
        assert data["release_id"] == 60

    def test_get_release_not_found(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases/{slug} should return 404 when not found."""
        mock_storage.load_release_metadata.return_value = None

        response = client.get("/api/v1/releases/nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_enrichment_found(
        self, client: TestClient, mock_storage: AsyncMock, sample_enrichment: ReleaseEnrichment
    ) -> None:
        """GET /releases/{slug}/enrichment should return enrichment when found."""
        mock_storage.load_enrichment.return_value = sample_enrichment

        response = client.get("/api/v1/releases/summer_26/enrichment")
        assert response.status_code == 200
        data = response.json()
        assert data["release_slug"] == "summer_26"
        assert data["executive_summary"] == "Resumo executivo."
        assert data["strategic_themes"] == ["Tema 1", "Tema 2"]
        assert len(data["categories"]) == 1

    def test_get_enrichment_not_found(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases/{slug}/enrichment should return 404 when not found."""
        mock_storage.load_enrichment.return_value = None

        response = client.get("/api/v1/releases/summer_26/enrichment")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_markdown_found(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases/{slug}/markdown/{category} should return markdown when found."""
        mock_storage.load_markdown.return_value = "# Lightning\n\nContent"

        response = client.get("/api/v1/releases/summer_26/markdown/Lightning")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "summer_26"
        assert data["category"] == "Lightning"
        assert data["locale"] == "pt_BR"
        assert data["content"] == "# Lightning\n\nContent"

    def test_get_markdown_with_locale(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases/{slug}/markdown/{category} should accept locale parameter."""
        mock_storage.load_markdown.return_value = "# Lightning\n\nContent"

        response = client.get("/api/v1/releases/summer_26/markdown/Lightning?locale=en_US")
        assert response.status_code == 200
        data = response.json()
        assert data["locale"] == "en_US"

    def test_get_markdown_not_found(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases/{slug}/markdown/{category} should return 404 when not found."""
        mock_storage.load_markdown.return_value = None

        response = client.get("/api/v1/releases/summer_26/markdown/Nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_diff_success(
        self, client: TestClient, mock_storage: AsyncMock, sample_release_metadata: ReleaseMetadata
    ) -> None:
        """GET /releases/diff should return diff between releases."""
        prev_meta = ReleaseMetadata(
            release_id=59,
            slug="spring_26",
            name="Spring '26",
            version="59.0",
            date="2026-02-01",
            total_features=8,
            avg_confidence=0.85,
            generated_at="2026-01-01T10:00:00",
            categories=[
                FeatureCategory(name="Lightning", count=3),
                FeatureCategory(name="Apex", count=5),
            ],
        )
        mock_storage.load_release_metadata.side_effect = [sample_release_metadata, prev_meta]

        response = client.get("/api/v1/releases/diff?current=summer_26&previous=spring_26")
        assert response.status_code == 200
        data = response.json()
        assert data["current"] == "Summer '26"
        assert data["previous"] == "Spring '26"
        assert data["total_delta"] == 2  # 10 - 8
        assert len(data["changes"]) == 2
        assert data["categories"] == []

    def test_get_diff_not_found(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """GET /releases/diff should return 404 when releases not found."""
        mock_storage.load_release_metadata.return_value = None

        response = client.get("/api/v1/releases/diff?current=summer_26&previous=spring_26")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_classify_feature(
        self, client: TestClient, mock_classification_service: AsyncMock
    ) -> None:
        """POST /classify should classify feature text."""
        from src.models.classification import (
            Audience,
            ClassifiedFeature,
            FeatureType,
            ImpactLevel,
            Priority,
        )

        mock_classification_service.classify_single.return_value = ClassifiedFeature(
            name="New AI feature for Lightning",
            impact=ImpactLevel.HIGH,
            feature_type=FeatureType.NEW_FEATURE,
            confidence=0.9,
            keywords_matched=(),
            audience=Audience.USERS,
            priority=Priority.IMPORTANT,
            justification="Test justification",
        )

        response = client.post(
            "/api/v1/classify",
            json={"text": "New AI feature for Lightning", "categories": ["Lightning"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["impact"] == "high"
        assert data["type"] == "new_feature"
        assert data["confidence"] == 0.9

    def test_summarize_release_success(
        self,
        client: TestClient,
        mock_storage: AsyncMock,
        mock_summarization_service: AsyncMock,
        sample_release_metadata: ReleaseMetadata,
        sample_enrichment: ReleaseEnrichment,
    ) -> None:
        """POST /summarize should generate release notes markdown."""
        mock_storage.load_release_metadata.return_value = sample_release_metadata
        mock_storage.load_enrichment.return_value = sample_enrichment

        def mock_generate(*args, **kwargs):
            return "# Release Notes\n\nSummary"

        mock_summarization_service.generate_release_notes_markdown = mock_generate

        response = client.post("/api/v1/summarize?release_slug=summer_26")
        assert response.status_code == 200
        data = response.json()
        assert data["release_slug"] == "summer_26"
        assert data["markdown"] == "# Release Notes\n\nSummary"

    def test_summarize_release_not_found(self, client: TestClient, mock_storage: AsyncMock) -> None:
        """POST /summarize should return 404 when release not found."""
        mock_storage.load_release_metadata.return_value = None

        response = client.post("/api/v1/summarize?release_slug=nonexistent")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_summarize_enrichment_not_found(
        self, client: TestClient, mock_storage: AsyncMock, sample_release_metadata: ReleaseMetadata
    ) -> None:
        """POST /summarize should return 404 when enrichment not found."""
        mock_storage.load_release_metadata.return_value = sample_release_metadata
        mock_storage.load_enrichment.return_value = None

        response = client.post("/api/v1/summarize?release_slug=summer_26")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAppRouter:
    """Test the backward compatibility router."""

    def test_app_router_exists(self) -> None:
        """app_router should be created."""
        from src.infrastructure.api.routes import app_router

        assert app_router is not None
        assert hasattr(app_router, "routes")
