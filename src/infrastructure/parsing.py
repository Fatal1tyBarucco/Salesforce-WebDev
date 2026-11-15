"""Parsing infrastructure — BeautifulSoup-based HTML parsing adapter.

Implements the ParsingStep contract from the domain layer.
"""

from __future__ import annotations

import logging
import re
from typing import Any, ClassVar

from bs4 import BeautifulSoup

from src.core.pipeline.steps import ParsingStep
from src.models.feature import Feature, FeatureCategory, FeatureStatus

logger = logging.getLogger(__name__)


class ParsingAdapter(ParsingStep):
    """Abstract parsing adapter interface."""

    @property
    def name(self) -> str:
        return "parsing_adapter"

    async def execute(self, html: str) -> list[FeatureCategory]:
        raise NotImplementedError


class BeautifulSoupParsingAdapter(ParsingAdapter):
    """BeautifulSoup-based HTML parsing implementation.

    Extracts feature categories and features from Salesforce
    Release Notes Feature Impact pages.
    """

    # CSS selectors for Salesforce Release Notes structure
    CATEGORY_SELECTOR = "section.slds-card, div.category, article.category"
    FEATURE_SELECTOR = "li.feature, div.feature-row, tr.feature-row"
    TITLE_SELECTORS: ClassVar[list[str]] = ["h2", "h3", "h4", ".category-title", ".section-title"]

    def __init__(self, locale: str = "pt_BR") -> None:
        self.locale = locale

    @property
    def name(self) -> str:
        return "beautifulsoup_parsing"

    async def execute(self, html: str) -> list[FeatureCategory]:
        """Parse HTML into feature categories."""
        soup = BeautifulSoup(html, "html.parser")
        categories: list[FeatureCategory] = []

        # Try multiple strategies to find categories
        category_elements = self._find_category_elements(soup)

        for cat_elem in category_elements:
            category = self._parse_category(cat_elem)
            if category and category.features:
                categories.append(category)

        # If no categories found, try fallback: treat whole page as one category
        if not categories:
            fallback = self._parse_fallback(soup)
            if fallback:
                categories.append(fallback)

        logger.info(
            "Parsed %d categories with %d total features",
            len(categories),
            sum(len(c.features) for c in categories),
        )
        return categories

    def _find_category_elements(self, soup: BeautifulSoup) -> list[Any]:
        """Find category container elements."""
        # Strategy 1: Look for section cards
        elements: list[Any] = soup.select(self.CATEGORY_SELECTOR)
        if elements:
            return elements

        # Strategy 2: Look for headings followed by lists
        elements = []
        for heading in soup.find_all(["h2", "h3"]):
            # Find the next sibling list or container
            next_elem = heading.find_next_sibling()
            if next_elem and next_elem.name in ("ul", "ol", "table", "div"):
                elements.append(next_elem)

        return elements

    def _parse_category(self, element: Any) -> FeatureCategory | None:
        """Parse a single category element."""
        # Extract category name
        name = self._extract_category_name(element)
        if not name:
            return None

        # Extract features
        features = self._extract_features(element, name)
        if not features:
            return None

        return FeatureCategory(
            name=name,
            features=tuple(features),
            locale=self.locale,
        )

    def _extract_category_name(self, element: Any) -> str | None:
        """Extract category name from element."""
        # Try heading within element
        for selector in self.TITLE_SELECTORS:
            heading = element.select_one(selector)
            if heading:
                text: str = heading.get_text(strip=True)
                if text and len(text) > 2:
                    return text

        # Try aria-label or data attributes
        for attr in ["aria-label", "data-category", "data-name"]:
            value = element.get(attr)
            if value:
                return str(value)

        # Try parent heading
        parent = element.find_previous(["h2", "h3"])
        if parent:
            return parent.get_text(strip=True)  # type: ignore[no-any-return]

        return None

    def _extract_features(self, element: Any, category_name: str) -> list[Feature]:
        """Extract feature list from category element."""
        features: list[Feature] = []

        # Strategy 1: List items
        for li in element.find_all("li"):
            text = li.get_text(strip=True)
            if text and len(text) > 5:
                features.append(
                    Feature(
                        name=text,
                        category=category_name,
                        raw_text=text,
                        status=FeatureStatus.RAW,
                        locale=self.locale,
                    )
                )

        # Strategy 2: Table rows
        for tr in element.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) >= 2:
                # First cell is usually the feature name
                name = cells[0].get_text(strip=True)
                desc = cells[1].get_text(strip=True)
                if name and len(name) > 3:
                    features.append(
                        Feature(
                            name=name,
                            description=desc,
                            category=category_name,
                            raw_text=f"{name}: {desc}",
                            status=FeatureStatus.RAW,
                            locale=self.locale,
                        )
                    )

        # Strategy 3: Divs with feature class
        for div in element.find_all("div", class_=re.compile(r"feature|item")):
            text = div.get_text(strip=True)
            if text and len(text) > 5:
                features.append(
                    Feature(
                        name=text.split("\n")[0][:100],
                        description=text,
                        category=category_name,
                        raw_text=text,
                        status=FeatureStatus.RAW,
                        locale=self.locale,
                    )
                )

        return features

    def _parse_fallback(self, soup: BeautifulSoup) -> FeatureCategory | None:
        """Fallback: parse entire page as one category."""
        features: list[Feature] = []

        # Find all list items in the page
        for li in soup.find_all("li"):
            text = li.get_text(strip=True)
            if text and len(text) > 10 and not self._is_noise(text):
                features.append(
                    Feature(
                        name=text[:100],
                        raw_text=text,
                        category="Geral",
                        status=FeatureStatus.RAW,
                        locale=self.locale,
                    )
                )

        # Find table rows
        for tr in soup.find_all("tr"):
            cells = tr.find_all(["td"])
            if len(cells) >= 1:
                name = cells[0].get_text(strip=True)
                if name and len(name) > 5 and not self._is_noise(name):
                    desc = " | ".join(c.get_text(strip=True) for c in cells[1:])
                    features.append(
                        Feature(
                            name=name,
                            description=desc,
                            category="Geral",
                            raw_text=f"{name}: {desc}",
                            status=FeatureStatus.RAW,
                            locale=self.locale,
                        )
                    )

        if features:
            return FeatureCategory(
                name="Geral",
                features=tuple(features),
                locale=self.locale,
            )
        return None

    def _is_noise(self, text: str) -> bool:
        """Filter out navigation, footer, and other noise text."""
        noise_patterns = [
            r"^(home|menu|search|login|footer|header|nav)",
            r"(copyright|terms|privacy|cookie)",
            r"^(pt|en|es|fr|de|ja)\b",
            r"^\d+$",
            r"^[^\w]{1,3}$",
        ]
        text_lower = text.lower()
        return any(re.search(p, text_lower) for p in noise_patterns)
