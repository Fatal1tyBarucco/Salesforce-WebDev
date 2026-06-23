"""
readme_updater.py — Atualizador automático do índice de releases no README.md.

Responsabilidade:
  Localiza o bloco delimitado por marcadores no README.md e injeta
  uma tabela Markdown atualizada com links para todos os artefatos gerados.

Marcadores esperados no README.md:
  <!-- RELEASE_INDEX_START -->
  (conteúdo gerado automaticamente — não editar manualmente)
  <!-- RELEASE_INDEX_END -->
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    KNOWN_RELEASES,
    README_INDEX_END_MARKER,
    README_INDEX_START_MARKER,
    README_PATH,
    RELEASES_DIR,
    ReleaseInfo,
)

logger: logging.Logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Updater
# ---------------------------------------------------------------------------


class ReadmeUpdater:
    """
    Atualiza o bloco de índice dinâmico no README.md principal do repositório.

    O conteúdo entre os marcadores é completamente substituído a cada execução.
    O restante do README.md é preservado intacto.
    """

    def __init__(
        self,
        readme_path: str = README_PATH,
        releases_dir: str = RELEASES_DIR,
    ) -> None:
        self._readme_path: Path = Path(readme_path)
        self._releases_dir: Path = Path(releases_dir)

    # ------------------------------------------------------------------
    # Interface Pública
    # ------------------------------------------------------------------

    def update(self) -> bool:
        """
        Lê o README.md, substitui o bloco de índice e escreve o arquivo.

        Returns:
            True se a atualização foi bem-sucedida, False caso contrário.
        """
        logger.info("[README_UPDATER] Iniciando atualização do README.md")

        if not self._readme_path.exists():
            logger.warning(
                "[README_UPDATER] README.md não encontrado em '%s'. "
                "Criando novo arquivo com marcadores.",
                self._readme_path,
            )
            self._create_initial_readme()

        original_content: str = self._readme_path.read_text(encoding="utf-8")

        if README_INDEX_START_MARKER not in original_content:
            logger.error(
                "[README_UPDATER] Marcador '%s' não encontrado no README.md. "
                "Adicione-o manualmente para habilitar o índice automático.",
                README_INDEX_START_MARKER,
            )
            return False

        new_index_block: str = self._build_index_block()
        updated_content: str = self._replace_index_block(
            original_content,
            new_index_block,
        )

        self._readme_path.write_text(updated_content, encoding="utf-8")
        logger.info(
            "[README_UPDATER] README.md atualizado com sucesso em '%s'",
            self._readme_path,
        )
        return True

    # ------------------------------------------------------------------
    # Métodos Privados
    # ------------------------------------------------------------------

    def _build_index_block(self) -> str:
        """
        Constrói o bloco Markdown com a tabela de releases e links.

        Descobre os tópicos dinamicamente a partir dos arquivos .md
        presentes em cada diretório de release.
        """
        updated_at: str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        all_topics: list[str] = self._discover_all_topics()

        header_cells = ["Release"] + [t.replace("_", " ").title() for t in all_topics]
        separator = ["| :---"] + [":---:" for _ in all_topics]
        lines: list[str] = [
            "",
            f"> ⚙️ Índice gerado automaticamente em **{updated_at}**.",
            "",
            "| " + " | ".join(header_cells) + " |",
            "| " + " | ".join(separator) + " |",
        ]

        for release in reversed(KNOWN_RELEASES):
            row: str = self._build_release_row(release, all_topics)
            lines.append(row)

        lines.append("")
        return "\n".join(lines)

    def _discover_all_topics(self) -> list[str]:
        """Scaneia todos os diretórios de release para descobrir tópicos únicos."""
        topics: set[str] = set()
        if not self._releases_dir.exists():
            return []

        for release_dir in self._releases_dir.iterdir():
            if not release_dir.is_dir():
                continue
            for md_file in release_dir.glob("*.md"):
                topics.add(md_file.stem)

        return sorted(topics)

    def _build_release_row(self, release: ReleaseInfo, all_topics: list[str]) -> str:
        """Constrói uma linha da tabela para uma release."""
        release_dir: Path = self._releases_dir / release.slug

        emoji = "❄️" if "Winter" in release.name else "☀️" if "Summer" in release.name else "🌸"

        cells: list[str] = [f"{emoji} **{release.name}**"]

        for topic_slug in all_topics:
            file_path: Path = release_dir / f"{topic_slug}.md"
            if file_path.exists():
                link: str = f"./{RELEASES_DIR}/{release.slug}/{topic_slug}.md"
                cells.append(f"[✅ Ver]({link})")
            else:
                cells.append("—")

        return "| " + " | ".join(cells) + " |"

    def _replace_index_block(
        self,
        original: str,
        new_block: str,
    ) -> str:
        """
        Substitui o conteúdo entre os marcadores pelo novo bloco.

        Preserva os próprios marcadores no arquivo final.
        """
        start_idx: int = original.index(README_INDEX_START_MARKER)
        end_idx: int = original.find(README_INDEX_END_MARKER)
        if end_idx == -1:
            logger.error(
                "[README_UPDATER] End marker '%s' not found. Appending after start marker.",
                README_INDEX_END_MARKER,
            )
            end_idx = len(original)

        before: str = original[: start_idx + len(README_INDEX_START_MARKER)]
        after: str = original[end_idx:]

        return before + new_block + after

    def _create_initial_readme(self) -> None:
        """Cria um README.md inicial com os marcadores posicionados."""
        initial_content: str = (
            "# Salesforce Release Notes — Automação\n\n"
            "Repositório com Release Notes do Salesforce segmentadas por tópico, "
            "extraídas automaticamente via pipeline Python + GitHub Actions.\n\n"
            f"{README_INDEX_START_MARKER}\n"
            f"{README_INDEX_END_MARKER}\n\n"
            "---\n\n"
            "## Como Funciona\n\n"
            "O pipeline é executado semanalmente via GitHub Actions.\n"
            "Consulte `.github/workflows/release_notes_pipeline.yml` para detalhes.\n"
        )
        self._readme_path.write_text(initial_content, encoding="utf-8")
        logger.info("[README_UPDATER] README.md inicial criado.")
