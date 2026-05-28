# src/scraper.py
import asyncio
import logging
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page
from config import BASE_URL, MAX_RETRIES

logger = logging.getLogger(__name__)

class SalesforceReleaseScraper:
    """Fetches HTML content from Salesforce release notes URLs using a headless browser."""

    async def fetch_release_notes(self, release_name: str) -> Optional[str]:
        """
        Fetches the fully rendered HTML content for a given Salesforce release topic page.
        """
        url: str = f"{BASE_URL}{release_name}"
        logger.info(f"Fetching URL with Playwright: {url}")

        for attempt in range(MAX_RETRIES):
            try:
                async with async_playwright() as p:
                    browser: Browser = await p.chromium.launch(headless=True)
                    page: Page = await browser.new_page()
                    await page.goto(url, wait_until='networkidle')  # Aguarda a página carregar completamente
                    
                    # Aguarda um seletor que indica que o conteúdo principal foi carregado
                    await page.wait_for_selector('div.content', timeout=10000)
                    
                    html_content: str = await page.content()
                    await browser.close()
                    logger.info(f"Successfully fetched and rendered content from {url}")
                    return html_content
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"All attempts to fetch {url} have failed.")
                    return None