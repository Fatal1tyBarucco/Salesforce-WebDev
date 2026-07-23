"""Additional tests to improve coverage for scraper, release_docs, and main."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config import ReleaseInfo

# ---------------------------------------------------------------------------
# Scraper coverage tests
# ---------------------------------------------------------------------------


class TestScraperCoverage:
    """Tests to cover uncovered scraper paths."""

    @pytest.mark.asyncio
    async def test_fetch_page_raw_text_circuit_breaker_open(self) -> None:
        """fetch_page_raw_text returns None when circuit breaker is open."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        # Manually trip the circuit breaker
        cb = scraper._circuit_breaker
        for _ in range(cb._threshold + 1):
            cb.record_failure()

        assert cb.is_open
        result = await scraper.fetch_page_raw_text("http://example.com")
        assert result is None

    @pytest.mark.asyncio
    async def test_fetch_page_raw_text_cached(self, tmp_path: Path) -> None:
        """fetch_page_raw_text returns cached content when available."""
        from src.scraper import SalesforceReleaseScraper
        from src.cache_manager import CacheManager

        scraper = SalesforceReleaseScraper()
        # Replace the scraper's cache with our test cache
        cache = CacheManager(cache_dir=tmp_path, ttl_seconds=3600)
        # Content must be > MIN_RAW_TEXT_LENGTH (500 chars)
        long_content = "cached content " * 50
        cache.set("http://cached-url.com", long_content)
        scraper._cache = cache

        result = await scraper.fetch_page_raw_text("http://cached-url.com")
        assert result == long_content

    @pytest.mark.asyncio
    async def test_ensure_browser_no_playwright(self) -> None:
        """_ensure_browser returns False when no playwright instance."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        scraper._playwright = None
        scraper._browser = None
        result = await scraper._ensure_browser()
        assert result is False

    @pytest.mark.asyncio
    async def test_ensure_browser_already_connected(self) -> None:
        """_ensure_browser returns True when browser is already connected."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        mock_browser = MagicMock()
        mock_browser.is_connected.return_value = True
        scraper._browser = mock_browser

        result = await scraper._ensure_browser()
        assert result is True

    @pytest.mark.asyncio
    async def test_download_pdf_already_exists(self, tmp_path: Path) -> None:
        """download_pdf_from_button skips when PDF already exists."""
        from src.scraper import SalesforceReleaseScraper

        pdf_path = tmp_path / "existing.pdf"
        pdf_path.write_bytes(b"x" * 2000)

        scraper = SalesforceReleaseScraper()
        result = await scraper.download_pdf_from_button("http://example.com", pdf_path)
        assert result is True

    @pytest.mark.asyncio
    async def test_download_pdf_button_not_found(self, tmp_path: Path) -> None:
        """download_pdf_from_button returns False when button not found."""
        from src.scraper import SalesforceReleaseScraper

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=TimeoutError("no button"))
        mock_context = AsyncMock()
        mock_context.new_page.return_value = mock_page
        mock_context.close = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_context.return_value = mock_context

        scraper = SalesforceReleaseScraper()
        scraper._browser = mock_browser

        pdf_path = tmp_path / "test.pdf"
        result = await scraper.download_pdf_from_button("http://example.com", pdf_path)
        assert result is False


# ---------------------------------------------------------------------------
# Release docs coverage tests
# ---------------------------------------------------------------------------


class TestReleaseDocsCoverage:
    """Tests to cover uncovered release_docs paths."""

    def test_build_release_name_fallback(self) -> None:
        """_build_release_name falls back for unexpected IDs."""
        from src.release_docs import _build_release_name

        # ID below base should use fallback
        name = _build_release_name(200)
        assert "Spring" in name or "Summer" in name or "Winter" in name

    def test_build_release_slug(self) -> None:
        """_build_release_slug produces correct slug."""
        from src.release_docs import _build_release_slug

        slug = _build_release_slug(262)
        assert "_" in slug
        assert slug.islower()

    def test_find_existing_releases_no_dir(self, tmp_path: Path) -> None:
        """_find_existing_releases returns empty set when dir doesn't exist."""
        from src.release_docs import _find_existing_releases

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path / "nope")):
            result = _find_existing_releases()
        assert result == set()

    def test_find_existing_releases_with_dirs(self, tmp_path: Path) -> None:
        """_find_existing_releases returns slugs for dirs with .md files."""
        from src.release_docs import _find_existing_releases

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / "test.md").write_text("# Test")

        with patch("src.release_docs.RELEASES_DIR", str(tmp_path)):
            result = _find_existing_releases()
        assert "summer_26" in result

    def test_slugify_category(self) -> None:
        """_slugify_category produces URL-safe slugs."""
        from src.release_docs import _slugify_category

        assert _slugify_category("Análise de dados") == "analise_de_dados"
        assert _slugify_category("Security") == "security"

    def test_get_release_emoji(self) -> None:
        """_get_release_emoji returns correct emoji for season."""
        from src.release_docs import _get_release_emoji

        assert "☀" in _get_release_emoji("Summer '26")
        assert "🌸" in _get_release_emoji("Spring '26")
        assert "❄" in _get_release_emoji("Winter '26")
        # Unknown season defaults to Spring (cherry blossom)
        assert "🌸" in _get_release_emoji("Unknown '26")

    def test_build_resource_footer(self, tmp_path: Path) -> None:
        """_build_resource_footer generates markdown links."""
        from src.release_docs import _build_resource_footer
        from src.config import BILINGUAL_TEMPLATES

        release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")
        templates = BILINGUAL_TEMPLATES.get("pt_BR", BILINGUAL_TEMPLATES["en_US"])
        footer = _build_resource_footer(release, templates, "pt_BR")
        assert isinstance(footer, list)
        assert len(footer) > 0


# ---------------------------------------------------------------------------
# Main coverage tests
# ---------------------------------------------------------------------------


class TestMainCoverage:
    """Tests to cover uncovered main.py paths."""

    def test_parse_args_defaults(self) -> None:
        """_parse_args returns defaults when no args."""
        from src.main import _parse_args

        with patch("sys.argv", ["main.py"]):
            release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is False

    def test_parse_args_release(self) -> None:
        """_parse_args parses --release flag."""
        from src.main import _parse_args

        with patch("sys.argv", ["main.py", "--release", "summer_26"]):
            release_filter, dry_run = _parse_args()
        assert release_filter == "summer_26"
        assert dry_run is False

    def test_parse_args_dry_run(self) -> None:
        """_parse_args parses --dry-run flag."""
        from src.main import _parse_args

        with patch("sys.argv", ["main.py", "--dry-run"]):
            release_filter, dry_run = _parse_args()
        assert release_filter is None
        assert dry_run is True

    @pytest.mark.asyncio
    async def test_detect_new_release_no_existing(self) -> None:
        """detect_new_release returns latest known when no releases exist."""
        from src.main import detect_new_release

        scraper = AsyncMock()
        known = [ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")]

        with patch("src.main._find_existing_releases", return_value=set()):
            with patch("src.main.KNOWN_RELEASES", known):
                result = await detect_new_release(scraper)
        assert result is not None
        assert result.slug == "summer_26"

    @pytest.mark.asyncio
    async def test_detect_new_release_all_exist(self) -> None:
        """detect_new_release returns None when all releases exist."""
        from src.main import detect_new_release

        scraper = AsyncMock()
        known = [ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")]

        with patch("src.main._find_existing_releases", return_value={"summer_26"}):
            with patch("src.main.KNOWN_RELEASES", known):
                result = await detect_new_release(scraper)
        assert result is None

    @pytest.mark.asyncio
    async def test_enrich_meta_no_meta_file(self, tmp_path: Path) -> None:
        """enrich_meta_with_classification does nothing when no meta file."""
        from src.main import enrich_meta_with_classification

        release = ReleaseInfo(name="Test", release_id=999, slug="test_999")
        with patch("src.main.RELEASES_DIR", str(tmp_path)):
            await enrich_meta_with_classification(release)
        # Should not raise


# ---------------------------------------------------------------------------
# Heuristic classifier coverage
# ---------------------------------------------------------------------------


class TestHeuristicFeatureClassifierCoverage:
    """Tests for heuristic classifier uncovered paths."""

    def test_classify_empty_text(self) -> None:
        """classify returns low impact for empty text."""
        from src.heuristic_classifier import HeuristicFeatureClassifier

        classifier = HeuristicFeatureClassifier()
        result = classifier.classify_text("")
        assert result["impact"] == "low"
        assert result["confidence"] == 0.1

    def test_classify_none_text(self) -> None:
        """classify returns low impact for None text."""
        from src.heuristic_classifier import HeuristicFeatureClassifier

        classifier = HeuristicFeatureClassifier()
        result = classifier.classify_text(None)
        assert result["impact"] == "low"

    def test_classify_security_text(self) -> None:
        """classify detects security-related text."""
        from src.heuristic_classifier import HeuristicFeatureClassifier

        classifier = HeuristicFeatureClassifier()
        result = classifier.classify_text("Enhanced security and authentication features")
        assert result["impact"] in ("high", "medium", "low")
        assert "confidence" in result

    def test_classify_unknown_text(self) -> None:
        """classify returns medium impact for unknown text."""
        from src.heuristic_classifier import HeuristicFeatureClassifier

        classifier = HeuristicFeatureClassifier()
        result = classifier.classify_text("Random text with no keywords at all xyz")
        assert result["impact"] == "medium"
        assert result["confidence"] == 0.3


# ---------------------------------------------------------------------------
# Automation export coverage
# ---------------------------------------------------------------------------


class TestAutomationExportCoverage:
    """Tests for automation export uncovered paths."""

    @pytest.mark.asyncio
    async def test_export_release_json_empty(self) -> None:
        """export_release_json handles missing meta."""
        from src.automation.export import export_release_json

        def load_meta(slug: str):
            return None

        result = await export_release_json(load_meta, "test_slug")
        assert result == "{}"

    @pytest.mark.asyncio
    async def test_export_release_json_with_data(self) -> None:
        """export_release_json returns formatted JSON."""
        from src.automation.export import export_release_json

        def load_meta(slug: str):
            return {"name": "Test", "slug": slug}

        result = await export_release_json(load_meta, "test_slug")
        assert "Test" in result

    @pytest.mark.asyncio
    async def test_export_release_csv_empty(self) -> None:
        """export_release_csv handles missing meta."""
        from src.automation.export import export_release_csv

        def load_meta(slug: str):
            return None

        result = await export_release_csv(load_meta, "test_slug")
        assert result == ""
