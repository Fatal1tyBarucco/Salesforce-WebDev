import time
import logging
from typing import Any, Optional, cast
from dataclasses import dataclass

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


@dataclass
class CircuitBreakerConfig:
    threshold: int = 3
    cooldown: float = 60.0


class LLMService:
    """Resilient service for interacting with OpenAI LLMs."""

    def __init__(
        self, config: CircuitBreakerConfig = CircuitBreakerConfig(), client: Any = None
    ) -> None:
        self._client = client if client is not None else openai.AsyncOpenAI()
        self._config = config
        self._failures = 0
        self._opened_at: float = 0.0
        self._logger = logging.getLogger(__name__)

    @property
    def is_circuit_open(self) -> bool:
        if self._failures < self._config.threshold:
            return False

        elapsed = time.time() - self._opened_at
        if elapsed > self._config.cooldown:
            # Half-open state: allow a test request
            return False
        return True

    def _record_success(self) -> None:
        self._failures = 0
        self._opened_at = 0.0

    def _record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._config.threshold:
            self._opened_at = time.time()
            self._logger.warning("LLM Service circuit breaker tripped. Cooldown started.")

    @retry(
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APIConnectionError, openai.InternalServerError)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(5),
        reraise=True,
    )
    async def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """Low-level OpenAI call with tenacity retries."""
        response = await self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content or ""

    async def generate_text(
        self, user_prompt: str, system_prompt: str = "You are a helpful assistant."
    ) -> Optional[str]:
        """Generate text with circuit breaker and retry logic."""
        if self.is_circuit_open:
            self._logger.error("LLM Service circuit open - skipping request")
            return None

        try:
            result = await self._call_openai(system_prompt, user_prompt)
            self._record_success()
            return result
        except openai.RateLimitError as e:
            # Tenacity handles retries, but if it ultimately fails, record it
            self._logger.error("LLM Service rate limit exceeded after retries: %s", e)
            self._record_failure()
            return None
        except Exception as e:
            self._logger.error("LLM Service unexpected error: %s", e)
            self._record_failure()
            return None

    async def classify_text(
        self, text: str, categories: list[str], system_prompt: Optional[str] = None
    ) -> dict[str, Any]:
        """Classify text into provided categories using the LLM."""
        if system_prompt is None:
            system_prompt = (
                "You are a professional classifier. Analyze the text and return a JSON object "
                "mapping each category to a boolean (true if it applies, false otherwise) "
                "and a confidence score (0.0-1.0). "
                'Example output: {"Security": {"applies": true, "confidence": 0.9}, ...}'
            )

        user_prompt = f"Categories: {categories}\n\nText: {text}"
        result = await self.generate_text(user_prompt, system_prompt)

        if not result:
            return {"error": "LLM failed to generate classification"}

        try:
            # Simple JSON extraction from the response
            import json

            start_idx = result.find("{")
            end_idx = result.rfind("}") + 1
            return cast(dict[str, Any], json.loads(result[start_idx:end_idx]))
        except (ValueError, IndexError) as e:
            self._logger.error("Failed to parse LLM classification JSON: %s", e)
            return {"error": "Invalid JSON response"}
