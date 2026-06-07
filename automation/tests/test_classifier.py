from automation.core.classifier import TopicClassifier
from automation.shared.topic_registry import TOPIC_REGISTRY


def test_topic_registry_contains_apex() -> None:
    assert "apex" in TOPIC_REGISTRY


def test_classifier_should_match_apex_topic() -> None:

    classifier = TopicClassifier()

    parsed_content = "Queueable Apex execution"

    result = classifier.classify(parsed_content)

    apex_topic = next(item for item in result if item.topic_name == "apex")

    assert "queueable apex execution" in apex_topic.content
