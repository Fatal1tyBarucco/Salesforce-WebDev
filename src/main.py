"""Main orchestrator for Salesforce release notes scraping (async version)."""
import asyncio
import logging
from typing import Optional
from bs4 import BeautifulSoup

from .scraper import SalesforceReleaseScraper
from .parser import ReleaseNotesParser
from .generator import MarkdownGenerator
from .logger import setup_logging
from .config import KNOWN_RELEASES, MONITORED_TOPICS

logger = logging.getLogger(__name__)

# Mapeamento temporário: slug do tópico → ID do artigo na URL
TOPIC_ARTICLE_MAP = {
    "apex": "rn_development",
    "lwc": "rn_lwc",
    "flow": "rn_flow",
    "security": "rn_security",
    "integrations": "rn_integration",
}

async def main() -> None:
    """Async main function to orchestrate scraping, parsing, and generation."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction process (async).")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator()

    for release in KNOWN_RELEASES:
        logger.info(f"Processing release: {release.name}")
        for topic in MONITORED_TOPICS:
            article_id = TOPIC_ARTICLE_MAP.get(topic.slug)
            if not article_id:
                logger.warning(f"No article mapping for topic '{topic.slug}', skipping.")
                continue

            url = f"https://help.salesforce.com/s/articleView?id=release-notes.{article_id}.htm&release={release.release_id}&type=5"
            logger.info(f"Fetching {topic.slug} from {url}")

            try:
                html_content: Optional[str] = await scraper.fetch_page(url)
                if not html_content:
                    logger.error(f"Failed to fetch HTML for {topic.slug} in {release.name}. Skipping.")
                    continue

                soup = BeautifulSoup(html_content, "lxml")
                parsed_data = parser.parse(soup, release.name)

                # parsed_data é TopicContentMap (dict slug -> list[str])
                generator.generate(release, parsed_data, source_url=url)

            except Exception as e:
                logger.exception(f"Error processing {topic.slug} for {release.name}: {e}")

    logger.info("Salesforce Release Notes extraction process finished.")

if __name__ == "__main__":
    asyncio.run(main())