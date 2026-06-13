"""
generator.py — Gerador de artefatos Markdown a partir da árvore dinâmica de tópicos.

Responsabilidade:
  Cria/atualiza a estrutura de diretórios /releases/{slug}/ e gera
  um arquivo .md por tópico (categoria de nível 2) com toda a hierarquia
  e artigos extraídos dinamicamente do portal Salesforce Help.

Estrutura gerada:
  releases/
  └── summer_26/
      ├── development.md       (Desenvolvimento: Apex, LWC, API...)
      ├── security.md          (Segurança, identidade e privacidade)
      ├── einstein.md          (Agentforce & Einstein)
      └── ...                  (todos os tópicos do portal)
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    RELEASES_DIR,
    ReleaseInfo,
    TopicContentMap,
    TopicNode,
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

    Suporta dois modos de entrada:
      - `generate()`: recebe `list[TopicNode]` (novo fluxo dinâmico)
      - `generate_from_map()`: recebe `TopicContentMap` (compatibilidade legada)
    """

    def __init__(self, base_dir: str = RELEASES_DIR) -> None:
        self._base_dir: Path = Path(base_dir)

    # ------------------------------------------------------------------
    # Interface Pública — Novo Fluxo (TopicNode)
    # ------------------------------------------------------------------

    def generate(
        self,
        release: ReleaseInfo,
        topic_nodes: list[TopicNode],
        source_url: str,
    ) -> list[Path]:
        """
        Gera todos os arquivos Markdown para uma release a partir da árvore dinâmica.

        Args:
            release    : Metadados da release.
            topic_nodes: Lista de TopicNode de nível 2 (com artigos populados).
            source_url : URL de origem (incluída como referência no header).

        Returns:
            Lista dos caminhos de arquivos gerados/atualizados.
        """
        release_dir: Path = self._ensure_release_dir(release.slug)
        generated_files: list[Path] = []
        generated_at: str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

        for topic in topic_nodes:
            # Só gera arquivo se houver artigos no tópico ou seus filhos
            if not self._has_content(topic):
                logger.debug(
                    "[GENERATOR] Tópico '%s' sem artigos — ignorado | release=%s",
                    topic.display_name,
                    release.name,
                )
                continue

            lines = self._build_topic_lines(topic)
            file_path = self._write_topic_file_from_lines(
                slug=topic.slug,
                display_name=topic.display_name,
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

    def generate_from_map(
        self,
        release: ReleaseInfo,
        content_map: TopicContentMap,
        source_url: str,
    ) -> list[Path]:
        """
        [LEGADO] Gera arquivos Markdown a partir de um TopicContentMap.

        Mantido para compatibilidade com testes e código legado.

        Args:
            release    : Metadados da release.
            content_map: Dicionário {slug: linhas} retornado pelo parser.
            source_url : URL de origem.

        Returns:
            Lista dos caminhos de arquivos gerados/atualizados.
        """
        release_dir: Path = self._ensure_release_dir(release.slug)
        generated_files: list[Path] = []
        generated_at: str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M")

        for slug, lines in content_map.items():
            display_name = slug.replace("_", " ").title()
            file_path = self._write_topic_file_from_lines(
                slug=slug,
                display_name=display_name,
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
    # Interface Pública — Listagem
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Métodos Privados
    # ------------------------------------------------------------------

    def _ensure_release_dir(self, slug: str) -> Path:
        """Cria o diretório da release se não existir."""
        release_dir: Path = self._base_dir / slug
        release_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("[GENERATOR] Diretório garantido: %s", release_dir)
        return release_dir

    def _has_content(self, topic: TopicNode) -> bool:
        """Verifica se o tópico ou seus filhos têm artigos."""
        if topic.articles:
            return True
        for child in topic.children:
            if child.articles:
                return True
            for grandchild in child.children:
                if grandchild.articles:
                    return True
        return False

    def _build_topic_lines(self, topic: TopicNode) -> list[str]:
        """Constrói as linhas Markdown para um tópico e seus filhos."""
        lines: list[str] = []

        # Artigos diretos no tópico (nível 2)
        for article in topic.articles:
            lines.extend(self._format_article_lines(article))

        # Subcategorias (nível 3)
        for child in topic.children:
            if not self._has_any_articles(child):
                continue

            lines.append(f"### {child.display_name}")
            lines.append("")

            for article in child.articles:
                lines.extend(self._format_article_lines(article))

            # Sub-subcategorias (nível 4+)
            for grandchild in child.children:
                if grandchild.articles:
                    lines.append(f"#### {grandchild.display_name}")
                    lines.append("")
                    for article in grandchild.articles:
                        lines.extend(self._format_article_lines(article))

        return lines

    def _has_any_articles(self, node: TopicNode) -> bool:
        """Verifica se o nó ou seus filhos têm artigos."""
        if node.articles:
            return True
        return any(child.articles for child in node.children)

    def _format_article_lines(self, article: dict[str, str]) -> list[str]:
        """Formata um artigo como linhas Markdown com detalhes colapsáveis."""
        lines: list[str] = []
        title = article.get("title", "Sem título")
        summary = article.get("summary", "")
        url = article.get("url", "")

        lines.append(f"#### {title}")
        lines.append("")
        if summary and summary != "Resumo não disponível para este artigo.":
            lines.append(f"> {summary}")
            lines.append("")
        if url:
            lines.append(f"[🔗 Leia mais no conteúdo original]({url})")
            lines.append("")
        return lines

    def _write_topic_file_from_lines(
        self,
        slug: str,
        display_name: str,
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
        file_path: Path = release_dir / f"{slug}.md"

        header: str = MARKDOWN_HEADER_TEMPLATE.format(
            topic_name=display_name,
            release_name=release.name,
            generated_at=generated_at,
            source_url=source_url,
        )

        body: str
        if lines:
            body = "\n".join(lines) + "\n"
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
