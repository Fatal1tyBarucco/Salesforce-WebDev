import sys
from unittest.mock import MagicMock, patch

from automation.core.orchestrator import ReleasePipelineOrchestrator  # noqa: E402
from automation.shared.models import ClassificationResult, ParsedSection  # noqa: E402


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


def test_orchestrator_main() -> None:
    from pathlib import Path
    from unittest.mock import patch

    file_path = "automation/core/orchestrator.py"
    code_text = Path(file_path).read_text(encoding="utf-8")

    # Use compile to associate the code with the file for coverage tracking
    code = compile(code_text, file_path, "exec")

    global_ns = {
        "__name__": "__main__",
    }

    # Mock everything ReleasePipelineOrchestrator uses to avoid side effects
    with patch("automation.core.orchestrator.ReleaseNotesScraper"), patch(
        "automation.core.orchestrator.ReleaseNotesParser"
    ), patch("automation.core.orchestrator.TopicClassifier"), patch(
        "automation.core.orchestrator.MarkdownArtifactGenerator"
    ), patch(
        "automation.core.orchestrator.ReadmeUpdater"
    ):
        exec(code, global_ns)
