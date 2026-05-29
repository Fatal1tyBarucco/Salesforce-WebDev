from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from automation.shared.models import ParsedSection


class SemanticParser:
    """
    Semantic HTML parser for Salesforce Release Notes.
    """

    HEADING_TAGS: tuple[str, ...] = ("h1", "h2", "h3", "h4")

    def parse_sections(self, html_content: str) -> list[ParsedSection]:
        soup = BeautifulSoup(html_content, "html.parser")

        parsed_sections: list[ParsedSection] = []

        current_heading: str | None = None
        current_content: list[str] = []

        for element in soup.find_all(self.HEADING_TAGS + ("p", "li")):
            if not isinstance(element, Tag):
                continue

            if element.name in self.HEADING_TAGS:
                if current_heading and current_content:
                    parsed_sections.append(
                        ParsedSection(
                            title=current_heading,
                            content="\n".join(current_content),
                        )
                    )

                current_heading = element.get_text(strip=True)
                current_content = []
                continue

            text_content = element.get_text(strip=True)

            if text_content:
                current_content.append(text_content)

        if current_heading and current_content:
            parsed_sections.append(
                ParsedSection(
                    title=current_heading,
                    content="\n".join(current_content),
                )
            )

        return parsed_sections
