"""Snapshot tests for scraper and parser output consistency.

These tests capture the expected structure of scraped/parsed data
and detect changes in the Salesforce Help portal DOM structure.

Run with: pytest tests/test_snapshot.py
Update snapshots: pytest tests/test_snapshot.py --snapshot-update
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from src.config import TopicNode
from src.parser import (
    FeatureImpactCategory,
    FeatureImpactEntry,
    FeatureImpactParser,
)

SAMPLE_HTML_TOC = """
<html>
<body>
<nav class="toc-container">
    <ul class="tree">
        <li role="treeitem" aria-level="1">
            <ul>
                <li role="treeitem" aria-level="2">
                    <span>Salesforce Flow</span>
                    <ul>
                        <li role="treeitem" aria-level="3">
                            <a href="/sf.flow.overview">Flow Overview</a>
                        </li>
                    </ul>
                </li>
                <li role="treeitem" aria-level="2">
                    <span>Desenvolvimento</span>
                    <ul>
                        <li role="treeitem" aria-level="3">
                            <a href="/sf.apex.overview">Apex Overview</a>
                        </li>
                    </ul>
                </li>
            </ul>
        </li>
    </ul>
</nav>
</body>
</html>
"""

SAMPLE_HTML_FEATURE_IMPACT = """
<html>
<body>
<div class="feature-impact-container">
    <h2 class="release-title">Winter '26 Release Notes</h2>

    <section class="feature-category" data-category="Platform">
        <h3>Platform Features</h3>
        <div class="feature-item" data-feature-id="W26-001">
            <span class="feature-name">Enhanced Flow Builder</span>
            <p class="feature-description">New drag-and-drop capabilities for Flow Builder.</p>
            <span class="feature-impact-level">High</span>
        </div>
    </section>

    <section class="feature-category" data-category="Apex">
        <h3>Apex Improvements</h3>
        <div class="feature-item" data-feature-id="W26-002">
            <span class="feature-name">Apex REST Annotations</span>
            <p class="feature-description">New annotations for simplified REST endpoints.</p>
            <span class="feature-impact-level">Medium</span>
        </div>
    </section>
</div>
</body>
</html>
"""

SAMPLE_FEATURE_IMPACT_TEXT = """
Winter '26 Feature Impact
=========================

Plataforma
Enhanced Flow Builder\tYes\tYes\tNo\tNo
New API Versioning\tYes\tYes\tYes\tNo

Desenvolvimento
Apex REST Annotations\tYes\tYes\tNo\tNo
SOQL Improvements\tYes\tYes\tYes\tNo

Total de Recursos: 4
"""

SAMPLE_FEATURE_IMPACT_TEXT_SINGLE = """
Winter '26 Feature Impact
=========================

Automação
Enhanced Flow Builder\tYes\tYes\tNo\tNo

Desenvolvimento
Apex REST Annotations\tYes\tYes\tNo\tNo

Total de Recursos: 2
"""


class TestParserSnapshot:
    """Snapshot tests for parser output structure."""

    def test_extract_topic_tree_structure(self, snapshot):
        """Test that topic tree extraction returns expected structure."""
        soup = BeautifulSoup(SAMPLE_HTML_TOC, "html.parser")
        from src.parser import ReleaseNotesParser

        parser = ReleaseNotesParser()
        topics = parser.extract_topic_tree(soup)

        topic_data = [
            {
                "name": t.slug,
                "display_name": t.display_name,
                "level": t.level,
                "has_url": bool(t.url),
                "article_count": len(t.articles),
                "children_count": len(t.children),
            }
            for t in topics
        ]

        assert topic_data == snapshot

    def test_feature_impact_parser_categories(self, snapshot):
        """Test that feature impact parser returns expected category structure."""
        parser = FeatureImpactParser()
        categories = parser.parse_text(SAMPLE_FEATURE_IMPACT_TEXT)

        category_data = self._serialize_categories(categories)
        assert category_data == snapshot

    def test_feature_impact_parser_single_category(self, snapshot):
        """Test feature impact parser with single category text."""
        parser = FeatureImpactParser()
        categories = parser.parse_text(SAMPLE_FEATURE_IMPACT_TEXT_SINGLE)

        category_data = self._serialize_categories(categories)
        assert category_data == snapshot

    def test_feature_impact_parser_stats(self, snapshot):
        """Test that parser stats are consistent across parses."""
        parser = FeatureImpactParser()

        parser.parse_text(SAMPLE_FEATURE_IMPACT_TEXT)
        stats1 = parser.parse_stats()

        parser.parse_text(SAMPLE_FEATURE_IMPACT_TEXT_SINGLE)
        stats2 = parser.parse_stats()

        assert {"stats1": stats1, "stats2": stats2} == snapshot

    def test_feature_impact_parser_quality_metrics(self, snapshot):
        """Test classification quality metrics are consistent."""
        parser = FeatureImpactParser()
        categories = parser.parse_text(SAMPLE_FEATURE_IMPACT_TEXT)

        quality = parser.classification_quality(categories)
        assert quality == snapshot

    @staticmethod
    def _serialize_categories(categories: list[FeatureImpactCategory]) -> dict[str, object]:
        """Serialize categories for snapshot comparison."""
        return {
            "count": len(categories),
            "categories": [
                {
                    "name": c.name,
                    "description": c.description or "",
                    "entries_count": len(c.entries),
                    "subcategories_count": len(c.subcategories),
                    "entries": [
                        {
                            "name": e.name,
                            "available_users": e.available_users,
                            "available_admins": e.available_admins,
                            "requires_config": e.requires_config,
                            "contact_sf": e.contact_sf,
                            "confidence": round(e.confidence, 2),
                        }
                        for e in c.entries[:3]
                    ],
                }
                for c in categories
            ],
        }


class TestFeatureImpactEntry:
    """Tests for FeatureImpactEntry data structure snapshots."""

    def test_entry_with_all_flags(self, snapshot):
        """Test entry serialization with all availability flags set."""
        entry = FeatureImpactEntry(
            name="Test Feature",
            available_users=True,
            available_admins=True,
            requires_config=True,
            contact_sf=False,
            confidence=1.0,
            docs_url="https://example.com/docs",
        )
        data = {
            "name": entry.name,
            "available_users": entry.available_users,
            "available_admins": entry.available_admins,
            "requires_config": entry.requires_config,
            "contact_sf": entry.contact_sf,
            "confidence": entry.confidence,
            "docs_url": entry.docs_url,
        }
        assert data == snapshot

    def test_entry_minimal(self, snapshot):
        """Test minimal entry with default values."""
        entry = FeatureImpactEntry(name="Minimal Feature", confidence=0.5)
        data = {
            "name": entry.name,
            "confidence": entry.confidence,
            "has_url": bool(entry.docs_url),
        }
        assert data == snapshot


class TestTopicNode:
    """Tests for TopicNode data structure snapshots."""

    def test_topic_node_serialization(self, snapshot):
        """Test TopicNode serialization for snapshot comparison."""
        node = TopicNode(
            slug="test_topic",
            display_name="Test Topic",
            level=2,
            url="/test/topic",
            children=[],
            articles=[{"title": "Article 1", "url": "/test/article1"}],
        )
        data = {
            "slug": node.slug,
            "display_name": node.display_name,
            "level": node.level,
            "url": node.url,
            "is_leaf": node.is_leaf(),
            "article_count": len(node.articles),
            "children_count": len(node.children),
        }
        assert data == snapshot

    def test_topic_node_with_children(self, snapshot):
        """Test TopicNode with nested children."""
        child = TopicNode(
            slug="child_topic",
            display_name="Child Topic",
            level=3,
            url="/test/child",
        )
        parent = TopicNode(
            slug="parent_topic",
            display_name="Parent Topic",
            level=2,
            url="",
            children=[child],
        )
        data = {
            "parent": {
                "slug": parent.slug,
                "is_leaf": parent.is_leaf(),
                "children_count": len(parent.children),
            },
            "child": {
                "slug": child.slug,
                "is_leaf": child.is_leaf(),
            },
            "all_articles_count": len(parent.all_articles()),
        }
        assert data == snapshot
