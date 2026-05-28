"""
generator.py — Gerador de artefatos Markdown a partir do conteúdo segmentado.

Responsabilidade:
  Cria/atualiza a estrutura de diretórios /releases/{slug}/ e gera
  um arquivo .md por tópico com formatação padronizada.

Estrutura gerada:
  releases/
  └── summer_26/
      ├── apex.md
      ├── lwc.md
      ├── flow.md
      ├── security.md
      └── integrations.md
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from config import (
    MONITORED_TOPICS,
    RELEASES_DIR,
    ReleaseInfo,
    TopicConfig,
    TopicContentMap,
)

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constante de template
# ---------------------------------------------------------------------------

MARKDOWN_HEADER_TEMPLATE: str = """\
# {topic_name} — {release_name}

> **Release:** {release_name}
> **Gerado em:** {generated_at} UTC
> **Fonte:** {source_url}

---

"""

NO_CONTENT_MESSAGE: str = (
    "_Nenhum conteúdo relevante identificado para este tópico nesta release._\n"
)


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------

class MarkdownGenerator:
    """
    Gera os arquivos Markdown de cada tópico por release.

    Cria os diretórios necessários automaticamente e nunca sobrescreve
    um arquivo existente sem que haja conteúdo novo (idempotente).
    """

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir: Path = Path(base_dir)

    # ------------------------------------------------------------------
    # Interface Pública
    # ------------------------------------------------------------------

    def generate(
        self,
        release: ReleaseInfo,
        content_map: TopicContentMap,
        source_url: str,
    ) -> list[Path]:
        """
        Gera todos os arquivos Markdown para uma release.

        Args:
            release    : Metadados da release.
            content_map: Dicionário {slug: linhas} retornado pelo parser.
            source_url : URL de origem (incluída como referência no header).

        Returns:
            Lista dos caminhos de arquivos gerados/atualizados.
        """
        release_dir: Path = self._ensure_release_dir(release.slug)
        generated_files: list[Path] = []
        generated_at: str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

        for topic in MONITORED_TOPICS:
            lines: list[str] = content_map.get(topic.slug, [])
            file_path: Path = self._write_topic_file(
                topic=topic,
                release=release,
                lines=lines,
                release_dir=release_dir,
                generated_at=generated_at,
                source_url=source_url,
            )
            generated_files.append(file_path)

        logger.info(
            "[GENERATOR] %d arquivos gerados em '%s' | release=%s",
            len(generated_files),
            release_dir,
            release.name,
        )
        return generated_files

    # ------------------------------------------------------------------
    # Métodos Privados
    # ------------------------------------------------------------------

    def _ensure_release_dir(self, slug: str) -> Path:
        """Cria o diretório da release se não existir."""
        release_dir: Path = self._base_dir / slug
        release_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("[GENERATOR] Diretório garantido: %s", release_dir)
        return release_dir

    def _write_topic_file(
        self,
        topic: TopicConfig,
        release: ReleaseInfo,
        lines: list[str],
        release_dir: Path,
        generated_at: str,
        source_url: str,
    ) -> Path:
        """
        Escreve o arquivo Markdown de um tópico específico.

        O arquivo é sobrescrito a cada execução para garantir que o
        conteúdo reflita sempre a extração mais recente.
        """
        file_path: Path = release_dir / f"{topic.slug}.md"

        header: str = MARKDOWN_HEADER_TEMPLATE.format(
            topic_name=topic.display_name,
            release_name=release.name,
            generated_at=generated_at,
            source_url=source_url,
        )

        body: str
        if lines:
            body = "\n\n".join(lines) + "\n"
        else:
            body = NO_CONTENT_MESSAGE

        full_content: str = header + body

        file_path.write_text(full_content, encoding="utf-8")
        logger.info(
            "[GENERATOR] Arquivo escrito: %s (%d linhas)",
            file_path,
            len(lines),
        )
        return file_path

    def list_generated_releases(self) -> list[tuple[str, list[str]]]:
        """
        Lista todas as releases e seus tópicos gerados no diretório base.

        Returns:
            Lista de tuplas: (slug_da_release, [nomes_dos_tópicos]).
        """
        result: list[tuple[str, list[str]]] = []

        if not self._base_dir.exists():
            return result

        for release_dir in sorted(self._base_dir.iterdir()):
            if not release_dir.is_dir():
                continue
            topics: list[str] = [
                f.stem for f in sorted(release_dir.glob("*.md"))
            ]
            result.append((release_dir.name, topics))

        return result
