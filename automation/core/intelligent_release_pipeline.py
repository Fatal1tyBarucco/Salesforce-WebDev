from __future__ import annotations

from automation.core.pdf_extraction_engine import PdfExtractionEngine
from automation.core.semantic_parser import SemanticParser
from automation.core.weighted_classifier import WeightedTopicClassifier


class IntelligentReleasePipeline:
    """
    Integrates semantic parsing, PDF extraction and weighted classification.
    """

    def __init__(self) -> None:
        self.pdf_extraction_engine = PdfExtractionEngine()
        self.semantic_parser = SemanticParser()
        self.weighted_classifier = WeightedTopicClassifier()

    def process_pdf_release(self, pdf_file_path: str):
        extracted_text = self.pdf_extraction_engine.extract_text(
            pdf_file_path,
        )

        parsed_sections = self.semantic_parser.parse_sections(
            extracted_text,
        )

        return self.weighted_classifier.classify(
            parsed_sections,
        )
