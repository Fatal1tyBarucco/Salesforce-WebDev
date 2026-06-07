import sys
from unittest.mock import MagicMock, patch

# Mock sys.modules['fitz'] antes de importar o código do projeto para evitar erro de importação
sys.modules["fitz"] = MagicMock()

from automation.core.pdf_extraction_engine import PdfExtractionEngine  # noqa: E402
from automation.strategies.pdf_strategy import PdfStrategy  # noqa: E402


def test_pdf_strategy_returns_raw_content() -> None:
    strategy = PdfStrategy()
    assert strategy.parse("some content") == "some content"


@patch("automation.core.pdf_extraction_engine.fitz")
def test_pdf_extraction_engine_extracts_text_correctly(mock_fitz: MagicMock) -> None:
    mock_doc = MagicMock()
    mock_page_1 = MagicMock()
    mock_page_1.get_text.return_value = "Page 1 Content"
    mock_page_2 = MagicMock()
    mock_page_2.get_text.return_value = "Page 2 Content"

    mock_doc.__iter__.return_value = [mock_page_1, mock_page_2]
    mock_fitz.open.return_value = mock_doc

    engine = PdfExtractionEngine()
    result = engine.extract_text("fake_path.pdf")

    assert result == "Page 1 Content\nPage 2 Content"
    mock_fitz.open.assert_called_once_with("fake_path.pdf")
    mock_doc.close.assert_called_once()
