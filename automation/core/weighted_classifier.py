from __future__ import annotations

from automation.shared.constants import TOPIC_KEYWORDS
from automation.shared.models import ClassificationResult
from automation.shared.models import ParsedSection


class WeightedTopicClassifier:
    """
    Weighted semantic topic classifier.
    """

    def classify(
        self,
        parsed_sections: list[ParsedSection],
    ) -> list[ClassificationResult]:
        results: list[ClassificationResult] = []

        for topic_name, keywords in TOPIC_KEYWORDS.items():
            matched_content: list[str] = []
            confidence_score: int = 0

            for parsed_section in parsed_sections:
                section_text = (
                    f"{parsed_section.title}\n{parsed_section.content}"
                ).lower()

                matched_keywords = [
                    keyword
                    for keyword in keywords
                    if keyword.lower() in section_text
                ]

                if matched_keywords:
                    matched_content.append(section_text)
                    confidence_score += len(matched_keywords)

            if matched_content:
                results.append(
                    ClassificationResult(
                        topic_name=topic_name,
                        content="\n\n".join(matched_content),
                        confidence_score=confidence_score,
                    )
                )

        return sorted(
            results,
            key=lambda result: result.confidence_score,
            reverse=True,
        )
