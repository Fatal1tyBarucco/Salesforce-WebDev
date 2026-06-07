import sys
from unittest.mock import MagicMock, patch

# Mock sys.modules['fitz'] antes de importar o código do projeto para evitar erro de importação
sys.modules['fitz'] = MagicMock()

from automation.core.orchestrator import ReleasePipelineOrchestrator
from automation.core.intelligent_release_pipeline import IntelligentReleasePipeline
from automation.shared.models import ClassificationResult, ParsedSection


@patch("automation.core.orchestrator.ReleaseNotesScraper")
@patch("automation.core.orchestrator.ReleaseNotesParser")
@patch("automation.core.orchestrator.TopicClassifier")
@patch("automation.core.orchestrator.MarkdownArtifactGenerator")
@patch("automation.core.orchestrator.ReadmeUpdater")
def test_orchestrator_execution_flow(
    mock_updater: MagicMock,
    mock_generator: MagicMock,
    mock_classifier: MagicMock,
    mock_parser: MagicMock,
    mock_scraper: MagicMock,
) -> None:
    # Configurando instâncias mock
    scraper_inst = MagicMock()
    scraper_inst.fetch_release_notes.return_value = "raw html"
    mock_scraper.return_value = scraper_inst

    parser_inst = MagicMock()
    parser_inst.parse.return_value = "parsed content"
    mock_parser.return_value = parser_inst

    classifier_inst = MagicMock()
    classifier_inst.classify.return_value = []
    mock_classifier.return_value = classifier_inst

    generator_inst = MagicMock()
    mock_generator.return_value = generator_inst

    updater_inst = MagicMock()
    mock_updater.return_value = updater_inst

    orchestrator = ReleasePipelineOrchestrator()
    orchestrator.execute()

    scraper_inst.fetch_release_notes.assert_called_once()
    parser_inst.parse.assert_called_once_with("raw html")
    classifier_inst.classify.assert_called_once_with("parsed content")
    generator_inst.generate.assert_called_once_with(release_name="Summer_26", topics=[])
    updater_inst.update.assert_called_once()


@patch("automation.core.intelligent_release_pipeline.PdfExtractionEngine")
@patch("automation.core.intelligent_release_pipeline.SemanticParser")
@patch("automation.core.intelligent_release_pipeline.WeightedTopicClassifier")
def test_intelligent_pipeline_flow(
    mock_weighted_classifier: MagicMock,
    mock_semantic_parser: MagicMock,
    mock_pdf_engine: MagicMock,
) -> None:
    pdf_inst = MagicMock()
    pdf_inst.extract_text.return_value = "extracted pdf text"
    mock_pdf_engine.return_value = pdf_inst

    parser_inst = MagicMock()
    parser_inst.parse_sections.return_value = [ParsedSection(title="title", content="content")]
    mock_semantic_parser.return_value = parser_inst

    classifier_inst = MagicMock()
    classifier_inst.classify.return_value = [
        ClassificationResult(topic_name="apex", content="content", confidence_score=10)
    ]
    mock_weighted_classifier.return_value = classifier_inst

    pipeline = IntelligentReleasePipeline()
    results = pipeline.process_pdf_release("dummy.pdf")

    assert len(results) == 1
    assert results[0].topic_name == "apex"
    pdf_inst.extract_text.assert_called_once_with("dummy.pdf")
    parser_inst.parse_sections.assert_called_once_with("extracted pdf text")
    classifier_inst.classify.assert_called_once()
