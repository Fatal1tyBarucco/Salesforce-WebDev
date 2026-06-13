"""Parser for Salesforce Help release notes — navigation tree extraction.

Extracts the topic hierarchy directly from the DOM navigation tree
(li[role="treeitem"]) instead of keyword-based matching. The Salesforce
Help portal already organizes articles by topic in its sidebar ToC.
"""

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from .config import EXCLUDED_NODE_SLUGS, TopicNode

logger: logging.Logger = logging.getLogger(__name__)

SOURCE_BASE = "https://help.salesforce.com"

# CSS selectors for the ToC container in the Salesforce Help SPA
TOC_SELECTORS: list[str] = [
    ".toc-container",
    "ul.tree",
    '[role="tree"]',
    "nav.toc",
    ".slds-tree__group",
]


class ReleaseNotesParser:
    """Parses the Salesforce Help release notes navigation tree."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_topic_tree(self, soup: BeautifulSoup) -> list[TopicNode]:
        """
        Extract the full topic hierarchy from the page navigation tree.

        The Salesforce Help portal renders a sidebar ToC with <li role="treeitem">
        elements organized by aria-level. Level 1 is the root (ignored).
        Level 2+ are real topics and subtopics.

        Args:
            soup: BeautifulSoup parsed HTML of the release notes page.

        Returns:
            List of TopicNode at level 2 (top-level categories), each with
            nested children and leaf articles.
        """
        logger.info("[PARSER] Extracting topic tree from navigation DOM")

        toc_container = self._find_toc_container(soup)
        if toc_container is None:
            logger.warning("[PARSER] ToC container not found in page DOM")
            return []

        tree_root = toc_container
        tree_ul = toc_container.find("ul", class_="tree")
        if isinstance(tree_ul, Tag):
            tree_root = tree_ul

        root_items = tree_root.find_all(
            "li", attrs={"role": "treeitem", "aria-level": "1"}, recursive=False
        )
        if not root_items:
            root_items = tree_root.find_all(
                "li", attrs={"role": "treeitem"}, recursive=False
            )

        topics: list[TopicNode] = []

        for root_li in root_items:
            child_items = root_li.find_all("li", attrs={"role": "treeitem"}, recursive=False)
            nested_ul = root_li.find("ul", recursive=False)
            if nested_ul and not child_items:
                child_items = nested_ul.find_all("li", attrs={"role": "treeitem"}, recursive=False)

            for li in child_items:
                node = self._build_node(li)
                if node and node.slug not in EXCLUDED_NODE_SLUGS:
                    topics.append(node)

        logger.info(
            "[PARSER] Extracted %d top-level topics from navigation tree",
            len(topics),
        )
        return topics

    def extract_article_summary(self, soup: BeautifulSoup) -> str:
        """
        Extracts a concise summary from an article page.
        Looks for 'Why' and 'How' sections or the first significant paragraph.
        """
        for header in soup.find_all(["h2", "h3", "p", "strong"]):
            text = header.get_text().strip().lower()
            if text in ["por que essa alteração é importante", "why", "por que"]:
                next_p = header.find_next("p")
                if next_p:
                    return ReleaseNotesParser._clean_text(next_p.get_text())

        content_div = soup.select_one("article, #articleViewContent, div.content")
        if content_div:
            paragraphs = content_div.find_all("p")
            for p in paragraphs:
                cleaned_text = ReleaseNotesParser._clean_text(p.get_text())
                if len(cleaned_text) > 50:
                    return cleaned_text

        return "Resumo não disponível para este artigo."

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_toc_container(self, soup: BeautifulSoup) -> Tag | None:
        """Try multiple selectors to locate the ToC container."""
        for selector in TOC_SELECTORS:
            container = soup.select_one(selector)
            if isinstance(container, Tag):
                logger.debug("[PARSER] ToC found with selector: %s", selector)
                return container

        treeitem = soup.find("li", attrs={"role": "treeitem"})
        if isinstance(treeitem, Tag) and isinstance(treeitem.parent, Tag):
            return treeitem.parent

        return None

    def _build_node(self, li: Tag) -> TopicNode | None:
        """
        Recursively build a TopicNode from an <li role="treeitem"> element.

        - Nodes with data-is-link="true" are article leaves
        - Nodes without are container nodes (categories/subcategories)
        - Nodes with both link and nested children are treated as containers
        """
        node_id = self._get_node_id(li)
        aria_level = self._get_aria_level(li)
        label_text = self._get_label_text(li)
        node_url = self._get_node_url(li)

        if not node_id or not label_text:
            return None

        slug = self._id_to_slug(node_id)

        data_is_link_raw = li.get("data-is-link")
        if data_is_link_raw and isinstance(data_is_link_raw, str):
            is_explicit_link = data_is_link_raw == "true"
        else:
            is_explicit_link = False

        nested_ul_result = li.find("ul", recursive=False)
        has_children = isinstance(nested_ul_result, Tag)

        if is_explicit_link and not has_children:
            return TopicNode(
                slug=slug,
                display_name=label_text,
                level=aria_level,
                url=node_url,
                children=[],
                articles=[],
            )

        children: list[TopicNode] = []
        articles: list[dict[str, str]] = []

        if has_children and isinstance(nested_ul_result, Tag):
            for child_li in nested_ul_result.find_all(
                "li", attrs={"role": "treeitem"}, recursive=False
            ):
                child_node = self._build_node(child_li)
                if child_node is None:
                    continue

                if child_node.is_leaf() and child_node.url and not child_node.articles:
                    articles.append(
                        {
                            "title": child_node.display_name,
                            "url": child_node.url,
                        }
                    )
                else:
                    children.append(child_node)

        node = TopicNode(
            slug=slug,
            display_name=label_text,
            level=aria_level,
            url=node_url,
            children=children,
            articles=articles,
        )

        if node.is_leaf() and node.url and not node.articles:
            return node

        return node

    def _get_node_id(self, li: Tag) -> str:
        raw_id = li.get("id", "")
        if isinstance(raw_id, list):
            raw_id = raw_id[0] if raw_id else ""
        return re.sub(r"[^a-zA-Z0-9_]", "", raw_id) if raw_id else ""

    def _get_aria_level(self, li: Tag) -> int:
        raw = li.get("aria-level", "1")
        if isinstance(raw, list):
            raw = raw[0] if raw else "1"
        try:
            return int(raw)
        except (ValueError, TypeError):
            return 1

    def _get_label_text(self, li: Tag) -> str:
        title_attr = li.get("title", "")
        if title_attr and isinstance(title_attr, str):
            cleaned = ReleaseNotesParser._clean_text(title_attr)
            if cleaned:
                return cleaned

        label_span = li.find("span", class_="tree-item-label")
        if isinstance(label_span, Tag):
            return ReleaseNotesParser._clean_text(label_span.get_text())

        label_div = li.find("div", attrs={"role": "label"})
        if isinstance(label_div, Tag):
            return ReleaseNotesParser._clean_text(label_div.get_text())

        first_text = li.get_text(strip=True)
        return ReleaseNotesParser._clean_text(first_text)

    def _find_link(self, li: Tag) -> Tag | None:
        """Find the <a> tag in a treeitem, checking direct children and slds-tree__item."""
        link = li.find("a", href=True, recursive=False)
        if isinstance(link, Tag):
            return link
        tree_item_div = li.find("div", class_="slds-tree__item")
        if isinstance(tree_item_div, Tag):
            link = tree_item_div.find("a", href=True, recursive=False)
            if isinstance(link, Tag):
                return link
        return None

    def _get_node_url(self, li: Tag) -> str:
        link = self._find_link(li)
        if isinstance(link, Tag):
            href = link.get("href", "")
            if isinstance(href, list):
                href = href[0] if href else ""
            if href:
                return str(urljoin(SOURCE_BASE, href))
        return ""

    def _id_to_slug(self, node_id: str) -> str:
        slug = re.sub(r"_leaf$", "", node_id)
        slug = re.sub(r"^rn_", "", slug)
        return slug if slug else node_id

    @staticmethod
    def _clean_text(raw: str) -> str:
        """Remove extras de espaço e textos muito curtos."""
        cleaned: str = re.sub(r"\s+", " ", raw).strip()
        if len(cleaned) < 3:
            return ""
        return cleaned
