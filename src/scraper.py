"""Scraper for Salesforce Help release notes using Playwright headless browser.

The Salesforce Help portal is a SPA that requires JavaScript rendering.
This scraper uses a resilient strategy:
1. Load page with 'domcontentloaded' (not 'networkidle' which never settles)
2. Wait for JS rendering with a manual delay
3. Scroll to trigger lazy-loaded content
4. Try multiple selectors before extracting content
5. Cache content hashes to avoid re-fetching unchanged pages
"""

import asyncio
import logging
import random
import time

import urllib.request
from pathlib import Path
from types import TracebackType
from typing import Optional, cast

from playwright.async_api import async_playwright, Browser, Page, Playwright

from .config import MAX_RETRY_ATTEMPTS, REQUEST_TIMEOUT_SECONDS, RETRY_BASE_DELAY_SECONDS
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


def is_rate_limited_response(status_code: int | str | None) -> bool:
    """Check if an HTTP response status code indicates rate limiting (429).

    Args:
        status_code: HTTP status code as int, str, or None.

    Returns:
        ``True`` when *status_code* equals 429; ``False`` otherwise
        (including ``None`` or non-numeric values).
    """
    if status_code is None:
        return False
    try:
        return int(status_code) == 429
    except (TypeError, ValueError):
        return False


def calculate_jittered_delay(base_delay: float, attempt: int) -> float:
    """Calculate exponential backoff delay with jitter.

    Formula: base_delay * (2 ** attempt) + random.uniform(0, base_delay)
    Jitter prevents Thundering Herd when multiple instances retry simultaneously.
    """
    exponential_delay: float = base_delay * (2**attempt)
    jitter: float = random.uniform(0, base_delay)
    return exponential_delay + jitter


MIN_VALID_CONTENT_SIZE = 1000
MIN_TOC_HTML_SIZE = 100
MIN_RAW_TEXT_LENGTH = 500
CACHE_DIR = Path("cache")

# Rate limiting: max requests per second to Salesforce
RATE_LIMIT_RPS = 2
RATE_LIMIT_MIN_INTERVAL = 1.0 / RATE_LIMIT_RPS

# Circuit breaker: after N consecutive failures, stop trying for cooldown
CIRCUIT_BREAKER_THRESHOLD = 3
CIRCUIT_BREAKER_COOLDOWN = 60  # seconds


class CircuitBreaker:
    """Circuit breaker — stops making requests after consecutive failures."""

    def __init__(
        self,
        threshold: int = CIRCUIT_BREAKER_THRESHOLD,
        cooldown: float = CIRCUIT_BREAKER_COOLDOWN,
    ) -> None:
        self._threshold = threshold
        self._cooldown = cooldown
        self._failures = 0
        self._opened_at: float = 0.0

    @property
    def is_open(self) -> bool:
        """True when circuit is tripped (too many failures, in cooldown)."""
        if self._failures < self._threshold:
            return False
        elapsed = time.monotonic() - self._opened_at
        if elapsed > self._cooldown:
            self._failures = 0
            return False
        return True

    def record_success(self) -> None:
        self._failures = 0

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._threshold:
            now = time.monotonic()
            # Reset cooldown timer if previous cooldown expired
            if self._opened_at == 0.0 or (now - self._opened_at) > self._cooldown:
                self._opened_at = now
                logger.warning(
                    "Circuit breaker tripped after %d failures, cooling down for %ds",
                    self._failures,
                    self._cooldown,
                )

    @property
    def failure_count(self) -> int:
        return self._failures


class RateLimiter:
    """Simple token-bucket rate limiter for async operations."""

    def __init__(self, min_interval: float = RATE_LIMIT_MIN_INTERVAL) -> None:
        self._min_interval = min_interval
        self._last_request: float = 0.0

    async def acquire(self) -> None:
        """Wait until enough time has passed since the last request."""
        now = time.monotonic()
        elapsed = now - self._last_request
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request = time.monotonic()


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
        self._rate_limiter = RateLimiter()
        self._circuit_breaker = CircuitBreaker()
        self._cache = CacheManager(cache_dir=Path("cache"))

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
        """Fetch fully rendered HTML content for a Salesforce Help URL.

        Args:
            url: The page URL to fetch.
            page: Optional existing Playwright ``Page`` to reuse.
            expand_toc: Whether to expand table-of-contents/navigation sections
                before extraction. Set to ``False`` to skip TOC expansion
                (typically faster, but may return less complete content).

        Returns:
            The rendered HTML as a string when a valid response is obtained.
            Returns ``None`` if all retry attempts fail or only insufficient
            content is retrieved.
        """
        logger.info("Fetching URL: %s", url)

        if self._circuit_breaker.is_open:
            logger.warning("Circuit breaker open — skipping fetch for %s", url)
            return None

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
                    self._circuit_breaker.record_success()
                    return html_content
                logger.warning(
                    "Attempt %d returned insufficient content (%d bytes)",
                    attempt,
                    len(html_content or ""),
                )
            except Exception as e:
                logger.error("Attempt %d failed: %s", attempt, e)
                self._circuit_breaker.record_failure()

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
        """Core Playwright fetch logic with resilient wait strategy.

        Args:
            url: The Salesforce Help URL to fetch.
            page: Optional existing Playwright page to reuse. If omitted, a standalone
                page (and browser when needed) is created for this request.
            expand_toc: Whether to expand table-of-contents/accordion content before
                extraction.
            return_text: When ``False`` (default), return rendered HTML content.
                When ``True``, return extracted visible text content instead.

        Returns:
            The fetched content as a string (HTML or text based on ``return_text``),
            or ``None`` if fetching fails.
        """
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
        """Internal execution of fetch logic on a provided page object."""
        await self._rate_limiter.acquire()
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
        """Click collapsed tree nodes in the ToC to reveal all topics.

        Checks element visibility and attachment before clicking to prevent
        stale element exceptions when the DOM updates during iteration.
        """
        try:
            collapsed = await page.query_selector_all('li[role="treeitem"][aria-expanded="false"]')
            expanded_count = 0
            for node in collapsed:
                try:
                    is_visible = await node.is_visible()
                    if not is_visible:
                        continue
                    box = await node.bounding_box()
                    if box is None:
                        continue
                    await node.scroll_into_view_if_needed()
                    await node.click()
                    await page.wait_for_timeout(300)
                    expanded_count += 1
                except Exception as e:
                    logger.debug("Falha ao expandir nó de ToC: %s", e)
            if expanded_count > 0:
                logger.info("Expanded %d collapsed ToC nodes", expanded_count)
        except Exception as e:
            logger.debug("ToC expansion skipped: %s", e)

    async def extract_toc_html(self, url: str, page: Optional[Page] = None) -> Optional[str]:
        """Extract just the ToC HTML from a release notes page.

        Loads the page and returns the HTML of the navigation tree container.
        Falls back to returning full page content if the ToC selector is not found
        after a successful page load.

        Returns:
            Optional[str]: ToC HTML when found; otherwise full page HTML when extraction
            succeeds but no ToC container is matched; ``None`` when page creation, navigation,
            or extraction raises an exception.
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
        """Navigate to URL and extract the ToC container HTML.

        Uses safe element access patterns — checks for None after query_selector
        and validates inner_html() result before returning.
        """
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
            if element is None:
                continue
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

        Uses CacheManager for TTL-based caching.
        Retries with exponential backoff on failure.
        """
        logger.info("Fetching raw text: %s", url)

        cached_text = self._cache.get(url)
        if cached_text and len(cached_text) > MIN_RAW_TEXT_LENGTH:
            logger.info("Using cached content (%d chars)", len(cached_text))
            return cast(str, cached_text)

        if self._circuit_breaker.is_open:
            logger.warning("Circuit breaker open — returning stale cache if available for %s", url)
            # The current CacheManager.get already handles TTL, so we'd need a 'get_stale'
            # but for now we just return None or rely on the user wanting fresh data.
            return None

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                if not await self._ensure_browser():
                    logger.error("Cannot recover browser for attempt %d", attempt)
                    break

                text = await self._fetch_with_playwright(url, return_text=True)
                if text and len(text) > MIN_RAW_TEXT_LENGTH:
                    logger.info("Fetched raw text (%d chars, attempt %d)", len(text), attempt)
                    self._cache.set(url, text)
                    self._circuit_breaker.record_success()
                    return text
                logger.warning(
                    "Attempt %d: insufficient text content (%d chars)",
                    attempt,
                    len(text or ""),
                )
            except Exception as e:
                logger.error("Attempt %d failed: %s", attempt, e)
                self._circuit_breaker.record_failure()
                self._browser = None

            if attempt < MAX_RETRY_ATTEMPTS:
                delay = calculate_jittered_delay(RETRY_BASE_DELAY_SECONDS, attempt)
                logger.info("Retrying in %.1fs...", delay)
                await asyncio.sleep(delay)

        logger.error("All %d attempts failed for raw text: %s", MAX_RETRY_ATTEMPTS, url)
        return None

    async def _ensure_browser(self) -> bool:
        """Ensure the browser is running. Relaunch if crashed."""
        if self._browser and self._browser.is_connected():
            return True
        try:
            if self._playwright:
                self._browser = await self._playwright.chromium.launch(headless=True)
                logger.info("Browser relaunched successfully")
                return True
        except Exception as e:
            logger.error("Failed to relaunch browser: %s", e)
        return False

    async def download_pdf_from_button(self, page_url: str, dest: Path) -> bool:
        """Navigate to a page, click the PDF download button, and save the file.

        The Salesforce Help pages have a <button title="Open PDF"> that triggers
        a download or opens a new tab with the PDF. This method handles both cases.
        Reuses the existing browser when available; falls back to a standalone launch.
        """
        if dest.exists() and dest.stat().st_size > MIN_VALID_CONTENT_SIZE:
            logger.info("PDF already exists, skipping: %s (%d bytes)", dest, dest.stat().st_size)
            return True

        logger.info("Downloading PDF via button click: %s -> %s", page_url, dest)

        browser_to_close = None
        try:
            if self._browser:
                browser = self._browser
                context = await browser.new_context(accept_downloads=True)
                page = await context.new_page()
            else:
                p = await async_playwright().start()
                browser_to_close = p
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(accept_downloads=True)
                page = await context.new_page()

            await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

            try:
                await page.wait_for_selector("button[title='Open PDF']", timeout=15000)
            except Exception:
                logger.warning("PDF button not found on %s", page_url)
                await context.close()
                if browser_to_close:
                    await browser.close()
                    await browser_to_close.stop()
                return False

            async with page.expect_download(timeout=30000) as download_info:
                await page.click("button[title='Open PDF']")

            download = await download_info.value
            await download.save_as(str(dest))

            await context.close()
            if browser_to_close:
                await browser.close()
                await browser_to_close.stop()

            if dest.exists() and dest.stat().st_size > MIN_VALID_CONTENT_SIZE:
                logger.info("PDF downloaded via button: %s (%d bytes)", dest, dest.stat().st_size)
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
