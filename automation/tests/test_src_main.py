from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from src.main import main, _update_readme
from src.config import TopicNode

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
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(return_value="<html>rendered</html>")
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    parser_inst = MagicMock()
    parser_inst.extract_topic_tree.return_value = [
        TopicNode(
            slug="apex",
            display_name="Apex",
            level=2,
            url="",
            children=[],
            articles=[],
        )
    ]
    parser_inst.extract_article_summary.return_value = "Test summary"
    mock_parser_class.return_value = parser_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = [("summer_26", ["apex"])]
    mock_generator_class.return_value = generator_inst

    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    main()

    mock_setup_logging.assert_called_once()
    mock_asyncio_run.assert_called()
    parser_inst.extract_topic_tree.assert_called()
    generator_inst.generate.assert_called()
    generator_inst.list_generated_releases.assert_called_once()
    mock_update_readme.assert_called_once()


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
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(return_value=None)
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = []
    mock_generator_class.return_value = generator_inst

    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    main()

    mock_parser_class.return_value.extract_topic_tree.assert_not_called()
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
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(side_effect=Exception("Scraping error"))
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = []
    mock_generator_class.return_value = generator_inst

    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    main()

    mock_update_readme.assert_called_once()


def test_update_readme_writes_file() -> None:
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("summer_26", ["apex", "lwc"])]
        _update_readme(releases, {})

        mock_write_text.assert_called_once()
        written_content = mock_write_text.call_args[0][0]
        assert "Summer 26" in written_content
        assert "APEX" in written_content
        assert "CI/CD Status & Conformidade" in written_content
        assert "banner.png" in written_content


def test_update_readme_with_highlights() -> None:
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("summer_26", ["apex"])]
        highlights = {
            "summer_26": {
                "apex": [
                    {
                        "title": "New Apex Feature",
                        "summary": "This is a test summary",
                        "url": "https://example.com",
                        "topic": "Apex",
                    }
                ]
            }
        }
        _update_readme(releases, highlights)

        mock_write_text.assert_called_once()
        written_content = mock_write_text.call_args[0][0]
        assert "<details>" in written_content
        assert "<summary>" in written_content
        assert "New Apex Feature" in written_content
        assert "This is a test summary" in written_content


def test_main_entrypoint() -> None:
    from pathlib import Path
    from unittest.mock import patch

    file_path = "src/main.py"
    code_text = Path(file_path).read_text(encoding="utf-8")

    code = compile(code_text, file_path, "exec")

    global_ns = {
        "__name__": "__main__",
        "__package__": "src",
    }

    with patch("src.main.SalesforceReleaseScraper"), patch("src.main.ReleaseNotesParser"), patch(
        "src.main.MarkdownGenerator"
    ), patch("src.main.asyncio.run"):
        exec(code, global_ns)
