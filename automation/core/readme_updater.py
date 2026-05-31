from pathlib import Path


class ReadmeUpdater:

    README_PATH = Path("README.md")

    def update(self) -> None:

        release_directories = sorted(
            Path("releases").glob("*")
        )

        lines: list[str] = [
            "# Salesforce Release Notes Knowledge Base",
            "",
            "## 📋 Releases Disponíveis",
            ""
        ]

        for release_directory in release_directories:

            release_name = release_directory.name.replace(
                "_",
                " "
            ).title()

            lines.append(f"### {release_name}")

            for markdown_file in sorted(
                release_directory.glob("*.md")
            ):

                topic_name = markdown_file.stem

                lines.append(
                    f"- [{topic_name}]"
                    f"(./{markdown_file.as_posix()})"
                )

        self.README_PATH.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )
