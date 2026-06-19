"""Parser for Salesforce Help release notes — navigation tree + feature impact.

Extracts the topic hierarchy directly from the DOM navigation tree
(li[role="treeitem"]) instead of keyword-based matching. The Salesforce
Help portal already organizes articles by topic in its sidebar ToC.

Also parses the Feature Impact page which contains ALL features with
availability information in a single page load.
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
            root_items = tree_root.find_all("li", attrs={"role": "treeitem"}, recursive=False)

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
        """Extract a concise summary from a release-note article page.

        Looks for a "Why" section first, then falls back to the first
        sufficiently informative paragraph in the main content region.

        Args:
            soup: BeautifulSoup DOM for a single article page, expected to
                contain headings/paragraphs from the article body.

        Returns:
            A summary string for the article. This method always returns a
            string (never ``None``); if no suitable content is found, it
            returns the fallback message:
            "Resumo não disponível para este artigo."
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
        """Recursively build a TopicNode from an ``<li role="treeitem">`` element.

        - Nodes with data-is-link="true" are article leaves
        - Nodes without are container nodes (categories/subcategories)
        - Nodes with both link and nested children are treated as containers

        Returns:
            TopicNode | None: Returns a TopicNode for valid tree items. Returns
            None when required metadata cannot be extracted (for example, when
            node_id or label_text is missing/empty).
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
        """Remove extra whitespace and very short text."""
        cleaned: str = re.sub(r"\s+", " ", raw).strip()
        if len(cleaned) < 3:
            return ""
        return cleaned


# ---------------------------------------------------------------------------
# FeatureImpactParser — parses the single-page feature impact table
# ---------------------------------------------------------------------------

SECTION_HEADERS_BY_LOCALE: dict[str, frozenset[str]] = {
    "pt-BR": frozenset(
        {
            "Salesforce geral",
            "Agentforce",
            "Análise de dados",
            "Automação",
            "Commerce",
            "Personalização",
            "Data 360",
            "Desenvolvimento",
            "Experience Cloud",
            "Field Service",
            "Hyperforce",
            "Setores",
            "Marketing",
            "MuleSoft",
            "Aplicativo móvel",
            "OmniStudio",
            "Partner Cloud",
            "Gerenciamento de receita",
            "Vendas",
            "Integrações do Salesforce para Slack",
            "Segurança, identidade e privacidade",
            "Serviço",
            "Outros produtos e serviços do Salesforce",
            "Documentação legal",
        }
    ),
}

DEFAULT_LOCALE = "pt-BR"
SECTION_HEADERS: frozenset[str] = SECTION_HEADERS_BY_LOCALE[DEFAULT_LOCALE]

AVAILABILITY_KEYWORDS: frozenset[str] = frozenset({"Yes"})


class FeatureImpactEntry:
    __slots__ = ("name", "available_users", "available_admins", "requires_config", "contact_sf")

    def __init__(
        self,
        name: str,
        available_users: bool = False,
        available_admins: bool = False,
        requires_config: bool = False,
        contact_sf: bool = False,
    ) -> None:
        self.name = name
        self.available_users = available_users
        self.available_admins = available_admins
        self.requires_config = requires_config
        self.contact_sf = contact_sf


class FeatureImpactCategory:
    __slots__ = ("name", "description", "entries", "subcategories")

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self.entries: list[FeatureImpactEntry] = []
        self.subcategories: dict[str, list[FeatureImpactEntry]] = {}


class FeatureImpactParser:
    """Parses the Feature Impact page text into structured categories."""

    def parse_text(self, text: str) -> list[FeatureImpactCategory]:
        lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
        categories: list[FeatureImpactCategory] = []
        current_cat: FeatureImpactCategory | None = None
        current_sub: str = ""
        i = 0

        while i < len(lines):
            line = lines[i]

            if self._is_section_header(line):
                existing = next((c for c in categories if c.name == line), None)
                if existing:
                    total_existing = len(existing.entries) + sum(
                        len(e) for e in existing.subcategories.values()
                    )
                    if total_existing > 5:
                        current_cat = None
                        i += 1
                        continue
                    categories.remove(existing)
                current_cat = FeatureImpactCategory(name=line)
                categories.append(current_cat)
                current_sub = ""
                i += 1
                continue

            if self._is_category_description(line, current_cat):
                if current_cat:
                    current_cat.description = line
                i += 1
                continue

            if self._is_table_header(line):
                i += 1
                continue

            if self._is_subcategory_header(line, current_cat):
                current_sub = line
                if current_cat and current_sub not in current_cat.subcategories:
                    current_cat.subcategories[current_sub] = []
                i += 1
                continue

            entry = self._parse_feature_line(line)
            if entry and current_cat:
                if current_sub and current_sub in current_cat.subcategories:
                    current_cat.subcategories[current_sub].append(entry)
                else:
                    current_cat.entries.append(entry)

            i += 1

        return [c for c in categories if c.entries or c.subcategories]

    def _is_section_header(self, line: str) -> bool:
        return line in SECTION_HEADERS

    def _is_category_description(self, line: str, cat: FeatureImpactCategory | None) -> bool:
        if not cat:
            return False
        if cat.description:
            return False
        if self._is_table_header(line):
            return False
        if line in SECTION_HEADERS:
            return False
        return len(line) > 20

    def _is_table_header(self, line: str) -> bool:
        return "RECURSO" in line and "ATIVADO" in line

    def _is_subcategory_header(self, line: str, cat: FeatureImpactCategory | None) -> bool:
        if not cat:
            return False
        if self._is_table_header(line):
            return False
        if line in SECTION_HEADERS:
            return False
        if self._parse_feature_line(line) is not None:
            return False
        if len(line) > 5 and len(line) < 80:
            if cat.entries or cat.subcategories:
                return True
        return False

    def _parse_feature_line(self, line: str) -> FeatureImpactEntry | None:
        if not line or len(line) < 5:
            return None
        if self._is_table_header(line):
            return None
        if line in SECTION_HEADERS:
            return None

        parts = [p.strip() for p in line.split("\t")]
        if len(parts) < 2:
            if "Yes" not in line and len(line) > 10:
                return FeatureImpactEntry(name=line)
            return None

        name = parts[0]
        if not name or len(name) < 3:
            return None

        flags = parts[1:] if len(parts) > 1 else []
        avail_users = any("Yes" in f for f in flags[:1]) if len(flags) >= 1 else False
        avail_admins = any("Yes" in f for f in flags[1:2]) if len(flags) >= 2 else False
        requires_config = any("Yes" in f for f in flags[2:3]) if len(flags) >= 3 else False
        contact_sf = any("Yes" in f for f in flags[3:4]) if len(flags) >= 4 else False

        return FeatureImpactEntry(
            name=name,
            available_users=avail_users,
            available_admins=avail_admins,
            requires_config=requires_config,
            contact_sf=contact_sf,
        )
