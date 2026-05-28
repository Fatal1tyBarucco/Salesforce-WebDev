"""Main orchestrator for Salesforce release notes extraction (PDF version)."""
import logging
#from typing import Optional

from .pdf_parser import PDFReleaseParser
from .generator import MarkdownGenerator
from .logger import setup_logging
from .config import KNOWN_RELEASES, RELEASES_DIR

logger = logging.getLogger(__name__)

def main() -> None:
    """Orquestra a extração a partir de PDFs locais."""
    setup_logging()
    logger.info("Starting Salesforce Release Notes extraction from PDFs.")

    pdf_parser = PDFReleaseParser()
    generator = MarkdownGenerator(base_dir=RELEASES_DIR)

    for release in KNOWN_RELEASES:
        logger.info(f"Processando release: {release.name}")
        try:
            content_map = pdf_parser.parse(release.slug, release.name)
            source_url = f"PDF local: {release.slug}.pdf"
            generator.generate(release, content_map, source_url=source_url)
        except Exception as e:
            logger.exception(f"Erro ao processar {release.name}: {e}")

    # Atualiza o README com as releases geradas
    releases_list = generator.list_generated_releases()
    _update_readme(releases_list)

def _update_readme(releases: list[tuple[str, list[str]]]) -> None:
    """Atualiza o README.md com um índice dinâmico."""
    readme_path = "README.md"
    index_lines = [
        "# Salesforce Release Notes Knowledge Base\n",
        "Este repositório armazena as notas de versão extraídas automaticamente dos PDFs oficiais.\n",
        "## 📋 Releases Disponíveis\n",
    ]
    for release_slug, topics in sorted(releases, reverse=True):
        release_dir = f"./releases/{release_slug}/"
        index_lines.append(f"### {release_slug.replace('_', ' ').title()}\n")
        for topic in topics:
            index_lines.append(f"- [{topic}]({release_dir}{topic}.md)\n")
        index_lines.append("")
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.writelines(index_lines)
    logger.info("README.md atualizado com índice.")

if __name__ == "__main__":
    main()