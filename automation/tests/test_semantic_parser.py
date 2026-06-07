from automation.core.semantic_parser import SemanticParser


def test_semantic_parser_extracts_sections_properly() -> None:
    parser = SemanticParser()
    html_content = """
    <html>
        <body>
            <h1>Apex Updates</h1>
            <p>Apex is getting better.</p>
            <li>Use new features.</li>
            <h2>LWC Updates</h2>
            <p>LWC is fast.</p>
            <h3>No content header</h3>
            <h1>Ending section</h1>
            <p>Goodbye</p>
        </body>
    </html>
    """
    sections = parser.parse_sections(html_content)

    assert len(sections) == 3

    assert sections[0].title == "Apex Updates"
    assert sections[0].content == "Apex is getting better.\nUse new features."

    assert sections[1].title == "LWC Updates"
    assert sections[1].content == "LWC is fast."

    assert sections[2].title == "Ending section"
    assert sections[2].content == "Goodbye"
