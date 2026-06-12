"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Fetch the release notes index page for each release via Playwright
  2. Parse the index page to discover article links grouped by topic
  3. Build markdown artifacts with deep-scraped summaries (pt-BR)
  4. Update README with dynamic release index and top highlights
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from .config import BASE_URL, KNOWN_RELEASES, MONITORED_TOPICS, RELEASES_DIR
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import ReleaseNotesParser
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


async def run_pipeline():
    """Versão assíncrona do orquestrador para suportar deep scraping e resumos pt-BR."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction with Deep Scraping (pt-BR).")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    all_highlights: Dict[str, List[Dict[str, str]]] = {}

    async with scraper:
        # Processar todas as releases conhecidas
        for release in KNOWN_RELEASES:
            logger.info("Processando release: %s", release.name)
            highlights: List[Dict[str, str]] = []
            try:
                url = BASE_URL.format(release_id=release.release_id)
                logger.info("Index URL: %s", url)

                html_index = await scraper.fetch_page(url)
                if not html_index:
                    logger.warning("Sem conteúdo para %s", release.name)
                    continue

                soup_index = BeautifulSoup(html_index, "lxml")
                topic_links = parser.extract_article_links(soup_index, release.name)

                content_map = {topic.slug: [] for topic in MONITORED_TOPICS}

                for topic in MONITORED_TOPICS:
                    articles = topic_links.get(topic.slug, [])
                    if not articles:
                        continue

                    content_map[topic.slug].append(f"## {topic.display_name} — {release.name}")
                    content_map[topic.slug].append("")

                    # Limite de artigos por tópico para equilíbrio entre profundidade e tempo
                    limit = 8
                    for article in articles[:limit]:
                        logger.info("Deep scraping [%s]: %s", topic.display_name, article['title'])
                        
                        # Forçar pt-BR no link
                        article_url = article['url']
                        if "language=pt_BR" not in article_url:
                            sep = "&" if "?" in article_url else "?"
                            article_url += f"{sep}language=pt_BR"
                        
                        html_article = await scraper.fetch_page(article_url)
                        summary = "Resumo não disponível."
                        if html_article:
                            soup_article = BeautifulSoup(html_article, "lxml")
                            summary = parser.extract_article_summary(soup_article)

                        # Adicionar aos destaques da release (apenas os primeiros 5 globais)
                        if len(highlights) < 5:
                            highlights.append({
                                "title": article['title'],
                                "summary": summary,
                                "url": article_url,
                                "topic": topic.display_name
                            })

                        content_map[topic.slug].append(f"### {article['title']}")
                        content_map[topic.slug].append(f"{summary}")
                        content_map[topic.slug].append(f"\n[🔗 Leia mais no conteúdo original]({article_url})")
                        content_map[topic.slug].append("")

                all_highlights[release.slug] = highlights
                generator.generate(release, content_map, source_url=url)

            except Exception as e:
                logger.exception("Erro ao processar %s: %s", release.name, e)

    releases_list = generator.list_generated_releases()
    _update_readme(releases_list, all_highlights)


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


def _update_readme(releases: List[tuple[str, List[str]]], highlights: Dict[str, List[Dict[str, str]]]) -> None:
    """Atualiza o README.md com um índice dinâmico e destaques em português."""
    readme_path = Path("README.md")
    
    # Header e Introdução
    content = [
        "# 🚀 Salesforce Release Intelligence\n\n",
        "Pipeline automatizado para extrair, classificar e resumir as Salesforce Release Notes. "
        "Focado em entregar conhecimento técnico estruturado em português.\n\n"
    ]

    # Destaques (Highlights) - Seção opcional baseada na execução atual
    if highlights:
        content.append("## 🌟 Destaques das Releases Processadas (pt-BR)\n\n")
        for slug in sorted(highlights.keys(), reverse=True):
            items = highlights[slug]
            if not items:
                continue
                
            content.append(f"### 🔥 {slug.replace('_', ' ').title()}\n\n")
            for item in items:
                content.append(f"- **{item['title']}** ({item['topic']})\n")
                content.append(f"  {item['summary'][:300]}...\n")
                content.append(f"  [Leia mais]({item['url']})\n\n")

    # Índice Geral
    content.append("## 📋 Arquivo Completo de Notas\n\n")
    for release_slug, topics in sorted(releases, reverse=True):
        release_name = release_slug.replace('_', ' ').title()
        content.append(f"### {release_name}\n")
        for topic in topics:
            content.append(f"- [{topic.upper()}](./releases/{release_slug}/{topic}.md)\n")
        content.append("")

    readme_path.write_text("".join(content), encoding="utf-8")
    logger.info("README.md atualizado com sucesso.")


if __name__ == "__main__":
    main()
