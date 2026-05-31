from automation.core.classifier import TopicClassifier
from automation.core.generator import MarkdownArtifactGenerator
from automation.core.parser import ReleaseNotesParser
from automation.core.readme_updater import ReadmeUpdater
from automation.core.scraper import ReleaseNotesScraper
from automation.shared.logger import build_logger


LOGGER = build_logger(__name__)


class ReleasePipelineOrchestrator:

    def __init__(self) -> None:

        self.scraper = ReleaseNotesScraper()

        self.parser = ReleaseNotesParser()

        self.classifier = TopicClassifier()

        self.generator = MarkdownArtifactGenerator()

        self.readme_updater = ReadmeUpdater()

    def execute(self) -> None:

        LOGGER.info("Starting release pipeline")

        raw_content = self.scraper.fetch_release_notes()

        parsed_content = self.parser.parse(raw_content)

        classified_topics = self.classifier.classify(
            parsed_content
        )

        self.generator.generate(
            release_name="Summer_26",
            topics=classified_topics
        )

        self.readme_updater.update()

        LOGGER.info("Pipeline finished successfully")


if __name__ == "__main__":
    ReleasePipelineOrchestrator().execute()
