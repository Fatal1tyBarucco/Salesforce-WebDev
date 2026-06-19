"""Scraper for Salesforce Help release notes using Playwright headless browser.

The Salesforce Help portal is a SPA that requires JavaScript rendering.
This scraper uses a resilient strategy:
1. Load page with 'domcontentloaded' (not 'networkidle' which never settles)
2. Wait for JS rendering with a manual delay
3. Scroll to trigger lazy-loaded content
4. Try multiple selectors before extracting content
5. Cache content hashes to avoid re-fetching unchanged pages
"""

import hashlib
import logging
import urllib.request
from pathlib import Path
from types import TracebackType
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, Playwright

from .config import MAX_RETRY_ATTEMPTS, REQUEST_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

MIN_VALID_CONTENT_SIZE = 1000
MIN_TOC_HTML_SIZE = 100
MIN_RAW_TEXT_LENGTH = 500


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

    async def fetch_page(
        self, url: str, page: Optional[Page] = None, *, expand_toc: bool = True
    ) -> Optional[str]:
        """Fetches the fully rendered HTML content for a given URL."""
        logger.info("Fetching URL: %s", url)

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                html_content = await self._fetch_with_playwright(url, page, expand_toc=expand_toc)
                if html_content and len(html_content) > MIN_VALID_CONTENT_SIZE:
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

    async def _fetch_with_playwright(
        self,
        url: str,
        page: Optional[Page] = None,
        *,
        expand_toc: bool = True,
        return_text: bool = False,
    ) -> Optional[str]:
        """Core Playwright fetch logic with resilient wait strategy."""
        is_standalone = page is None

        if is_standalone:
            if not self._browser:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)
                    page = await browser.new_page()
                    try:
                        return await self._exec_fetch(
                            url, page, expand_toc=expand_toc, return_text=return_text
                        )
                    finally:
                        await browser.close()
            else:
                page = await self._browser.new_page()

        assert page is not None
        try:
            return await self._exec_fetch(url, page, expand_toc=expand_toc, return_text=return_text)
        finally:
            if is_standalone and self._browser and page is not None:
                await page.close()

    async def _exec_fetch(
        self, url: str, page: Page, *, expand_toc: bool = True, return_text: bool = False
    ) -> str:
        """Internal execution of fetch logic on a provided page object.

        If return_text is True, returns page.inner_text('body') instead of page.content().
        """
        await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=REQUEST_TIMEOUT_SECONDS * 1000,
        )

        try:
            await page.wait_for_selector(
                "ul.tree, li[role='treeitem'], article, table, main",
                timeout=15000,
            )
        except Exception:
            await page.wait_for_timeout(5000)

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)

        if expand_toc:
            await self._expand_toc_nodes(page)

        if return_text:
            return await page.inner_text("body")
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

        try:
            if is_standalone:
                if not self._browser:
                    async with async_playwright() as p:
                        browser = await p.chromium.launch(headless=True)
                        page = await browser.new_page()
                        try:
                            return await self._extract_toc_from_page(url, page)
                        finally:
                            await browser.close()
                else:
                    page = await self._browser.new_page()

            assert page is not None
            return await self._extract_toc_from_page(url, page)
        except Exception as e:
            logger.error("ToC extraction failed: %s", e)
            return None
        finally:
            if is_standalone and page is not None and self._browser:
                await page.close()

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
                if html and len(html) > MIN_TOC_HTML_SIZE:
                    logger.info(
                        "ToC extracted with selector '%s' (%d bytes)",
                        selector,
                        len(html),
                    )
                    return html

        logger.warning("No ToC container found, returning full page HTML")
        return await page.content()

    async def fetch_page_raw_text(self, url: str) -> Optional[str]:
        """Fetch page and return inner_text of body (for feature impact page).

        Uses content hash caching to avoid re-fetching unchanged pages.
        """
        logger.info("Fetching raw text: %s", url)

        # Check cache
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_file = CACHE_DIR / f"{url_hash}.txt"

        if cache_file.exists():
            cached = cache_file.read_text(encoding="utf-8")
            if len(cached) > MIN_RAW_TEXT_LENGTH:
                logger.info("Using cached content (%d chars)", len(cached))
                return cached

        try:
            text = await self._fetch_with_playwright(url, return_text=True)
            if text and len(text) > MIN_RAW_TEXT_LENGTH:
                logger.info("Fetched raw text (%d chars)", len(text))
                cache_file.write_text(text, encoding="utf-8")
                return text
            logger.warning("Insufficient text content (%d chars)", len(text or ""))
            return None
        except Exception as e:
            logger.error("Failed to fetch raw text: %s", e)
            return None

    async def download_pdf_from_button(self, page_url: str, dest: Path) -> bool:
        """Navigate to a page, click the PDF download button, and save the file.

        The Salesforce Help pages have a <button title="Open PDF"> that triggers
        a download or opens a new tab with the PDF. This method handles both cases.
        """
        logger.info("Downloading PDF via button click: %s -> %s", page_url, dest)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(accept_downloads=True)
                page = await context.new_page()

                await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

                try:
                    await page.wait_for_selector("button[title='Open PDF']", timeout=15000)
                except Exception:
                    logger.warning("PDF button not found on %s", page_url)
                    await browser.close()
                    return False

                async with page.expect_download(timeout=30000) as download_info:
                    await page.click("button[title='Open PDF']")

                download = await download_info.value
                await download.save_as(str(dest))

                await browser.close()

                if dest.exists() and dest.stat().st_size > MIN_VALID_CONTENT_SIZE:
                    logger.info(
                        "PDF downloaded via button: %s (%d bytes)", dest, dest.stat().st_size
                    )
                    return True
                logger.warning("PDF too small: %d bytes", dest.stat().st_size)
                return False

        except Exception as e:
            logger.warning("PDF button download failed: %s", e)
            return False

    async def download_pdf(self, url: str, dest: Path) -> bool:
        """Download a PDF file to dest using urllib (fallback)."""
        logger.info("Downloading PDF: %s -> %s", url, dest)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urllib.request.urlopen(req, timeout=30)
            data = response.read()
            dest.write_bytes(data)
            if dest.exists() and dest.stat().st_size > MIN_VALID_CONTENT_SIZE:
                logger.info("PDF downloaded: %s (%d bytes)", dest, dest.stat().st_size)
                return True
            logger.warning("PDF too small: %d bytes", dest.stat().st_size)
            return False
        except Exception as e:
            logger.warning("PDF download failed: %s", e)
            return False
