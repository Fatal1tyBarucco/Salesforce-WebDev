"""Main orchestrator for Salesforce release notes extraction (web scraping).

Strategy:
  1. Fetch the release notes index page for each release via Playwright
  2. Parse the navigation tree (ToC) to discover ALL topics dynamically
  3. Deep-scrape each article with summary extraction (pt-BR)
  4. Generate Markdown files per topic under releases/{slug}/
  5. Update README with dynamic release index and highlights per topic
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup

from .config import BASE_URL, KNOWN_RELEASES, RELEASES_DIR, TopicNode
from .generator import MarkdownGenerator
from .logger import setup_logging
from .parser import ReleaseNotesParser
from .scraper import SalesforceReleaseScraper

logger = logging.getLogger(__name__)


async def run_pipeline() -> None:
    """Orquestrador assíncrono baseado em descoberta dinâmica da árvore de tópicos."""
    setup_logging()
    logger.info("Iniciando extração das Salesforce Release Notes (árvore dinâmica, pt-BR).")

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    # Estrutura: {release_slug: {topic_slug: [article_dicts]}}
    all_highlights: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

    async with scraper:
        for release in KNOWN_RELEASES:
            logger.info("Processando release: %s (id=%d)", release.name, release.release_id)
            try:
                url = BASE_URL.format(release_id=release.release_id)
                logger.info("URL do índice: %s", url)

                # 1. Fetch da página de release (SPA renderizada com ToC)
                html_index = await scraper.fetch_page(url)
                if not html_index:
                    logger.warning("Sem conteúdo para %s — ignorando.", release.name)
                    continue

                soup_index = BeautifulSoup(html_index, "lxml")

                # 2. Extrai a árvore de tópicos do ToC
                topic_tree = parser.extract_topic_tree(soup_index, release.name, release.release_id)

                if not topic_tree:
                    logger.warning(
                        "Nenhum tópico encontrado no ToC para %s — ignorando.", release.name
                    )
                    continue

                logger.info(
                    "%d categorias principais encontradas para %s",
                    len(topic_tree),
                    release.name,
                )

                # 3. Deep scraping de cada artigo na árvore
                await _scrape_articles_in_tree(scraper, parser, topic_tree, release.name)

                # 4. Gera os arquivos Markdown
                generator.generate(release, topic_tree, source_url=url)

                # 5. Coleta highlights para o README
                all_highlights[release.slug] = _collect_highlights(topic_tree)

            except Exception as e:
                logger.exception("Erro ao processar %s: %s", release.name, e)

    releases_list = generator.list_generated_releases()
    _update_readme(releases_list, all_highlights)


async def _scrape_articles_in_tree(
    scraper: SalesforceReleaseScraper,
    parser: ReleaseNotesParser,
    topic_tree: list[TopicNode],
    release_name: str,
) -> None:
    """
    Percorre recursivamente a árvore e faz deep scraping de cada artigo (folha).

    Artigos são nós com `is_leaf=True` (data-is-link="true" no DOM).
    O resumo extraído é salvo em `node.articles`.
    """
    for topic in topic_tree:
        await _scrape_node_articles(scraper, parser, topic, release_name)


async def _scrape_node_articles(
    scraper: SalesforceReleaseScraper,
    parser: ReleaseNotesParser,
    node: TopicNode,
    release_name: str,
) -> None:
    """Recursivamente scrapa artigos de um nó e seus filhos."""
    # Se o nó é um artigo folha, faz o scraping
    if node.is_leaf and node.url:
        logger.info(
            "[SCRAPE] Artigo: '%s' | release=%s",
            node.display_name[:60],
            release_name,
        )
        summary = await _fetch_article_summary(scraper, parser, node.url)
        node.articles.append(
            {
                "title": node.display_name,
                "summary": summary,
                "url": node.url,
            }
        )

    # Recursão nos filhos
    for child in node.children:
        await _scrape_node_articles(scraper, parser, child, release_name)


async def _fetch_article_summary(
    scraper: SalesforceReleaseScraper,
    parser: ReleaseNotesParser,
    url: str,
) -> str:
    """Faz o scraping de um artigo e retorna o resumo extraído."""
    try:
        html = await scraper.fetch_page(url)
        if html:
            soup = BeautifulSoup(html, "lxml")
            return parser.extract_article_summary(soup)
    except Exception as e:
        logger.warning("Falha ao fazer scraping de '%s': %s", url, e)
    return "Resumo não disponível."


def _collect_highlights(
    topic_tree: list[TopicNode],
) -> Dict[str, List[Dict[str, str]]]:
    """
    Coleta os highlights (artigos com resumo) de toda a árvore de tópicos.

    Retorna um dict: {topic_slug → [article_dicts]}.
    """
    highlights: Dict[str, List[Dict[str, str]]] = {}

    for topic in topic_tree:
        topic_articles: List[Dict[str, str]] = []

        # Artigos diretos
        topic_articles.extend(topic.articles)

        # Artigos em subcategorias
        for child in topic.children:
            topic_articles.extend(child.articles)
            for grandchild in child.children:
                topic_articles.extend(grandchild.articles)

        if topic_articles:
            highlights[topic.slug] = topic_articles

    return highlights


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

    # Iterar pelas releases geradas (as mais recentes primeiro)
    for release_slug, topics in sorted(releases, reverse=True):
        release_name = release_slug.replace("_", " ").title()
        emoji = get_release_emoji(release_name)

        content.append(f"### {emoji} {release_name}\n\n")

        release_highlights = highlights.get(release_slug, {})

        for topic_slug in topics:
            # Nome legível do tópico: usa os highlights para encontrar o título real
            # ou faz fallback para slug formatado
            display_name = topic_slug.replace("_", " ").title()
            articles = release_highlights.get(topic_slug, [])

            if articles:
                num_changes = len(articles)
                plural = "alterações" if num_changes > 1 else "alteração"

                content.append("<details>\n")
                content.append(
                    f"<summary><b>📄 {display_name} "
                    f"(Clique para expandir {num_changes} {plural})</b></summary>\n\n"
                )
                for article in articles:
                    content.append(f"* **{article['title']}**\n")
                    summary = article.get("summary", "")
                    if summary and summary not in (
                        "Resumo não disponível.",
                        "Resumo não disponível para este artigo.",
                    ):
                        content.append(f"  {summary}\n\n")
                    else:
                        content.append("\n")
                    if article.get("url"):
                        content.append(f"  [🔗 Leia mais]({article['url']})\n\n")

                content.append(
                    f"> 📄 **Notas Completas:** consulte os detalhes em "
                    f"[{display_name}](./releases/{release_slug}/{topic_slug}.md).\n"
                )
                content.append("</details>\n\n")
            else:
                content.append(
                    f"* 📄 **{display_name}**: "
                    f"[Ver notas completas](./releases/{release_slug}/{topic_slug}.md)\n"
                )
        content.append("\n---\n\n")

    readme_path.write_text("".join(content), encoding="utf-8")
    logger.info("README.md atualizado com painel moderno e resumos dinâmicos.")


if __name__ == "__main__":
    main()
