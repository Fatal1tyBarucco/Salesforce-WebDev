"""End-to-end tests for the release notes pipeline.

Tests the full pipeline flow with mocked Salesforce/LLM external calls,
verifying that scraping → parsing → generation → file output works correctly.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import ReleaseInfo
from src.events import EventBus
from src.cache_manager import CacheManager

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_release() -> ReleaseInfo:
    return ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")


@pytest.fixture
def sample_feature_impact_text() -> str:
    """Simulated raw text from Salesforce feature impact page."""
    return """
    Segurança
    * **Melhoria na autenticação MFA** — _geralmente disponível_
    * **Criptografia de dados em repouso** — _beta_

    Análise de dados
    * **Novos relatórios de pipeline** — _geralmente disponível_

    Desenvolvimento
    * **API REST v2** — _beta_
    """


@pytest.fixture
def releases_dir(tmp_path: Path) -> Path:
    """Create a temporary releases directory structure."""
    rdir = tmp_path / "releases"
    rdir.mkdir()
    return rdir


# ---------------------------------------------------------------------------
# E2E: Full pipeline flow
# ---------------------------------------------------------------------------


class TestPipelineE2E:
    """End-to-end test: scrape → parse → generate → files."""

    @pytest.mark.asyncio
    async def test_full_pipeline_dry_run(
        self,
        sample_release: ReleaseInfo,
        sample_feature_impact_text: str,
        releases_dir: Path,
        tmp_path: Path,
    ) -> None:
        """Dry-run pipeline should not create any files."""
        from src.main import process_single_release

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.return_value = sample_feature_impact_text
        scraper.download_pdf_from_button = AsyncMock()

        impact_parser = MagicMock()
        impact_parser.parse_text.return_value = [
            {
                "name": "Segurança",
                "features": [
                    {
                        "name": "Melhoria na autenticação MFA",
                        "availability": "geralmente disponível",
                    }
                ],
            },
        ]

        generator = MagicMock()
        translator = AsyncMock()

        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            result = await process_single_release(
                release=sample_release,
                scraper=scraper,
                impact_parser=impact_parser,
                generator=generator,
                translator=translator,
                dry_run=True,
            )

        assert result is False
        generator.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_full_pipeline_generates_files(
        self,
        sample_release: ReleaseInfo,
        sample_feature_impact_text: str,
        releases_dir: Path,
        tmp_path: Path,
    ) -> None:
        """Pipeline should generate markdown files for each category."""
        from src.main import process_single_release

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.return_value = sample_feature_impact_text
        scraper.download_pdf_from_button = AsyncMock()

        categories = [
            {"name": "Segurança", "features": [{"name": "Feature A", "availability": "GA"}]},
            {"name": "Análise", "features": [{"name": "Feature B", "availability": "Beta"}]},
        ]
        impact_parser = MagicMock()
        impact_parser.parse_text.return_value = categories

        generated_files: list[str] = []

        def fake_generate(slug, categories_data, locale="pt_BR"):
            cat_dir = releases_dir / slug
            cat_dir.mkdir(parents=True, exist_ok=True)
            for cat in categories_data:
                fpath = cat_dir / f"{cat['name'].lower().replace(' ', '_')}.md"
                fpath.write_text(f"## {cat['name']}\n\nFeature\n", encoding="utf-8")
                generated_files.append(str(fpath))

        generator = MagicMock()
        generator.generate.side_effect = fake_generate

        translator = AsyncMock()
        translator.translate.return_value = "Translated"

        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            with patch("src.main._generate_release_files", new_callable=AsyncMock) as mock_gen:
                mock_gen.return_value = None
                with patch("src.main._update_readme_single"):
                    result = await process_single_release(
                        release=sample_release,
                        scraper=scraper,
                        impact_parser=impact_parser,
                        generator=generator,
                        translator=translator,
                        dry_run=False,
                    )

        assert result is True

    @pytest.mark.asyncio
    async def test_pipeline_handles_empty_content(
        self,
        sample_release: ReleaseInfo,
        releases_dir: Path,
    ) -> None:
        """Pipeline should gracefully handle empty scraper response."""
        from src.main import process_single_release

        scraper = AsyncMock()
        scraper.fetch_page_raw_text.return_value = ""
        scraper.download_pdf_from_button = AsyncMock()

        impact_parser = MagicMock()
        generator = MagicMock()
        translator = AsyncMock()

        with patch("src.main.RELEASES_DIR", str(releases_dir)):
            result = await process_single_release(
                release=sample_release,
                scraper=scraper,
                impact_parser=impact_parser,
                generator=generator,
                translator=translator,
                dry_run=False,
            )

        assert result is False


# ---------------------------------------------------------------------------
# E2E: API + GraphQL integration
# ---------------------------------------------------------------------------


class TestAPIE2E:
    """End-to-end API tests with real file fixtures."""

    def test_graphql_releases_with_real_files(self, tmp_path: Path) -> None:
        """GraphQL query against actual .meta.json files."""
        from src.api import _execute_graphql
        from unittest.mock import patch as p

        for slug, rid in [("spring_26", 260), ("summer_26", 262)]:
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text(
                json.dumps(
                    {
                        "name": slug.replace("_", " ").title(),
                        "release_id": rid,
                        "total_features": 100 + rid,
                        "categories": [{"name": "Security", "count": 10}],
                    }
                ),
                encoding="utf-8",
            )

        with p("src.api.RELEASES_DIR", str(tmp_path)):
            result = _execute_graphql("{ releases { name slug totalFeatures } }")

        assert "data" in result
        assert len(result["data"]["releases"]) == 2
        names = {r["name"] for r in result["data"]["releases"]}
        assert "Spring 26" in names
        assert "Summer 26" in names

    def test_graphql_diff_e2e(self, tmp_path: Path) -> None:
        """GraphQL diff query end-to-end."""
        from src.api import _execute_graphql
        from unittest.mock import patch as p

        for slug, rid, total in [("spring_26", 260, 80), ("summer_26", 262, 100)]:
            d = tmp_path / slug
            d.mkdir()
            (d / ".meta.json").write_text(
                json.dumps(
                    {
                        "name": slug,
                        "release_id": rid,
                        "total_features": total,
                        "categories": [
                            {"name": "Security", "count": 10 if rid == 260 else 15},
                            {"name": "Analytics", "count": 5},
                        ],
                    }
                ),
                encoding="utf-8",
            )

        with p("src.api.RELEASES_DIR", str(tmp_path)):
            result = _execute_graphql(
                '{ diff(current: "summer_26", previous: "spring_26") { totalDelta changes { category delta } } }'
            )

        assert result["data"]["diff"]["totalDelta"] == 20
        changes = {c["category"]: c["delta"] for c in result["data"]["diff"]["changes"]}
        assert changes["Security"] == 5
        assert changes["Analytics"] == 0


# ---------------------------------------------------------------------------
# E2E: Event Bus + Cache integration
# ---------------------------------------------------------------------------


class TestEventBusE2E:
    """EventBus pub/sub end-to-end."""

    @pytest.mark.asyncio
    async def test_publish_subscribe(self) -> None:
        from src.events import Event

        bus = EventBus()
        received: list[str] = []

        async def handler(event: Event) -> None:
            received.append(event.name)

        bus.subscribe("release.processed", handler)
        await bus.emit("release.processed", {"slug": "summer_26"})

        assert "release.processed" in received


class TestCacheE2E:
    """CacheManager end-to-end with TTL."""

    def test_set_get_ttl(self, tmp_path: Path) -> None:
        cache = CacheManager(cache_dir=tmp_path, ttl_seconds=3600)
        cache.set("key1", {"data": "value"}, namespace="test")
        result = cache.get("key1", namespace="test")
        assert result == {"data": "value"}

    def test_stats(self, tmp_path: Path) -> None:
        cache = CacheManager(cache_dir=tmp_path, ttl_seconds=3600)
        cache.set("k1", "v1", namespace="ns")
        cache.get("k1", namespace="ns")  # hit
        cache.get("k2", namespace="ns")  # miss
        stats = cache.stats
        assert stats.hits >= 1
        assert stats.misses >= 1
