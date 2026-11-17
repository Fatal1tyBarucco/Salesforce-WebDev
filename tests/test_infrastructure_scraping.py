"""Tests for src/infrastructure/scraping.py — 100% coverage target."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.scraping import (
    CachedScrapingAdapter,
    PlaywrightScrapingAdapter,
    ScrapingAdapter,
)


class MockScrapingAdapter(ScrapingAdapter):
    """Mock scraping adapter for testing."""

    def __init__(self, html: str = "<html><body>Mock content</body></html>") -> None:
        self._html = html
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock_scraping"

    async def execute(self, url: str) -> str:
        self.call_count += 1
        return self._html


class TestScrapingAdapter:
    """Tests for the abstract ScrapingAdapter base class."""

    @pytest.mark.asyncio
    async def test_abstract_execute_raises_not_implemented(self) -> None:
        """Abstract execute should raise NotImplementedError."""
        adapter = ScrapingAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.execute("https://example.com")

    def test_name_property(self) -> None:
        """Base adapter name property."""
        adapter = ScrapingAdapter()
        assert adapter.name == "scraping_adapter"


class TestPlaywrightScrapingAdapter:
    """Tests for PlaywrightScrapingAdapter."""

    @pytest.fixture
    def adapter(self) -> PlaywrightScrapingAdapter:
        """Create Playwright scraping adapter."""
        return PlaywrightScrapingAdapter(
            headless=True,
            timeout_ms=30000,
            wait_for_selector="main",
        )

    @pytest.mark.asyncio
    async def test_init_sets_properties(self, adapter: PlaywrightScrapingAdapter) -> None:
        """Should initialize with correct properties."""
        assert adapter.headless is True
        assert adapter.timeout_ms == 30000
        assert adapter.wait_for_selector == "main"
        assert adapter._browser is None
        assert adapter._playwright is None

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: PlaywrightScrapingAdapter) -> None:
        """Adapter name should be correct."""
        assert adapter.name == "playwright_scraping"

    @pytest.mark.asyncio
    async def test_execute_fetches_html(self, adapter: PlaywrightScrapingAdapter) -> None:
        """Should fetch and return HTML content."""
        mock_page = AsyncMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Page content</body></html>")

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
            mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            html = await adapter.execute("https://example.com")

        assert html == "<html><body>Page content</body></html>"
        mock_playwright.chromium.launch.assert_called_once_with(headless=True)
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="networkidle",
            timeout=30000,
        )
        mock_page.wait_for_selector.assert_called_once_with("main", timeout=30000)
        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_raises_on_http_error(self, adapter: PlaywrightScrapingAdapter) -> None:
        """Should raise RuntimeError on HTTP error status."""
        mock_page = AsyncMock()
        mock_response = MagicMock()
        mock_response.status = 404
        mock_page.goto = AsyncMock(return_value=mock_response)

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
            mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(RuntimeError, match="HTTP 404 for https://example.com"):
                await adapter.execute("https://example.com")

    @pytest.mark.asyncio
    async def test_execute_without_wait_for_selector(
        self, adapter: PlaywrightScrapingAdapter
    ) -> None:
        """Should work without wait_for_selector."""
        adapter.wait_for_selector = None

        mock_page = AsyncMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.content = AsyncMock(return_value="<html>Content</html>")

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
            mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            html = await adapter.execute("https://example.com")

        assert html == "<html>Content</html>"
        mock_page.wait_for_selector.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_closes_browser_on_exception(
        self, adapter: PlaywrightScrapingAdapter
    ) -> None:
        """Should close browser even when exception occurs."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=RuntimeError("Network error"))

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
            mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            with pytest.raises(RuntimeError, match="Network error"):
                await adapter.execute("https://example.com")

        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_page_raw_text_success(self, adapter: PlaywrightScrapingAdapter) -> None:
        """fetch_page_raw_text should extract text from HTML."""
        mock_page = AsyncMock()
        mock_response = MagicMock()
        mock_response.status = 200
        mock_page.goto = AsyncMock(return_value=mock_response)
        mock_page.wait_for_selector = AsyncMock()
        mock_page.content = AsyncMock(
            return_value="<html><body><h1>Title</h1><p>Content</p></body></html>"
        )

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
            mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            text = await adapter.fetch_page_raw_text("https://example.com")

        assert text is not None
        assert "Title" in text
        assert "Content" in text

    @pytest.mark.asyncio
    async def test_fetch_page_raw_text_returns_none_on_error(
        self, adapter: PlaywrightScrapingAdapter
    ) -> None:
        """fetch_page_raw_text should return None on error."""
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=RuntimeError("Network error"))

        mock_browser = AsyncMock()
        mock_browser.new_page = AsyncMock(return_value=mock_page)
        mock_browser.close = AsyncMock()

        mock_playwright = AsyncMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)

        with patch("playwright.async_api.async_playwright") as mock_async_playwright:
            mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_playwright)
            mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=None)

            text = await adapter.fetch_page_raw_text("https://example.com")

        assert text is None


class TestCachedScrapingAdapter:
    """Tests for CachedScrapingAdapter."""

    @pytest.fixture
    def mock_base_adapter(self) -> MockScrapingAdapter:
        """Create mock base adapter."""
        return MockScrapingAdapter("<html><body>Cached content</body></html>")

    @pytest.fixture
    def cached_adapter(self, mock_base_adapter: MockScrapingAdapter) -> CachedScrapingAdapter:
        """Create cached scraping adapter."""
        return CachedScrapingAdapter(
            base_adapter=mock_base_adapter,
            cache_dir=".cache/test_scraping",
            ttl_seconds=3600,
        )

    @pytest.mark.asyncio
    async def test_name_property(self, cached_adapter: CachedScrapingAdapter) -> None:
        """Adapter name should include base adapter name."""
        assert cached_adapter.name == "cached_mock_scraping"

    @pytest.mark.asyncio
    async def test_execute_caches_result(
        self, cached_adapter: CachedScrapingAdapter, mock_base_adapter: MockScrapingAdapter
    ) -> None:
        """Should cache result on first call."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            cached_adapter._cache_dir = tmpdir

            # First call - should fetch from base
            html1 = await cached_adapter.execute("https://example.com/page1")
            assert html1 == "<html><body>Cached content</body></html>"
            assert mock_base_adapter.call_count == 1

            # Second call - should use cache
            html2 = await cached_adapter.execute("https://example.com/page1")
            assert html2 == "<html><body>Cached content</body></html>"
            assert mock_base_adapter.call_count == 1  # Not called again

    @pytest.mark.asyncio
    async def test_execute_different_urls_different_cache(
        self, cached_adapter: CachedScrapingAdapter, mock_base_adapter: MockScrapingAdapter
    ) -> None:
        """Different URLs should have different cache entries."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            cached_adapter._cache_dir = tmpdir

            html1 = await cached_adapter.execute("https://example.com/page1")
            html2 = await cached_adapter.execute("https://example.com/page2")

            assert html1 == "<html><body>Cached content</body></html>"
            assert html2 == "<html><body>Cached content</body></html>"
            assert mock_base_adapter.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_expired_cache_refetches(
        self, cached_adapter: CachedScrapingAdapter, mock_base_adapter: MockScrapingAdapter
    ) -> None:
        """Should refetch when cache is expired."""
        import asyncio
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            cached_adapter._cache_dir = tmpdir
            cached_adapter._ttl = 1  # 1 second TTL

            # First call
            _ = await cached_adapter.execute("https://example.com/page1")
            assert mock_base_adapter.call_count == 1

            # Wait for cache to expire
            await asyncio.sleep(1.1)

            # Second call - should refetch
            _ = await cached_adapter.execute("https://example.com/page1")
            assert mock_base_adapter.call_count == 2

    @pytest.mark.asyncio
    async def test_execute_creates_cache_directory(
        self, cached_adapter: CachedScrapingAdapter, mock_base_adapter: MockScrapingAdapter
    ) -> None:
        """Should create cache directory if it doesn't exist."""
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir) / "new_cache_dir"
            cached_adapter._cache_dir = str(cache_dir)

            html = await cached_adapter.execute("https://example.com/page1")

            assert cache_dir.exists()
            assert html == "<html><body>Cached content</body></html>"

    @pytest.mark.asyncio
    async def test_execute_cache_key_is_deterministic(
        self, cached_adapter: CachedScrapingAdapter, mock_base_adapter: MockScrapingAdapter
    ) -> None:
        """Cache key should be deterministic for same URL."""
        import hashlib
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            cached_adapter._cache_dir = tmpdir

            # First call
            await cached_adapter.execute("https://example.com/page1")

            # Check cache file exists with expected name
            cache_key = hashlib.sha256(b"https://example.com/page1").hexdigest()[:16]
            cache_path = Path(tmpdir) / f"{cache_key}.html"

            assert cache_path.exists()

    @pytest.mark.asyncio
    async def test_init_with_custom_parameters(self) -> None:
        """Should initialize with custom parameters."""
        mock_base = MockScrapingAdapter()
        adapter = CachedScrapingAdapter(
            base_adapter=mock_base,
            cache_dir="custom/cache/dir",
            ttl_seconds=7200,
        )

        assert adapter._cache_dir == "custom/cache/dir"
        assert adapter._ttl == 7200
        assert adapter._base is mock_base

    @pytest.mark.asyncio
    async def test_execute_preserves_base_adapter_errors(
        self, cached_adapter: CachedScrapingAdapter
    ) -> None:
        """Should propagate errors from base adapter."""
        import tempfile

        mock_base = MockScrapingAdapter()
        mock_base._html = None
        mock_base.execute = AsyncMock(side_effect=RuntimeError("Fetch failed"))

        cached_adapter = CachedScrapingAdapter(
            base_adapter=mock_base,
            cache_dir=tempfile.mkdtemp(),
        )

        with pytest.raises(RuntimeError, match="Fetch failed"):
            await cached_adapter.execute("https://example.com/page1")
