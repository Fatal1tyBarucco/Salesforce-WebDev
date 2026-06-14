"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Detect new releases by probing Salesforce for unseen release IDs
  2. Scrape only new releases (not already in releases/ dir)
  3. Deep-scrape each article for summaries (pt-BR)
  4. Generate Markdown artifacts per topic
  5. Update README organized chronologically (newest on top)
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup

from .config import (
    ARTICLE_FETCH_TIMEOUT_SECONDS,
    BASE_URL,
    KNOWN_RELEASES,
    MAX_CONCURRENT_PAGES,
    RELEASES_DIR,
    ReleaseInfo,
    TopicNode,
    build_release_info,
)
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import ReleaseNotesParser
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


def _find_existing_releases() -> set[str]:
    """Return slugs for release dirs that already exist in releases/."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return set()
    return {
        d.name for d in releases_dir.iterdir()
        if d.is_dir() and (d / "*.md" or any(d.glob("*.md")))
    }


def _highest_known_id() -> int:
    return max(r.release_id for r in KNOWN_RELEASES)


async def detect_new_releases(
    scraper: SalesforceReleaseScraper, parser: ReleaseNotesParser
) -> list[ReleaseInfo]:
    """Probe Salesforce for release IDs beyond what we know. Return new ones."""
    existing_slugs = _find_existing_releases()
    base_id = _highest_known_id()
    new_releases: list[ReleaseInfo] = []

    for offset in range(2, 20, 2):
        candidate_id = base_id + offset
        info = build_release_info(candidate_id)
        if info.slug in existing_slugs:
            logger.info("Release %s already exists locally, skipping probe", info.slug)
            continue

        url = BASE_URL.format(release_id=candidate_id)
        logger.info("Probing for new release: %s (id=%d)", info.name, candidate_id)

        html = await scraper.fetch_page(url, expand_toc=False)
        if not html or len(html) < 2000:
            logger.info("Release %s not found (id=%d)", info.name, candidate_id)
            break

        soup = BeautifulSoup(html, "lxml")
        topics = parser.extract_topic_tree(soup)
        if topics:
            logger.info("New release found: %s (%d topics)", info.name, len(topics))
            new_releases.append(info)
        else:
            logger.info("Release %s exists but no topics extracted", info.name)
            break

    return new_releases


async def run_pipeline() -> None:
    """Orquestrador principal: detecta release(s) novas, extrai, gera artefatos."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction.")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    args = sys.argv[1:]
    release_filter: str | None = None

    for i, arg in enumerate(args):
        if arg == "--release" and i + 1 < len(args):
            release_filter = args[i + 1]

    all_highlights: dict[str, dict[str, list[dict[str, str]]]] = {}

    async with scraper:
        releases_to_process: list[ReleaseInfo] = []

        if release_filter:
            for r in KNOWN_RELEASES:
                if r.slug == release_filter:
                    releases_to_process.append(r)
                    break
            if not releases_to_process:
                logger.error("Release '%s' not found in KNOWN_RELEASES", release_filter)
                return
        else:
            new_releases = await detect_new_releases(scraper, parser)
            releases_to_process = new_releases

            if not releases_to_process:
                logger.info("No new releases detected. Updating README only.")

        for release in releases_to_process:
            logger.info("Processing release: %s", release.name)
            try:
                url = BASE_URL.format(release_id=release.release_id)
                logger.info("Index URL: %s", url)

                html_index = await scraper.fetch_page(url)
                if not html_index:
                    logger.warning("No content for %s", release.name)
                    continue

                soup_index = BeautifulSoup(html_index, "lxml")
                topic_nodes = parser.extract_topic_tree(soup_index)

                if not topic_nodes:
                    logger.warning("No topics extracted for %s", release.name)
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
                logger.exception("Error processing %s: %s", release.name, e)

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
                html_article = await asyncio.wait_for(
                    scraper.fetch_page(article_url, page, expand_toc=False),
                    timeout=ARTICLE_FETCH_TIMEOUT_SECONDS,
                )
                summary = "Resumo não disponível."
                if html_article:
                    soup_article = BeautifulSoup(html_article, "lxml")
                    summary = parser.extract_article_summary(soup_article)
            except asyncio.TimeoutError:
                logger.warning(
                    "Timeout fetching [%s]: %s", node.display_name, title
                )
                summary = "Resumo não disponível."
            except Exception as e:
                logger.error(
                    "Error fetching [%s] %s: %s", node.display_name, title, e
                )
                summary = "Resumo não disponível."
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

    slug_to_id = {r.slug: r.release_id for r in KNOWN_RELEASES}
    for release_slug, topics in sorted(
        releases, key=lambda x: slug_to_id.get(x[0], 0), reverse=True
    ):
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
