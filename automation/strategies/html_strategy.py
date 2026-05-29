from bs4 import BeautifulSoup

from automation.strategies.parser_strategy import ParserStrategy


class HtmlStrategy(ParserStrategy):

    def parse(self, raw_content: str) -> str:
        soup = BeautifulSoup(raw_content, "lxml")

        return soup.get_text(separator="\n")
