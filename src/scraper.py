"""Scraper for Salesforce Help release notes using Playwright headless browser.

The Salesforce Help portal is a SPA that requires JavaScript rendering.
This scraper uses a resilient strategy:
1. Load page with 'domcontentloaded' (not 'networkidle' which never settles)
2. Wait for JS rendering with a manual delay
3. Scroll to trigger lazy-loaded content
4. Try multiple selectors before extracting content
"""

import asyncio
import logging
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page

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

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetches the fully rendered HTML content for a given URL."""
        logger.info("Fetching URL with Playwright: %s", url)

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                html_content = await self._fetch_with_playwright(url)
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

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Core Playwright fetch logic with resilient wait strategy."""
        async with async_playwright() as p:
            browser: Browser = await p.chromium.launch(headless=True)
            page: Page = await browser.new_page()

            # Step 1: Navigate with domcontentloaded (not networkidle)
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

            # Step 4: Try content selectors
            content_found = False
            for selector in self.CONTENT_SELECTORS:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        logger.info("Found content selector: %s", selector)
                        content_found = True
                        break
                except Exception:
                    continue

            if not content_found:
                logger.warning(
                    "No known content selector found — extracting full page body"
                )

            # Step 5: Extract content
            html_content: str = await page.content()
            await browser.close()
            return html_content