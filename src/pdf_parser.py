"""
pdf_parser.py — Extrai e segmenta conteúdo das Release Notes a partir de PDFs oficiais.

Responsabilidade:
  - Localizar os PDFs no diretório `pdfs/`.
  - Extrair texto bruto com pdfplumber.
  - Segmentar por headings e estrutura do documento.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import pdfplumber

logger = logging.getLogger(__name__)

PDF_DIR = Path("pdfs")

TopicContentMap = dict[str, list[str]]


class PDFReleaseParser:
    """Parser para PDFs de Release Notes da Salesforce."""

    def parse(self, release_slug: str, release_name: str) -> TopicContentMap:
        """
        Extrai e segmenta o conteúdo do PDF de uma release.

        Args:
            release_slug: slug da release (ex: 'summer_26').
            release_name: nome de exibição (ex: "Summer '26").

        Returns:
            Dicionário {slug_do_seção: lista_de_linhas_extraídas}.
        """
        pdf_path = self._find_pdf(release_slug)
        if not pdf_path:
            logger.warning("PDF não encontrado para %s. Pulando.", release_slug)
            return {}

        logger.info("Processando PDF: %s", pdf_path)
        full_text = self._extract_text(pdf_path)
        if not full_text:
            logger.error("Falha ao extrair texto do PDF %s", pdf_path)
            return {}

        return self._segment_by_headings(full_text)

    def _find_pdf(self, release_slug: str) -> Optional[Path]:
        """Localiza o arquivo PDF pelo slug da release."""
        if not PDF_DIR.exists():
            return None

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
            logger.exception("Erro ao processar PDF: %s", e)
            return ""

    def _segment_by_headings(self, text: str) -> TopicContentMap:
        """
        Segmenta o texto por headings (linhas em maiúsculas ou com #).
        Cada heading vira uma chave no dicionário de resultado.
        """
        result: TopicContentMap = {}
        current_key: str = "_general"
        current_lines: list[str] = []

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                continue

            is_heading = bool(re.match(r"^[A-Z][A-Z &/']{2,}$", stripped)) or stripped.startswith(
                "#"
            )

            if is_heading:
                if current_lines:
                    result.setdefault(current_key, []).extend(current_lines)
                slug = re.sub(r"[^a-z0-9]+", "_", stripped.lower()).strip("_")
                current_key = slug
                current_lines = []
            else:
                current_lines.append(stripped)

        if current_lines:
            result.setdefault(current_key, []).extend(current_lines)

        return result
