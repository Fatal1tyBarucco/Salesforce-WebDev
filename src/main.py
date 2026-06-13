"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Fetch the release notes page for each release via Playwright
  2. Parse the navigation tree to discover topics dynamically
  3. Deep-scrape each article for summaries (pt-BR)
  4. Generate Markdown artifacts per topic
  5. Update README with dynamic release index and collapsible highlights
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from bs4 import BeautifulSoup

from .config import (
    BASE_URL,
    KNOWN_RELEASES,
    MAX_CONCURRENT_PAGES,
    RELEASES_DIR,
    TopicNode,
)
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import ReleaseNotesParser
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


async def run_pipeline() -> None:
    """Orquestrador principal: scraping + geração de artefatos Markdown."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction (dynamic topics).")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    all_highlights: dict[str, dict[str, list[dict[str, str]]]] = {}

    async with scraper:
        for release in KNOWN_RELEASES:
            logger.info("Processando release: %s", release.name)
            try:
                url = BASE_URL.format(release_id=release.release_id)
                logger.info("Index URL: %s", url)

                html_index = await scraper.fetch_page(url)
                if not html_index:
                    logger.warning("Sem conteúdo para %s", release.name)
                    continue

                soup_index = BeautifulSoup(html_index, "lxml")
                topic_nodes = parser.extract_topic_tree(soup_index)

                if not topic_nodes:
                    logger.warning("Nenhum tópico extraído da árvore para %s", release.name)
                    continue

                release_highlights: dict[str, list[dict[str, str]]] = {}

                semaphore = asyncio.Semaphore(MAX_CONCURRENT_PAGES)

                tasks = [
                    _process_topic_node(
                        node=node,
                        scraper=scraper,
                        parser=parser,
                        release_slug=release.slug,
                        release_highlights=release_highlights,
                        semaphore=semaphore,
                    )
                    for node in topic_nodes
                ]

                await asyncio.gather(*tasks)

                all_highlights[release.slug] = release_highlights
                generator.generate(release, topic_nodes, source_url=url)

            except Exception as e:
                logger.exception("Erro ao processar %s: %s", release.name, e)

    releases_list = generator.list_generated_releases()
    _update_readme(releases_list, all_highlights)


async def _process_topic_node(
    node: TopicNode,
    scraper: SalesforceReleaseScraper,
    parser: ReleaseNotesParser,
    release_slug: str,
    release_highlights: dict[str, list[dict[str, str]]],
    semaphore: asyncio.Semaphore,
) -> None:
    """Deep-scrape artigos de um TopicNode e popula highlights (paralelo)."""
    all_articles = node.all_articles()

    if not all_articles:
        return

    logger.info(
        "Topic '%s': %d articles to deep-scrape",
        node.display_name,
        len(all_articles),
    )

    async def _scrape_one(article: dict[str, str]) -> dict[str, str] | None:
        async with semaphore:
            article_url = article.get("url", "")
            title = article.get("title", "Sem título")

            if not article_url:
                return None

            if "language=pt_BR" not in article_url:
                sep = "&" if "?" in article_url else "?"
                article_url += f"{sep}language=pt_BR"

            logger.info("Deep scraping [%s]: %s", node.display_name, title)

            page = await scraper._browser.new_page()  # type: ignore[union-attr]
            try:
                html_article = await scraper.fetch_page(
                    article_url, page, expand_toc=False
                )
                summary = "Resumo não disponível."
                if html_article:
                    soup_article = BeautifulSoup(html_article, "lxml")
                    summary = parser.extract_article_summary(soup_article)
            finally:
                await page.close()

            return {
                "title": title,
                "summary": summary,
                "url": article_url,
                "topic": node.display_name,
            }

    tasks = [_scrape_one(article) for article in all_articles]
    results = await asyncio.gather(*tasks)

    article_summaries = [r for r in results if r is not None]
    release_highlights[node.slug] = article_summaries

    child_tasks = [
        _process_topic_node(
            node=child,
            scraper=scraper,
            parser=parser,
            release_slug=release_slug,
            release_highlights=release_highlights,
            semaphore=semaphore,
        )
        for child in node.children
    ]
    if child_tasks:
        await asyncio.gather(*child_tasks)


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


def _update_readme(
    releases: list[tuple[str, list[str]]],
    highlights: dict[str, dict[str, list[dict[str, str]]]],
) -> None:
    """Atualiza o README.md com painel de status e resumos colapsáveis."""
    readme_path = Path("README.md")

    content: list[str] = [
        "![Salesforce Release Intelligence](./assets/banner.png)\n\n",
        "# 🚀 Salesforce Release Notes Intelligence\n\n",
        "Pipeline automatizado para extração, classificação e versionamento das "
        "**Salesforce Release Notes** como artefatos Markdown estruturados "
        "(*Knowledge-as-Code*).\n\n",
    ]

    content.extend(
        [
            "### ⚙️ CI/CD Status & Conformidade\n\n",
            "[![Python Quality & Validation]"
            "(https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/"
            "python-quality.yml/badge.svg)]"
            "(https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/"
            "python-quality.yml)\n",
            "![Python](https://img.shields.io/badge/Python-3.14-blue.svg?"
            "logo=python&logoColor=white) \n",
            "![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?"
            "logo=playwright&logoColor=white) \n",
            "![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg) \n",
            "![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg) \n",
            "![Black](https://img.shields.io/badge/Formatter-Black-000000.svg)\n\n",
        ]
    )

    content.extend(
        [
            "| Tecnologia / Ferramenta | Descrição | Status no Pipeline |\n",
            "| :--- | :--- | :---: |\n",
            "| 🐍 **Python 3.14** | Ambiente de execução principal | `Conforme` |\n",
            "| 🎭 **Playwright** | Scraper Headless para aplicações SPA do Salesforce Help | `Ativo` |\n",
            "| 🧪 **Pytest** | Suíte de testes unitários automatizados | `100% Cobertura` |\n",
            "| 🔍 **Mypy** | Verificação estática de tipos com modo estrito | `Strict` |\n",
            "| ⚡ **Ruff & Black** | Linter e formatação estrita de código (line-length = 100) | `Conforme` |\n\n",
            "---\n\n",
        ]
    )

    content.append("## 📋 Notas de Release e Resumos por Tópico\n\n")

    def get_release_emoji(name: str) -> str:
        name_lower = name.lower()
        if "winter" in name_lower:
            return "❄️"
        elif "summer" in name_lower:
            return "☀️"
        return "🌸"

    for release_slug, topics in sorted(releases, reverse=True):
        release_name = release_slug.replace("_", " ").title()
        emoji = get_release_emoji(release_name)

        content.append(f"### {emoji} {release_name}\n\n")

        release_highlights = highlights.get(release_slug, {})

        for topic_slug in topics:
            topic_emoji = "📄"
            display_name = topic_slug.upper().replace("_", " ")

            articles = release_highlights.get(topic_slug, [])

            if articles:
                num_changes = len(articles)
                plural = "alterações" if num_changes > 1 else "alteração"

                content.append("<details>\n")
                content.append(
                    f"<summary><b>{topic_emoji} {display_name} "
                    f"(Clique para expandir {num_changes} {plural})</b></summary>\n\n"
                )
                for article in articles:
                    content.append(f"* **{article['title']}**\n")
                    content.append(f"  {article['summary']}\n\n")

                content.append(
                    f"> 📄 **Notas Completas:** consulte os detalhes completos na página "
                    f"do tópico [{display_name}]"
                    f"(./releases/{release_slug}/{topic_slug}.md).\n"
                )
                content.append("</details>\n\n")
            else:
                content.append(
                    f"* {topic_emoji} **{display_name}**: "
                    f"Acesse o arquivo de notas de versão em "
                    f"[./releases/{release_slug}/{topic_slug}.md]"
                    f"(./releases/{release_slug}/{topic_slug}.md).\n"
                )
        content.append("\n---\n\n")

    readme_path.write_text("".join(content), encoding="utf-8")
    logger.info("README.md atualizado com painel moderno e resumos.")


if __name__ == "__main__":
    main()
