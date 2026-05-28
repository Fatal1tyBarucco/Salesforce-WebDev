"""Main orchestrator for Salesforce release notes scraping (async version)."""
import asyncio
import logging
from typing import Dict, Optional

from scraper import SalesforceReleaseScraper
from parser import ReleaseNoteParser
from generator import MarkdownGenerator
from logger import setup_logging
from config import RELEASES_TO_MONITOR, TOPICS_OF_INTEREST

logger = logging.getLogger(__name__)

async def main() -> None:
    """Async main function to orchestrate scraping, parsing, and generation."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction process (async).")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNoteParser()
    generator = MarkdownGenerator()

    for release_name in RELEASES_TO_MONITOR:
        logger.info(f"Processing release: {release_name}")
        try:
            # 1. Extract (async)
            html_content: Optional[str] = await scraper.fetch_release_notes(release_name)
            if not html_content:
                logger.error(f"Failed to fetch HTML for {release_name}. Skipping.")
                continue

            # 2. Parse (sync)
            parsed_data: Dict[str, str] = parser.parse_html(html_content, release_name, TOPICS_OF_INTEREST)
            if not parsed_data:
                logger.warning(f"No relevant content found for {release_name}.")
                continue

            # 3. Generate Markdown (sync)
            generator.write_markdown_files(release_name, parsed_data)

        except Exception as e:
            logger.exception(f"An unexpected error occurred while processing {release_name}: {e}")

    # 4. Update README
    generator.update_readme_index(RELEASES_TO_MONITOR)
    logger.info("Salesforce Release Notes extraction process finished.")

if __name__ == "__main__":
    asyncio.run(main())