from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationConfig:

    release_notes_base_url: str = "https://help.salesforce.com/s/articleView"

    release_notes_path: str = "?id=release-notes.salesforce_release_notes.htm"

    request_timeout_seconds: int = 30

    releases_directory: str = "releases"

    cache_directory: str = "cache"
