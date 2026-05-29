from automation.core.parser import ReleaseNotesParser


def test_parser_should_extract_text() -> None:

    parser = ReleaseNotesParser()

    html_content = "<html><body><h1>Apex</h1></body></html>"

    parsed_content = parser.parse(html_content)

    assert "Apex" in parsed_content
