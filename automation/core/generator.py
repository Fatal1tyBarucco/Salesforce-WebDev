from pathlib import Path

from slugify import slugify

from automation.shared.file_utils import ensure_directory_exists
from automation.shared.models import ReleaseTopicContent


class MarkdownArtifactGenerator:

    def generate(self, release_name: str, topics: list[ReleaseTopicContent]) -> None:

        base_directory = f"releases/{slugify(release_name)}"

        ensure_directory_exists(base_directory)

        for topic in topics:

            file_path = Path(base_directory) / f"{topic.topic_name}.md"

            markdown_content = f"# {topic.topic_name.upper()}\n\n" f"{topic.content}"

            file_path.write_text(markdown_content, encoding="utf-8")
