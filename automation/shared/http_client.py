from typing import Optional

import requests
from tenacity import retry
from tenacity import stop_after_attempt
from tenacity import wait_exponential

from automation.shared.logger import build_logger


LOGGER = build_logger(__name__)


class HttpClient:

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2)
    )
    def get(
        self,
        url: str,
        timeout_seconds: Optional[int] = 30
    ) -> str:

        LOGGER.info(f"Executing request to: {url}")

        response = requests.get(
            url,
            timeout=timeout_seconds,
            headers={
                "User-Agent": (
                    "Salesforce-WebDev-Release-Intelligence"
                )
            }
        )

        response.raise_for_status()

        return response.text
