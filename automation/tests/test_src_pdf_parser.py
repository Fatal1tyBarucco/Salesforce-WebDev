from pathlib import Path
from unittest.mock import MagicMock, patch
from src.pdf_parser import PDFReleaseParser


@patch("src.pdf_parser.pdfplumber")
def test_pdf_release_parser_flows(mock_pdfplumber: MagicMock) -> None:
    mock_pdf = MagicMock()
    mock_page_1 = MagicMock()
    mock_page_1.extract_text.return_value = (
        "APEX SECTION\nApex and Trigger modifications\n\nLWC SECTION\nLWC Wire Adaptor component"
    )
    mock_pdf.pages = [mock_page_1]

    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

    parser = PDFReleaseParser()

    with patch.object(parser, "_find_pdf", return_value=Path("pdfs/summer_26.pdf")):
        result = parser.parse("summer_26", "Summer '26")

        assert len(result) > 0
        all_text = " ".join(" ".join(v) for v in result.values())
        assert "Apex" in all_text or "LWC" in all_text


def test_pdf_release_parser_pdf_not_found() -> None:
    parser = PDFReleaseParser()
    with patch.object(parser, "_find_pdf", return_value=None):
        result = parser.parse("summer_26", "Summer '26")
        assert result == {}


def test_find_pdf_not_exists(tmp_path: Path) -> None:
    parser = PDFReleaseParser()
    with patch("src.pdf_parser.PDF_DIR", tmp_path / "non_existing_dir"):
        result = parser._find_pdf("summer_26")
        assert result is None


def test_find_pdf_exists(tmp_path: Path) -> None:
    parser = PDFReleaseParser()

    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    pdf_file = pdf_dir / "summer_26_release.pdf"
    pdf_file.write_text("dummy")
    with patch("src.pdf_parser.PDF_DIR", pdf_dir):
        result = parser._find_pdf("summer_26")
        assert result is not None
        assert result.name == "summer_26_release.pdf"

        result_unmatched = parser._find_pdf("winter_26")
        assert result_unmatched is None


@patch("src.pdf_parser.pdfplumber")
def test_pdf_release_parser_extract_text_empty(mock_pdfplumber: MagicMock) -> None:
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_text.return_value = ""
    mock_pdf.pages = [mock_page]
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

    parser = PDFReleaseParser()
    with patch.object(parser, "_find_pdf", return_value=Path("pdfs/summer_26.pdf")):
        result = parser.parse("summer_26", "Summer '26")
        assert result == {}


@patch("src.pdf_parser.pdfplumber")
def test_pdf_release_parser_extract_exception(mock_pdfplumber: MagicMock) -> None:
    mock_pdfplumber.open.side_effect = Exception("Corrupted PDF file")

    parser = PDFReleaseParser()
    result = parser._extract_text(Path("pdfs/summer_26.pdf"))
    assert result == ""
