"""Tests for src/scraper.py — retry logic and PDF download edge cases."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.cache_manager import CacheManager


class TestDownloadPDF:
    """download_pdf_from_button: skip on existing, fail on missing selector."""

    @pytest.mark.asyncio
    async def test_skip_when_pdf_exists(self, tmp_path: Path) -> None:
        from src.scraper import SalesforceReleaseScraper

        pdf_path = tmp_path / "existing.pdf"
        pdf_path.write_bytes(b"x" * 2000)

        scraper = SalesforceReleaseScraper()
        result = await scraper.download_pdf_from_button("http://example.com", pdf_path)
        assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_button_not_found(self, tmp_path: Path) -> None:
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


class TestFetchPageRawText:
    """fetch_page_raw_text: cache hit and circuit-breaker-open paths."""

    @pytest.mark.asyncio
    async def test_returns_cached_content(self, tmp_path: Path) -> None:
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        cache = CacheManager(cache_dir=tmp_path, ttl_seconds=3600)
        long_content = "cached content " * 50
        cache.set("http://cached-url.com", long_content)
        scraper._cache = cache

        result = await scraper.fetch_page_raw_text("http://cached-url.com")
        assert result == long_content

    @pytest.mark.asyncio
    async def test_returns_none_when_breaker_open(self) -> None:
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        cb = scraper._circuit_breaker
        for _ in range(cb._threshold + 1):
            cb.record_failure()

        assert cb.is_open
        result = await scraper.fetch_page_raw_text("http://example.com")
        assert result is None


class TestEnsureBrowser:
    """_ensure_browser: no-op when no playwright, no-op when already connected."""

    @pytest.mark.asyncio
    async def test_returns_false_when_no_playwright(self) -> None:
        from unittest.mock import patch

        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        scraper._playwright = None
        scraper._browser = None

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.start.side_effect = OSError("playwright not available")
            result = await scraper._ensure_browser()

        assert result is False

    @pytest.mark.asyncio
    async def test_returns_true_when_already_connected(self) -> None:
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        mock_browser = MagicMock()
        mock_browser.is_connected.return_value = True
        scraper._browser = mock_browser

        result = await scraper._ensure_browser()
        assert result is True


class TestFetchFeaturesWithLinks:
    """fetch_features_with_links: retry on empty, handle browser errors."""

    @pytest.mark.asyncio
    async def test_retries_when_no_features_found(self) -> None:
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        call_count = 0

        async def mock_fetch(url: str, return_text: bool = False) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return "<html><body>Empty</body></html>"
            return '<table><tr><td><a href="https://help.salesforce.com/s/articleView?id=test">Feature</a></td></tr></table>'

        with (
            patch.object(scraper, "_ensure_browser", return_value=True),
            patch.object(scraper, "_fetch_with_playwright", side_effect=mock_fetch),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await scraper.fetch_features_with_links("http://example.com")

        assert len(result) == 1
        assert call_count >= 3

    @pytest.mark.asyncio
    async def test_returns_empty_on_browser_error(self) -> None:
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()

        async def mock_ensure():
            return True

        async def mock_fetch(url: str, return_text: bool = False):
            raise TimeoutError("Browser timeout")

        with (
            patch.object(scraper, "_ensure_browser", side_effect=mock_ensure),
            patch.object(scraper, "_fetch_with_playwright", side_effect=mock_fetch),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            result = await scraper.fetch_features_with_links("http://example.com")

        assert result == []
