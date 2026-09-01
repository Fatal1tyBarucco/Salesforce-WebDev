"""Test data factories for Salesforce release notes pipeline.

Provides factory functions to generate realistic test data including:
- HTML ToC trees (mimicking Salesforce Help portal structure)
- Feature impact pages with availability flags
- ReleaseInfo objects with realistic metadata
- TopicNode hierarchies

Usage:
    from tests.factories import make_release, make_toc_html, make_feature_impact_text

    release = make_release(name="Summer '26", release_id=262, slug="summer_26")
    html = make_toc_html(categories=["Apex", "Flow"])
    text = make_feature_impact_text(features=10)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.config import KNOWN_RELEASES, ReleaseInfo, TopicNode

_RELEASE_SEQUENCE = 0


def _next_release_id() -> int:
    """Generate a unique release_id for test releases."""
    global _RELEASE_SEQUENCE
    _RELEASE_SEQUENCE += 1
    return 900 + _RELEASE_SEQUENCE


def make_release(
    name: str | None = None,
    release_id: int | None = None,
    slug: str | None = None,
) -> ReleaseInfo:
    """Create a ReleaseInfo with defaults from a known release.

    Args:
        name: Release display name (e.g., "Summer '26").
        release_id: Numeric ID used in Salesforce URLs.
        slug: URL-safe identifier (e.g., "summer_26").

    Returns:
        A configured ReleaseInfo instance.
    """
    if name is None and release_id is None and slug is None:
        known = KNOWN_RELEASES[0]
        return ReleaseInfo(
            name=known.name,
            release_id=known.release_id,
            slug=known.slug,
        )

    if release_id is None:
        release_id = _next_release_id()
    if name is None:
        name = f"Custom Release {release_id}"
    if slug is None:
        slug = name.lower().replace(" ", "_").replace("'", "")

    return ReleaseInfo(name=name, release_id=release_id, slug=slug)


def make_topic_node(
    slug: str = "test_topic",
    display_name: str = "Test Topic",
    level: int = 2,
    url: str = "/test/topic",
    children: list[TopicNode] | None = None,
    articles: list[dict[str, str]] | None = None,
) -> TopicNode:
    """Create a TopicNode for testing.

    Args:
        slug: Node ID without prefix (e.g., "rn_apex").
        display_name: Human-readable label.
        level: Hierarchy depth (1=root, 2+=content).
        url: Full URL to the node.
        children: Nested TopicNode instances.
        articles: List of article dicts with "title" and "url" keys.

    Returns:
        A configured TopicNode.
    """
    return TopicNode(
        slug=slug,
        display_name=display_name,
        level=level,
        url=url,
        children=children or [],
        articles=articles or [],
    )


def make_topic_tree(
    categories: list[str] | None = None,
    articles_per_category: int = 3,
) -> list[TopicNode]:
    """Create a hierarchical topic tree for testing.

    Args:
        categories: List of category names. Defaults to common SF categories.
        articles_per_category: Number of articles to generate per category.

    Returns:
        List of top-level TopicNode instances with nested children.
    """
    if categories is None:
        categories = ["Apex", "Flow", "Lightning Web Components", "Einstein"]

    tree: list[TopicNode] = []
    for idx, cat_name in enumerate(categories):
        articles = [
            {
                "title": f"{cat_name} Article {j + 1}",
                "url": f"/test/{cat_name.lower().replace(' ', '_')}/article{j + 1}",
            }
            for j in range(articles_per_category)
        ]
        child = make_topic_node(
            slug=f"rn_{cat_name.lower().replace(' ', '_')}",
            display_name=cat_name,
            level=3,
            url=f"/test/{cat_name.lower().replace(' ', '_')}",
            articles=articles,
        )
        parent = make_topic_node(
            slug=f"rn_{cat_name.lower().replace(' ', '_')}_parent",
            display_name=cat_name,
            level=2,
            url="",
            children=[child],
        )
        tree.append(parent)

    return tree


def make_toc_html(
    categories: list[str] | None = None,
    articles_per_category: int = 2,
) -> str:
    """Generate HTML mimicking Salesforce Help ToC structure.

    Args:
        categories: List of category names.
        articles_per_category: Articles per category.

    Returns:
        HTML string with realistic ToC structure.
    """
    if categories is None:
        categories = ["Salesforce Flow", "Desenvolvimento", "Vendas"]

    items_html: list[str] = []
    for cat in categories:
        cat_slug = cat.lower().replace(" ", "_")
        article_items: list[str] = []
        for i in range(1, articles_per_category + 1):
            article_items.append(f"""        <li role="treeitem" aria-level="3">
          <div class="slds-tree__item" data-is-link="true" data-node-id="rn_{cat_slug}_art{i}">
            <a href="/s/articleView?id=release-notes.rn_{cat_slug}_art{i}.htm">{cat} Article {i}</a>
          </div>
        </li>""")
        items_html.append(f"""      <li role="treeitem" aria-level="2">
        <div class="slds-tree__item" data-node-id="rn_{cat_slug}">
          <span class="tree-item-label">{cat}</span>
        </div>
        <ul>
{chr(10).join(article_items)}
        </ul>
      </li>""")

    return f"""<html>
<body>
<nav class="toc-container">
  <ul class="tree">
    <li role="treeitem" aria-level="1">
      <ul>
{chr(10).join(items_html)}
      </ul>
    </li>
  </ul>
</nav>
</body>
</html>"""


def make_feature_impact_text(
    categories: list[str] | None = None,
    features_per_category: int = 3,
) -> str:
    """Generate text mimicking Salesforce Feature Impact page.

    Args:
        categories: List of category names.
        features_per_category: Features per category.

    Returns:
        Tab-separated text with availability flags.
    """
    if categories is None:
        categories = ["Plataforma", "Desenvolvimento", "Vendas"]

    sections: list[str] = ["Winter '26 Feature Impact\n=========================\n"]

    total_features = 0
    for cat in categories:
        sections.append(f"\n{cat}\n")
        for i in range(1, features_per_category + 1):
            available = "Yes" if i % 2 == 0 else "Yes"
            admins = "Yes" if i % 3 != 0 else "No"
            config = "Yes" if i % 4 == 0 else "No"
            contact = "No"
            feature_name = f"{cat} Feature {i}"
            sections.append(f"{feature_name}\t{available}\t{admins}\t{config}\t{contact}")
            total_features += 1

    sections.append(f"\nTotal de Recursos: {total_features}\n")
    return "\n".join(sections)


def make_feature_impact_html(
    categories: list[str] | None = None,
    features_per_category: int = 2,
) -> str:
    """Generate HTML mimicking Salesforce Feature Impact page.

    Args:
        categories: List of category names.
        features_per_category: Features per category.

    Returns:
        HTML string with feature tables.
    """
    if categories is None:
        categories = ["Plataforma", "Desenvolvimento"]

    sections: list[str] = ["<html><body><div class='feature-impact-container'>"]

    for cat_idx, cat in enumerate(categories):
        cat_id = f"cat_{cat_idx}"
        sections.append(f"""<section class="feature-category" data-category="{cat}" id="{cat_id}">
  <h2>{cat}</h2>""")
        for i in range(1, features_per_category + 1):
            sections.append(
                f"""  <div class="feature-item" data-feature-id="W26-{cat_idx:02d}{i:02d}">
    <span class="feature-name">{cat} Feature {i}</span>
    <p class="feature-description">Description for {cat} feature {i}.</p>
    <span class="feature-impact-level">Medium</span>
  </div>"""
            )
        sections.append("</section>")

    sections.append("</div></body></html>")
    return "\n".join(sections)


def make_release_metadata(
    release: ReleaseInfo | None = None,
    total_features: int = 50,
    categories: list[str] | None = None,
) -> dict[str, Any]:
    """Create a metadata dict for a release.

    Args:
        release: ReleaseInfo instance. Auto-generated if None.
        total_features: Total number of features.
        categories: List of category names.

    Returns:
        Dict with release metadata matching the .meta.json format.
    """
    if release is None:
        release = make_release()
    if categories is None:
        categories = ["Apex", "Flow", "LWC", "Einstein"]

    return {
        "name": release.name,
        "release_id": release.release_id,
        "slug": release.slug,
        "total_features": total_features,
        "categories": [
            {"name": cat, "count": total_features // len(categories)} for cat in categories
        ],
        "generated_at": datetime.now().isoformat(),
        "source": "test_factory",
    }


def make_mock_html_response(
    url: str = "https://help.salesforce.com/test",
    status_code: int = 200,
    body_size: int = 5000,
) -> dict[str, Any]:
    """Create a mock HTTP response for testing scrapers.

    Args:
        url: The URL of the response.
        status_code: HTTP status code.
        body_size: Approximate size of the body in bytes.

    Returns:
        Dict with response metadata.
    """
    return {
        "url": url,
        "status": status_code,
        "headers": {
            "content-type": "text/html; charset=utf-8",
            "x-sf-source": "test_factory",
        },
        "body": "<html><body>" + ("x" * body_size) + "</body></html>",
    }
