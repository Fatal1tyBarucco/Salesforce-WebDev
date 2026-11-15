"""Scraping infrastructure — Playwright-based web scraping adapter.

Implements the ScrapingStep contract from the domain layer.
"""

from __future__ import annotations

import logging
from typing import Any

from src.core.pipeline.steps import ScrapingStep

logger = logging.getLogger(__name__)


class ScrapingAdapter(ScrapingStep):
    """Abstract scraping adapter interface."""

    @property
    def name(self) -> str:
        return "scraping_adapter"

    async def execute(self, url: str) -> str:
        raise NotImplementedError


class PlaywrightScrapingAdapter(ScrapingAdapter):
    """Playwright-based scraping implementation.

    Uses headless Chromium to fetch JavaScript-rendered pages.
    """

    def __init__(
        self,
        headless: bool = True,
        timeout_ms: int = 30000,
        wait_for_selector: str | None = None,
    ) -> None:
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.wait_for_selector = wait_for_selector
        self._browser: Any = None
        self._playwright: Any = None

    @property
    def name(self) -> str:
        return "playwright_scraping"

    async def execute(self, url: str) -> str:
        """Fetch and return raw HTML content from the URL."""
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            self._playwright = p
            self._browser = await p.chromium.launch(headless=self.headless)
            page = await self._browser.new_page()

            try:
                logger.info("Fetching URL: %s", url)
                response = await page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=self.timeout_ms,
                )

                if response and response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status} for {url}")

                if self.wait_for_selector:
                    await page.wait_for_selector(self.wait_for_selector, timeout=self.timeout_ms)

                html: str = await page.content()
                logger.info("Successfully fetched %d chars from %s", len(html), url)
                return html

            except Exception as e:
                logger.error("Scraping failed for %s: %s", url, e)
                raise
            finally:
                if self._browser:
                    await self._browser.close()
                self._browser = None
                self._playwright = None

    async def fetch_page_raw_text(self, url: str) -> str | None:
        """Fetch page and return raw text content (for discovery service)."""
        try:
            html = await self.execute(url)
            # Extract text from HTML (basic)
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator="\n", strip=True)  # type: ignore[no-any-return]
        except Exception as e:
            logger.error("Failed to fetch raw text from %s: %s", url, e)
            return None


class CachedScrapingAdapter(ScrapingAdapter):
    """Scraping adapter with filesystem caching."""

    def __init__(
        self,
        base_adapter: ScrapingAdapter,
        cache_dir: str = ".cache/scraping",
        ttl_seconds: int = 3600,
    ) -> None:
        self._base = base_adapter
        self._cache_dir = cache_dir
        self._ttl = ttl_seconds

    @property
    def name(self) -> str:
        return f"cached_{self._base.name}"

    async def execute(self, url: str) -> str:
        """Fetch with caching."""
        import hashlib
        import time
        from pathlib import Path

        cache_key = hashlib.sha256(url.encode()).hexdigest()[:16]
        cache_path = Path(self._cache_dir) / f"{cache_key}.html"

        # Check cache
        if cache_path.exists():
            mtime = cache_path.stat().st_mtime
            if time.time() - mtime < self._ttl:
                logger.info("Cache hit for %s", url)
                return cache_path.read_text(encoding="utf-8")

        # Fetch from base adapter
        html = await self._base.execute(url)

        # Write to cache
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(html, encoding="utf-8")

        return html
