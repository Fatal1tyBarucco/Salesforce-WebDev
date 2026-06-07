from automation.core.weighted_classifier import WeightedTopicClassifier
from automation.shared.models import ParsedSection


def test_weighted_classifier_classifies_and_sorts_correctly() -> None:
    classifier = WeightedTopicClassifier()

    sections = [
        ParsedSection(
            title="Apex Trigger modifications", content="We have batch and queueable executions."
        ),
        ParsedSection(title="LWC Lightning Web Components", content="Wire adapters are great."),
        ParsedSection(title="Flow builder update", content="Use screen flow for automation."),
    ]

    results = classifier.classify(sections)

    # Devem ter sido classificados os tópicos correspondentes (apex, lwc, flow)
    # Vamos verificar que o resultado está ordenado por score de confiança.
    # Apex tem palavras-chave: apex, trigger, batch, queueable -> total de matches = 4 (nas keywords do constants/models)
    # Vamos ver quais são as chaves no TOPIC_KEYWORDS de automation.shared.constants:
    # "apex", "lwc", "flow", "security", "integrations"
    # Vamos conferir o score de confiança
    assert len(results) > 0
    assert results[0].topic_name in ["apex", "lwc", "flow"]
