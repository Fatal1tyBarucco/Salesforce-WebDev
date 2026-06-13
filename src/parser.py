"""Parser for Salesforce Help release notes — navigation tree and article pages.

The Salesforce Help portal organizes release notes as a hierarchical tree:
  - A navigation sidebar (ToC) with all topics, subtopics and articles
  - Individual article pages for each feature/change

This parser handles:
  - extract_topic_tree(): builds the full topic hierarchy from the ToC DOM
  - extract_article_summary(): extracts a concise summary from an article page
"""

import logging
import re
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .config import EXCLUDED_TOPIC_IDS, TopicContentMap, TopicNode

logger: logging.Logger = logging.getLogger(__name__)

HEADING_TAGS: tuple[str, ...] = ("h1", "h2", "h3", "h4")
CONTENT_TAGS: tuple[str, ...] = ("p", "ul", "ol", "li", "table", "pre", "blockquote")

SOURCE_BASE = "https://help.salesforce.com"

# Prefixo padrão da URL de release note no portal Salesforce Help
RELEASE_NOTES_PATH_PREFIX = "release-notes."


class ReleaseNotesParser:
    """Parses Salesforce Help release notes navigation tree and article pages."""

    # ------------------------------------------------------------------
    # Interface Pública
    # ------------------------------------------------------------------

    def extract_topic_tree(
        self,
        soup: BeautifulSoup,
        release_name: str,
        release_id: int,
    ) -> list[TopicNode]:
        """
        Extrai a hierarquia completa de tópicos do ToC da página de release notes.

        Constrói uma árvore de TopicNode onde:
          - Nível 2: Categorias principais (ex: "Desenvolvimento", "Segurança")
          - Nível 3: Subcategorias (ex: "Apex", "LWC", "API")
          - Nível 4+: Artigos individuais (folhas com data-is-link="true")

        Args:
            soup        : BeautifulSoup da página de release notes (SPA renderizada).
            release_name: Nome da release (ex: "Winter '26") — usado para logging.
            release_id  : ID numérico da release (ex: 258) — para normalizar URLs.

        Returns:
            Lista de TopicNode de nível 2 com seus filhos aninhados.
        """
        logger.info("[PARSER] Extraindo árvore de tópicos | release=%s", release_name)

        # Busca todos os <li role="treeitem"> no DOM
        treeitem_elements = soup.find_all("li", attrs={"role": "treeitem"})

        if not treeitem_elements:
            logger.warning(
                "[PARSER] Nenhum <li role='treeitem'> encontrado | release=%s", release_name
            )
            return []

        logger.info(
            "[PARSER] %d elementos treeitem encontrados | release=%s",
            len(treeitem_elements),
            release_name,
        )

        # Constrói lista linear de nós
        raw_nodes: list[TopicNode] = []
        for element in treeitem_elements:
            node = self._parse_treeitem(element, release_id)
            if node is not None:
                raw_nodes.append(node)

        # Constrói a hierarquia aninhada
        tree = self._build_tree(raw_nodes)

        # Filtra nós excluídos e retorna apenas nível 2
        result = [node for node in tree if node.node_id not in EXCLUDED_TOPIC_IDS]

        logger.info(
            "[PARSER] %d tópicos de nível 2 extraídos | release=%s",
            len(result),
            release_name,
        )
        return result

    def extract_article_summary(self, soup: BeautifulSoup) -> str:
        """
        Extrai um resumo conciso de uma página de artigo de release note.

        Estratégia:
          1. Tenta encontrar seções "Por que" ou "Why"
          2. Fallback: primeiro parágrafo significativo da área de conteúdo
        """
        # 1. Tenta encontrar seção "Por que" ou "Why"
        for header in soup.find_all(["h2", "h3", "p", "strong"]):
            text: str = header.get_text().strip().lower()
            if text in ["por que essa alteração é importante", "why", "por que"]:
                next_p = header.find_next("p")
                if next_p:
                    return ReleaseNotesParser._clean_text(next_p.get_text())

        # 2. Fallback: primeiro parágrafo significativo na área de conteúdo
        content_div = soup.select_one("article, #articleViewContent, div.content")
        if content_div:
            paragraphs = content_div.find_all("p")
            for p in paragraphs:
                cleaned_text: str = ReleaseNotesParser._clean_text(p.get_text())
                if len(cleaned_text) > 50:
                    return cleaned_text

        return "Resumo não disponível para este artigo."

    def build_topic_content_map(
        self,
        topic_nodes: list[TopicNode],
        release_name: str,
    ) -> TopicContentMap:
        """
        Constrói um TopicContentMap a partir da árvore de TopicNode com artigos.

        Usado pelo MarkdownGenerator para gerar os arquivos .md.
        Cada chave é o slug do tópico de nível 2; o valor é a lista de linhas Markdown.

        Args:
            topic_nodes : Lista de TopicNode de nível 2 (com artigos já populados).
            release_name: Nome da release para cabeçalhos.

        Returns:
            Dict[slug → list[linhas Markdown]].
        """
        result: TopicContentMap = {}

        for topic in topic_nodes:
            lines: list[str] = []
            lines.append(f"## {topic.display_name} — {release_name}")
            lines.append("")

            # Artigos diretos no nível 2
            if topic.articles:
                for article in topic.articles:
                    lines.extend(self._format_article_lines(article))

            # Artigos em subcategorias (nível 3+)
            for child in topic.children:
                if child.articles or child.children:
                    lines.append(f"### {child.display_name}")
                    lines.append("")
                    for article in child.articles:
                        lines.extend(self._format_article_lines(article))
                    # Nível 4+ (sub-subcategorias)
                    for grandchild in child.children:
                        if grandchild.articles:
                            lines.append(f"#### {grandchild.display_name}")
                            lines.append("")
                            for article in grandchild.articles:
                                lines.extend(self._format_article_lines(article))

            if len(lines) > 2:  # Tem conteúdo além do cabeçalho
                result[topic.slug] = lines

        return result

    # ------------------------------------------------------------------
    # Métodos Privados — Extração da Árvore
    # ------------------------------------------------------------------

    def _parse_treeitem(self, element: Any, release_id: int) -> TopicNode | None:
        """
        Parseia um <li role="treeitem"> e retorna um TopicNode.

        Retorna None se o elemento não for válido ou não tiver link.
        """
        if not isinstance(element, Tag):
            return None

        item_id_raw: str = element.get("id", "")  # type: ignore[assignment]
        if not item_id_raw:
            return None

        # Remove sufixo _leaf para obter o node_id canônico
        node_id: str = item_id_raw
        if node_id.endswith("_leaf"):
            node_id = node_id[:-5]

        # Verifica o nível
        level_str: str = element.get("aria-level", "0")  # type: ignore[assignment]
        try:
            level: int = int(level_str)
        except ValueError:
            return None

        if level < 1:
            return None

        # Extrai o link <a role="presentation">
        link_tag = element.find("a", attrs={"role": "presentation"})
        if not link_tag or not isinstance(link_tag, Tag):
            return None

        href: str = link_tag.get("href", "")  # type: ignore[assignment]
        title: str = element.get("title", "") or link_tag.get_text(strip=True)  # type: ignore[assignment]

        if not href or not title:
            return None

        # Normaliza a URL
        full_url = self._normalize_url(href, release_id)

        # is_leaf: artigo individual (tem data-is-link="true")
        data_is_link: str = str(element.get("data-is-link", "") or "")
        is_leaf: bool = data_is_link.lower() == "true"

        return TopicNode(
            node_id=node_id,
            display_name=title.strip(),
            level=level,
            url=full_url,
            is_leaf=is_leaf,
        )

    def _build_tree(self, nodes: list[TopicNode]) -> list[TopicNode]:
        """
        Constrói a hierarquia aninhada a partir da lista linear de nós.

        Usa uma pilha para rastrear o caminho de pais conforme o nível aumenta.
        Retorna apenas os nós de nível 2 (filhos diretos do root).
        """
        result: list[TopicNode] = []
        # Pilha de (level, node) para rastrear pais
        stack: list[tuple[int, TopicNode]] = []

        for node in nodes:
            # Ignora o nível 1 (root da árvore)
            if node.level <= 1:
                continue

            # Remove da pilha todos os nós com nível >= ao atual
            while stack and stack[-1][0] >= node.level:
                stack.pop()

            if not stack:
                # Nível 2 — adiciona à raiz
                if node.level == 2:
                    result.append(node)
                    stack.append((node.level, node))
            else:
                # Adiciona como filho do último nó da pilha
                parent = stack[-1][1]
                parent.children.append(node)
                stack.append((node.level, node))

        return result

    def _normalize_url(self, href: str, release_id: int) -> str:
        """
        Normaliza uma URL do portal Salesforce Help:
          - Garante o domínio base
          - Garante o parâmetro release correto
          - Garante language=pt_BR
        """
        if href.startswith("/s/"):
            href = f"{SOURCE_BASE}{href}"
        elif href.startswith("/"):
            href = f"{SOURCE_BASE}{href}"
        elif not href.startswith("http"):
            href = urljoin(SOURCE_BASE, href)

        # Garante parâmetro de release
        if f"release={release_id}" not in href:
            sep = "&" if "?" in href else "?"
            href = re.sub(r"[?&]release=\d+", "", href)
            href += f"{sep}release={release_id}"

        # Garante language=pt_BR
        if "language=pt_BR" not in href:
            sep = "&" if "?" in href else "?"
            href += f"{sep}language=pt_BR"

        return href

    # ------------------------------------------------------------------
    # Métodos Privados — Formatação
    # ------------------------------------------------------------------

    def _format_article_lines(self, article: dict[str, str]) -> list[str]:
        """Formata um artigo como linhas Markdown."""
        lines: list[str] = []
        title = article.get("title", "Sem título")
        summary = article.get("summary", "")
        url = article.get("url", "")

        lines.append(f"### {title}")
        lines.append("")
        if summary:
            lines.append(summary)
            lines.append("")
        if url:
            lines.append(f"[🔗 Leia mais no conteúdo original]({url})")
            lines.append("")
        return lines

    # ------------------------------------------------------------------
    # Métodos Privados — Utilitários
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_text(raw: str) -> str:
        """Remove espaços extras e linhas muito curtas."""
        cleaned: str = re.sub(r"\s+", " ", raw).strip()
        if len(cleaned) < 3:
            return ""
        return cleaned
