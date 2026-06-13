"""Testes para src/main.py — Orquestrador do pipeline de extração dinâmica."""

from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from src.main import main, _update_readme
from src.config import TopicNode

_original_asyncio_run = asyncio.run


def _make_sample_tree() -> list[TopicNode]:
    """Cria uma árvore de tópicos de amostra para testes."""
    article_node = TopicNode(
        node_id="rn_apex_triggers",
        display_name="Nova funcionalidade de Triggers",
        level=4,
        url="https://help.salesforce.com/rn_apex_triggers?release=258&language=pt_BR",
        is_leaf=True,
    )
    article_node.articles = [
        {
            "title": "Nova funcionalidade de Triggers",
            "summary": "Triggers agora executam de forma assíncrona.",
            "url": "https://help.salesforce.com/rn_apex_triggers?release=258&language=pt_BR",
        }
    ]

    apex_node = TopicNode(
        node_id="rn_apex",
        display_name="Apex",
        level=3,
        url="https://help.salesforce.com/rn_apex?release=258&language=pt_BR",
        children=[article_node],
    )

    dev_node = TopicNode(
        node_id="rn_development",
        display_name="Desenvolvimento",
        level=2,
        url="https://help.salesforce.com/rn_development?release=258&language=pt_BR",
        children=[apex_node],
    )

    return [dev_node]


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
    """Deve executar o pipeline completo sem erros quando scraper retorna HTML válido."""
    # Setup mocks
    scraper_inst = MagicMock()
    scraper_inst.fetch_page = AsyncMock(return_value="<html>rendered</html>")
    scraper_inst.__aenter__ = AsyncMock(return_value=scraper_inst)
    scraper_inst.__aexit__ = AsyncMock(return_value=None)
    mock_scraper_class.return_value = scraper_inst

    sample_tree = _make_sample_tree()
    parser_inst = MagicMock()
    parser_inst.extract_topic_tree.return_value = sample_tree
    parser_inst.extract_article_summary.return_value = "Resumo de teste."
    mock_parser_class.return_value = parser_inst

    generator_inst = MagicMock()
    generator_inst.list_generated_releases.return_value = [("winter_26", ["development"])]
    mock_generator_class.return_value = generator_inst

    # Fazer asyncio.run executar a corrotina real
    mock_asyncio_run.side_effect = lambda coro: _original_asyncio_run(coro)

    # Executa main
    main()

    # Asserts básicos
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
    """Não deve chamar o parser quando o scraper retorna None."""
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

    # Não deve chamar parser quando HTML é None
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
    """Deve capturar exceções no loop sem interromper execução global."""
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

    # Não deve quebrar a execução global, apenas logar e prosseguir
    mock_update_readme.assert_called_once()


def test_update_readme_writes_file() -> None:
    """Deve escrever o README com o conteúdo correto."""
    with patch("src.main.Path.write_text") as mock_write_text:
        releases = [("winter_26", ["development", "security"])]
        highlights = {
            "winter_26": {
                "development": [
                    {
                        "title": "Nova Funcionalidade Apex",
                        "summary": "Resumo da nova funcionalidade.",
                        "url": "https://help.salesforce.com/rn_apex",
                    }
                ]
            }
        }
        _update_readme(releases, highlights)

        mock_write_text.assert_called_once()
        written_content = mock_write_text.call_args[0][0]
        assert "Winter 26" in written_content
        assert "CI/CD Status" in written_content
        assert "banner.png" in written_content
        assert "Nova Funcionalidade Apex" in written_content


def test_update_readme_handles_empty_releases() -> None:
    """Deve escrever um README mesmo sem releases."""
    with patch("src.main.Path.write_text") as mock_write_text:
        _update_readme([], {})
        mock_write_text.assert_called_once()
        content = mock_write_text.call_args[0][0]
        assert "Salesforce Release Notes Intelligence" in content


def test_main_entrypoint() -> None:
    """Testa o bloco if __name__ == '__main__' sem efeitos colaterais."""
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

    with patch("src.main.SalesforceReleaseScraper"), patch("src.main.ReleaseNotesParser"), patch(
        "src.main.MarkdownGenerator"
    ), patch("src.main.asyncio.run"):
        exec(code, global_ns)
