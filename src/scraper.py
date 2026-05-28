# src/scraper.py
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page
from .config import MAX_RETRY_ATTEMPTS

logger = logging.getLogger(__name__)

class SalesforceReleaseScraper:
    """Fetches HTML content from Salesforce release notes URLs using a headless browser."""

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetches the fully rendered HTML content for a given URL.
        """
        logger.info(f"Fetching URL with Playwright: {url}")

        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                async with async_playwright() as p:
                    browser: Browser = await p.chromium.launch(headless=True)
                    page: Page = await browser.new_page()
                    await page.goto(url, wait_until='networkidle')
                    await page.wait_for_selector('div.content', timeout=10000)
                    html_content: str = await page.content()
                    await browser.close()
                    logger.info(f"Successfully fetched content from {url}")
                    return html_content
            except Exception as e:
                logger.error(f"Attempt {attempt} failed: {e}")
                if attempt == MAX_RETRY_ATTEMPTS:
                    logger.error(f"All {MAX_RETRY_ATTEMPTS} attempts failed.")
        return None