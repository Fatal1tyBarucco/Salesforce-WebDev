"""Tests for scraper feature link extraction and parser docs_url integration."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.parser import FeatureImpactEntry, FeatureImpactParser

# ---------------------------------------------------------------------------
# Scraper: _extract_features_from_html
# ---------------------------------------------------------------------------


class TestExtractFeaturesFromHtml:
    """Tests for SalesforceReleaseScraper._extract_features_from_html."""

    def test_extract_from_table_rows(self) -> None:
        """Extracts features from HTML table rows with links."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <table>
            <tr><th>Feature</th><th>Status</th></tr>
            <tr>
                <td>Voice Feature</td>
                <td><a href="/s/articleView?id=release-notes.rn_voice.htm">Docs</a></td>
            </tr>
            <tr>
                <td>Chat Feature</td>
                <td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_chat.htm">Docs</a></td>
            </tr>
        </table>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 2
        assert features[0]["name"] == "Voice Feature"
        assert "release-notes" in features[0]["docs_url"]
        assert features[1]["name"] == "Chat Feature"
        assert features[1]["docs_url"].startswith("https://")

    def test_extract_from_list_items(self) -> None:
        """Extracts features from HTML list items with links."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <ul>
            <li><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_feature1.htm">Feature One</a></li>
            <li><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_feature2.htm">Feature Two</a></li>
        </ul>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 2
        assert features[0]["name"] == "Feature One"

    def test_extract_from_anchors(self) -> None:
        """Extracts features from any anchor with release-notes in href."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <div>
            <a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_xyz.htm">Some Feature</a>
            <a href="https://example.com/other">Not a feature</a>
        </div>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 1
        assert features[0]["name"] == "Some Feature"

    def test_deduplicates_by_name(self) -> None:
        """Deduplicates features with the same name."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <table>
            <tr><td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_dup.htm">Duplicate</a></td></tr>
            <tr><td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_dup.htm">Duplicate</a></td></tr>
            <tr><td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_unique.htm">Unique</a></td></tr>
        </table>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 2
        names = [f["name"] for f in features]
        assert "Duplicate" in names
        assert "Unique" in names

    def test_empty_html(self) -> None:
        """Returns empty list for empty HTML."""
        from src.scraper import SalesforceReleaseScraper

        assert SalesforceReleaseScraper._extract_features_from_html("") == []

    def test_no_features(self) -> None:
        """Returns empty list when no features found."""
        from src.scraper import SalesforceReleaseScraper

        html = "<html><body><p>No features here</p></body></html>"
        assert SalesforceReleaseScraper._extract_features_from_html(html) == []

    def test_short_names_skipped(self) -> None:
        """Skips feature names shorter than 3 characters."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <table>
            <tr><td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_ab.htm">AB</a></td></tr>
            <tr><td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_long.htm">Long Name Here</a></td></tr>
        </table>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 1
        assert features[0]["name"] == "Long Name Here"

    def test_relative_url_converted(self) -> None:
        """Converts relative URLs to absolute."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <table>
            <tr><td><a href="/s/articleView?id=release-notes.rn_test.htm">Test Feature</a></td></tr>
        </table>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert features[0]["docs_url"].startswith("https://help.salesforce.com")

    def test_non_salesforce_link_skipped(self) -> None:
        """Skips links that are not from Salesforce."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <table>
            <tr>
                <td>External Feature</td>
                <td><a href="https://example.com/docs">External</a></td>
            </tr>
        </table>
        """

        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 1
        assert features[0]["docs_url"] == ""

    def test_malformed_html(self) -> None:
        """Handles malformed HTML gracefully."""
        from src.scraper import SalesforceReleaseScraper

        html = "<<invalid>><<><<>"
        # Should not raise
        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert isinstance(features, list)


# ---------------------------------------------------------------------------
# Scraper: fetch_features_with_links
# ---------------------------------------------------------------------------


class TestFetchFeaturesWithLinks:
    """Tests for SalesforceReleaseScraper.fetch_features_with_links."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_open(self) -> None:
        """Returns empty list when circuit breaker is open."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        for _ in range(scraper._circuit_breaker._threshold + 1):
            scraper._circuit_breaker.record_failure()

        assert scraper._circuit_breaker.is_open
        result = await scraper.fetch_features_with_links("http://example.com")
        assert result == []

    @pytest.mark.asyncio
    async def test_success(self) -> None:
        """Returns features when HTML is fetched successfully."""
        from src.scraper import SalesforceReleaseScraper

        html = """
        <table>
            <tr><td><a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_test.htm">Test Feature</a></td></tr>
        </table>
        """

        scraper = SalesforceReleaseScraper()
        with patch.object(scraper, "_ensure_browser", return_value=True):
            with patch.object(scraper, "_fetch_with_playwright", return_value=html):
                result = await scraper.fetch_features_with_links("http://example.com")

        assert len(result) == 1
        assert result[0]["name"] == "Test Feature"

    @pytest.mark.asyncio
    async def test_empty_html(self) -> None:
        """Retries when HTML is empty."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        with patch.object(scraper, "_ensure_browser", return_value=True):
            with patch.object(scraper, "_fetch_with_playwright", return_value=""):
                result = await scraper.fetch_features_with_links("http://example.com")

        assert result == []

    @pytest.mark.asyncio
    async def test_browser_failure(self) -> None:
        """Returns empty list when browser fails."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper()
        with patch.object(scraper, "_ensure_browser", return_value=False):
            result = await scraper.fetch_features_with_links("http://example.com")

        assert result == []


# ---------------------------------------------------------------------------
# Parser: docs_url integration
# ---------------------------------------------------------------------------


class TestParserDocsUrl:
    """Tests for parser docs_url integration."""

    def test_parse_feature_line_with_docs_url(self) -> None:
        """_parse_feature_line stores docs_url."""
        parser = FeatureImpactParser()
        entry = parser._parse_feature_line("Feature Name\tYes", docs_url="https://example.com")
        assert entry is not None
        assert entry.docs_url == "https://example.com"

    def test_parse_feature_line_without_docs_url(self) -> None:
        """_parse_feature_line works without docs_url."""
        parser = FeatureImpactParser()
        entry = parser._parse_feature_line("Feature Name\tYes")
        assert entry is not None
        assert entry.docs_url == ""

    def test_parse_text_with_link_map(self) -> None:
        """parse_text associates docs_url from link_map."""
        parser = FeatureImpactParser()
        text = "Salesforce geral\nFeature One\tYes\nFeature Two\t\tYes"
        link_map = {"Feature One": "https://example.com/one"}

        categories = parser.parse_text(text, link_map=link_map)
        assert len(categories) >= 1

        # Find all entries
        all_entries: list[FeatureImpactEntry] = []
        for cat in categories:
            all_entries.extend(cat.entries)
            for sub_entries in cat.subcategories.values():
                all_entries.extend(sub_entries)

        # At least one should have docs_url
        found_with_url = [e for e in all_entries if e.docs_url]
        assert len(found_with_url) >= 1

    def test_parse_text_without_link_map(self) -> None:
        """parse_text works without link_map."""
        parser = FeatureImpactParser()
        text = "Salesforce geral\nFeature One\tYes"

        categories = parser.parse_text(text)
        assert len(categories) >= 1

    def test_feature_impact_entry_docs_url_slot(self) -> None:
        """FeatureImpactEntry has docs_url attribute."""
        entry = FeatureImpactEntry(name="Test", docs_url="https://example.com")
        assert entry.docs_url == "https://example.com"
        assert hasattr(entry, "docs_url")


# ---------------------------------------------------------------------------
# Release docs: _format_entry_table with docs_url
# ---------------------------------------------------------------------------


class TestFormatEntryTableDocsUrl:
    """Tests for _format_entry_table with docs_url."""

    def test_format_with_entry_docs_url(self) -> None:
        """Uses entry's docs_url when available."""
        from src.release_docs import _format_entry_table

        entry = FeatureImpactEntry(
            name="Test Feature",
            available_users=True,
            docs_url="https://help.salesforce.com/article",
        )
        result = _format_entry_table(entry)
        assert "🔗" in result
        assert "https://help.salesforce.com/article" in result

    def test_format_with_parameter_docs_url(self) -> None:
        """Falls back to parameter docs_url when entry has none."""
        from src.release_docs import _format_entry_table

        entry = FeatureImpactEntry(name="Test Feature", available_users=True)
        result = _format_entry_table(entry, docs_url="https://example.com/fallback")
        assert "🔗" in result
        assert "https://example.com/fallback" in result

    def test_format_without_any_docs_url(self) -> None:
        """No docs link when neither entry nor parameter has URL."""
        from src.release_docs import _format_entry_table

        entry = FeatureImpactEntry(name="Test Feature", available_users=True)
        result = _format_entry_table(entry)
        assert "🔗" not in result

    def test_entry_docs_url_takes_priority(self) -> None:
        """Entry's docs_url takes priority over parameter."""
        from src.release_docs import _format_entry_table

        entry = FeatureImpactEntry(
            name="Test",
            available_users=True,
            docs_url="https://entry-url.com",
        )
        result = _format_entry_table(entry, docs_url="https://param-url.com")
        assert "entry-url.com" in result
        assert "param-url.com" not in result
