from __future__ import annotations

import fitz


class PdfExtractionEngine:
    """
    Enterprise PDF extraction engine.
    """

    def extract_text(self, pdf_file_path: str) -> str:
        extracted_pages: list[str] = []

        document = fitz.open(pdf_file_path)

        try:
            for page in document:
                extracted_pages.append(page.get_text())
        finally:
            document.close()

        return "\n".join(extracted_pages)
