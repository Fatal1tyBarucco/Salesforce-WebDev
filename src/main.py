"""
main.py — Orquestrador principal do pipeline de Release Notes.

Fluxo de execução:
  1. Configura logging centralizado.
  2. Para cada release em KNOWN_RELEASES:
     a. Scraper busca o HTML com retry.
     b. Parser segmenta por tópico.
     c. Generator escreve os arquivos Markdown.
  3. ReadmeUpdater injeta o índice atualizado no README.md.

Uso:
  python main.py                        # processa todas as releases
  python main.py --release summer_26    # processa apenas uma release
  python main.py --dry-run              # simula sem escrever arquivos
"""

import argparse
import logging
import sys
from pathlib import Path

# Adiciona /src ao path para imports diretos (compatível com GitHub Actions)
sys.path.insert(0, str(Path(__file__).parent))

from config import BASE_URL, KNOWN_RELEASES, ReleaseInfo
from generator import MarkdownGenerator
from parser import ReleaseNotesParser
from readme_updater import ReadmeUpdater
from scraper import SalesforceReleaseScraper


# ---------------------------------------------------------------------------
# Logging Centralizado
# ---------------------------------------------------------------------------

def configure_logging() -> None:
    """
    Configura o logger raiz com formato padronizado para GitHub Actions.

    O formato inclui timestamp ISO 8601 e nível de log, facilitando
    a leitura nos logs do workflow e em ferramentas de observabilidade.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_arguments() -> argparse.Namespace:
    """Define e parseia os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description="Pipeline de extração das Release Notes do Salesforce."
    )
    parser.add_argument(
        "--release",
        type=str,
        default=None,
        help="Slug da release a processar (ex: summer_26). "
             "Se omitido, processa todas as releases em KNOWN_RELEASES.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Executa o pipeline sem escrever arquivos no disco.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Lógica Principal
# ---------------------------------------------------------------------------

def resolve_target_releases(slug_filter: str | None) -> list[ReleaseInfo]:
    """
    Retorna a lista de releases a processar com base no filtro passado via CLI.

    Args:
        slug_filter: Slug de uma release específica ou None para todas.

    Returns:
        Lista de ReleaseInfo a processar.

    Raises:
        SystemExit: Se o slug fornecido não for encontrado em KNOWN_RELEASES.
    """
    logger: logging.Logger = logging.getLogger(__name__)

    if slug_filter is None:
        return KNOWN_RELEASES

    matched: list[ReleaseInfo] = [
        r for r in KNOWN_RELEASES if r.slug == slug_filter
    ]
    if not matched:
        available: str = ", ".join(r.slug for r in KNOWN_RELEASES)
        logger.error(
            "[MAIN] Release '%s' não encontrada. Disponíveis: %s",
            slug_filter,
            available,
        )
        sys.exit(1)

    return matched


def run_pipeline(
    releases: list[ReleaseInfo],
    dry_run: bool,
) -> dict[str, bool]:
    """
    Executa o pipeline completo para cada release fornecida.

    Args:
        releases: Lista de releases a processar.
        dry_run : Se True, apenas loga sem escrever arquivos.

    Returns:
        Dicionário {slug: True/False} com o resultado de cada release.
    """
    logger: logging.Logger = logging.getLogger(__name__)
    results: dict[str, bool] = {}

    scraper = SalesforceReleaseScraper()
    parser = ReleaseNotesParser()
    generator = MarkdownGenerator()

    try:
        for release in releases:
            logger.info(
                "=" * 60 + "\n[MAIN] Processando: %s (id=%d)",
                release.name,
                release.release_id,
            )

            # 1. Extração
            soup = scraper.fetch(release)
            if soup is None:
                logger.error(
                    "[MAIN] Skipping release '%s' — falha na extração.",
                    release.name,
                )
                results[release.slug] = False
                continue

            # 2. Parsing
            content_map = parser.parse(soup, release.name)

            # 3. Geração de artefatos
            source_url: str = BASE_URL.format(release_id=release.release_id)

            if dry_run:
                total_lines: int = sum(len(v) for v in content_map.values())
                logger.info(
                    "[MAIN][DRY-RUN] Release '%s': %d linhas extraídas. "
                    "Nenhum arquivo escrito.",
                    release.name,
                    total_lines,
                )
            else:
                generated = generator.generate(release, content_map, source_url)
                logger.info(
                    "[MAIN] %d arquivos gerados para '%s'.",
                    len(generated),
                    release.name,
                )

            results[release.slug] = True

    finally:
        scraper.close()

    return results


def update_readme(dry_run: bool) -> None:
    """Atualiza o README.md com o índice das releases geradas."""
    logger: logging.Logger = logging.getLogger(__name__)

    if dry_run:
        logger.info("[MAIN][DRY-RUN] README.md não será atualizado.")
        return

    updater = ReadmeUpdater()
    success: bool = updater.update()

    if success:
        logger.info("[MAIN] README.md atualizado com sucesso.")
    else:
        logger.warning("[MAIN] README.md não foi atualizado — verifique os logs acima.")


def main() -> None:
    configure_logging()
    logger: logging.Logger = logging.getLogger(__name__)

    args: argparse.Namespace = parse_arguments()
    logger.info(
        "[MAIN] Pipeline iniciado | dry_run=%s | release_filter=%s",
        args.dry_run,
        args.release or "todas",
    )

    target_releases: list[ReleaseInfo] = resolve_target_releases(args.release)
    logger.info(
        "[MAIN] %d release(s) na fila: %s",
        len(target_releases),
        [r.name for r in target_releases],
    )

    results: dict[str, bool] = run_pipeline(target_releases, args.dry_run)

    # Sumário
    successes: int = sum(1 for ok in results.values() if ok)
    failures: int = len(results) - successes
    logger.info(
        "[MAIN] Pipeline concluído | sucessos=%d | falhas=%d",
        successes,
        failures,
    )

    update_readme(args.dry_run)

    if failures > 0:
        logger.error("[MAIN] Pipeline finalizado com %d falha(s).", failures)
        sys.exit(1)

    logger.info("[MAIN] Pipeline finalizado com sucesso.")


if __name__ == "__main__":
    main()
