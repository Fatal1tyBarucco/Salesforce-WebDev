from bs4 import BeautifulSoup
from src.parser import ReleaseNotesParser
from src.config import MONITORED_TOPICS


def test_src_parser_extract_article_links() -> None:
    parser = ReleaseNotesParser()
    
    html = """
    <html>
        <body>
            <!-- Link do Apex que bate no padrão de URL rn_apex -->
            <a href="/s/articleView?id=release-notes.rn_apex_class.htm">Apex Feature Article</a>
            <!-- Link do LWC que bate no padrão de URL rn_lwc -->
            <a href="/s/articleView?id=release-notes.rn_lwc_cmp.htm">Lightning Web Component Feature</a>
            <!-- Link que não é release notes -->
            <a href="/s/articleView?id=other_doc">Random Doc</a>
            <!-- Link muito curto -->
            <a href="/s/articleView?id=release-notes.rn_flow.htm">Flow</a>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    links_map = parser.extract_article_links(soup, "Summer '26")

    assert "apex" in links_map
    assert len(links_map["apex"]) == 1
    assert links_map["apex"][0]["title"] == "Apex Feature Article"

    assert "lwc" in links_map
    assert len(links_map["lwc"]) == 1
    assert links_map["lwc"][0]["title"] == "Lightning Web Component Feature"


def test_src_parser_build_topic_content_from_links() -> None:
    parser = ReleaseNotesParser()
    topic_links = {
        "apex": [
            {"url": "https://help.salesforce.com/s/articleView?id=rn_apex_class", "title": "New Apex Class"}
        ],
        "lwc": []
    }
    soup = BeautifulSoup("", "html.parser")
    content_map = parser.build_topic_content_from_links(topic_links, soup, "Summer '26")

    assert "apex" in content_map
    # Linhas de texto geradas
    apex_content = "\n".join(content_map["apex"])
    assert "## Apex — Summer '26" in apex_content
    assert "New Apex Class" in apex_content


def test_src_parser_legacy_parse_fallback() -> None:
    parser = ReleaseNotesParser()
    
    html = """
    <html>
        <body>
            <h1>Apex Trigger Updates</h1>
            <p>Triggers now execute asynchronously under some contexts.</p>
            <h2>LWC Lightning Components</h2>
            <p>New components for wire adapter.</p>
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")
    content_map = parser.parse(soup, "Summer '26")

    assert "apex" in content_map
    apex_lines = "\n".join(content_map["apex"])
    assert "Apex Trigger Updates" in apex_lines
    assert "Triggers now execute asynchronously" in apex_lines
