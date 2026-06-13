"""Scraper for Salesforce Help release notes using Playwright headless browser.

The Salesforce Help portal is a SPA that requires JavaScript rendering.
This scraper uses a resilient strategy:
1. Load page with 'domcontentloaded' (not 'networkidle' which never settles)
2. Wait for JS rendering with a manual delay
3. Scroll to trigger lazy-loaded content
4. Try multiple selectors before extracting content
"""

import logging
from types import TracebackType
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, Playwright

from .config import MAX_RETRY_ATTEMPTS, REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


class SalesforceReleaseScraper:
    """Fetches fully rendered HTML from Salesforce Help release notes URLs."""

    # Selectors to try, ordered by likelihood
    CONTENT_SELECTORS: list[str] = [
        "article",
        "#articleViewContent",
        ".release-notes-content",
        "div.content",
        ".slds-card__body",
        "main",
    ]

    def __init__(self) -> None:
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None

    async def __aenter__(self) -> "SalesforceReleaseScraper":
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def fetch_page(self, url: str, page: Optional[Page] = None) -> Optional[str]:
        """Fetches the fully rendered HTML content for a given URL."""
        logger.info("Fetching URL: %s", url)

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                html_content = await self._fetch_with_playwright(url, page)
                if html_content and len(html_content) > 1000:
                    logger.info(
                        "Successfully fetched content from %s (%d bytes, attempt %d)",
                        url,
                        len(html_content),
                        attempt,
                    )
                    return html_content
                logger.warning(
                    "Attempt %d returned insufficient content (%d bytes)",
                    attempt,
                    len(html_content or ""),
                )
            except Exception as e:
                logger.error("Attempt %d failed: %s", attempt, e)

        logger.error("All %d attempts failed for %s", MAX_RETRY_ATTEMPTS, url)
        return None

    async def _fetch_with_playwright(self, url: str, page: Optional[Page] = None) -> Optional[str]:
        """Core Playwright fetch logic with resilient wait strategy."""
        is_standalone = page is None

        if is_standalone:
            if not self._browser:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    content = await self._exec_fetch(url, page)
                    await browser.close()
                    return content
            else:
                page = await self._browser.new_page()

        assert page is not None
        try:
            return await self._exec_fetch(url, page)
        finally:
            if is_standalone and self._browser and page is not None:
                await page.close()

    async def _exec_fetch(self, url: str, page: Page) -> str:
        """Internal execution of fetch logic on a provided page object."""
        # Step 1: Navigate with domcontentloaded
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=REQUEST_TIMEOUT_SECONDS * 1000,
        )

        # Step 2: Wait for JS rendering
        await page.wait_for_timeout(5000)

        # Step 3: Scroll to trigger lazy content
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # Step 4: Expand all ToC tree nodes to ensure full navigation is visible
        await self._expand_toc_nodes(page)

        # Step 5: Extract content
        return await page.content()

    async def _expand_toc_nodes(self, page: Page) -> None:
        """Click collapsed tree nodes in the ToC to reveal all topics."""
        try:
            collapsed = await page.query_selector_all('li[role="treeitem"][aria-expanded="false"]')
            for node in collapsed:
                try:
                    await node.click()
                    await page.wait_for_timeout(300)
                except Exception:
                    pass
            if collapsed:
                logger.info("Expanded %d collapsed ToC nodes", len(collapsed))
        except Exception as e:
            logger.debug("ToC expansion skipped: %s", e)

    async def extract_toc_html(self, url: str, page: Optional[Page] = None) -> Optional[str]:
        """
        Extract just the ToC HTML from a release notes page.

        Loads the page and returns the HTML of the navigation tree container.
        Falls back to returning full page content if ToC selector not found.
        """
        logger.info("Extracting ToC HTML from: %s", url)

        is_standalone = page is None
        browser: Optional[Browser] = None

        try:
            if is_standalone:
                if not self._browser:
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=True)
                        page = await browser.new_page()
                        content = await self._extract_toc_from_page(url, page)
                        await browser.close()
                        return content
                else:
                    page = await self._browser.new_page()

            assert page is not None
            return await self._extract_toc_from_page(url, page)
        except Exception as e:
            logger.error("ToC extraction failed: %s", e)
            return None
        finally:
            if is_standalone and browser:
                await browser.close()

    async def _extract_toc_from_page(self, url: str, page: Page) -> Optional[str]:
        """Navigate to URL and extract the ToC container HTML."""
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=REQUEST_TIMEOUT_SECONDS * 1000,
        )
        await page.wait_for_timeout(5000)

        await self._expand_toc_nodes(page)

        toc_selectors = [
            ".toc-container",
            "ul.tree",
            '[role="tree"]',
            "nav.toc",
        ]
        for selector in toc_selectors:
            element = await page.query_selector(selector)
            if element:
                html = await element.inner_html()
                if html and len(html) > 100:
                    logger.info(
                        "ToC extracted with selector '%s' (%d bytes)",
                        selector,
                        len(html),
                    )
                    return html

        logger.warning("No ToC container found, returning full page HTML")
        return await page.content()
