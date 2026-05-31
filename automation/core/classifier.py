from automation.shared.constants import TOPIC_MAPPING
from automation.shared.models import ReleaseTopicContent


class TopicClassifier:

    def classify(
        self,
        parsed_content: str
    ) -> list[ReleaseTopicContent]:

        topic_results: list[ReleaseTopicContent] = []

        normalized_content = parsed_content.lower()

        for topic_name, keywords in TOPIC_MAPPING.items():

            matched_lines: list[str] = []

            for line in normalized_content.splitlines():

                if any(
                    keyword.lower() in line
                    for keyword in keywords
                ):
                    matched_lines.append(line)

            topic_results.append(
                ReleaseTopicContent(
                    topic_name=topic_name,
                    content="\n".join(matched_lines)
                )
            )

        return topic_results
