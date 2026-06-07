from pathlib import Path
from unittest.mock import MagicMock, patch
from src.pdf_parser import PDFReleaseParser


@patch("src.pdf_parser.pdfplumber")
def test_pdf_release_parser_flows(mock_pdfplumber: MagicMock) -> None:
    # Cenário de PDF encontrado
    mock_pdf = MagicMock()
    mock_page_1 = MagicMock()
    mock_page_1.extract_text.return_value = "Apex and Trigger modifications\n\nLWC Wire Adaptor component"
    mock_pdf.pages = [mock_page_1]
    
    mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

    parser = PDFReleaseParser()

    # Mock _find_pdf para retornar um Path fictício
    with patch.object(parser, "_find_pdf", return_value=Path("pdfs/summer_26.pdf")):
        result = parser.parse("summer_26", "Summer '26")

        assert "apex" in result
        assert len(result["apex"]) > 0
        assert "LWC Wire Adaptor component" in result["lwc"]


def test_pdf_release_parser_pdf_not_found() -> None:
    parser = PDFReleaseParser()
    with patch.object(parser, "_find_pdf", return_value=None):
        result = parser.parse("summer_26", "Summer '26")
        assert all(len(result[key]) == 0 for key in result)


def test_pdf_find_pdf_not_exists(tmp_path: Path) -> None:
    parser = PDFReleaseParser()
    # Mock de PDF_DIR apontando para um diretório que não existe
    with patch("src.pdf_parser.PDF_DIR", tmp_path / "non_existing_dir"):
        result = parser._find_pdf("summer_26")
        assert result is None


def test_pdf_find_pdf_exists(tmp_path: Path) -> None:
    parser = PDFReleaseParser()
    
    # Criamos o diretório e um arquivo pdf temporário
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    pdf_file = pdf_dir / "summer_26_release.pdf"
    pdf_file.write_text("dummy")

    with patch("src.pdf_parser.PDF_DIR", pdf_dir):
        result = parser._find_pdf("summer_26")
        assert result is not None
        assert result.name == "summer_26_release.pdf"
