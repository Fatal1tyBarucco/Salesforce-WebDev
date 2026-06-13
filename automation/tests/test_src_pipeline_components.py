import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from src.config import ReleaseInfo, TopicNode
from src.generator import MarkdownGenerator
from src.readme_updater import ReadmeUpdater
from src.scraper import SalesforceReleaseScraper


def test_markdown_generator_generate(tmp_path: Path) -> None:
    generator = MarkdownGenerator(base_dir=str(tmp_path))
    release = ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26")

    nodes = [
        TopicNode(
            slug="apex",
            display_name="Apex",
            level=2,
            url="",
            children=[],
            articles=[
                {"title": "Feature 1", "url": "http://a.com", "summary": "Summary 1"},
            ],
        ),
        TopicNode(
            slug="lwc",
            display_name="LWC",
            level=2,
            url="",
            children=[],
            articles=[],
        ),
    ]

    generator.generate(release, nodes, "https://fake-source.com")

    apex_file = tmp_path / "summer_26" / "apex.md"
    lwc_file = tmp_path / "summer_26" / "lwc.md"

    assert apex_file.exists()
    assert lwc_file.exists()

    apex_content = apex_file.read_text()
    assert "# Apex — Summer '26" in apex_content
    assert "Feature 1" in apex_content

    lwc_content = lwc_file.read_text()
    assert "Nenhum conteúdo relevante" in lwc_content


def test_markdown_generator_nested_topics(tmp_path: Path) -> None:
    generator = MarkdownGenerator(base_dir=str(tmp_path))
    release = ReleaseInfo(name="Winter '26", release_id=258, slug="winter_26")

    nodes = [
        TopicNode(
            slug="development",
            display_name="Desenvolvimento",
            level=2,
            url="",
            children=[
                TopicNode(
                    slug="apex",
                    display_name="Apex",
                    level=3,
                    url="",
                    children=[],
                    articles=[
                        {"title": "Apex Feature", "url": "http://a.com", "summary": "Test"},
                    ],
                ),
            ],
            articles=[],
        ),
    ]

    generator.generate(release, nodes, "https://fake-source.com")

    dev_file = tmp_path / "winter_26" / "development.md"
    assert dev_file.exists()
    content = dev_file.read_text()
    assert "Desenvolvimento" in content
    assert "Apex Feature" in content


def test_markdown_generator_list_releases(tmp_path: Path) -> None:
    non_existent = tmp_path / "does_not_exist"
    generator = MarkdownGenerator(base_dir=str(non_existent))
    assert generator.list_generated_releases() == []

    base_dir = tmp_path / "releases_list"
    base_dir.mkdir()

    sub_dir = base_dir / "summer_26"
    sub_dir.mkdir()
    (sub_dir / "apex.md").write_text("details")

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

    summer_dir = tmp_path / "summer_26"
    summer_dir.mkdir()
    (summer_dir / "apex.md").write_text("details")

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


def test_readme_updater_dynamic_topics(tmp_path: Path) -> None:
    readme_file = tmp_path / "README.md"
    readme_file.write_text("<!-- RELEASE_INDEX_START -->\nold\n<!-- RELEASE_INDEX_END -->")

    updater = ReadmeUpdater(readme_path=str(readme_file), releases_dir=str(tmp_path))

    summer_dir = tmp_path / "summer_26"
    summer_dir.mkdir()
    (summer_dir / "development.md").write_text("dev content")
    (summer_dir / "security.md").write_text("sec content")

    winter_dir = tmp_path / "winter_26"
    winter_dir.mkdir()
    (winter_dir / "development.md").write_text("dev content")

    with patch(
        "src.readme_updater.KNOWN_RELEASES",
        [
            ReleaseInfo(name="Winter '26", release_id=258, slug="winter_26"),
            ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26"),
        ],
    ):
        success = updater.update()
        assert success is True

        content = readme_file.read_text()
        assert "Development" in content
        assert "Security" in content
        assert "[✅ Ver](./releases/summer_26/development.md)" in content
        assert "[✅ Ver](./releases/winter_26/development.md)" in content


def test_readme_updater_non_existent_readme(tmp_path: Path) -> None:
    readme_file = tmp_path / "README_NEW.md"
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


def test_readme_updater_non_existent_releases_dir(tmp_path: Path) -> None:
    readme_file = tmp_path / "README.md"
    readme_file.write_text(
        "<!-- RELEASE_INDEX_START -->\nold\n<!-- RELEASE_INDEX_END -->"
    )
    non_existent = tmp_path / "non_existent_releases"
    updater = ReadmeUpdater(readme_path=str(readme_file), releases_dir=str(non_existent))

    with patch("src.readme_updater.KNOWN_RELEASES", []):
        success = updater.update()
        assert success is True


def test_scraper_fetch_page_success() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = "<html><body>" + ("a" * 1005) + "</body></html>"

            result = await scraper.fetch_page("https://fake.url")
            assert result is not None
            assert "a" * 1005 in result
            mock_fetch.assert_called_once_with("https://fake.url", None, expand_toc=True)

    asyncio.run(run())


def test_scraper_fetch_page_all_attempts_fail() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = Exception("Browser error")

            result = await scraper.fetch_page("https://fake.url")
            assert result is None
            assert mock_fetch.call_count == 5

    asyncio.run(run())


def test_scraper_fetch_page_insufficient_content() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.side_effect = ["<html>short</html>", None, None, None, None]

            result = await scraper.fetch_page("https://fake.url")
            assert result is None
            assert mock_fetch.call_count == 5

    asyncio.run(run())


def test_fetch_with_playwright_internal_flow() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()
        mock_element = MagicMock()

        mock_page.content.return_value = "mocked HTML body content"
        mock_page.query_selector.return_value = mock_element
        mock_browser.new_page.return_value = mock_page

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        with patch("src.scraper.async_playwright") as mock_ap:
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

        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright_instance)

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value = mock_ap_instance

            async with scraper:
                assert scraper._browser is not None
                result = await scraper.fetch_page("https://fake.url")
                assert result == "mocked HTML context content" * 50

                mock_browser.new_page.assert_called_once()
                mock_browser.close.assert_not_called()

            mock_browser.close.assert_called_once()

    asyncio.run(run())


def test_scraper_expand_toc_nodes() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_browser = AsyncMock()
        mock_page = AsyncMock()

        mock_collapsed_node = AsyncMock()
        mock_page.query_selector_all.return_value = [mock_collapsed_node]
        mock_page.content.return_value = "html content " * 100
        mock_browser.new_page.return_value = mock_page

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        mock_ap_instance = MagicMock()
        mock_ap_instance.start = AsyncMock(return_value=mock_playwright_instance)

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value = mock_ap_instance

            async with scraper:
                await scraper.fetch_page("https://fake.url")

                mock_page.query_selector_all.assert_called_with(
                    'li[role="treeitem"][aria-expanded="false"]'
                )
                assert mock_collapsed_node.click.call_count >= 1

    asyncio.run(run())


def test_expand_toc_nodes_click_exception() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_node = AsyncMock()
        mock_node.click.side_effect = Exception("Click failed")
        mock_page.query_selector_all.return_value = [mock_node]

        await scraper._expand_toc_nodes(mock_page)
        mock_page.query_selector_all.assert_called_once()

    asyncio.run(run())


def test_expand_toc_nodes_query_exception() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_page.query_selector_all.side_effect = Exception("Query failed")

        await scraper._expand_toc_nodes(mock_page)

    asyncio.run(run())


def test_expand_toc_nodes_empty() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_page.query_selector_all.return_value = []

        await scraper._expand_toc_nodes(mock_page)
        mock_page.query_selector_all.assert_called_once()

    asyncio.run(run())


def test_extract_toc_html_standalone_no_browser() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.inner_html.return_value = "<ul>" + "x" * 200 + "</ul>"
        mock_page.query_selector.return_value = mock_element
        mock_page.content.return_value = "<html>" + "y" * 200 + "</html>"

        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        mock_playwright_instance = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.__aenter__.return_value = mock_playwright_instance

            result = await scraper.extract_toc_html("https://fake.url")
            assert result is not None
            assert "x" * 200 in result

    asyncio.run(run())


def test_extract_toc_html_with_existing_browser() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.inner_html.return_value = "<ul>" + "z" * 200 + "</ul>"
        mock_page.query_selector.return_value = mock_element

        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page

        scraper._browser = mock_browser

        result = await scraper.extract_toc_html("https://fake.url")
        assert result is not None
        mock_browser.new_page.assert_called_once()

    asyncio.run(run())


def test_extract_toc_html_exception() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.__aenter__.side_effect = Exception("PW failed")

            result = await scraper.extract_toc_html("https://fake.url")
            assert result is None

    asyncio.run(run())


def test_extract_toc_from_page_fallback_to_full_content() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_page.query_selector.return_value = None
        mock_page.content.return_value = "<html>full page content here</html>"

        result = await scraper._extract_toc_from_page("https://fake.url", mock_page)
        assert result == "<html>full page content here</html>"

    asyncio.run(run())


def test_extract_toc_from_page_toc_too_short() -> None:
    scraper = SalesforceReleaseScraper()

    async def run() -> None:
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        mock_element.inner_html.return_value = "short"
        mock_page.query_selector.return_value = mock_element
        mock_page.content.return_value = "<html>" + "x" * 200 + "</html>"

        result = await scraper._extract_toc_from_page("https://fake.url", mock_page)
        assert "x" * 200 in result

    asyncio.run(run())
