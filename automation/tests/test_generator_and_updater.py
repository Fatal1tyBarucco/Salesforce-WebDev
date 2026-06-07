from pathlib import Path
from unittest.mock import patch
from automation.core.generator import MarkdownArtifactGenerator
from automation.core.readme_updater import ReadmeUpdater
from automation.shared.models import ReleaseTopicContent


def test_markdown_artifact_generator_writes_files(tmp_path: Path) -> None:
    generator = MarkdownArtifactGenerator()

    topics = [
        ReleaseTopicContent(topic_name="apex", content="Apex modifications details"),
        ReleaseTopicContent(topic_name="lwc", content="LWC modifications details"),
    ]

    # Mudamos o diretório atual no patch ou passamos releases/ como mock?
    # Como o gerador escreve em f"releases/{slugify(release_name)}" relativo ao diretório atual,
    # podemos mockar o ensure_directory_exists e Path.write_text, ou simplesmente alterar o Cwd nos testes,
    # ou mockar a escrita no Path.
    with patch("automation.core.generator.ensure_directory_exists") as mock_ensure, patch(
        "automation.core.generator.Path.write_text"
    ) as mock_write:

        generator.generate("Summer '26", topics)

        assert mock_ensure.call_count == 1
        assert mock_write.call_count == 2


def test_readme_updater_generates_readme(tmp_path: Path) -> None:
    updater = ReadmeUpdater()
    temp_readme = tmp_path / "README.md"
    updater.README_PATH = temp_readme

    # Criamos estrutura de diretório de releases temporária
    releases_dir = tmp_path / "releases"
    releases_dir.mkdir()

    release_1 = releases_dir / "summer_26"
    release_1.mkdir()
    (release_1 / "apex.md").write_text("# APEX\ndetails", encoding="utf-8")
    (release_1 / "lwc.md").write_text("# LWC\ndetails", encoding="utf-8")

    with patch("automation.core.readme_updater.Path") as mock_path:
        # Faremos com que sorted(Path("releases").glob("*")) retorne nossa pasta temporária
        mock_path.return_value.glob.side_effect = lambda pattern: (
            [release_1] if pattern == "*" else [release_1 / "apex.md", release_1 / "lwc.md"]
        )
        # O nome do diretório deve ser summer_26
        type(mock_path.return_value).name = "summer_26"

        updater.update()

        content = temp_readme.read_text(encoding="utf-8")
        assert "# Salesforce Release Notes Knowledge Base" in content
        assert "### Summer 26" in content
        assert "[apex]" in content
        assert "[lwc]" in content
