from bs4 import BeautifulSoup
from src.parser import ReleaseNotesParser


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
    from src.config import TopicNode

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
    from src.config import TopicNode

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


def test_id_to_slug_various() -> None:
    parser = ReleaseNotesParser()
    assert parser._id_to_slug("rn_development_leaf") == "development"
    assert parser._id_to_slug("rn_apex") == "apex"
    assert parser._id_to_slug("rn_security") == "security"
    assert parser._id_to_slug("plain_id") == "plain_id"
