from abc import ABC
from abc import abstractmethod


class ParserStrategy(ABC):

    @abstractmethod
    def parse(self, raw_content: str) -> str:
        """
        Parse raw release content.
        """
