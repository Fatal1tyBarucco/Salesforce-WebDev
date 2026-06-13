from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from src.main import main, _update_readme, _process_topic_node
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


@patch("src.main.setup_logging")
@patch("src.main.SalesforceReleaseScraper")
@patch("src.main.ReleaseNotesParser")
@patch("src.main.MarkdownGenerator")
@patch("src.main._update_readme")
@patch("src.main.asyncio.run")
def test_main_execution_empty_topic_nodes(
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
    parser_inst.extract_topic_tree.return_value = []
    mock_parser_class.return_value = parser_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = []
    mock_generator_class.return_value = generator_inst

    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    main()

    generator_inst.generate.assert_not_called()


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


def test_update_readme_winter_emoji() -> None:
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("winter_26", ["apex"])]
        _update_readme(releases, {})
        written_content = mock_write_text.call_args[0][0]
        assert "❄️" in written_content


def test_update_readme_spring_emoji() -> None:
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("spring_26", ["apex"])]
        _update_readme(releases, {})
        written_content = mock_write_text.call_args[0][0]
        assert "🌸" in written_content


def test_update_readme_summer_emoji() -> None:
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("summer_26", ["apex"])]
        _update_readme(releases, {})
        written_content = mock_write_text.call_args[0][0]
        assert "☀️" in written_content


def test_update_readme_no_articles_fallback() -> None:
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("summer_26", ["apex"])]
        _update_readme(releases, {})
        written_content = mock_write_text.call_args[0][0]
        assert "Acesse o arquivo de notas de versão" in written_content


def test_process_topic_node_with_articles() -> None:
    async def run() -> None:
        mock_page = AsyncMock()
        scraper = MagicMock()
        scraper._browser = MagicMock()
        scraper._browser.new_page = AsyncMock(return_value=mock_page)
        scraper.fetch_page = AsyncMock(return_value="<html><p>Summary text here</p></html>")

        parser = MagicMock()
        parser.extract_article_summary.return_value = "Extracted summary"

        node = TopicNode(
            slug="apex",
            display_name="Apex",
            level=2,
            url="",
            children=[],
            articles=[
                {"title": "Feature 1", "url": "https://help.salesforce.com/article?id=123"}
            ],
        )
        highlights: dict[str, list[dict[str, str]]] = {}
        semaphore = asyncio.Semaphore(8)

        await _process_topic_node(node, scraper, parser, "summer_26", highlights, semaphore)

        assert "apex" in highlights
        assert len(highlights["apex"]) == 1
        assert highlights["apex"][0]["title"] == "Feature 1"
        assert highlights["apex"][0]["summary"] == "Extracted summary"
        assert "language=pt_BR" in highlights["apex"][0]["url"]

    asyncio.run(run())


def test_process_topic_node_no_articles() -> None:
    async def run() -> None:
        scraper = MagicMock()
        parser = MagicMock()

        node = TopicNode(slug="empty", display_name="Empty", level=2, url="")
        highlights: dict[str, list[dict[str, str]]] = {}
        semaphore = asyncio.Semaphore(8)

        await _process_topic_node(node, scraper, parser, "summer_26", highlights, semaphore)

        assert "empty" not in highlights
        scraper.fetch_page.assert_not_called()

    asyncio.run(run())


def test_process_topic_node_article_without_url() -> None:
    async def run() -> None:
        scraper = MagicMock()
        parser = MagicMock()

        node = TopicNode(
            slug="no_url",
            display_name="No URL",
            level=2,
            url="",
            children=[],
            articles=[{"title": "No URL Article", "url": ""}],
        )
        highlights: dict[str, list[dict[str, str]]] = {}
        semaphore = asyncio.Semaphore(8)

        await _process_topic_node(node, scraper, parser, "summer_26", highlights, semaphore)

        assert highlights.get("no_url", []) == []
        scraper.fetch_page.assert_not_called()

    asyncio.run(run())


def test_process_topic_node_scraper_returns_none() -> None:
    async def run() -> None:
        mock_page = AsyncMock()
        scraper = MagicMock()
        scraper._browser = MagicMock()
        scraper._browser.new_page = AsyncMock(return_value=mock_page)
        scraper.fetch_page = AsyncMock(return_value=None)

        parser = MagicMock()

        node = TopicNode(
            slug="apex",
            display_name="Apex",
            level=2,
            url="",
            children=[],
            articles=[{"title": "Feature", "url": "https://help.salesforce.com/article?id=1"}],
        )
        highlights: dict[str, list[dict[str, str]]] = {}
        semaphore = asyncio.Semaphore(8)

        await _process_topic_node(node, scraper, parser, "summer_26", highlights, semaphore)

        assert highlights["apex"][0]["summary"] == "Resumo não disponível."

    asyncio.run(run())


def test_process_topic_node_recursive_children() -> None:
    async def run() -> None:
        mock_page = AsyncMock()
        scraper = MagicMock()
        scraper._browser = MagicMock()
        scraper._browser.new_page = AsyncMock(return_value=mock_page)
        scraper.fetch_page = AsyncMock(return_value="<html><p>Summary</p></html>")

        parser = MagicMock()
        parser.extract_article_summary.return_value = "Child summary"

        child = TopicNode(
            slug="child",
            display_name="Child",
            level=3,
            url="",
            children=[],
            articles=[{"title": "Child Art", "url": "https://help.salesforce.com/article?id=2"}],
        )
        parent = TopicNode(
            slug="parent",
            display_name="Parent",
            level=2,
            url="",
            children=[child],
            articles=[],
        )
        highlights: dict[str, list[dict[str, str]]] = {}
        semaphore = asyncio.Semaphore(8)

        await _process_topic_node(parent, scraper, parser, "summer_26", highlights, semaphore)

        assert "child" in highlights
        assert len(highlights["child"]) == 1

    asyncio.run(run())


def test_process_topic_node_article_already_has_pt_br() -> None:
    async def run() -> None:
        mock_page = AsyncMock()
        scraper = MagicMock()
        scraper._browser = MagicMock()
        scraper._browser.new_page = AsyncMock(return_value=mock_page)
        scraper.fetch_page = AsyncMock(return_value="<html><p>Summary</p></html>")

        parser = MagicMock()
        parser.extract_article_summary.return_value = "Summary"

        node = TopicNode(
            slug="apex",
            display_name="Apex",
            level=2,
            url="",
            children=[],
            articles=[
                {
                    "title": "Feature",
                    "url": "https://help.salesforce.com/article?id=1&language=pt_BR",
                }
            ],
        )
        highlights: dict[str, list[dict[str, str]]] = {}
        semaphore = asyncio.Semaphore(8)

        await _process_topic_node(node, scraper, parser, "summer_26", highlights, semaphore)

        called_url = scraper.fetch_page.call_args[0][0]
        assert called_url.count("language=pt_BR") == 1

    asyncio.run(run())


def test_main_entrypoint() -> None:
    from pathlib import Path

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
