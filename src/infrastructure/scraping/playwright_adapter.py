"""Playwright-based scraper adapter implementing ScraperPort."""

from __future__ import annotations

from typing import Any

import asyncio
import hashlib
import logging
import random
import time
import uuid
from pathlib import Path
from types import TracebackType
from urllib.parse import urlparse

from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError as PlaywrightTimeout
from playwright.async_api import Browser, Page, Playwright, async_playwright

from src.cache_manager import CacheManager
from src.circuit_breaker import CircuitBreaker
from src.config import REQUEST_TIMEOUT_SECONDS, RETRY_BASE_DELAY_SECONDS
from src.domain.scraper import (
    ScraperConfig,
    ScraperError,
    ScraperErrorCode,
    ScraperMetrics,
    ScraperPort,
    SelectorContract,
    DEFAULT_SELECTOR_CONTRACTS,
)
from src.infrastructure.scraping.cache_adapter import ScraperCacheAdapter
from src.infrastructure.scraping.rate_limiter import AsyncRateLimiter
from src.infrastructure.scraping.observability import ScraperObservabilityAdapter

logger = logging.getLogger(__name__)


def calculate_jittered_delay(base_delay: float, attempt: int, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay with jitter."""
    exponential_delay = min(base_delay * (2**attempt), max_delay)
    jitter = random.uniform(0, base_delay)
    return float(min(exponential_delay + jitter, max_delay))


class PlaywrightScraperAdapter(ScraperPort):
    """Resilient Playwright-based scraper for Salesforce Help."""

    def __init__(
        self,
        config: ScraperConfig | None = None,
        selector_contracts: tuple[SelectorContract, ...] = DEFAULT_SELECTOR_CONTRACTS,
        cache: ScraperCacheAdapter | None = None,
        rate_limiter: AsyncRateLimiter | None = None,
        observability: ScraperObservabilityAdapter | None = None,
    ) -> None:
        self.config = config or ScraperConfig()
        self.selector_contracts = selector_contracts
        self.cache = cache or ScraperCacheAdapter(CacheManager(cache_dir=self.config.cache_dir))
        self.rate_limiter = rate_limiter or AsyncRateLimiter(
            rps=self.config.rate_limit_rps, burst=self.config.rate_limit_burst
        )
        self.observability = observability or ScraperObservabilityAdapter()

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._circuit_breaker = CircuitBreaker(
            threshold=self.config.circuit_breaker_threshold,
            cooldown=self.config.circuit_breaker_cooldown_seconds,
        )

        # Selector validation cache
        self._selector_cache: dict[str, str] = {}

    async def __aenter__(self) -> PlaywrightScraperAdapter:
        await self._ensure_browser()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._close_browser()

    async def _ensure_browser(self) -> bool:
        """Ensure browser is running, launch if needed."""
        if self._browser and self._browser.is_connected():
            return True

        try:
            if not self._playwright:
                self._playwright = await async_playwright().start()
                logger.info("Playwright instance started")

            self._browser = await self._playwright.chromium.launch(
                headless=self.config.headless,
                args=list(self.config.browser_args),
            )
            logger.info("Browser launched successfully")
            return True
        except (PlaywrightError, OSError) as e:
            logger.error("Failed to launch browser: %s", e)
            return False

    async def _close_browser(self) -> None:
        """Close browser and playwright cleanly."""
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._playwright:
            await self._playwright.stop()
            self._playwright = None

    def _get_correlation_id(self) -> str:
        """Generate correlation ID for request tracing."""
        return uuid.uuid4().hex[:12]

    async def _find_working_selector(self, page: Page, contract: SelectorContract) -> str | None:
        """Find first working selector from contract, with caching."""
        cache_key = (
            f"{contract.name}:{hashlib.md5(str(contract.selectors).encode()).hexdigest()[:8]}"
        )

        if cache_key in self._selector_cache:
            selector = self._selector_cache[cache_key]
            element = await page.query_selector(selector)
            if element:
                return selector

        for selector in contract.selectors:
            element = await page.query_selector(selector)
            if element:
                self._selector_cache[cache_key] = selector
                return selector

        return None  # type: ignore[return-value]

    async def _extract_with_selectors(self, page: Page, contract: SelectorContract) -> str | None:
        """Extract content using selector contract."""
        selector = await self._find_working_selector(page, contract)
        if not selector:
            return None  # type: ignore[return-value]

        element = await page.query_selector(selector)
        if not element:
            return None  # type: ignore[return-value]

        html = await element.inner_html()
        if html and len(html) >= (
            self.config.min_toc_html_size
            if contract.name == "toc"
            else self.config.min_valid_content_size
        ):
            logger.debug(
                "Extracted %s with selector '%s' (%d bytes)", contract.name, selector, len(html)
            )
            return str(html)

        return None  # type: ignore[return-value]

    async def _wait_for_content(self, page: Page, correlation_id: str) -> None:
        """Wait for page content to be ready with multiple strategies."""
        try:
            await page.wait_for_selector(
                "ul.tree, li[role='treeitem'], article, table, main",
                timeout=self.config.selector_timeout_seconds * 1000,
            )
        except PlaywrightTimeout, PlaywrightError:
            logger.debug("[%s] Selector wait timeout, using fallback delay", correlation_id)

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(self.config.scroll_wait_seconds * 1000)

    async def _expand_toc(self, page: Page, correlation_id: str) -> int:
        """Expand all collapsed TOC nodes."""
        expanded = 0
        try:
            collapsed = await page.query_selector_all('li[role="treeitem"][aria-expanded="false"]')
            for node in collapsed:
                try:
                    if not await node.is_visible():
                        continue
                    box = await node.bounding_box()
                    if box is None:
                        continue
                    await node.scroll_into_view_if_needed()
                    await node.click()
                    await page.wait_for_timeout(self.config.toc_expand_wait_seconds * 1000)
                    expanded += 1
                except (PlaywrightTimeout, PlaywrightError, OSError) as e:
                    logger.debug("[%s] Failed to expand TOC node: %s", correlation_id, e)

            if expanded > 0:
                logger.info("[%s] Expanded %d TOC nodes", correlation_id, expanded)
        except (PlaywrightError, OSError) as e:
            logger.debug("[%s] TOC expansion skipped: %s", correlation_id, e)

        return expanded

    async def _exec_fetch(
        self,
        url: str,
        page: Page,
        *,
        expand_toc: bool = True,
        return_text: bool = False,
        correlation_id: str,
    ) -> str:
        """Execute fetch on provided page."""
        await self.rate_limiter.acquire()

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.config.navigation_timeout_seconds * 1000,
            )
        except (PlaywrightTimeout, PlaywrightError) as e:
            raise ScraperError(
                f"Navigation failed: {e}",
                code=ScraperErrorCode.TIMEOUT,
                url=url,
                original_error=e,
            )

        await self._wait_for_content(page, correlation_id)

        if expand_toc:
            await self._expand_toc(page, correlation_id)

        if return_text:
            return str(await page.inner_text("body"))

        return str(await page.content())

    def _validate_content(self, content: str | None, min_size: int) -> bool:
        """Validate content meets minimum size."""
        return content is not None and len(content) >= min_size

    async def _validate_layout(self, url: str, html: str, correlation_id: str) -> None:
        """Validate selector contracts against HTML to detect layout changes."""
        failed = []

        for contract in self.selector_contracts:
            if not contract.required:
                continue
            valid, error = contract.validate(html)
            if not valid:
                failed.append(contract.name)
                logger.warning("[%s] Layout change detected: %s", correlation_id, contract.name)

        if failed:
            self.observability.log_layout_change(url, failed, correlation_id)

    async def fetch_html(self, url: str, *, expand_toc: bool = True) -> str | None:
        """Fetch fully rendered HTML from URL."""
        correlation_id = self._get_correlation_id()
        start_time = time.perf_counter()
        logger.info("[%s] Fetching HTML: %s", correlation_id, url)

        if self._circuit_breaker.is_open:
            logger.warning("[%s] Circuit breaker open, skipping fetch", correlation_id)
            self.observability.record_metrics(
                ScraperMetrics(
                    url=url,
                    attempt=0,
                    success=False,
                    latency_ms=0,
                    content_size=0,
                    error_code=ScraperErrorCode.CIRCUIT_OPEN,
                    correlation_id=correlation_id,
                    circuit_breaker_state="open",
                )
            )
            return None  # type: ignore[return-value]

        # Check cache first
        cached = await self.cache.get(url)
        if cached and self._validate_content(cached, self.config.min_valid_content_size):
            logger.info("[%s] Cache hit for %s (%d bytes)", correlation_id, url, len(cached))
            self.observability.record_metrics(
                ScraperMetrics(
                    url=url,
                    attempt=0,
                    success=True,
                    latency_ms=0,
                    content_size=len(cached),
                    cache_hit=True,
                    correlation_id=correlation_id,
                )
            )
            return cached

        for attempt in range(1, self.config.max_retry_attempts + 1):
            try:
                if not await self._ensure_browser():
                    raise ScraperError(
                        "Cannot launch browser",
                        code=ScraperErrorCode.BROWSER_CRASH,
                        url=url,
                    )

                if not self._browser:
                    raise ScraperError(
                        "Browser not available", code=ScraperErrorCode.BROWSER_CRASH, url=url
                    )

                context = await self._browser.new_context(accept_downloads=True)
                page = await context.new_page()

                try:
                    html = await self._exec_fetch(
                        url,
                        page,
                        expand_toc=expand_toc,
                        return_text=False,
                        correlation_id=correlation_id,
                    )

                    if self._validate_content(html, self.config.min_valid_content_size):
                        # Validate selector contracts (detect layout changes)
                        await self._validate_layout(url, html, correlation_id)

                        # Cache successful result
                        await self.cache.set(url, html, self.config.cache_ttl_seconds)

                        latency_ms = int((time.perf_counter() - start_time) * 1000)
                        self.observability.record_metrics(
                            ScraperMetrics(
                                url=url,
                                attempt=attempt,
                                success=True,
                                latency_ms=latency_ms,
                                content_size=len(html),
                                correlation_id=correlation_id,
                            )
                        )
                        self._circuit_breaker.record_success()
                        return html

                    logger.warning(
                        "[%s] Attempt %d: insufficient content (%d bytes)",
                        correlation_id,
                        attempt,
                        len(html or ""),
                    )

                finally:
                    await page.close()
                    await context.close()

            except ScraperError as e:
                logger.error("[%s] Attempt %d failed: %s", correlation_id, attempt, e)
                self._circuit_breaker.record_failure()

                if not e.retryable or attempt == self.config.max_retry_attempts:
                    self.observability.record_metrics(
                        ScraperMetrics(
                            url=url,
                            attempt=attempt,
                            success=False,
                            latency_ms=0,
                            content_size=0,
                            error_code=e.code,
                            correlation_id=correlation_id,
                        )
                    )
                    raise

            except (PlaywrightError, OSError, TimeoutError) as e:
                logger.error("[%s] Attempt %d error: %s", correlation_id, attempt, e)
                self._circuit_breaker.record_failure()

            if attempt < self.config.max_retry_attempts:
                delay = calculate_jittered_delay(
                    RETRY_BASE_DELAY_SECONDS, attempt, self.config.max_retry_delay_seconds
                )
                logger.info("[%s] Retrying in %.1fs...", correlation_id, delay)
                await asyncio.sleep(delay)

        logger.error(
            "[%s] All %d attempts failed for %s",
            correlation_id,
            self.config.max_retry_attempts,
            url,
        )
        return None  # type: ignore[return-value]

    async def fetch_text(self, url: str) -> str | None:
        """Fetch extracted text content from URL."""
        correlation_id = self._get_correlation_id()
        logger.info("[%s] Fetching text: %s", correlation_id, url)

        if self._circuit_breaker.is_open:
            return None  # type: ignore[return-value]

        # Check cache
        cache_key = f"text:{url}"
        cached = await self.cache.get(cache_key)
        if cached and len(cached) >= self.config.min_raw_text_length:
            return cached

        for attempt in range(1, self.config.max_retry_attempts + 1):
            try:
                if not await self._ensure_browser():
                    return None  # type: ignore[return-value]

                if not self._browser:
                    return None  # type: ignore[return-value]

                context = await self._browser.new_context()
                page = await context.new_page()
                try:
                    text = await self._exec_fetch(
                        url, page, return_text=True, correlation_id=correlation_id
                    )

                    if text and len(text) >= self.config.min_raw_text_length:
                        await self.cache.set(cache_key, text, self.config.cache_ttl_seconds)
                        return text

                finally:
                    await page.close()
                    await context.close()

            except (ScraperError, PlaywrightError, OSError, TimeoutError) as e:
                logger.error("[%s] Attempt %d failed: %s", correlation_id, attempt, e)

            if attempt < self.config.max_retry_attempts:
                await asyncio.sleep(calculate_jittered_delay(RETRY_BASE_DELAY_SECONDS, attempt))

        return None  # type: ignore[return-value]

    async def fetch_toc(self, url: str) -> str | None:
        """Fetch table of contents HTML from URL."""
        correlation_id = self._get_correlation_id()
        logger.info("[%s] Fetching TOC: %s", correlation_id, url)

        if self._circuit_breaker.is_open:
            return None  # type: ignore[return-value]

        for attempt in range(1, self.config.max_retry_attempts + 1):
            try:
                if not await self._ensure_browser():
                    return None  # type: ignore[return-value]

                if not self._browser:
                    return None  # type: ignore[return-value]

                context = await self._browser.new_context()
                page = await context.new_page()
                try:
                    await page.goto(
                        url, wait_until="domcontentloaded", timeout=REQUEST_TIMEOUT_SECONDS * 1000
                    )
                    await page.wait_for_timeout(5000)
                    await self._expand_toc(page, correlation_id)

                    toc_html = await self._extract_with_selectors(
                        page,
                        SelectorContract(
                            name="toc",
                            selectors=(".toc-container", "ul.tree", '[role="tree"]', "nav.toc"),
                            required=True,
                        ),
                    )

                    if toc_html:
                        return toc_html

                    # Fallback: return full page
                    logger.warning(
                        "[%s] No TOC container found, returning full page", correlation_id
                    )
                    return str(await page.content())

                finally:
                    await page.close()
                    await context.close()

            except (ScraperError, PlaywrightError, OSError, TimeoutError) as e:
                logger.error("[%s] Attempt %d failed: %s", correlation_id, attempt, e)

            if attempt < self.config.max_retry_attempts:
                await asyncio.sleep(calculate_jittered_delay(RETRY_BASE_DELAY_SECONDS, attempt))

        return None  # type: ignore[return-value]

    async def fetch_features_with_links(self, url: str) -> list[dict[str, str]]:
        """Fetch feature names and their documentation links."""
        correlation_id = self._get_correlation_id()
        logger.info("[%s] Fetching features with links: %s", correlation_id, url)

        if self._circuit_breaker.is_open:
            return []

        html = await self.fetch_html(url, expand_toc=False)
        if not html:
            return []

        return self._extract_features_from_html(html)

    @staticmethod
    def _extract_features_from_html(html: str) -> list[dict[str, str]]:
        """Extract feature names and documentation links from HTML."""
        from bs4 import BeautifulSoup

        def _is_allowed_salesforce_href(href: str) -> bool:
            if href.startswith("/"):
                return True
            parsed = urlparse(href)
            if parsed.scheme not in {"http", "https"}:
                return False
            host = parsed.hostname
            if not host:
                return False
            return host == "salesforce.com" or host.endswith(".salesforce.com")

        features: list[dict[str, str]] = []
        soup = BeautifulSoup(html, "lxml")

        # Strategy 1: Table rows
        for tr in soup.find_all("tr"):
            cells = tr.find_all("td")
            if not cells:
                continue
            name = cells[0].get_text(strip=True)
            if not name or len(name) < 3:
                continue
            link = tr.find("a", href=True)
            docs_url = ""
            if link:
                href = link.get("href", "")
                if isinstance(href, str) and _is_allowed_salesforce_href(href):
                    docs_url = (
                        href if href.startswith("http") else f"https://help.salesforce.com{href}"
                    )
            features.append({"name": name, "docs_url": docs_url})

        # Strategy 2: List items
        if not features:
            for li in soup.find_all("li"):
                link = li.find("a", href=True)
                if not link:
                    continue
                name = link.get_text(strip=True)
                if not name or len(name) < 3:
                    continue
                href = link.get("href", "")
                if (
                    isinstance(href, str)
                    and "release-notes" in href
                    and _is_allowed_salesforce_href(href)
                ):
                    docs_url = (
                        href if href.startswith("http") else f"https://help.salesforce.com{href}"
                    )
                    features.append({"name": name, "docs_url": docs_url})

        # Deduplicate
        seen = set()
        unique = []
        for f in features:
            if f["name"] not in seen:
                seen.add(f["name"])
                unique.append(f)

        return unique

    async def fetch_multiple(self, urls: list[str], max_concurrent: int = 5) -> list[str | None]:
        """Fetch multiple URLs concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _fetch_one(url: str) -> str | None:
            async with semaphore:
                return await self.fetch_html(url)

        return await asyncio.gather(*(_fetch_one(u) for u in urls))

    async def download_pdf(self, page_url: str, dest: Path) -> bool:
        """Download PDF from page (via button click or direct URL)."""
        if dest.exists() and dest.stat().st_size > 1000:
            return True

        if not await self._ensure_browser():
            return False

        if not self._browser:
            return False

        context = await self._browser.new_context(accept_downloads=True)
        page = await context.new_page()

        try:
            await page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

            # Try button click first
            try:
                await page.wait_for_selector("button[title='Open PDF']", timeout=15000)
                async with page.expect_download(timeout=30000) as download_info:
                    await page.click("button[title='Open PDF']")
                download = await download_info.value
                await download.save_as(str(dest))
                return dest.exists() and dest.stat().st_size > 1000
            except PlaywrightTimeout, PlaywrightError:
                pass

            # Fallback: direct URL download
            pdf_links = await page.query_selector_all("a[href$='.pdf']")
            for link in pdf_links:
                href = await link.get_attribute("href")
                if href and "release-notes" in href:
                    full_url = (
                        href if href.startswith("http") else f"https://help.salesforce.com{href}"
                    )
                    import urllib.request

                    req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
                    response = await asyncio.to_thread(urllib.request.urlopen, req, timeout=30)
                    dest.write_bytes(response.read())
                    return dest.exists() and dest.stat().st_size > 1000

            return False

        finally:
            await context.close()

    async def health_check(self) -> bool:
        """Check if scraper is functional."""
        try:
            if not await self._ensure_browser():
                return False
            if not self._browser:
                return False
            page = await self._browser.new_page()
            await page.goto(
                "https://help.salesforce.com", wait_until="domcontentloaded", timeout=10000
            )
            await page.close()
            return True
        except Exception:
            return False


# Backwards compatibility alias
SalesforceReleaseScraper = PlaywrightScraperAdapter


# ============================================================
# Backwards Compatibility Wrapper
# Implements the old PlaywrightScrapingAdapter interface for characterization tests
# ============================================================


class PlaywrightScrapingAdapter:
    """Legacy interface wrapper for characterization tests."""

    def __init__(
        self,
        headless: bool = True,
        timeout_ms: int = 30000,
        wait_for_selector: str | None = "main",
    ) -> None:
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.wait_for_selector = wait_for_selector
        self._browser = None
        self._playwright = None
        self.name = "playwright_scraping"

        # Create config from legacy params
        self._config = ScraperConfig(
            headless=headless,
            navigation_timeout_seconds=timeout_ms // 1000,
            selector_timeout_seconds=timeout_ms // 1000,
        )
        self._adapter = PlaywrightScraperAdapter(config=self._config)

    @property
    def browser(self) -> Any:
        return self._browser

    @browser.setter
    def browser(self, value: Any) -> None:
        self._browser = value

    @property
    def playwright(self) -> Any:
        return self._playwright

    @playwright.setter
    def playwright(self, value: Any) -> None:
        self._playwright = value

    async def execute(self, url: str) -> str:  # type: ignore[no-untyped-def]
        """Execute scraping and return HTML (legacy interface)."""
        # Use the same approach as the original legacy code for mock compatibility
        from playwright.async_api import async_playwright

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless)
            page = await browser.new_page()

            try:
                response = await page.goto(
                    url,
                    wait_until="networkidle" if self.wait_for_selector else "domcontentloaded",
                    timeout=self.timeout_ms,
                )
                if response and response.status >= 400:
                    raise RuntimeError(f"HTTP {response.status} for {url}")

                if self.wait_for_selector:
                    try:
                        await page.wait_for_selector(
                            self.wait_for_selector,
                            timeout=self.timeout_ms,
                        )
                    except Exception:
                        pass  # Ignore selector timeout in legacy mode

                html = await page.content()
                return html
            finally:
                await browser.close()

    async def fetch_page_raw_text(self, url: str) -> str | None:  # type: ignore[no-untyped-def]
        """Fetch and extract text from page (legacy interface)."""
        try:
            html = await self.execute(url)
            # Extract text from HTML (simple extraction)
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "lxml")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text(separator=" ", strip=True)  # type: ignore[return-value]
        except Exception:
            return None  # type: ignore[return-value]

    async def __aenter__(self) -> PlaywrightScrapingAdapter:
        await self._adapter.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self._adapter.__aexit__(exc_type, exc_val, exc_tb)


class CachedScrapingAdapter:
    """Legacy cached scraping adapter interface."""

    def __init__(
        self,
        base_adapter: PlaywrightScrapingAdapter,
        cache_dir: str = "cache",
        ttl_seconds: int = 3600,
    ) -> None:
        self._base = base_adapter
        self._cache_dir = cache_dir
        self._ttl = ttl_seconds
        self.name = f"cached_{base_adapter.name}"
        self._cache = ScraperCacheAdapter(CacheManager(cache_dir=Path(cache_dir)))

    @property
    def base_adapter(self) -> PlaywrightScrapingAdapter:
        return self._base

    @property
    def cache_dir(self) -> str:
        return self._cache_dir

    @property
    def ttl_seconds(self) -> int:
        return self._ttl

    async def execute(self, url: str) -> str:  # type: ignore[no-untyped-def]
        """Execute with caching (legacy interface)."""
        import hashlib
        from pathlib import Path

        # Use legacy cache key format: sha256(url)[:16]
        cache_key = hashlib.sha256(url.encode()).hexdigest()[:16]
        cache_path = Path(self._cache_dir) / f"{cache_key}.html"

        # Check cache file
        if cache_path.exists():
            # Check TTL
            import time

            if time.time() - cache_path.stat().st_mtime < self._ttl:
                return cache_path.read_text()
            else:
                cache_path.unlink()

        # Fetch and cache
        html = await self.base_adapter.execute(url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(html)
        return html


# Export the legacy names
__all__ = [
    "PlaywrightScraperAdapter",
    "SalesforceReleaseScraper",
    "PlaywrightScrapingAdapter",  # Legacy
    "CachedScrapingAdapter",  # Legacy
]
