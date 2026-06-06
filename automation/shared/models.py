from dataclasses import dataclass


@dataclass
class ReleaseTopicContent:
    topic_name: str
    content: str


@dataclass
class ParsedSection:
    title: str
    content: str


@dataclass
class ClassificationResult:
    topic_name: str
    content: str
    confidence_score: int
