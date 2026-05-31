from automation.strategies.html_strategy import HtmlStrategy


class ReleaseNotesParser:

    def __init__(self) -> None:
        self.strategy = HtmlStrategy()

    def parse(self, raw_content: str) -> str:
        return self.strategy.parse(raw_content)
