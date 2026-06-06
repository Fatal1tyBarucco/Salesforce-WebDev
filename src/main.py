"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Fetch the release notes index page for each release via Playwright
  2. Parse the index page to discover article links grouped by topic
  3. Build markdown artifacts from the index summaries + article links
  4. Update README with dynamic release index
"""

import asyncio
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .config import BASE_URL, KNOWN_RELEASES, RELEASES_DIR
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import ReleaseNotesParser
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


def main() -> None:
    """Orquestra a extração a partir do Salesforce Help (web scraping)."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction from web.")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    for release in KNOWN_RELEASES:
        logger.info("Processando release: %s", release.name)
        try:
            url = BASE_URL.format(release_id=release.release_id)
            logger.info("Index URL: %s", url)

            html_content = asyncio.run(scraper.fetch_page(url))
            if not html_content:
                logger.warning("Sem conteúdo para %s — pulando.", release.name)
                continue

            soup = BeautifulSoup(html_content, "lxml")

            # Extract article links grouped by topic
            topic_links = parser.extract_article_links(soup, release.name)

            # Build content from index links (fast approach — no individual article fetch)
            content_map = parser.build_topic_content_from_links(
                topic_links, soup, release.name
            )

            # Generate markdown artifacts
            generator.generate(release, content_map, source_url=url)

        except Exception as e:
            logger.exception("Erro ao processar %s: %s", release.name, e)

    # Update README with generated releases
    releases_list = generator.list_generated_releases()
    _update_readme(releases_list)


def _update_readme(releases: list[tuple[str, list[str]]]) -> None:
    """Atualiza o README.md com um índice dinâmico."""
    readme_path = Path("README.md")
    index_lines = [
        "# Salesforce Release Notes Knowledge Base\n",
        "Este repositório armazena as notas de versão extraídas automaticamente "
        "do Salesforce Help.\n",
        "## 📋 Releases Disponíveis\n",
    ]
    for release_slug, topics in sorted(releases, reverse=True):
        release_dir = f"./releases/{release_slug}/"
        index_lines.append(f"### {release_slug.replace('_', ' ').title()}\n")
        for topic in topics:
            index_lines.append(f"- [{topic}]({release_dir}{topic}.md)\n")
        index_lines.append("")

    readme_path.write_text("".join(index_lines), encoding="utf-8")
    logger.info("README.md atualizado com índice.")


if __name__ == "__main__":
    main()