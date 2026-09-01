"""Tests for the test data factory.

Validates that factories produce consistent, usable test data.
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from tests.factories import (
    make_feature_impact_html,
    make_feature_impact_text,
    make_mock_html_response,
    make_release,
    make_release_metadata,
    make_toc_html,
    make_topic_node,
    make_topic_tree,
)


class TestReleaseFactory:
    def test_default_release(self):
        r = make_release()
        assert r.name
        assert r.release_id
        assert r.slug

    def test_custom_release(self):
        r = make_release(name="Custom '27", release_id=270, slug="custom_27")
        assert r.name == "Custom '27"
        assert r.release_id == 270
        assert r.slug == "custom_27"

    def test_sequential_release_ids(self, monkeypatch):
        from tests import factories

        monkeypatch.setattr(factories, "_RELEASE_SEQUENCE", 0)
        r1 = factories.make_release(name="Test1", slug="test1")
        r2 = factories.make_release(name="Test2", slug="test2")
        assert r1.release_id != r2.release_id
        assert r1.release_id == 901
        assert r2.release_id == 902

    def test_release_from_known(self):
        from src.config import KNOWN_RELEASES

        first = KNOWN_RELEASES[0]
        r = make_release(name=first.name, release_id=first.release_id, slug=first.slug)
        assert r == first


class TestTopicNodeFactory:
    def test_simple_node(self):
        node = make_topic_node(slug="apex", display_name="Apex", level=3)
        assert node.slug == "apex"
        assert node.display_name == "Apex"
        assert node.level == 3
        assert node.is_leaf() is True
        assert len(node.articles) == 0
        assert len(node.children) == 0

    def test_node_with_children(self):
        child = make_topic_node(slug="child", display_name="Child")
        parent = make_topic_node(slug="parent", display_name="Parent", children=[child])
        assert parent.is_leaf() is False
        assert len(parent.all_articles()) == 0

    def test_node_with_articles(self):
        node = make_topic_node(
            slug="topic",
            articles=[{"title": "Art 1", "url": "/a1"}, {"title": "Art 2", "url": "/a2"}],
        )
        assert len(node.all_articles()) == 2


class TestTopicTreeFactory:
    def test_default_tree(self):
        tree = make_topic_tree()
        assert len(tree) == 4
        for node in tree:
            assert node.is_leaf() is False
            assert len(node.children) > 0

    def test_custom_categories(self):
        tree = make_topic_tree(categories=["A", "B"], articles_per_category=5)
        assert len(tree) == 2
        for node in tree:
            assert len(node.children[0].articles) == 5

    def test_all_articles_aggregated(self):
        tree = make_topic_tree(categories=["A", "B", "C"], articles_per_category=2)
        for node in tree:
            assert len(node.all_articles()) == 2


class TestTocHtmlFactory:
    def test_default_html(self):
        html = make_toc_html()
        assert "toc-container" in html
        assert 'role="treeitem"' in html

    def test_custom_categories(self):
        html = make_toc_html(categories=["Apex"], articles_per_category=3)
        soup = BeautifulSoup(html, "html.parser")
        articles = soup.find_all("li", attrs={"role": "treeitem", "aria-level": "3"})
        assert len(articles) == 3

    def test_html_is_parseable(self):
        html = make_toc_html()
        soup = BeautifulSoup(html, "html.parser")
        assert soup.find("nav", class_="toc-container") is not None


class TestFeatureImpactTextFactory:
    def test_default_text(self):
        text = make_feature_impact_text()
        assert "Feature Impact" in text
        assert "Total de Recursos" in text
        assert "\t" in text

    def test_custom_categories(self):
        text = make_feature_impact_text(categories=["A", "B"], features_per_category=2)
        assert "A" in text
        assert "B" in text
        assert "Total de Recursos: 4" in text

    def test_yes_no_flags(self):
        text = make_feature_impact_text(categories=["A"], features_per_category=5)
        lines = [line for line in text.split("\n") if "\t" in line]
        assert len(lines) == 5
        for line in lines:
            fields = line.split("\t")
            assert len(fields) == 5


class TestFeatureImpactHtmlFactory:
    def test_default_html(self):
        html = make_feature_impact_html()
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="feature-item")
        assert len(items) > 0

    def test_custom_features(self):
        html = make_feature_impact_html(categories=["A"], features_per_category=3)
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", class_="feature-item")
        assert len(items) == 3


class TestReleaseMetadataFactory:
    def test_default_metadata(self):
        meta = make_release_metadata()
        assert meta["total_features"] == 50
        assert "generated_at" in meta
        assert len(meta["categories"]) > 0

    def test_custom_metadata(self):
        meta = make_release_metadata(total_features=100, categories=["A", "B"])
        assert meta["total_features"] == 100
        assert len(meta["categories"]) == 2

    def test_metadata_categories_sum(self):
        meta = make_release_metadata(total_features=60, categories=["A", "B", "C"])
        total = sum(c["count"] for c in meta["categories"])
        assert total == 60


class TestMockHtmlResponseFactory:
    def test_default_response(self):
        resp = make_mock_html_response()
        assert resp["status"] == 200
        assert "body" in resp
        assert resp["headers"]["content-type"] == "text/html; charset=utf-8"

    def test_custom_status(self):
        resp = make_mock_html_response(status_code=404)
        assert resp["status"] == 404

    def test_body_size(self):
        resp = make_mock_html_response(body_size=1000)
        assert len(resp["body"]) >= 1000
