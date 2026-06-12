from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from src.main import main, _update_readme
from src.config import KNOWN_RELEASES

_original_asyncio_run = asyncio.run


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.ReleaseNotesParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._update_readme")
@patch("src.main.asyncio.run")
def test_main_execution_success(
    mock_asyncio_run: MagicMock,
    mock_update_readme: MagicMock,
    mock_generator_class: MagicMock,
    mock_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    # Setup mocks
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(return_value="<html>rendered</html>")
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    parser_inst = MagicMock()
    parser_inst.extract_article_links.return_value = {}
    parser_inst.build_topic_content_from_links.return_value = {}
    mock_parser_class.return_value = parser_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = [("summer_26", ["apex"])]
    mock_generator_class.return_value = generator_inst

    # Fazer asyncio.run executar a corrotina real
    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    # Executa main
    main()

    # Asserts
    mock_setup_logging.assert_called_once()
    mock_asyncio_run.assert_called()
    parser_inst.extract_article_links.assert_called()
    generator_inst.generate.assert_called()
    from src.config import MONITORED_TOPICS

    expected_highlights: dict[str, dict[str, list[dict[str, str]]]] = {
        release.slug: {topic.slug: [] for topic in MONITORED_TOPICS} for release in KNOWN_RELEASES
    }
    generator_inst.list_generated_releases.assert_called_once()
    mock_update_readme.assert_called_once_with([("summer_26", ["apex"])], expected_highlights)


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.ReleaseNotesParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._update_readme")
@patch("src.main.asyncio.run")
def test_main_execution_scraper_returns_none(
    mock_asyncio_run: MagicMock,
    mock_update_readme: MagicMock,
    mock_generator_class: MagicMock,
    mock_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    # Simula scraper retornando None ou vazio
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(return_value=None)
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = []
    mock_generator_class.return_value = generator_inst

    # Fazer asyncio.run executar a corrotina real
    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    main()

    # Nao deve chamar parseamento nem geracao
    mock_parser_class.return_value.extract_article_links.assert_not_called()
    generator_inst.generate.assert_not_called()


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.ReleaseNotesParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._update_readme")
@patch("src.main.asyncio.run")
def test_main_execution_exception_handled(
    mock_asyncio_run: MagicMock,
    mock_update_readme: MagicMock,
    mock_generator_class: MagicMock,
    mock_parser_class: MagicMock,
    mock_scraper_class: MagicMock,
    mock_setup_logging: MagicMock,
) -> None:
    # Simula exception sendo disparada e tratada no loop
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(side_effect=Exception("Scraping error"))
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = []
    mock_generator_class.return_value = generator_inst

    # Fazer asyncio.run executar a corrotina real
    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    main()

    # Nao quebra a execucao global, apenas loga e prossegue
    mock_update_readme.assert_called_once()


def test_update_readme_writes_file() -> None:
    # Mock do Path.write_text
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("summer_26", ["apex", "lwc"])]
        _update_readme(releases, {})

        mock_write_text.assert_called_once()
        written_content = mock_write_text.call_args[0][0]
        assert "Summer 26" in written_content
        assert "Apex" in written_content
        assert "CI/CD Status & Conformidade" in written_content
        assert "banner.png" in written_content


def test_main_entrypoint() -> None:
    from pathlib import Path
    from unittest.mock import patch

    file_path = "src/main.py"
    code_text = Path(file_path).read_text(encoding="utf-8")

    # Use compile to associate the code with the file for coverage tracking
    code = compile(code_text, file_path, "exec")

    global_ns = {
        "__name__": "__main__",
        "__package__": "src",
    }

    # Mock everything main() uses to avoid side effects and errors
    with patch("src.main.SalesforceReleaseScraper"), patch("src.main.ReleaseNotesParser"), patch(
        "src.main.MarkdownGenerator"
    ), patch("src.main.asyncio.run"):
        exec(code, global_ns)
