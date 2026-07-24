"""
generator.py — Gerador de artefatos Markdown a partir da árvore de tópicos dinâmica.

Responsabilidade:
  Cria/atualiza a estrutura de diretórios /releases/{slug}/ e gera
  um arquivo .md por tópico com formatação padronizada.

Estrutura gerada:
  releases/
  └── summer_26/
      ├── rn_development.md
      ├── rn_security.md
      └── rn_integrations.md
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from string import Template

from .ai.generators.badges import release_meta_badges
from .config import RELEASES_DIR, ReleaseInfo, TopicNode

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constante de template
# ---------------------------------------------------------------------------

MARKDOWN_HEADER_TEMPLATE: Template = Template("""\
# ${topic_name} — ${release_name}

> **Release:** ${release_name}
> **Gerado em:** ${generated_at} UTC
> **Fonte:** ${source_url}

---

""")

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
        topic_nodes: list[TopicNode],
        source_url: str,
    ) -> list[Path]:
        """
        Gera todos os arquivos Markdown para uma release a partir da árvore.

        Args:
            release     : Metadados da release.
            topic_nodes : Lista de TopicNode raiz (nível 2) da árvore.
            source_url  : URL de origem (incluída como referência no header).

        Returns:
            Lista dos caminhos de arquivos gerados/atualizados.
        """
        release_dir: Path = self._ensure_release_dir(release.slug)
        generated_files: list[Path] = []
        generated_at: str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

        for node in topic_nodes:
            lines: list[str] = self._build_topic_lines(node, release.name)
            file_path: Path = self._write_topic_file(
                node=node,
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

    def _build_topic_lines(self, node: TopicNode, release_name: str) -> list[str]:
        """Constrói as linhas Markdown para um tópico e seus sub-tópicos."""
        lines: list[str] = []

        if node.articles:
            lines.append(f"## {node.display_name}")
            lines.append("")
            for article in node.articles:
                lines.append(f"### {article['title']}")
                lines.append("")
                if article.get("summary"):
                    lines.append(article["summary"])
                    lines.append("")
                if article.get("url"):
                    lines.append(f"[🔗 Leia mais no conteúdo original]({article['url']})")
                    lines.append("")

        for child in node.children:
            child_lines = self._build_topic_lines(child, release_name)
            lines.extend(child_lines)

        return lines

    def _write_topic_file(
        self,
        node: TopicNode,
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
        file_path: Path = release_dir / f"{node.topic_file_slug()}.md"

        template_vars: dict[str, str] = {
            "topic_name": node.display_name or "Untitled",
            "release_name": release.name or "Unknown Release",
            "generated_at": generated_at or "N/A",
            "source_url": source_url or "",
        }

        header: str = MARKDOWN_HEADER_TEMPLATE.safe_substitute(template_vars)

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
            topics: list[str] = [f.stem for f in sorted(release_dir.glob("*.md"))]
            result.append((release_dir.name, topics))

        return result

    def generate_release_header_with_badges(
        self,
        release: ReleaseInfo,
        total_features: int = 0,
        category_count: int = 0,
    ) -> str:
        """
        Gera um cabeçalho visual com badges para uma release.

        Args:
            release: Metadados da release.
            total_features: Total de features (opcional).
            category_count: Número de categorias (opcional).

        Returns:
            String Markdown com cabeçalho e badges.
        """
        badges = release_meta_badges(
            release_name=release.name,
            total_features=total_features,
            category_count=category_count,
        )
        return f"# {release.name}\n\n{badges}\n\n---\n\n"
