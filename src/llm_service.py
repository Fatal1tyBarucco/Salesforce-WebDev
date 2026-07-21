"""LLM service with fallback chain across multiple providers."""

import asyncio
import time
import logging
import os
from typing import Any, Optional
from dataclasses import dataclass

import openai
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


@dataclass
class CircuitBreakerConfig:
    threshold: int = 3
    cooldown: float = 60.0


@dataclass
class LLMProvider:
    """A single LLM provider configuration."""

    name: str
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o"
    provider_type: str = "openai"  # "openai", "google", or "opencode"


@dataclass
class ProviderState:
    """Tracks circuit breaker state for a provider."""

    failures: int = 0
    opened_at: float = 0.0
    is_open: bool = False


class LLMService:
    """Resilient LLM service with automatic fallback across providers.

    Tries providers in order: OpenAI → Google Gemini → OpenCode → MiMoCode.
    When one fails, moves to the next after circuit breaker cooldown.
    """

    def __init__(
        self,
        config: CircuitBreakerConfig = CircuitBreakerConfig(),
        client: Any = None,
        providers: list[LLMProvider] | None = None,
    ) -> None:
        self._config = config
        self._logger = logging.getLogger(__name__)
        self._provider_states: dict[str, ProviderState] = {}
        self._providers: list[LLMProvider] = []

        if providers:
            self._providers = providers
        else:
            self._providers = self._load_providers_from_env()

        for p in self._providers:
            self._provider_states[p.name] = ProviderState()

        self._client = client

    def _load_providers_from_env(self) -> list[LLMProvider]:
        """Load provider configurations from environment variables.

        Priority order:
        1. OPENAI_API_KEY (primary OpenAI)
        2. GOOGLE_API_KEY (Google Gemini)
        3. OPENCODE_API_KEY (OpenCode - OpenAI compatible)
        4. MIMOCODE_API_KEY (MiMoCode - OpenAI compatible)
        """
        providers: list[LLMProvider] = []

        # 1. OpenAI (primary)
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            providers.append(
                LLMProvider(
                    name="openai",
                    api_key=openai_key,
                    base_url="https://api.openai.com/v1",
                    model="gpt-4o",
                    provider_type="openai",
                )
            )

        # 2. Google Gemini (secondary)
        google_key = os.environ.get("GOOGLE_API_KEY", "")
        if google_key:
            providers.append(
                LLMProvider(
                    name="google",
                    api_key=google_key,
                    model="gemma-4-26b-a4b-it",
                    provider_type="google",
                )
            )

        # 3. OpenCode (tertiary - OpenAI compatible)
        opencode_key = os.environ.get("OPENCODE_API_KEY", "")
        if opencode_key:
            providers.append(
                LLMProvider(
                    name="opencode",
                    api_key=opencode_key,
                    base_url="https://api.opencode.ai/v1",
                    model="gpt-4o",
                    provider_type="opencode",
                )
            )

        # 4. MiMoCode (quaternary - OpenAI compatible)
        mimocode_key = os.environ.get("MIMOCODE_API_KEY", "")
        if mimocode_key:
            providers.append(
                LLMProvider(
                    name="mimocode",
                    api_key=mimocode_key,
                    base_url="https://api.mimocode.ai/v1",
                    model="mimo-auto",
                    provider_type="mimocode",
                )
            )

        return providers

    def _get_provider_state(self, provider: LLMProvider) -> ProviderState:
        return self._provider_states[provider.name]

    def _is_provider_available(self, provider: LLMProvider) -> bool:
        state = self._get_provider_state(provider)
        if state.failures < self._config.threshold:
            return True
        elapsed = time.time() - state.opened_at
        if elapsed > self._config.cooldown:
            state.is_open = False
            return True
        return False

    def _record_success(self, provider: LLMProvider) -> None:
        state = self._get_provider_state(provider)
        state.failures = 0
        state.opened_at = 0.0
        state.is_open = False

    def _record_failure(self, provider: LLMProvider) -> None:
        state = self._get_provider_state(provider)
        state.failures += 1
        if state.failures >= self._config.threshold:
            state.opened_at = time.time()
            state.is_open = True
            self._logger.warning(
                "Provider '%s' circuit breaker tripped. Cooldown started.", provider.name
            )

    @retry(
        retry=retry_if_exception_type((openai.APIConnectionError, openai.InternalServerError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _call_openai_provider(
        self, provider: LLMProvider, system_prompt: str, user_prompt: str
    ) -> str:
        """Call OpenAI-compatible provider with timeout and retry."""
        client = openai.AsyncOpenAI(
            api_key=provider.api_key,
            base_url=provider.base_url,
            timeout=30.0,
        )
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=provider.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
            ),
            timeout=60.0,
        )
        # Handle both standard OpenAI response and raw string responses
        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content or ""
        elif isinstance(response, str):
            return response
        return str(response)

    @retry(
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _call_google_provider(
        self, provider: LLMProvider, system_prompt: str, user_prompt: str
    ) -> str:
        """Call Google Gemini provider with timeout and retry."""
        client = genai.Client(api_key=provider.api_key)
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model=provider.model,
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.0,
                ),
            ),
            timeout=60.0,
        )
        return response.text or ""

    async def _call_provider(
        self, provider: LLMProvider, system_prompt: str, user_prompt: str
    ) -> str:
        """Call a specific provider based on type."""
        if provider.provider_type == "google":
            return await self._call_google_provider(provider, system_prompt, user_prompt)
        return await self._call_openai_provider(provider, system_prompt, user_prompt)

    async def generate_text(
        self, user_prompt: str, system_prompt: str = "You are a helpful assistant."
    ) -> Optional[str]:
        """Generate text with automatic fallback across providers.

        Tries each provider in order. If one fails, moves to the next.
        Returns the first successful response.
        """
        for provider in self._providers:
            if not self._is_provider_available(provider):
                self._logger.debug("Provider '%s' unavailable, trying next", provider.name)
                continue

            try:
                result = await self._call_provider(provider, system_prompt, user_prompt)
                self._record_success(provider)
                self._logger.info("Provider '%s' succeeded", provider.name)
                return result
            except openai.RateLimitError as e:
                self._logger.warning("Provider '%s' rate limited: %s", provider.name, e)
                self._record_failure(provider)
                continue
            except openai.AuthenticationError as e:
                self._logger.warning("Provider '%s' auth error: %s", provider.name, e)
                self._record_failure(provider)
                continue
            except (openai.APIConnectionError, openai.InternalServerError) as e:
                self._logger.error("Provider '%s' connection/server error: %s", provider.name, e)
                self._record_failure(provider)
                continue
            except (TimeoutError, asyncio.TimeoutError) as e:
                self._logger.error("Provider '%s' timeout: %s", provider.name, e)
                self._record_failure(provider)
                continue
            except Exception as e:
                self._logger.error("Provider '%s' unexpected error: %s", provider.name, e)
                self._record_failure(provider)
                continue

        # Legacy single-client fallback
        if self._client:
            try:
                response = await self._client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.0,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                self._logger.error("Legacy client error: %s", e)

        self._logger.error("All LLM providers exhausted")
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
            import json

            start_idx = result.find("{")
            end_idx = result.rfind("}") + 1
            parsed = json.loads(result[start_idx:end_idx])
            return parsed if isinstance(parsed, dict) else {"error": "Invalid JSON structure"}
        except (ValueError, IndexError) as e:
            self._logger.error("Failed to parse LLM classification JSON: %s", e)
            return {"error": "Invalid JSON response"}
