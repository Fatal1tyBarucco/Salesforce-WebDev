"""Tests for src/infrastructure/parsing.py — 100% coverage target."""

from __future__ import annotations


import pytest

from src.infrastructure.parsing import (
    BeautifulSoupParsingAdapter,
    ParsingAdapter,
)
from src.models.feature import FeatureStatus


class TestParsingAdapter:
    """Tests for the abstract ParsingAdapter base class."""

    @pytest.mark.asyncio
    async def test_abstract_execute_raises_not_implemented(self) -> None:
        """Abstract execute should raise NotImplementedError."""
        adapter = ParsingAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.execute("")

    def test_name_property(self) -> None:
        """Base adapter name property."""
        adapter = ParsingAdapter()
        assert adapter.name == "parsing_adapter"


class TestBeautifulSoupParsingAdapter:
    """Tests for BeautifulSoupParsingAdapter."""

    @pytest.fixture
    def adapter(self) -> BeautifulSoupParsingAdapter:
        """Create parsing adapter."""
        return BeautifulSoupParsingAdapter(locale="pt_BR")

    @pytest.fixture
    def sample_html_single_category(self) -> str:
        """Sample HTML with one category."""
        return """
        <html>
            <body>
                <section class="slds-card">
                    <h2>Lightning</h2>
                    <ul>
                        <li>New Lightning component for dashboards</li>
                        <li>Improved Lightning performance</li>
                    </ul>
                </section>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_html_multiple_categories(self) -> str:
        """Sample HTML with multiple categories."""
        return """
        <html>
            <body>
                <section class="slds-card">
                    <h2>Lightning</h2>
                    <ul>
                        <li>New Lightning component for dashboards</li>
                    </ul>
                </section>
                <section class="slds-card">
                    <h2>Apex</h2>
                    <ul>
                        <li>New Apex feature</li>
                    </ul>
                </section>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_html_table_features(self) -> str:
        """Sample HTML with table-based features."""
        return """
        <html>
            <body>
                <section class="slds-card">
                    <h2>Platform</h2>
                    <table>
                        <tr>
                            <td>Feature 1</td>
                            <td>Description 1</td>
                        </tr>
                        <tr>
                            <td>Feature 2</td>
                            <td>Description 2</td>
                        </tr>
                    </table>
                </section>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_html_div_features(self) -> str:
        """Sample HTML with div-based features."""
        return """
        <html>
            <body>
                <section class="slds-card">
                    <h2>Analytics</h2>
                    <div class="feature-item">Analytics feature 1</div>
                    <div class="feature">Analytics feature 2</div>
                </section>
            </body>
        </html>
        """

    @pytest.fixture
    def sample_html_fallback(self) -> str:
        """Sample HTML that triggers fallback parsing."""
        return """
        <html>
            <body>
                <ul>
                    <li>Valid feature one with enough text</li>
                    <li>Valid feature two with enough text</li>
                    <li>home</li>
                    <li>copyright 2024</li>
                </ul>
            </body>
        </html>
        """

    @pytest.fixture
    def empty_html(self) -> str:
        """Empty HTML."""
        return "<html><body></body></html>"

    @pytest.mark.asyncio
    async def test_name_property(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Adapter name should be correct."""
        assert adapter.name == "beautifulsoup_parsing"

    @pytest.mark.asyncio
    async def test_execute_parses_single_category(
        self, adapter: BeautifulSoupParsingAdapter, sample_html_single_category: str
    ) -> None:
        """Should parse single category with list items."""
        categories = await adapter.execute(sample_html_single_category)

        assert len(categories) == 1
        cat = categories[0]
        assert cat.name == "Lightning"
        assert cat.locale == "pt_BR"
        assert len(cat.features) == 2

        feat1 = cat.features[0]
        assert feat1.name == "New Lightning component for dashboards"
        assert feat1.category == "Lightning"
        assert feat1.status == FeatureStatus.RAW
        assert feat1.locale == "pt_BR"

    @pytest.mark.asyncio
    async def test_execute_parses_multiple_categories(
        self, adapter: BeautifulSoupParsingAdapter, sample_html_multiple_categories: str
    ) -> None:
        """Should parse multiple categories."""
        categories = await adapter.execute(sample_html_multiple_categories)

        assert len(categories) == 2
        assert categories[0].name == "Lightning"
        assert categories[1].name == "Apex"
        assert len(categories[0].features) == 1
        assert len(categories[1].features) == 1

    @pytest.mark.asyncio
    async def test_execute_parses_table_features(
        self, adapter: BeautifulSoupParsingAdapter, sample_html_table_features: str
    ) -> None:
        """Should parse features from table rows."""
        categories = await adapter.execute(sample_html_table_features)

        assert len(categories) == 1
        cat = categories[0]
        assert cat.name == "Platform"
        assert len(cat.features) == 2

        feat1 = cat.features[0]
        assert feat1.name == "Feature 1"
        assert feat1.description == "Description 1"
        assert feat1.raw_text == "Feature 1: Description 1"

    @pytest.mark.asyncio
    async def test_execute_parses_div_features(
        self, adapter: BeautifulSoupParsingAdapter, sample_html_div_features: str
    ) -> None:
        """Should parse features from divs with feature class."""
        categories = await adapter.execute(sample_html_div_features)

        assert len(categories) == 1
        cat = categories[0]
        assert cat.name == "Analytics"
        assert len(cat.features) == 2

    @pytest.mark.asyncio
    async def test_execute_fallback_parses_entire_page(
        self, adapter: BeautifulSoupParsingAdapter, sample_html_fallback: str
    ) -> None:
        """Should fallback to parsing entire page when no categories found."""
        categories = await adapter.execute(sample_html_fallback)

        assert len(categories) == 1
        cat = categories[0]
        assert cat.name == "Geral"
        # Should filter out noise (home, copyright)
        assert len(cat.features) == 2
        for feat in cat.features:
            assert feat.category == "Geral"

    @pytest.mark.asyncio
    async def test_execute_returns_empty_for_empty_html(
        self, adapter: BeautifulSoupParsingAdapter, empty_html: str
    ) -> None:
        """Should return empty list for empty HTML."""
        categories = await adapter.execute(empty_html)
        assert categories == []

    @pytest.mark.asyncio
    async def test_extract_category_name_from_heading(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract category name from heading."""
        from bs4 import BeautifulSoup

        html = "<div><h2>Test Category</h2></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        name = adapter._extract_category_name(element)
        assert name == "Test Category"

    @pytest.mark.asyncio
    async def test_extract_category_name_from_aria_label(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract category name from aria-label."""
        from bs4 import BeautifulSoup

        html = '<div aria-label="Aria Category"></div>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        name = adapter._extract_category_name(element)
        assert name == "Aria Category"

    @pytest.mark.asyncio
    async def test_extract_category_name_from_data_attribute(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract category name from data-category attribute."""
        from bs4 import BeautifulSoup

        html = '<div data-category="Data Category"></div>'
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        name = adapter._extract_category_name(element)
        assert name == "Data Category"

    @pytest.mark.asyncio
    async def test_extract_category_name_from_parent_heading(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract category name from parent heading."""
        from bs4 import BeautifulSoup

        html = "<h2>Parent Category</h2><div>Content</div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        name = adapter._extract_category_name(element)
        assert name == "Parent Category"

    @pytest.mark.asyncio
    async def test_extract_category_name_returns_none_for_no_name(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should return None when no name can be extracted."""
        from bs4 import BeautifulSoup

        html = "<div><span>No heading here</span></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        name = adapter._extract_category_name(element)
        assert name is None

    @pytest.mark.asyncio
    async def test_extract_features_from_list_items(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract features from list items."""
        from bs4 import BeautifulSoup

        html = "<div><ul><li>Feature 1</li><li>Feature 2</li></ul></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        features = adapter._extract_features(element, "Test Category")

        assert len(features) == 2
        assert features[0].name == "Feature 1"
        assert features[1].name == "Feature 2"

    @pytest.mark.asyncio
    async def test_extract_features_skips_short_text(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should skip very short text items."""
        from bs4 import BeautifulSoup

        html = "<div><ul><li>Ok</li><li>Valid feature text</li></ul></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        features = adapter._extract_features(element, "Test Category")

        assert len(features) == 1
        assert features[0].name == "Valid feature text"

    @pytest.mark.asyncio
    async def test_extract_features_from_table_rows(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract features from table rows."""
        from bs4 import BeautifulSoup

        html = "<div><table><tr><td>Name</td><td>Desc</td></tr></table></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        features = adapter._extract_features(element, "Test Category")

        assert len(features) == 1
        assert features[0].name == "Name"
        assert features[0].description == "Desc"

    @pytest.mark.asyncio
    async def test_extract_features_skips_table_rows_with_few_cells(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should skip table rows with insufficient cells."""
        from bs4 import BeautifulSoup

        html = "<div><table><tr><td>Only one cell</td></tr></table></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        features = adapter._extract_features(element, "Test Category")

        assert len(features) == 0

    @pytest.mark.asyncio
    async def test_extract_features_from_divs_with_feature_class(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should extract features from divs with feature class."""
        from bs4 import BeautifulSoup

        html = "<div><div class='feature-item'>Feature div 1</div><div class='feature'>Feature div 2</div></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        features = adapter._extract_features(element, "Test Category")

        assert len(features) == 2

    @pytest.mark.asyncio
    async def test_parse_fallback_filters_noise(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Fallback should filter out navigation/noise text."""
        from bs4 import BeautifulSoup

        html = "<ul><li>home</li><li>Valid feature text here</li><li>copyright 2024</li></ul>"
        soup = BeautifulSoup(html, "html.parser")

        category = adapter._parse_fallback(soup)

        assert category is not None
        assert category.name == "Geral"
        assert len(category.features) == 1
        assert category.features[0].name == "Valid feature text here"

    @pytest.mark.asyncio
    async def test_parse_fallback_returns_none_when_no_valid_features(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Fallback should return None when no valid features found."""
        from bs4 import BeautifulSoup

        html = "<ul><li>home</li><li>menu</li></ul>"
        soup = BeautifulSoup(html, "html.parser")

        category = adapter._parse_fallback(soup)

        assert category is None

    @pytest.mark.asyncio
    async def test_is_noise_identifies_navigation(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should identify navigation text as noise."""
        assert adapter._is_noise("home") is True
        assert adapter._is_noise("menu") is True
        assert adapter._is_noise("search") is True
        assert adapter._is_noise("login") is True

    @pytest.mark.asyncio
    async def test_is_noise_identifies_footer(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Should identify footer text as noise."""
        assert adapter._is_noise("copyright 2024") is True
        assert adapter._is_noise("terms of service") is True
        assert adapter._is_noise("privacy policy") is True
        assert adapter._is_noise("cookie settings") is True

    @pytest.mark.asyncio
    async def test_is_noise_identifies_language_codes(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should identify language codes as noise."""
        assert adapter._is_noise("pt") is True
        assert adapter._is_noise("en") is True
        assert adapter._is_noise("es") is True
        assert adapter._is_noise("fr") is True

    @pytest.mark.asyncio
    async def test_is_noise_identifies_numbers_only(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should identify numbers-only as noise."""
        assert adapter._is_noise("123") is True
        assert adapter._is_noise("42") is True

    @pytest.mark.asyncio
    async def test_is_noise_identifies_short_punctuation(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should identify short punctuation as noise."""
        assert adapter._is_noise("...") is True
        assert adapter._is_noise("...") is True
        assert adapter._is_noise("!!") is True

    @pytest.mark.asyncio
    async def test_is_noise_allows_valid_text(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Should allow valid feature text."""
        assert adapter._is_noise("Valid feature description") is False
        assert adapter._is_noise("New Lightning component") is False
        assert adapter._is_noise("Improved performance metrics") is False

    @pytest.mark.asyncio
    async def test_locale_parameter_respected(self) -> None:
        """Should respect locale parameter."""
        adapter_en = BeautifulSoupParsingAdapter(locale="en_US")
        adapter_pt = BeautifulSoupParsingAdapter(locale="pt_BR")

        assert adapter_en.locale == "en_US"
        assert adapter_pt.locale == "pt_BR"

    @pytest.mark.asyncio
    async def test_parse_category_returns_none_when_no_name(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """_parse_category should return None when no name extracted."""
        from bs4 import BeautifulSoup

        html = "<div><ul><li>Feature</li></ul></div>"
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        category = adapter._parse_category(element)

        assert category is None

    @pytest.mark.asyncio
    async def test_parse_category_returns_none_when_no_features(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """_parse_category should return None when no features extracted."""
        from bs4 import BeautifulSoup

        html = "<div><h2>Category Name</h2><ul><li>ab</li></ul></div>"  # too short
        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("div")

        category = adapter._parse_category(element)

        assert category is None


class TestFindCategoryElements:
    """Tests for _find_category_elements method."""

    @pytest.fixture
    def adapter(self) -> BeautifulSoupParsingAdapter:
        return BeautifulSoupParsingAdapter()

    @pytest.mark.asyncio
    async def test_finds_section_cards(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Should find section cards with slds-card class."""
        from bs4 import BeautifulSoup

        html = "<section class='slds-card'>Content</section>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_finds_category_divs(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Should find divs with category class."""
        from bs4 import BeautifulSoup

        html = "<div class='category'>Content</div>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_finds_article_categories(self, adapter: BeautifulSoupParsingAdapter) -> None:
        """Should find articles with category class."""
        from bs4 import BeautifulSoup

        html = "<article class='category'>Content</article>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_fallback_to_headings_with_lists(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should fallback to headings followed by lists."""
        from bs4 import BeautifulSoup

        html = "<h2>Heading</h2><ul><li>Item</li></ul>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_fallback_to_headings_with_tables(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should fallback to headings followed by tables."""
        from bs4 import BeautifulSoup

        html = "<h2>Heading</h2><table><tr><td>Cell</td></tr></table>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_fallback_to_headings_with_divs(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should fallback to headings followed by divs."""
        from bs4 import BeautifulSoup

        html = "<h2>Heading</h2><div>Content</div>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert len(elements) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_when_nothing_found(
        self, adapter: BeautifulSoupParsingAdapter
    ) -> None:
        """Should return empty list when nothing matches."""
        from bs4 import BeautifulSoup

        html = "<span>Just a span</span>"
        soup = BeautifulSoup(html, "html.parser")

        elements = adapter._find_category_elements(soup)

        assert elements == []
