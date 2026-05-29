from automation.services.release_discovery_service import ReleaseDiscoveryService
from automation.shared.config import ApplicationConfig
from automation.shared.http_client import HttpClient


class ReleaseNotesScraper:

    def __init__(self) -> None:
        self.config = ApplicationConfig()
        self.http_client = HttpClient()
        self.discovery_service = ReleaseDiscoveryService()

    def fetch_release_notes(self) -> str:

        release_url = self.discovery_service.build_release_url(
            release_number=262
        )

        return self.http_client.get(
            release_url,
            self.config.request_timeout_seconds
        )
