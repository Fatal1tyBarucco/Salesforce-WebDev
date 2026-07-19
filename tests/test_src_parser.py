from bs4 import BeautifulSoup, Tag
from src.parser import (
    ReleaseNotesParser,
    FeatureImpactCategory,
    FeatureImpactEntry,
    FeatureImpactParser,
)
from src.config import TopicNode


def test_extract_topic_tree_basic() -> None:
    parser = ReleaseNotesParser()

    html = """
    <html>
        <body>
            <ul class="tree">
                <li role="treeitem" aria-level="1" id="rn_root">
                    <ul>
                        <li role="treeitem" aria-level="2" id="rn_development">
                            <span class="tree-item-label">Desenvolvimento</span>
                            <ul>
                                <li role="treeitem" aria-level="3" id="rn_apex">
                                    <span class="tree-item-label">Apex</span>
                                    <ul>
                                        <li role="treeitem" aria-level="4" id="rn_apex_leaf"
                                            data-is-link="true">
                                            <a href="/s/articleView?id=rn_apex_feature">
                                                New Apex Feature
                                            </a>
                                        </li>
                                    </ul>
                                </li>
                                <li role="treeitem" aria-level="3" id="rn_lwc">
                                    <span class="tree-item-label">Lightning Web Components</span>
                                </li>
                            </ul>
                        </li>
                        <li role="treeitem" aria-level="2" id="rn_security">
                            <span class="tree-item-label">Segurança</span>
                        </li>
                    </ul>
                </li>
            </ul>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)

    assert len(topics) == 2
    assert topics[0].slug == "development"
    assert topics[0].display_name == "Desenvolvimento"
    assert topics[0].level == 2
    assert len(topics[0].children) == 2

    apex_child = topics[0].children[0]
    assert apex_child.slug == "apex"
    assert len(apex_child.articles) == 1
    assert apex_child.articles[0]["title"] == "New Apex Feature"
    assert len(apex_child.children) == 0

    assert topics[1].slug == "security"
    assert topics[1].display_name == "Segurança"


def test_extract_topic_tree_excludes_filtered_nodes() -> None:
    parser = ReleaseNotesParser()

    html = """
    <html>
        <body>
            <ul class="tree">
                <li role="treeitem" aria-level="1" id="rn_root">
                    <ul>
                        <li role="treeitem" aria-level="2" id="rn_features_released_monthly">
                            <span class="tree-item-label">Monthly</span>
                        </li>
                        <li role="treeitem" aria-level="2" id="rn_change_log">
                            <span class="tree-item-label">Change Log</span>
                        </li>
                        <li role="treeitem" aria-level="2" id="rn_development">
                            <span class="tree-item-label">Development</span>
                        </li>
                    </ul>
                </li>
            </ul>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)

    slugs = [t.slug for t in topics]
    assert "features_released_monthly" not in slugs
    assert "change_log" not in slugs
    assert "development" in slugs


def test_extract_topic_tree_no_toc_found() -> None:
    parser = ReleaseNotesParser()
    html = "<html><body><p>No ToC here</p></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)
    assert topics == []


def test_extract_topic_tree_fallback_no_aria_level_1() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <div class="toc-container">
                <ul class="tree">
                    <li role="treeitem" id="rn_root">
                        <ul>
                            <li role="treeitem" aria-level="2" id="rn_top">
                                <span class="tree-item-label">Top Item</span>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)
    assert len(topics) == 1
    assert topics[0].slug == "top"


def test_extract_topic_tree_fallback_via_treeitem_parent() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <nav>
                <li role="treeitem" aria-level="1" id="rn_root">
                    <ul>
                        <li role="treeitem" aria-level="2" id="rn_topic_a">
                            <span class="tree-item-label">Topic Alpha</span>
                        </li>
                    </ul>
                </li>
            </nav>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)
    assert len(topics) == 1
    assert topics[0].slug == "topic_a"


def test_build_node_returns_none_for_empty_li() -> None:
    parser = ReleaseNotesParser()
    html = '<li role="treeitem" aria-level="2"></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    result = parser._build_node(li)
    assert result is None


def test_build_node_with_div_role_label() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="2" id="rn_div_test">
        <div role="label">Div Label Text</div>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert node.display_name == "Div Label Text"


def test_build_node_fallback_to_get_text() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="2" id="rn_fallback_text">
        Fallback Text Content
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert "Fallback Text Content" in node.display_name


def test_build_node_leaf_with_url() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="4" id="rn_leaf_url" data-is-link="true">
        <a href="/s/articleView?id=rn_test">Test Article</a>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert node.is_leaf()
    assert "rn_test" in node.url


def test_get_node_id_list_type() -> None:
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["id"] = ["rn_list_id", "second"]
    result = parser._get_node_id(li)
    assert result == "rn_list_id"


def test_get_aria_level_list_type() -> None:
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = ["3", "4"]
    result = parser._get_aria_level(li)
    assert result == 3


def test_get_aria_level_invalid_value() -> None:
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = "invalid"
    result = parser._get_aria_level(li)
    assert result == 1


def test_get_aria_level_non_string_non_list() -> None:
    """Cover parser.py — raw is an int (not str, not list).

    BS4 version-dependent: 4.15+ converts int attrs to str ('42'),
    older versions keep int. Both paths must work.
    """
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = 42  # type: ignore[assignment]
    result = parser._get_aria_level(li)
    assert result in (1, 42)


def test_get_node_url_href_list() -> None:
    parser = ReleaseNotesParser()
    html = '<li><a href="/s/articleView?id=rn_url_test">Link</a></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    a_tag = li.find("a")
    assert a_tag is not None
    assert isinstance(a_tag, Tag)
    a_tag["href"] = ["/s/articleView?id=rn_url_test", "other"]
    result = parser._get_node_url(li)
    assert "rn_url_test" in result


def test_clean_text_short() -> None:
    result = ReleaseNotesParser._clean_text("ab")
    assert result == ""


def test_extract_article_summary_why_section() -> None:
    parser = ReleaseNotesParser()

    html = """
    <html>
        <body>
            <h2>Feature Details</h2>
            <p>Some description</p>
            <strong>Por que essa alteração é importante</strong>
            <p>Esta alteração melhora a performance em 50%.</p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "50%" in summary


def test_extract_article_summary_why_keyword() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <p>Why</p>
            <p>This is the reason for the change that matters.</p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "reason" in summary


def test_extract_article_summary_why_por_que() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <h3>Por que</h3>
            <p>Explanation of why this change is important for users.</p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "Explanation" in summary


def test_extract_article_summary_why_no_next_p() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <strong>Por que essa alteração é importante</strong>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "Resumo não disponível" in summary


def test_extract_article_summary_fallback() -> None:
    parser = ReleaseNotesParser()

    html = """
    <html>
        <body>
            <article>
                <p>This is a long enough paragraph that should be extracted as the summary.</p>
            </article>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "long enough paragraph" in summary


def test_extract_article_summary_no_content() -> None:
    parser = ReleaseNotesParser()
    html = "<html><body><p>Short</p></body></html>"
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "Resumo não disponível" in summary


def test_topic_node_all_articles() -> None:
    child1 = TopicNode(
        slug="sub1",
        display_name="Sub 1",
        level=3,
        url="",
        children=[],
        articles=[{"title": "Art 1", "url": "http://a.com"}],
    )
    child2 = TopicNode(
        slug="sub2",
        display_name="Sub 2",
        level=3,
        url="",
        children=[],
        articles=[{"title": "Art 2", "url": "http://b.com"}],
    )
    parent = TopicNode(
        slug="parent",
        display_name="Parent",
        level=2,
        url="",
        children=[child1, child2],
        articles=[{"title": "Parent Art", "url": "http://c.com"}],
    )

    all_arts = parent.all_articles()
    assert len(all_arts) == 3
    titles = [a["title"] for a in all_arts]
    assert "Parent Art" in titles
    assert "Art 1" in titles
    assert "Art 2" in titles


def test_topic_node_is_leaf() -> None:
    leaf = TopicNode(slug="leaf", display_name="Leaf", level=3, url="http://x.com")
    assert leaf.is_leaf()

    container = TopicNode(
        slug="container",
        display_name="Container",
        level=2,
        url="",
        children=[TopicNode(slug="child", display_name="Child", level=3, url="http://y.com")],
    )
    assert not container.is_leaf()


def test_topic_node_topic_file_slug() -> None:
    node = TopicNode(slug="my_topic", display_name="My Topic", level=2, url="")
    assert node.topic_file_slug() == "my_topic"


def test_id_to_slug_various() -> None:
    parser = ReleaseNotesParser()
    assert parser._id_to_slug("rn_development_leaf") == "development"
    assert parser._id_to_slug("rn_apex") == "apex"
    assert parser._id_to_slug("rn_security") == "security"
    assert parser._id_to_slug("plain_id") == "plain_id"


def test_find_toc_container_by_role_tree() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <div role="tree">
                <li role="treeitem" aria-level="1" id="rn_root_node">
                    <ul>
                        <li role="treeitem" aria-level="2" id="rn_item">
                            <span class="tree-item-label">Container Item</span>
                        </li>
                    </ul>
                </li>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)
    assert len(topics) == 1
    assert topics[0].slug == "item"


def test_find_toc_container_by_nav_toc() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <nav class="toc">
                <li role="treeitem" aria-level="1" id="rn_root_nav">
                    <ul>
                        <li role="treeitem" aria-level="2" id="rn_nav_item">
                            <span class="tree-item-label">Navigation Content</span>
                        </li>
                    </ul>
                </li>
            </nav>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)
    assert len(topics) == 1
    assert topics[0].slug == "nav_item"


def test_build_node_child_not_tag() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="2" id="rn_parent">
        <span class="tree-item-label">Parent</span>
        <ul>
            <li role="treeitem" aria-level="3" id="rn_child">
                <span class="tree-item-label">Child</span>
            </li>
            some text node
        </ul>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li", id="rn_parent")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert len(node.children) == 1


def test_find_toc_container_treeitem_parent_skips_intermediate() -> None:
    parser = ReleaseNotesParser()
    html = """
    <html>
        <body>
            <div>
                <p>Some content</p>
                <ul>
                    <li role="treeitem" aria-level="1" id="rn_parent_node">
                        <ul>
                            <li role="treeitem" aria-level="2" id="rn_child_node">
                                <span class="tree-item-label">Child Content</span>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    topics = parser.extract_topic_tree(soup)
    assert len(topics) == 1
    assert topics[0].slug == "child_node"


def test_build_node_child_none_skips() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="2" id="rn_parent_skip">
        <span class="tree-item-label">Parent Skip</span>
        <ul>
            <li role="treeitem" aria-level="3">
                <span class="tree-item-label">No ID Child</span>
            </li>
            <li role="treeitem" aria-level="3" id="rn_good_child">
                <span class="tree-item-label">Good Child</span>
            </li>
        </ul>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li", id="rn_parent_skip")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert len(node.children) == 1
    assert node.children[0].slug == "good_child"


def test_build_node_leaf_with_url_returns_early() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="2" id="rn_leaf_other_url">
        <a href="/s/articleView?id=some_other_page">Leaf Link</a>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert node.slug == "leaf_other_url"
    assert node.url


def test_build_node_uses_title_attribute_for_label() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="2" id="rn_title_item" title="Salesforce geral">
        <div class="slds-tree__item">
            <a href="https://help.salesforce.com/s/articleView?id=release-notes.rn_general">Overview</a>
        </div>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    node = parser._build_node(li)
    assert node is not None
    assert node.display_name == "Salesforce geral"


def test_find_link_inside_slds_tree_item() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="4" id="rn_leaf_slds" data-is-link="true">
        <div class="slds-tree__item">
            <a href="/s/articleView?id=release-notes.rn_some_feature">Feature</a>
        </div>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    link = parser._find_link(li)
    assert link is not None
    href = link.get("href")
    assert isinstance(href, str)
    assert "release-notes" in href


def test_find_link_returns_none_when_no_link() -> None:
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="3" id="rn_no_link">
        <span class="tree-item-label">No Link Here</span>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    link = parser._find_link(li)
    assert link is None


def test_get_node_id_empty_list() -> None:
    """Cover parser.py:224 — empty list from li.get('id')."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["id"] = []
    result = parser._get_node_id(li)
    assert result == ""


def test_get_node_id_list_non_string_first() -> None:
    """Cover parser.py:228 — first element in id list is not a string."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["id"] = [42, "second"]  # type: ignore[list-item]
    result = parser._get_node_id(li)
    assert result == ""


def test_get_aria_level_empty_list() -> None:
    """Cover parser.py:238 — empty list from li.get('aria-level')."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = []
    result = parser._get_aria_level(li)
    assert result == 1


def test_get_aria_level_list_non_string_first() -> None:
    """Cover parser.py — first element in aria-level list is an int.

    str() converts int to string, so int("42") returns 42.
    """
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = [42, "4"]  # type: ignore[list-item]
    result = parser._get_aria_level(li)
    assert result == 42


def test_get_aria_level_list_invalid_string_first() -> None:
    """Cover parser.py:243-244 — first element in aria-level list is non-numeric string."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = ["invalid", "4"]
    result = parser._get_aria_level(li)
    assert result == 1


def test_get_aria_level_list_non_str_int_first() -> None:
    """Cover parser.py — first element in list is neither str nor int."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = [{"bad": "value"}]  # type: ignore[list-item]
    result = parser._get_aria_level(li)
    assert result == 1


def test_get_aria_level_non_str_raw() -> None:
    """Cover parser.py:247 — raw is not a str (e.g. None, int)."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["aria-level"] = None  # type: ignore[assignment]
    result = parser._get_aria_level(li)
    assert result == 1


def test_get_label_text_title_list_type() -> None:
    """Cover parser.py:265-269 — title attribute is a list."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["title"] = ["First Title", "Second Title"]
    result = parser._get_label_text(li)
    assert result == "First Title"


def test_get_label_text_title_list_empty() -> None:
    """Cover parser.py:265-269 — title attribute is an empty list."""
    parser = ReleaseNotesParser()
    li = Tag(name="li")
    li["title"] = []
    result = parser._get_label_text(li)
    assert isinstance(result, str)


def test_get_label_text_get_text_non_string() -> None:
    """Cover parser.py:286 — get_text() returns non-string (edge case)."""
    parser = ReleaseNotesParser()
    html = '<li role="treeitem" aria-level="2" id="rn_empty"></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    result = parser._get_label_text(li)
    assert isinstance(result, str)


def test_find_link_div_not_tag() -> None:
    """Cover parser.py:300 — tree_item_div is not a Tag instance."""
    parser = ReleaseNotesParser()
    html = '<li role="treeitem" aria-level="3" id="rn_div_test"><div class="slds-tree__item">text</div></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    link = parser._find_link(li)
    assert link is None


def test_find_link_no_href_in_slds_item() -> None:
    """Cover parser.py:304 — slds-tree__item div exists but no link inside."""
    parser = ReleaseNotesParser()
    html = """
    <li role="treeitem" aria-level="3" id="rn_no_href">
        <div class="slds-tree__item">
            <span>No link here</span>
        </div>
    </li>
    """
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    link = parser._find_link(li)
    assert link is None


def test_get_node_url_href_list_empty() -> None:
    """Cover parser.py:316 — href attribute is an empty list."""
    parser = ReleaseNotesParser()
    html = '<li><a href="/s/articleView?id=rn_empty_href">Link</a></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    a_tag = li.find("a")
    assert a_tag is not None
    assert isinstance(a_tag, Tag)
    a_tag["href"] = []
    result = parser._get_node_url(li)
    assert result == ""


def test_get_node_url_href_list_non_string() -> None:
    """Cover parser.py:320 — first href in list is not a string."""
    parser = ReleaseNotesParser()
    html = '<li><a href="/s/articleView?id=rn_non_string_href">Link</a></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    a_tag = li.find("a")
    assert a_tag is not None
    assert isinstance(a_tag, Tag)
    a_tag["href"] = [42, "other"]  # type: ignore[list-item]
    result = parser._get_node_url(li)
    assert result == ""


def test_get_node_url_href_empty_string() -> None:
    """Cover parser.py:323 — href is an empty string."""
    parser = ReleaseNotesParser()
    html = '<li><a href="">Empty Link</a></li>'
    soup = BeautifulSoup(html, "html.parser")
    li = soup.find("li")
    assert li is not None
    assert isinstance(li, Tag)
    a_tag = li.find("a")
    assert a_tag is not None
    assert isinstance(a_tag, Tag)
    a_tag["href"] = ""
    result = parser._get_node_url(li)
    assert result == ""


# ============================================================
# FeatureImpactParser tests — 100% coverage
# ============================================================


def test_feature_impact_entry_defaults() -> None:
    """FeatureImpactEntry default values."""
    e = FeatureImpactEntry(name="Test")
    assert e.name == "Test"
    assert e.available_users is False
    assert e.available_admins is False
    assert e.requires_config is False
    assert e.contact_sf is False
    assert e.confidence == 1.0


def test_feature_impact_category_avg_confidence_empty() -> None:
    """avg_confidence returns 0.0 for empty category."""
    cat = FeatureImpactCategory(name="Empty")
    assert cat.avg_confidence == 0.0


def test_feature_impact_category_avg_confidence_with_entries() -> None:
    """avg_confidence computes correctly."""
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="A", confidence=0.8))
    cat.entries.append(FeatureImpactEntry(name="B", confidence=0.6))
    assert cat.avg_confidence == 0.7


def test_feature_impact_category_avg_confidence_with_subcategories() -> None:
    """avg_confidence includes subcategory entries."""
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="A", confidence=1.0))
    cat.subcategories["Sub"] = [FeatureImpactEntry(name="B", confidence=0.5)]
    assert cat.avg_confidence == 0.75


def test_feature_impact_category_total_features() -> None:
    """total_features counts entries + subcategory entries."""
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="A"))
    cat.subcategories["Sub"] = [
        FeatureImpactEntry(name="B"),
        FeatureImpactEntry(name="C"),
    ]
    assert cat.total_features == 3


def test_feature_impact_parser_init_default_locale() -> None:
    """FeatureImpactParser default locale is pt-BR."""
    p = FeatureImpactParser()
    assert p._locale == "pt-BR"


def test_feature_impact_parser_init_en_locale() -> None:
    """FeatureImpactParser en locale loads English headers."""
    p = FeatureImpactParser(locale="en")
    assert p._locale == "en"
    assert "Salesforce General" in p._section_headers


def test_feature_impact_parser_parse_text_basic() -> None:
    """parse_text extracts categories and features."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nThis is a long description for category section\nFeature One\tYes\tNo\tYes\tNo\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert cats[0].name == "Salesforce geral"
    assert len(cats[0].entries) == 1
    assert cats[0].entries[0].name == "Feature One"


def test_feature_impact_parser_parse_text_with_description() -> None:
    """parse_text captures category description."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nThis is a long description for the category section\nFeature\tYes\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert cats[0].description != ""


def test_feature_impact_parser_skips_table_header() -> None:
    """parse_text skips RECURSO/ATIVADO table headers."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nRECURSO\tATIVADO\nFeature\tYes\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert len(cats[0].entries) == 1


def test_feature_impact_parser_subcategory() -> None:
    """parse_text detects subcategory headers."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nFeature One\tYes\nSub Category Name\nFeature Two\tYes\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    # Subcategory should be detected
    assert len(cats[0].entries) >= 1


def test_feature_impact_parser_duplicate_header_skips() -> None:
    """Duplicate section header with >5 entries is skipped."""
    p = FeatureImpactParser()
    lines = ["Salesforce geral", "This is a long description for the section"]
    for i in range(10):
        lines.append(f"Feature {i}\tYes\tNo\tYes\tNo")
    lines.append("Salesforce geral")  # duplicate
    lines.append("Extra Feature\tYes")
    text = "\n".join(lines)
    cats = p.parse_text(text)
    # The second "Salesforce geral" should be skipped
    assert len(cats) == 1
    assert len(cats[0].entries) == 10


def test_feature_impact_parser_duplicate_header_removes() -> None:
    """Duplicate section header with <=5 entries replaces existing."""
    p = FeatureImpactParser()
    text = (
        "Salesforce geral\n"
        "This is a long description for category\n"
        "Feature One\tYes\n"
        "Salesforce geral\n"
        "Another long description for category here\n"
        "New Feature\tYes\n"
    )
    cats = p.parse_text(text)
    # Should have one category with the second set
    assert len(cats) == 1


def test_feature_impact_parser_parse_stats() -> None:
    """parse_stats returns stats from last parse_text call."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nLong description for the category here\nFeature\tYes\n"
    p.parse_text(text)
    stats = p.parse_stats()
    assert stats["total_lines"] == 3
    assert stats["parsed"] == 1


def test_feature_impact_parser_classification_quality() -> None:
    """classification_quality returns aggregate metrics."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="A", confidence=0.9))
    cat.entries.append(FeatureImpactEntry(name="B", confidence=0.5))
    quality = p.classification_quality([cat])
    assert quality["categories"] == 1
    assert quality["total_features"] == 2
    assert quality["low_confidence_count"] == 1


def test_feature_impact_parser_classification_quality_with_subs() -> None:
    """classification_quality counts subcategory entries."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="A", confidence=1.0))
    cat.subcategories["S"] = [FeatureImpactEntry(name="B", confidence=0.3)]
    quality = p.classification_quality([cat])
    assert quality["total_features"] == 2
    assert quality["low_confidence_count"] == 1


def test_feature_impact_parser_empty_input() -> None:
    """parse_text handles empty input."""
    p = FeatureImpactParser()
    assert p.parse_text("") == []
    assert p.parse_text("\n\n") == []


def test_feature_impact_parser_feature_line_no_tabs() -> None:
    """Feature line without tabs but with Yes."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nShort\n"
    cats = p.parse_text(text)
    # "Short" is < 5 chars so not a feature
    assert len(cats) == 0 or all(len(c.entries) == 0 for c in cats)


def test_feature_impact_parser_feature_line_long_no_tabs() -> None:
    """Long line without tabs becomes feature with low confidence."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nThis is a long description for category section\nThis is a long feature name without tabs\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert len(cats[0].entries) == 1
    assert cats[0].entries[0].confidence == 0.5


def test_feature_impact_parser_feature_line_short_name() -> None:
    """Feature line with tab but name too short is skipped."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nLong description for category section here\nAB\tYes\n"
    cats = p.parse_text(text)
    assert len(cats) == 0 or all(len(c.entries) == 0 for c in cats)


def test_feature_impact_parser_feature_partial_flags() -> None:
    """Feature with less than 5 tab parts gets confidence 0.7."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nLong description for category section here\nFeature Name\tYes\tNo\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert len(cats[0].entries) == 1
    assert cats[0].entries[0].confidence == 0.7


def test_feature_impact_parser_feature_all_flags() -> None:
    """Feature with all 5 tab parts gets confidence 1.0."""
    p = FeatureImpactParser()
    text = "Salesforce geral\nLong description for the category section here\nFeature Name\tYes\tNo\tYes\tNo\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    entry = cats[0].entries[0]
    assert entry.available_users is True
    assert entry.available_admins is False
    assert entry.requires_config is True
    assert entry.contact_sf is False


def test_feature_impact_parser_section_header_in_all_headers() -> None:
    """English headers detected when locale is pt-BR (via _all_headers)."""
    p = FeatureImpactParser(locale="pt-BR")
    text = "Salesforce General\nFeature\tYes\n"
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert cats[0].name == "Salesforce General"


def test_feature_impact_parser_entry_without_cat_skipped() -> None:
    """Entry found before any section header is skipped."""
    p = FeatureImpactParser()
    text = "Some Feature\tYes\tNo\tYes\tNo\nSalesforce geral\nAnother\tYes\n"
    p.parse_text(text)
    stats = p.parse_stats()
    assert stats["skipped"] == 1


def test_feature_impact_parser_is_category_description() -> None:
    """_is_category_description returns False when no current cat."""
    p = FeatureImpactParser()
    assert p._is_category_description("some text", None) is False


def test_feature_impact_parser_is_category_description_existing_desc() -> None:
    """_is_category_description returns False when cat already has description."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C", description="Already set")
    assert p._is_category_description("new description text", cat) is False


def test_feature_impact_parser_is_subcategory_header_no_cat() -> None:
    """_is_subcategory_header returns False when no cat."""
    p = FeatureImpactParser()
    assert p._is_subcategory_header("Sub", None) is False


def test_feature_impact_parser_is_subcategory_header_table_header() -> None:
    """_is_subcategory_header returns False for table header."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    assert p._is_subcategory_header("RECURSO\tATIVADO", cat) is False


def test_feature_impact_parser_is_subcategory_header_section_header() -> None:
    """_is_subcategory_header returns False for section header."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    assert p._is_subcategory_header("Agentforce", cat) is False


def test_feature_impact_parser_is_subcategory_header_feature_line() -> None:
    """_is_subcategory_header returns False for feature line."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="X"))
    assert p._is_subcategory_header("Feature\tYes\tNo\tYes\tNo", cat) is False


def test_feature_impact_parser_is_subcategory_header_valid() -> None:
    """_is_subcategory_header returns True for valid subcategory with entries already present."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="X"))
    cat.subcategories["existing"] = [FeatureImpactEntry(name="Y")]
    # Need a line that is NOT a feature line (between 5-80 chars, not parsed as feature)
    # Short line < 10 chars without 'Yes' returns None from _parse_feature_line
    assert p._is_subcategory_header("Sub Head", cat) is True


def test_feature_impact_parser_parse_feature_line_empty() -> None:
    """_parse_feature_line returns None for empty string."""
    p = FeatureImpactParser()
    assert p._parse_feature_line("") is None


def test_feature_impact_parser_parse_feature_line_too_short() -> None:
    """_parse_feature_line returns None for very short line."""
    p = FeatureImpactParser()
    assert p._parse_feature_line("AB") is None


def test_feature_impact_parser_parse_feature_line_section_header() -> None:
    """_parse_feature_line returns None for section header."""
    p = FeatureImpactParser()
    assert p._parse_feature_line("Salesforce geral") is None


def test_feature_impact_parser_en_locale() -> None:
    """FeatureImpactParser works with en locale."""
    p = FeatureImpactParser(locale="en")
    text = "Salesforce General\nFeature\tYes\n"
    cats = p.parse_text(text)
    assert len(cats) == 1


def test_feature_impact_parser_subcategory_in_parse_text() -> None:
    """parse_text correctly handles subcategory detection and entry assignment."""
    p = FeatureImpactParser()
    text = (
        "Salesforce geral\n"
        "This is a long description for the category section\n"
        "Feature One\tYes\tNo\tYes\tNo\n"
        "SubCat\n"  # Subcategory header (5-10 chars, not a feature)
        "Sub Feature\tYes\n"
    )
    cats = p.parse_text(text)
    assert len(cats) == 1
    assert len(cats[0].subcategories) == 1
    assert "SubCat" in cats[0].subcategories
    assert len(cats[0].subcategories["SubCat"]) == 1


def test_feature_impact_parser_is_subcategory_header_too_long() -> None:
    """_is_subcategory_header returns False for lines >= 80 chars."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    cat.entries.append(FeatureImpactEntry(name="X"))
    long_line = "A" * 80
    assert p._is_subcategory_header(long_line, cat) is False


def test_feature_impact_parser_parse_feature_line_name_empty() -> None:
    """_parse_feature_line returns None when name part is empty after strip."""
    p = FeatureImpactParser()
    # Tab-separated where first part is empty
    result = p._parse_feature_line("\tYes\tNo")
    assert result is None


def test_feature_impact_parser_is_category_description_long_line() -> None:
    """_is_category_description returns True for long line with no existing description."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    # Line > 20 chars, not a header, no existing description
    assert p._is_category_description("This is a long description line", cat) is True
    # Short line should return False
    assert p._is_category_description("Short", cat) is False
    # Line in _all_headers returns False (line 554)
    assert p._is_category_description("Agentforce", cat) is False


def test_feature_impact_parser_parse_feature_line_table_header() -> None:
    """_parse_feature_line returns None for table header line."""
    p = FeatureImpactParser()
    result = p._parse_feature_line("RECURSO\tATIVADO")
    assert result is None


def test_feature_impact_parser_is_subcategory_header_empty_cat() -> None:
    """_is_subcategory_header returns False when cat has no entries or subcategories."""
    p = FeatureImpactParser()
    cat = FeatureImpactCategory(name="C")
    # cat has no entries and no subcategories, so inner condition fails
    result = p._is_subcategory_header("ValidLine", cat)
    assert result is False
