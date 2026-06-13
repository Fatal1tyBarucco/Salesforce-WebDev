import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.config import ReleaseInfo, TopicNode
from src.generator import MarkdownGenerator
from src.readme_updater import ReadmeUpdater
from src.scraper import SalesforceReleaseScraper


def test_markdown_generator_generate_from_map_legacy(tmp_path: Path) -> None:
    """[LEGADO] Testa generate_from_map com TopicContentMap (dict)."""
    generator = MarkdownGenerator(base_dir=str(tmp_path))
    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    content_map = {"apex": ["Feature 1", "Feature 2"], "lwc": []}

    generator.generate_from_map(release, content_map, "https://fake-source.com")

    # Verifica se os arquivos foram criados
    apex_file = tmp_path / "summer_26" / "apex.md"
    lwc_file = tmp_path / "summer_26" / "lwc.md"

    assert apex_file.exists()
    assert lwc_file.exists()

    apex_content = apex_file.read_text()
    assert "# Apex — Summer '26" in apex_content
    assert "Feature 1" in apex_content

    lwc_content = lwc_file.read_text()
    assert "Nenhum conteúdo relevante" in lwc_content


def test_markdown_generator_generate_with_topic_nodes(tmp_path: Path) -> None:
    """Testa o novo generate() com TopicNode (fluxo dinâmico)."""
    generator = MarkdownGenerator(base_dir=str(tmp_path))
    release = ReleaseInfo(name="Winter '26", release_id=258, slug="winter_26")

    # Cria TopicNode com artigos
    apex_child = TopicNode(
        node_id="rn_apex",
        display_name="Apex",
        level=3,
        url="https://help.salesforce.com/rn_apex",
    )
    apex_child.articles = [
        {
            "title": "New Apex Feature",
            "summary": "Resumo do Apex.",
            "url": "https://help.salesforce.com/rn_apex_feature",
        }
    ]

    dev_node = TopicNode(
        node_id="rn_development",
        display_name="Desenvolvimento",
        level=2,
        url="https://help.salesforce.com/rn_development",
        children=[apex_child],
    )

    # Nó sem artigos (não deve gerar arquivo)
    empty_node = TopicNode(
        node_id="rn_empty",
        display_name="Vazio",
        level=2,
        url="https://help.salesforce.com/rn_empty",
    )

    generated = generator.generate(release, [dev_node, empty_node], "https://fake-source.com")

    # Deve gerar apenas o arquivo do nó com conteúdo
    assert len(generated) == 1
    dev_file = tmp_path / "winter_26" / "development.md"
    assert dev_file.exists()

    content = dev_file.read_text()
    assert "# Desenvolvimento — Winter '26" in content
    assert "New Apex Feature" in content
    assert "Resumo do Apex." in content


def test_markdown_generator_list_releases(tmp_path: Path) -> None:
    # 1. Diretorio base nao existe
    non_existent = tmp_path / "does_not_exist"
    generator = MarkdownGenerator(base_dir=str(non_existent))
    assert generator.list_generated_releases() == []

    # 2. Diretorio base existe com estrutura
    base_dir = tmp_path / "releases_list"
    base_dir.mkdir()

    # Subpasta valida
    sub_dir = base_dir / "summer_26"
    sub_dir.mkdir()
    (sub_dir / "apex.md").write_text("details")

    # Arquivo solto (nao e pasta de release) -> deve ser ignorado pela linha 177-178
    (base_dir / "stray_file.txt").write_text("should be ignored")

    generator2 = MarkdownGenerator(base_dir=str(base_dir))
    releases = generator2.list_generated_releases()

    assert len(releases) == 1
    assert releases[0][0] == "summer_26"
    assert "apex" in releases[0][1]


def test_readme_updater_update_flow(tmp_path: Path) -> None:
    readme_file = tmp_path / "README.md"
    readme_file.write_text(
        "Some Header\n<!-- RELEASE_INDEX_START -->\nold index\n<!-- RELEASE_INDEX_END -->\nSome Footer"
    )

    updater = ReadmeUpdater(readme_path=str(readme_file), releases_dir=str(tmp_path))

    # Criamos pastas e arquivos de releases fake
    summer_dir = tmp_path / "summer_26"
    summer_dir.mkdir()
    (summer_dir / "apex.md").write_text("details")

    # Vamos mockar o KNOWN_RELEASES e MONITORED_TOPICS no teste para usar apenas a release existente
    with patch(
        "src.readme_updater.KNOWN_RELEASES",
        [ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")],
    ), patch(
        "src.readme_updater.MONITORED_TOPICS",
        [TopicConfig(slug="apex", display_name="Apex")],
    ):
        success = updater.update()
        assert success is True

        content = readme_file.read_text()
        assert "<!-- RELEASE_INDEX_START -->" in content
        assert "Summer '26" in content
        assert "[✅ Ver](./releases/summer_26/apex.md)" in content


def test_readme_updater_non_existent_readme(tmp_path: Path) -> None:
    readme_file = tmp_path / "README_NEW.md"
    # Não criamos o arquivo, ele não existe!
    updater = ReadmeUpdater(readme_path=str(readme_file), releases_dir=str(tmp_path))

    with patch("src.readme_updater.KNOWN_RELEASES", []):
        success = updater.update()
        assert success is True
        assert readme_file.exists()
        content = readme_file.read_text()
        assert "<!-- RELEASE_INDEX_START -->" in content
        assert "<!-- RELEASE_INDEX_END -->" in content


def test_readme_updater_missing_markers(tmp_path: Path) -> None:
    readme_file = tmp_path / "README_NO_MARKERS.md"
    readme_file.write_text("No markers inside this file at all.")
    updater = ReadmeUpdater(readme_path=str(readme_file), releases_dir=str(tmp_path))

    success = updater.update()
    assert success is False


def test_scraper_fetch_page_success() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        # Mock do _fetch_with_playwright
        with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "<html><body>" + ("a" * 1005) + "</body></html>"

            result = await scraper.fetch_page("https://fake.url")
            assert result is not None
            assert "a" * 1005 in result
            mock_fetch.assert_called_once_with("https://fake.url", None)

    asyncio.run(run())


def test_scraper_fetch_page_all_attempts_fail() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Browser error")

            result = await scraper.fetch_page("https://fake.url")
            assert result is None
            # MAX_RETRY_ATTEMPTS é 5
            assert mock_fetch.call_count == 5

    asyncio.run(run())


def test_scraper_fetch_page_insufficient_content() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
            # Retorna html curto na tentativa (insuficiente) e depois um nulo
            mock_fetch.side_effect = ["<html>short</html>", None, None, None, None]

            result = await scraper.fetch_page("https://fake.url")
            assert result is None
            assert mock_fetch.call_count == 5

    asyncio.run(run())


def test_fetch_with_playwright_internal_flow() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        # Mocks para o fluxo do playwright
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_element = MagicMock()

        mock_page.content.return_value = "mocked HTML body content"
        mock_page.query_selector.return_value = mock_element
        mock_browser.new_page.return_value = mock_page

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        with patch("src.scraper.async_playwright") as mock_ap:
            # Configura o context manager assíncrono
            mock_ap.return_value.__aenter__.return_value = mock_playwright_instance

            result = await scraper._fetch_with_playwright("https://fake.url")

            assert result == "mocked HTML body content"
            mock_playwright_instance.chromium.launch.assert_called_once_with(headless=True)
            mock_browser.new_page.assert_called_once()
            mock_page.goto.assert_called_once()
            mock_page.wait_for_timeout.assert_called()
            mock_page.evaluate.assert_called_once_with(
                "window.scrollTo(0, document.body.scrollHeight)"
            )
            mock_browser.close.assert_called_once()

    asyncio.run(run())


def test_fetch_with_playwright_context_manager_flow() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_page.content.return_value = "mocked HTML context content" * 50
        mock_browser.new_page.return_value = mock_page

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        # Configura o mock do async_playwright().start()
        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright_instance)

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value = mock_ap_instance

            # Entra no context manager para inicializar _playwright e _browser
            async with scraper:
                assert scraper._browser is not None
                # Chama fetch_page (que chamará _fetch_with_playwright com is_standalone = True e self._browser definido)
                result = await scraper.fetch_page("https://fake.url")
                assert result == "mocked HTML context content" * 50

                # Deve abrir uma página a partir do browser já existente
                mock_browser.new_page.assert_called_once()
                # Não deve fechar o browser no final do fetch_page individual
                mock_browser.close.assert_not_called()

            # Fora do context manager, o browser deve ser fechado
            mock_browser.close.assert_called_once()

    asyncio.run(run())
