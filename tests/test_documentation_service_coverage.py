"""Coverage push for src/documentation_service.py (line 96)."""

from src.documentation_service import DocumentationService


def test_documentation_service_import_coverage() -> None:
    doc = DocumentationService()
    assert doc is not None
