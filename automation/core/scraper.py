from automation.shared.config import ApplicationConfig
from automation.shared.http_client import HttpClient


class ReleaseNotesScraper:

    def __init__(self) -> None:
        self.config = ApplicationConfig()
        self.http_client = HttpClient()

    def fetch_release_notes(self) -> str:
        base_url = self.config.release_notes_base_url
        path = self.config.release_notes_path
        release_url = f"{base_url}{path}&release=262&type=5"

        return self.http_client.get(release_url, self.config.request_timeout_seconds)
