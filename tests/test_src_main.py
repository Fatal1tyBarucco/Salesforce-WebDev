from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import sys
from src.main import (
    main,
    _generate_release_files,
    _format_entry,
    _format_entry_table,
    _find_existing_releases,
    _slugify_category,
)
from src.config import ReleaseInfo
from src.parser import FeatureImpactCategory, FeatureImpactEntry


def test_find_existing_releases_empty() -> None:
    with (
        patch("src.main.RELEASES_DIR", "/nonexistent"),
        patch("src.release_docs.RELEASES_DIR", "/nonexistent"),
    ):
        result = _find_existing_releases()
        assert result == set()


def test_format_entry_all_flags() -> None:
    entry = FeatureImpactEntry(
        name="Test Feature",
        available_users=True,
        available_admins=True,
        requires_config=True,
        contact_sf=True,
    )
    result = _format_entry(entry)
    assert "Test Feature" in result
    assert "usuários" in result
    assert "admins/devs" in result
    assert "configuração" in result
    assert "Salesforce" in result


def test_format_entry_no_flags() -> None:
    entry = FeatureImpactEntry(name="Basic Feature")
    result = _format_entry(entry)
    assert "Basic Feature" in result


def test_generate_release_files() -> None:
    from src.parser import FeatureImpactParser
    from pathlib import Path
    import tempfile

    parser = FeatureImpactParser()
    sample_text = (
        "Salesforce geral\n"
        "Description of category.\n"
        "RECURSO\tATIVADO PARA USUÁRIOS\n"
        "Feature One\tYes\n"
        "Feature Two\t\tYes\n"
    )
    categories = parser.parse_text(sample_text)
    assert len(categories) >= 1

    release = ReleaseInfo(name="Test", release_id=262, slug="test_release")
    generator = MagicMock()
    translator = MagicMock()

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch("src.main.RELEASES_DIR", tmpdir), patch("src.release_docs.RELEASES_DIR", tmpdir):
            asyncio.run(_generate_release_files(release, categories, generator, translator))

            release_dir = Path(tmpdir) / "test_release"
            assert release_dir.exists()
            md_files = list(release_dir.rglob("*.md"))
            assert len(md_files) >= 1
            content = md_files[0].read_text()
            assert "Feature One" in content


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.FeatureImpactParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._generate_release_files")
@patch("src.main._update_readme_all")
@patch("src.main._update_readme_single")
@patch("src.main._find_existing_releases")
def test_main_execution_success(
    mock_find_existing: MagicMock,
    mock_update_single: MagicMock,
    mock_update_readme: MagicMock,
    mock_generate_files: MagicMock,
    mock_generator_class: MagicMock,
    mock_impact_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    scraper_inst = MagicMock()
    sample_text = (
        "Salesforce geral\n"
        "Description of category.\n"
        "RECURSO\tATIVADO PARA USUÁRIOS\n"
        "Feature One\tYes\n"
    )
    scraper_inst.fetch_page_raw_text = AsyncMock(return_value=sample_text)
    scraper_inst.download_pdf_from_button = AsyncMock(return_value=True)
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    parser_inst = MagicMock()
    parser_inst.parse_text.return_value = [FeatureImpactCategory(name="Test Cat")]
    mock_impact_parser_class.return_value = parser_inst

    generator_inst = MagicMock()
    mock_generator_class.return_value = generator_inst

    mock_find_existing.return_value = set()

    original_argv = sys.argv
    try:
        sys.argv = ["main.py", "--release", "summer_26"]
        main()
    finally:
        sys.argv = original_argv

    mock_setup_logging.assert_called_once()
    scraper_inst.fetch_page_raw_text.assert_awaited()
    parser_inst.parse_text.assert_called()
    mock_generate_files.assert_called()
    mock_update_single.assert_called()


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.FeatureImpactParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._generate_release_files")
@patch("src.main._update_readme_all")
@patch("src.main._find_existing_releases")
@patch("src.main.run_pipeline", new_callable=AsyncMock)
def test_main_execution_no_content(
    mock_run_pipeline: MagicMock,
    mock_find_existing: MagicMock,
    mock_update_readme: MagicMock,
    mock_generate_files: MagicMock,
    mock_generator_class: MagicMock,
    mock_impact_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    scraper_inst = MagicMock()
    scraper_inst.fetch_page_raw_text = AsyncMock(return_value=None)
    scraper_inst.download_pdf_from_button = AsyncMock(return_value=False)
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    mock_generator_class.return_value = generator_inst

    mock_find_existing.return_value = set()

    main()

    mock_run_pipeline.assert_called_once()


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.FeatureImpactParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._generate_release_files")
@patch("src.main._update_readme_all")
@patch("src.main.detect_new_release", new_callable=AsyncMock)
@patch("src.main.run_pipeline", new_callable=AsyncMock)
def test_main_execution_all_releases_exist(
    mock_run_pipeline: MagicMock,
    mock_detect: MagicMock,
    mock_update_readme: MagicMock,
    mock_generate_files: MagicMock,
    mock_generator_class: MagicMock,
    mock_impact_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    scraper_inst = MagicMock()
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    mock_generator_class.return_value = generator_inst

    mock_detect.return_value = None

    main()

    mock_run_pipeline.assert_called_once()


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.FeatureImpactParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._generate_release_files")
@patch("src.main._update_readme_all")
@patch("src.main._find_existing_releases")
@patch("src.main.run_pipeline", new_callable=AsyncMock)
def test_main_execution_valid_release_filter(
    mock_run_pipeline: MagicMock,
    mock_find_existing: MagicMock,
    mock_update_readme: MagicMock,
    mock_generate_files: MagicMock,
    mock_generator_class: MagicMock,
    mock_impact_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    scraper_inst = MagicMock()
    scraper_inst.fetch_page_raw_text = AsyncMock(
        return_value="Salesforce geral\nFeature\tYes\nAnother Feature\t\tYes"
    )
    scraper_inst.download_pdf_from_button = AsyncMock(return_value=False)
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    parser_inst = MagicMock()
    parser_inst.parse_text.return_value = []
    mock_impact_parser_class.return_value = parser_inst

    generator_inst = MagicMock()
    mock_generator_class.return_value = generator_inst

    original_argv = sys.argv
    try:
        sys.argv = ["main.py", "--release", "summer_26"]
        main()
    finally:
        sys.argv = original_argv

    mock_run_pipeline.assert_called_once()
    mock_find_existing.assert_not_called()


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.FeatureImpactParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._generate_release_files")
@patch("src.main._update_readme_all")
@patch("src.main._find_existing_releases")
@patch("src.main.run_pipeline", new_callable=AsyncMock)
def test_main_execution_unknown_release(
    mock_run_pipeline: MagicMock,
    mock_find_existing: MagicMock,
    mock_update_readme: MagicMock,
    mock_generate_files: MagicMock,
    mock_generator_class: MagicMock,
    mock_impact_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    scraper_inst = MagicMock()
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    mock_generator_class.return_value = generator_inst

    original_argv = sys.argv
    try:
        sys.argv = ["main.py", "--release", "nonexistent_slug"]
        main()
    finally:
        sys.argv = original_argv

    mock_run_pipeline.assert_called_once()
    generator_inst.generate.assert_not_called()


def test_slugify_category_portuguese() -> None:
    assert _slugify_category("Documentação legal") == "documentacao_legal"
    assert _slugify_category("Análise de dados") == "analise_de_dados"
    assert (
        _slugify_category("Segurança, identidade e privacidade")
        == "seguranca_identidade_e_privacidade"
    )
    assert _slugify_category("Automação") == "automacao"
    assert _slugify_category("Personalização") == "personalizacao"
    assert _slugify_category("Gerenciamento de receita") == "gerenciamento_de_receita"
    assert _slugify_category("Aplicativo móvel") == "aplicativo_movel"
    assert (
        _slugify_category("Outros produtos e serviços do Salesforce")
        == "outros_produtos_e_servicos_do_salesforce"
    )
    assert (
        _slugify_category("Integrações do Salesforce para Slack")
        == "integracoes_do_salesforce_para_slack"
    )


def test_format_entry_table_with_docs_link() -> None:
    entry = FeatureImpactEntry(
        name="Test Feature",
        available_users=True,
        available_admins=False,
        requires_config=True,
        contact_sf=False,
    )
    result = _format_entry_table(entry, docs_url="https://help.salesforce.com/test")
    assert "🔗" in result
    assert "https://help.salesforce.com/test" in result
    assert "**Test Feature**" in result


def test_format_entry_table_no_docs_link() -> None:
    entry = FeatureImpactEntry(
        name="No Docs Feature",
        available_users=True,
        available_admins=True,
        requires_config=False,
        contact_sf=False,
    )
    result = _format_entry_table(entry)
    assert "🔗" not in result
    assert "| |" in result


def test_format_entry_table_docs_empty_string() -> None:
    entry = FeatureImpactEntry(name="Empty Docs")
    result = _format_entry_table(entry, docs_url="")
    assert "🔗" not in result


def test_format_entry_table_docs_header_in_output() -> None:
    entry = FeatureImpactEntry(
        name="Feature",
        available_users=True,
        available_admins=True,
        requires_config=False,
        contact_sf=False,
    )
    result = _format_entry_table(entry, docs_url="https://example.com")
    assert result.endswith("|")
    parts = result.split("|")
    assert len(parts) == 8
