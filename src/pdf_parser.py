"""
pdf_parser.py — Extrai e segmenta conteúdo das Release Notes a partir de PDFs oficiais.

Responsabilidade:
  - Localizar os PDFs no diretório `pdfs/`.
  - Extrair texto bruto com pdfplumber.
  - Segmentar por tópicos usando palavras-chave e estrutura de headings.
"""

import logging
import re
from pathlib import Path
from typing import Optional

import pdfplumber

from .config import MONITORED_TOPICS, TopicContentMap

logger = logging.getLogger(__name__)

PDF_DIR = Path("pdfs")

class PDFReleaseParser:
    """Parser para PDFs de Release Notes da Salesforce."""

    def parse(self, release_slug: str, release_name: str) -> TopicContentMap:
        """
        Extrai e segmenta o conteúdo do PDF de uma release.

        Args:
            release_slug: slug da release (ex: 'summer_26').
            release_name: nome de exibição (ex: "Summer '26").

        Returns:
            Dicionário {slug_do_tópico: lista_de_linhas_extraídas}.
        """
        pdf_path = self._find_pdf(release_slug)
        if not pdf_path:
            logger.warning(f"PDF não encontrado para {release_slug}. Pulando.")
            return {topic.slug: [] for topic in MONITORED_TOPICS}

        logger.info(f"Processando PDF: {pdf_path}")
        full_text = self._extract_text(pdf_path)
        if not full_text:
            logger.error(f"Falha ao extrair texto do PDF {pdf_path}")
            return {topic.slug: [] for topic in MONITORED_TOPICS}

        return self._segment_by_topics(full_text, release_name)

    def _find_pdf(self, release_slug: str) -> Optional[Path]:
        """Localiza o arquivo PDF pelo slug da release."""
        if not PDF_DIR.exists():
            return None

        # Procura por arquivo que contenha o slug no nome
        for pdf_file in PDF_DIR.glob("*.pdf"):
            if release_slug in pdf_file.stem.lower():
                return pdf_file
        return None

    def _extract_text(self, pdf_path: Path) -> str:
        """Extrai todo o texto de um PDF usando pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                return "\n".join(text_parts)
        except Exception as e:
            logger.exception(f"Erro ao processar PDF: {e}")
            return ""

    def _segment_by_topics(self, text: str, release_name: str) -> TopicContentMap:
        """
        Segmenta o texto por tópicos usando palavras-chave e limites de seção.
        """
        result: TopicContentMap = {topic.slug: [] for topic in MONITORED_TOPICS}
        
        # Divide o texto em seções por linhas que parecem cabeçalhos
        sections = re.split(r'\n(?=[A-Z][A-Za-z &]+)\n', text)  # headings em maiúsculas
        
        for section in sections:
            for topic in MONITORED_TOPICS:
                if self._topic_in_section(section, topic.keywords):
                    # Adiciona a seção inteira como uma lista de linhas
                    lines = [line.strip() for line in section.split('\n') if line.strip()]
                    if lines:
                        result[topic.slug].extend(lines)
        
        return result

    def _topic_in_section(self, section_text: str, keywords: list[str]) -> bool:
        """Verifica se alguma palavra-chave aparece na seção."""
        section_lower = section_text.lower()
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', section_lower):
                return True
        return False