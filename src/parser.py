"""Parser for Salesforce Help release notes — index and article pages.

The Salesforce Help portal organizes release notes as:
  1. An index page listing all feature articles as links
  2. Individual article pages for each feature/change

This parser handles both:
  - extract_article_links(): discovers and groups links by topic
  - build_topic_content_from_links(): creates content summaries from link titles
  - parse(): legacy heading-based segmentation (fallback)
"""

import logging
import re
from typing import Dict
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .config import MONITORED_TOPICS, TopicContentMap

logger: logging.Logger = logging.getLogger(__name__)

HEADING_TAGS: tuple[str, ...] = ("h1", "h2", "h3", "h4")
CONTENT_TAGS: tuple[str, ...] = ("p", "ul", "ol", "li", "table", "pre", "blockquote")

# URL path patterns that indicate topic categories
TOPIC_URL_PATTERNS: dict[str, list[str]] = {
    "apex": ["rn_apex", "rn_code"],
    "lwc": ["rn_lwc", "rn_lightning_web", "rn_rd_lwc", "rn_rd_embed_lwc"],
    "flow": ["rn_automate_flow", "rn_automate_process", "rn_flow"],
    "security": ["rn_security", "rn_identity", "rn_shield", "rn_encryption", "rn_permission"],
    "integrations": [
        "rn_integration",
        "rn_api",
        "rn_rest",
        "rn_soap",
        "rn_bulk",
        "rn_platform_event",
        "rn_connected_app",
        "rn_mulesoft",
    ],
}

SOURCE_BASE = "https://help.salesforce.com"


class ReleaseNotesParser:
    """Parses Salesforce Help release notes index and article pages."""

    def extract_article_links(
        self,
        soup: BeautifulSoup,
        release_name: str,
    ) -> dict[str, list[Dict[str, str]]]:
        """
        Extract article links from the index page and group by topic.

        Returns dict mapping topic slug -> list of {url, title} dicts.
        """
        logger.info("[PARSER] Extracting article links | release=%s", release_name)

        links = soup.find_all("a", href=True)
        topic_links: dict[str, list[dict[str, str]]] = {
            topic.slug: [] for topic in MONITORED_TOPICS
        }

        for link in links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if not title or len(title) < 5:
                continue

            if "release-notes" not in href.lower():
                continue

            full_url = urljoin(SOURCE_BASE, href)

            matched_slug = self._match_link_to_topic(href, title)
            if matched_slug:
                topic_links[matched_slug].append({"url": full_url, "title": title})

        for topic in MONITORED_TOPICS:
            count = len(topic_links[topic.slug])
            logger.info(
                "[PARSER] Topic '%s': %d article links | release=%s",
                topic.slug,
                count,
                release_name,
            )

        return topic_links

    def build_topic_content_from_links(
        self,
        topic_links: dict[str, list[dict[str, str]]],
        soup: BeautifulSoup,
        release_name: str,
    ) -> TopicContentMap:
        """
        Build topic content map from index page link titles.

        Creates a structured summary listing each feature article
        with its title and link URL.
        """
        logger.info("[PARSER] Building content from index links | release=%s", release_name)

        result: TopicContentMap = {topic.slug: [] for topic in MONITORED_TOPICS}

        for topic in MONITORED_TOPICS:
            articles = topic_links.get(topic.slug, [])
            if not articles:
                continue

            result[topic.slug].append(f"## {topic.display_name} — {release_name}")
            result[topic.slug].append("")
            result[topic.slug].append("### Feature Articles")
            result[topic.slug].append("")

            for article in articles:
                result[topic.slug].append(f"- **{article['title']}**")
                result[topic.slug].append(f"  [{article['title']}]({article['url']})")
                result[topic.slug].append("")

        for topic in MONITORED_TOPICS:
            count = len(result[topic.slug])
            logger.info(
                "[PARSER] Topic '%s': %d lines | release=%s",
                topic.slug,
                count,
                release_name,
            )

        return result

    def parse(
        self,
        soup: BeautifulSoup,
        release_name: str,
    ) -> TopicContentMap:
        """Legacy heading-based segmentation (fallback)."""
        logger.info("[PARSER] Iniciando segmentação | release=%s", release_name)

        sections: list[dict] = self._extract_sections(soup)
        logger.info(
            "[PARSER] %d seções identificadas no DOM | release=%s",
            len(sections),
            release_name,
        )

        result: TopicContentMap = {topic.slug: [] for topic in MONITORED_TOPICS}

        for section in sections:
            matched_slugs: list[str] = self._match_section_to_topics(section)
            for slug in matched_slugs:
                result[slug].extend(section["lines"])

        return result

    def _extract_sections(self, soup: BeautifulSoup) -> list[dict[str, any]]:
        """Percorre o DOM e agrupa conteúdo em seções delimitadas por headings."""
        sections: list[dict] = []
        current_section: dict | None = None

        for element in soup.find_all(True):
            tag_name: str = element.name if hasattr(element, "name") else ""

            if tag_name in HEADING_TAGS:
                if current_section is not None and current_section["lines"]:
                    sections.append(current_section)

                heading_text: str = self._clean_text(element.get_text())
                if not heading_text:
                    current_section = None
                    continue

                current_section = {
                    "heading": heading_text,
                    "level": int(tag_name[1]),
                    "lines": [f"### {heading_text}"],
                }

            elif tag_name in CONTENT_TAGS and current_section is not None:
                line: str = self._clean_text(element.get_text())
                if line:
                    current_section["lines"].append(line)

        if current_section is not None and current_section["lines"]:
            sections.append(current_section)

        return sections

    def _match_section_to_topics(self, section: dict) -> list[str]:
        """Verifica quais tópicos correspondem a uma seção."""
        matched: list[str] = []
        searchable_text: str = " ".join([section["heading"]] + section["lines"][:10]).lower()

        for topic in MONITORED_TOPICS:
            if self._matches_any_keyword(searchable_text, topic.keywords):
                matched.append(topic.slug)

        return matched

    def _match_link_to_topic(self, href: str, title: str) -> str | None:
        """Match an article link to a topic using URL patterns and title keywords."""
        href_lower = href.lower()

        for slug, patterns in TOPIC_URL_PATTERNS.items():
            for pattern in patterns:
                if pattern in href_lower:
                    return slug

        title_lower = title.lower()
        for topic in MONITORED_TOPICS:
            for keyword in topic.keywords:
                pattern = rf"\b{re.escape(keyword)}\b"
                if re.search(pattern, title_lower, re.IGNORECASE):
                    return topic.slug

        return None

    def _matches_any_keyword(self, text: str, keywords: list[str]) -> bool:
        """Keyword matching case-insensitive com word boundary."""
        for keyword in keywords:
            pattern: str = rf"\b{re.escape(keyword)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def _clean_text(raw: str) -> str:
        """Remove espaços extras e linhas muito curtas."""
        cleaned: str = re.sub(r"\s+", " ", raw).strip()
        if len(cleaned) < 3:
            return ""
        return cleaned
