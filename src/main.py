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
from typing import Dict, List

from bs4 import BeautifulSoup

from .config import BASE_URL, KNOWN_RELEASES, MONITORED_TOPICS, RELEASES_DIR, TopicContentMap
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import ReleaseNotesParser
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


async def run_pipeline() -> None:
    """Versão assíncrona do orquestrador para suportar deep scraping e resumos pt-BR."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction with Deep Scraping (pt-BR).")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    all_highlights: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

    async with scraper:
        # Processar todas as releases conhecidas
        for release in KNOWN_RELEASES:
            logger.info("Processando release: %s", release.name)
            release_highlights: Dict[str, List[Dict[str, str]]] = {
                topic.slug: [] for topic in MONITORED_TOPICS
            }
            try:
                url = BASE_URL.format(release_id=release.release_id)
                logger.info("Index URL: %s", url)

                html_index = await scraper.fetch_page(url)
                if not html_index:
                    logger.warning("Sem conteúdo para %s", release.name)
                    continue

                soup_index = BeautifulSoup(html_index, "lxml")
                topic_links = parser.extract_article_links(soup_index, release.name)

                content_map: TopicContentMap = {topic.slug: [] for topic in MONITORED_TOPICS}

                for topic in MONITORED_TOPICS:
                    articles = topic_links.get(topic.slug, [])
                    if not articles:
                        continue

                    content_map[topic.slug].append(f"## {topic.display_name} — {release.name}")
                    content_map[topic.slug].append("")

                    for article in articles:
                        logger.info("Deep scraping [%s]: %s", topic.display_name, article["title"])

                        # Forçar pt-BR no link
                        article_url = article["url"]
                        if "language=pt_BR" not in article_url:
                            sep = "&" if "?" in article_url else "?"
                            article_url += f"{sep}language=pt_BR"

                        html_article = await scraper.fetch_page(article_url)
                        summary = "Resumo não disponível."
                        if html_article:
                            soup_article = BeautifulSoup(html_article, "lxml")
                            summary = parser.extract_article_summary(soup_article)

                        # Adicionar aos destaques do tópico desta release
                        release_highlights[topic.slug].append(
                            {
                                "title": article["title"],
                                "summary": summary,
                                "url": article_url,
                                "topic": topic.display_name,
                            }
                        )

                        content_map[topic.slug].append(f"### {article['title']}")
                        content_map[topic.slug].append(f"{summary}")
                        content_map[topic.slug].append(
                            f"\n[🔗 Leia mais no conteúdo original]({article_url})"
                        )
                        content_map[topic.slug].append("")

                all_highlights[release.slug] = release_highlights
                generator.generate(release, content_map, source_url=url)

            except Exception as e:
                logger.exception("Erro ao processar %s: %s", release.name, e)

    releases_list = generator.list_generated_releases()
    _update_readme(releases_list, all_highlights)


def main() -> None:
    """Entrypoint do script."""
    asyncio.run(run_pipeline())


def _update_readme(
    releases: List[tuple[str, List[str]]],
    highlights: Dict[str, Dict[str, List[Dict[str, str]]]],
) -> None:
    """Atualiza o README.md com painel de status e resumos detalhados em pt-BR."""
    readme_path = Path("README.md")

    # Header moderno com banner
    content = [
        "![Salesforce Release Intelligence](./assets/banner.png)\n\n",
        "# 🚀 Salesforce Release Notes Intelligence\n\n",
        "Pipeline automatizado para extração, classificação e versionamento das **Salesforce Release Notes** "
        "como artefatos Markdown estruturados (*Knowledge-as-Code*).\n\n",
    ]

    # Badges de Status e Ferramentas
    content.extend(
        [
            "### ⚙️ CI/CD Status & Conformidade\n\n",
            "[![Python Quality & Validation](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml)\n",
            "![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python&logoColor=white) \n",
            "![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?logo=playwright&logoColor=white) \n",
            "![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg) \n",
            "![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg) \n",
            "![Black](https://img.shields.io/badge/Formatter-Black-000000.svg)\n\n",
        ]
    )

    # Tabela de conformidade de ferramentas
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

    # Mapeamento estético para as releases (estação do ano)
    def get_release_emoji(name: str) -> str:
        name_lower = name.lower()
        if "winter" in name_lower:
            return "❄️"
        elif "summer" in name_lower:
            return "☀️"
        return "🌸"

    # Mapeamento estético para tópicos
    topic_emojis = {"apex": "💻", "lwc": "⚡", "flow": "⚙️", "security": "🔒", "integrations": "🔌"}

    # Iterar pelas releases geradas (as mais recentes primeiro)
    for release_slug, topics in sorted(releases, reverse=True):
        release_name = release_slug.replace("_", " ").title()
        emoji = get_release_emoji(release_name)

        content.append(f"### {emoji} {release_name}\n\n")

        # Verificar se há destaques detalhados para esta release
        release_highlights = highlights.get(release_slug, {})

        for topic_slug in topics:
            # Encontrar nome legível do tópico
            display_name = topic_slug.upper()
            for t_cfg in MONITORED_TOPICS:
                if t_cfg.slug == topic_slug:
                    display_name = t_cfg.display_name
                    break

            topic_emoji = topic_emojis.get(topic_slug, "📄")
            articles = release_highlights.get(topic_slug, [])

            if articles:
                num_changes = len(articles)
                plural = "alterações" if num_changes > 1 else "alteração"

                content.append("<details>\n")
                content.append(
                    f"<summary><b>{topic_emoji} {display_name} (Clique para expandir {num_changes} {plural})</b></summary>\n\n"
                )
                for article in articles:
                    content.append(f"* **{article['title']}**\n")
                    content.append(f"  {article['summary']}\n\n")

                # Link local no final de cada tópico com resumo
                content.append(
                    f"> 📄 **Notas Completas:** consulte os detalhes completos na página do tópico "
                    f"[{display_name}](./releases/{release_slug}/{topic_slug}.md).\n"
                )
                content.append("</details>\n\n")
            else:
                # Caso não tenha resumos disponíveis nesta execução (ex: histórico anterior)
                content.append(
                    f"* {topic_emoji} **{display_name}**: "
                    f"Acesse o arquivo de notas de versão em [./releases/{release_slug}/{topic_slug}.md](./releases/{release_slug}/{topic_slug}.md).\n"
                )
        content.append("\n---\n\n")

    readme_path.write_text("".join(content), encoding="utf-8")
    logger.info("README.md atualizado com painel moderno e resumos.")


if __name__ == "__main__":
    main()
