"""Coverage push for src/generator.py (lines 222, 227)."""

from src.config import ReleaseInfo
from src.generator import MarkdownGenerator


def test_generate_release_header_with_badges() -> None:
    generator = MarkdownGenerator()
    release = ReleaseInfo(name="Test", slug="test", release_id=1)
    result = generator.generate_release_header_with_badges(release, total_features=5)
    assert "Test" in result
