"""
parser.py — Segmentador de conteúdo das Release Notes por tópico arquitetural.

Responsabilidade:
  Recebe o DOM parseado (BeautifulSoup) e retorna um dicionário
  mapeando cada tópico (slug) ao seu conteúdo extraído em texto limpo.

Estratégia de extração:
  1. Percorre todos os elementos de título (h1-h4) do DOM.
  2. Para cada seção, verifica se algum keyword do tópico está presente
     no texto do título ou nos parágrafos subsequentes.
  3. Extrai o bloco de conteúdo até o próximo elemento de mesmo nível.
"""

import logging
import re

from bs4 import BeautifulSoup

from config import MONITORED_TOPICS, TopicContentMap

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------

HEADING_TAGS: tuple[str, ...] = ("h1", "h2", "h3", "h4")
CONTENT_TAGS: tuple[str, ...] = ("p", "ul", "ol", "li", "table", "pre", "blockquote")


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class ReleaseNotesParser:
    """
    Segmenta o HTML das Release Notes do Salesforce em tópicos monitorados.

    O parser é stateless — cada chamada a `parse()` é independente.
    """

    def parse(
        self,
        soup: BeautifulSoup,
        release_name: str,
    ) -> TopicContentMap:
        """
        Ponto de entrada principal.

        Args:
            soup        : DOM parseado da página de release notes.
            release_name: Nome da release (usado apenas para logs).

        Returns:
            Dicionário {slug_do_tópico: lista_de_linhas_extraídas}.
            Tópicos sem conteúdo retornam lista vazia.
        """
        logger.info("[PARSER] Iniciando segmentação | release=%s", release_name)

        sections: list[dict] = self._extract_sections(soup)
        logger.info(
            "[PARSER] %d seções identificadas no DOM | release=%s",
            len(sections),
            release_name,
        )

        result: TopicContentMap = {topic.slug: [] for topic in MONITORED_TOPICS}

        for section in sections:
            matched_slugs: list[str] = self._match_section_to_topics(section)
            for slug in matched_slugs:
                result[slug].extend(section["lines"])

        for topic in MONITORED_TOPICS:
            count: int = len(result[topic.slug])
            logger.info(
                "[PARSER] Tópico '%s': %d linhas extraídas | release=%s",
                topic.slug,
                count,
                release_name,
            )

        return result

    # ------------------------------------------------------------------
    # Extração de Seções
    # ------------------------------------------------------------------

    def _extract_sections(self, soup: BeautifulSoup) -> list[dict]:
        """
        Percorre o DOM e agrupa o conteúdo em seções delimitadas por headings.

        Cada seção é um dicionário:
        {
            "heading": str,       — texto do título
            "level"  : int,       — nível do heading (1-4)
            "lines"  : list[str], — linhas de texto extraídas
        }
        """
        sections: list[dict] = []
        current_section: dict | None = None

        for element in soup.find_all(True):  # itera todos os elementos
            tag_name: str = element.name if hasattr(element, "name") else ""

            if tag_name in HEADING_TAGS:
                # Salva seção anterior antes de iniciar nova
                if current_section is not None and current_section["lines"]:
                    sections.append(current_section)

                heading_text: str = self._clean_text(element.get_text())
                if not heading_text:
                    current_section = None
                    continue

                current_section = {
                    "heading": heading_text,
                    "level": int(tag_name[1]),  # h2 → 2
                    "lines": [f"### {heading_text}"],
                }

            elif tag_name in CONTENT_TAGS and current_section is not None:
                line: str = self._clean_text(element.get_text())
                if line:
                    current_section["lines"].append(line)

        # Adiciona última seção
        if current_section is not None and current_section["lines"]:
            sections.append(current_section)

        return sections

    # ------------------------------------------------------------------
    # Matching de Tópicos
    # ------------------------------------------------------------------

    def _match_section_to_topics(self, section: dict) -> list[str]:
        """
        Verifica quais tópicos monitorados correspondem a uma seção.

        A correspondência é feita por keyword matching (case-insensitive)
        no heading e nas primeiras linhas de conteúdo da seção.
        """
        matched: list[str] = []
        searchable_text: str = " ".join(
            [section["heading"]] + section["lines"][:5]
        ).lower()

        for topic in MONITORED_TOPICS:
            if self._matches_any_keyword(searchable_text, topic.keywords):
                matched.append(topic.slug)

        return matched

    def _matches_any_keyword(
        self,
        text: str,
        keywords: list[str],
    ) -> bool:
        """Verifica se algum keyword está presente no texto (word boundary)."""
        for keyword in keywords:
            # Usa \b para evitar falsos positivos (ex: "flow" em "workflow")
            pattern: str = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_text(raw: str) -> str:
        """Remove espaços extras, quebras de linha e caracteres invisíveis."""
        cleaned: str = re.sub(r"\s+", " ", raw).strip()
        # Remove linhas que são só pontuação ou muito curtas (ruído)
        if len(cleaned) < 3:
            return ""
        return cleaned
