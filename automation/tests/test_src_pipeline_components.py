import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.config import ReleaseInfo
from src.generator import MarkdownGenerator
from src.readme_updater import ReadmeUpdater
from src.scraper import SalesforceReleaseScraper


def test_markdown_generator_generate(tmp_path: Path) -> None:
    generator = MarkdownGenerator(base_dir=str(tmp_path))
    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    content_map = {"apex": ["Feature 1", "Feature 2"], "lwc": []}

    generator.generate(release, content_map, "https://fake-source.com")

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

    # Vamos mockar o KNOWN_RELEASES no teste para usar apenas a release existente
    with patch(
        "src.readme_updater.KNOWN_RELEASES",
        [ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")],
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
            mock_fetch.assert_called_once_with("https://fake.url")

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


def test_fetch_with_playwright_selector_exception_and_missing() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        # Primeiro seletor lança Exception (cobrindo a linha 89-90: except Exception: continue)
        # Os próximos retornam None (cobrindo a linha 93: No known content selector found)
        mock_page.query_selector.side_effect = [Exception("Selector error")] + [None] * (
            len(scraper.CONTENT_SELECTORS) - 1
        )
        mock_page.content.return_value = "fallback html"
        mock_browser.new_page.return_value = mock_page

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.__aenter__.return_value = mock_playwright_instance

            result = await scraper._fetch_with_playwright("https://fake.url")
            assert result == "fallback html"
            assert mock_page.query_selector.call_count == len(scraper.CONTENT_SELECTORS)

    asyncio.run(run())
