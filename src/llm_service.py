"""LLM service with fallback chain across multiple providers."""

import asyncio
import hashlib
import inspect
import logging
import os
import time
from typing import Any, Optional
from dataclasses import dataclass, field

import openai
from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .circuit_breaker import CircuitBreaker
from .cache_manager import CacheManager


@dataclass
class RateLimiter:
    """Async token-bucket rate limiter.

    Limits the number of requests per time window.  Thread-safe via asyncio.Lock.
    """

    max_requests: int = 60
    window_seconds: float = 60.0
    _timestamps: list[float] = field(default_factory=list, repr=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def acquire(self) -> None:
        """Wait until a request slot is available."""
        async with self._lock:
            now = time.monotonic()
            # Purge timestamps outside the window
            self._timestamps = [t for t in self._timestamps if now - t < self.window_seconds]
            if len(self._timestamps) >= self.max_requests:
                # Sleep until the oldest timestamp expires
                sleep_until = self._timestamps[0] + self.window_seconds
                wait = sleep_until - now
                if wait > 0:
                    await asyncio.sleep(wait)
                now = time.monotonic()
                self._timestamps = [t for t in self._timestamps if now - t < self.window_seconds]
            self._timestamps.append(time.monotonic())


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

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
        cache: CacheManager | None = None,
        rate_limiter: RateLimiter | None = None,
    ) -> None:
        self._config = config
        self._logger = logging.getLogger(__name__)
        self._provider_states: dict[str, CircuitBreaker] = {}
        self._providers: list[LLMProvider] = []
        self._clients: dict[str, Any] = {}  # Lazy-initialized, cached per provider
        self._cache = cache
        self._rate_limiter = rate_limiter or RateLimiter(max_requests=60, window_seconds=60.0)

        _auto_loaded = providers is None
        if providers is not None:
            self._providers = providers
        else:
            self._providers = self._load_providers_from_env()

        if _auto_loaded and not self._providers and client is None:
            raise ValueError(
                "No LLM providers configured. Set at least one of: "
                "OPENAI_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY, "
                "OPENROUTER_API_KEY, OPENCODE_API_KEY, MIMOCODE_API_KEY "
                "or pass a client/providers directly."
            )

        for p in self._providers:
            self._provider_states[p.name] = CircuitBreaker(
                threshold=config.threshold, cooldown=config.cooldown
            )

        self._client = client

    @staticmethod
    def _prompt_hash(system_prompt: str, user_prompt: str) -> str:
        """Generate a deterministic hash for a prompt pair."""
        combined = f"{system_prompt}\x00{user_prompt}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    async def __aenter__(self) -> "LLMService":
        """Enter async context — pre-warm clients for all providers."""
        for provider in self._providers:
            self._get_or_create_client(provider)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Exit async context — close all cached clients."""
        for name, client in self._clients.items():
            try:
                close = getattr(client, "close", None)
                if close and inspect.iscoroutinefunction(close):
                    await close()
                elif close:
                    close()
            except Exception:
                self._logger.debug("Error closing client %s", name, exc_info=True)
        self._clients.clear()

    def _get_or_create_client(self, provider: LLMProvider) -> Any:
        """Return a cached client for the provider, creating one if needed."""
        if provider.name in self._clients:
            return self._clients[provider.name]

        client: Any
        if provider.provider_type == "google":
            client = genai.Client(api_key=provider.api_key)
        else:
            client = openai.AsyncOpenAI(
                api_key=provider.api_key,
                base_url=provider.base_url,
                timeout=30.0,
            )
        self._clients[provider.name] = client
        return client

    def _load_providers_from_env(self) -> list[LLMProvider]:
        """Load provider configurations from environment variables.

        Priority order:
        1. OPENAI_API_KEY (primary OpenAI)
        2. GOOGLE_API_KEY (Google Gemini)
        3. DEEPSEEK_API_KEY (DeepSeek)
        4. OPENROUTER_API_KEY (OpenRouter)
        5. OPENCODE_API_KEY (OpenCode - OpenAI compatible)
        6. MIMOCODE_API_KEY (MiMoCode - OpenAI compatible)
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
                    model="gemini-2.5-flash",
                    provider_type="google",
                )
            )

        # 3. DeepSeek (tertiary - OpenAI compatible, cost-effective)
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if deepseek_key:
            providers.append(
                LLMProvider(
                    name="deepseek",
                    api_key=deepseek_key,
                    base_url="https://api.deepseek.com/v1",
                    model="deepseek-chat",
                    provider_type="openai",
                )
            )

        # 4. OpenRouter (quaternary - multi-model gateway)
        openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
        if openrouter_key:
            providers.append(
                LLMProvider(
                    name="openrouter",
                    api_key=openrouter_key,
                    base_url="https://openrouter.ai/api/v1",
                    model="anthropic/claude-sonnet-4-20250514",
                    provider_type="openai",
                )
            )

        # 5. OpenCode (OpenAI compatible)
        opencode_key = os.environ.get("OPENCODE_API_KEY", "")
        if opencode_key:
            providers.append(
                LLMProvider(
                    name="opencode",
                    api_key=opencode_key,
                    base_url="https://api.opencode.ai/v1",
                    model="gpt-4o",
                    provider_type="openai",
                )
            )

        # 6. MiMoCode (OpenAI compatible)
        mimocode_key = os.environ.get("MIMOCODE_API_KEY", "")
        if mimocode_key:
            providers.append(
                LLMProvider(
                    name="mimocode",
                    api_key=mimocode_key,
                    base_url="https://api.mimocode.ai/v1",
                    model="mimo-auto",
                    provider_type="openai",
                )
            )

        return providers

    def _get_provider_state(self, provider: LLMProvider) -> CircuitBreaker:
        return self._provider_states[provider.name]

    def _is_provider_available(self, provider: LLMProvider) -> bool:
        breaker = self._get_provider_state(provider)
        return not breaker.is_open

    def _record_success(self, provider: LLMProvider) -> None:
        self._get_provider_state(provider).record_success()

    def _record_failure(self, provider: LLMProvider) -> None:
        self._get_provider_state(provider).record_failure()

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
        client = self._get_or_create_client(provider)
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
        return ""

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
        client = self._get_or_create_client(provider)
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
        Returns the first successful response.  Uses prompt-hash cache
        when a CacheManager was provided at construction time.
        """
        return await self.generate_text_with_tier(user_prompt, system_prompt, tier="standard")

    async def generate_text_with_tier(
        self,
        user_prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        tier: str = "standard",
    ) -> Optional[str]:
        """Generate text with cost-aware provider selection.

        Tiers:
        - "cheap": Use cheapest available provider (classification, simple tasks)
        - "standard": Normal fallback chain (default)
        - "premium": Use best available provider (code generation, complex analysis)

        Args:
            user_prompt: The user prompt.
            system_prompt: System prompt.
            tier: Cost tier for provider selection.

        Returns:
            Generated text or None.
        """
        # Cache lookup
        cache_key = self._prompt_hash(system_prompt, user_prompt)
        if self._cache is not None:
            cached = self._cache.get(cache_key, namespace="llm")
            if cached is not None:
                self._logger.debug("LLM cache hit for key=%s", cache_key[:12])
                return str(cached)

        # Select providers based on tier
        providers = self._select_providers_by_tier(tier)

        # Rate limiting
        await self._rate_limiter.acquire()

        for provider in providers:
            if not self._is_provider_available(provider):
                self._logger.debug("Provider '%s' unavailable, trying next", provider.name)
                continue

            try:
                result = await self._call_provider(provider, system_prompt, user_prompt)
                self._record_success(provider)
                self._logger.info("Provider '%s' succeeded (tier=%s)", provider.name, tier)
                if self._cache is not None:
                    self._cache.set(cache_key, result, namespace="llm")
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
                result = response.choices[0].message.content or ""
                if self._cache is not None:
                    self._cache.set(cache_key, result, namespace="llm")
                return result
            except Exception as e:
                self._logger.error("Legacy client error: %s", e)

        self._logger.error("All LLM providers exhausted (tier=%s)", tier)
        return None

    def _select_providers_by_tier(self, tier: str) -> list[LLMProvider]:
        """Select providers ordered by cost tier.

        Args:
            tier: "cheap", "standard", or "premium".

        Returns:
            Ordered list of providers for the tier.
        """
        if not self._providers:
            return []

        if tier == "cheap":
            # Prefer DeepSeek/Google (cheaper), then OpenRouter, then OpenAI
            cheap_order = ["deepseek", "google", "openrouter", "opencode", "mimocode", "openai"]
        elif tier == "premium":
            # Prefer OpenAI (best quality), then OpenRouter, then Google
            cheap_order = ["openai", "openrouter", "google", "deepseek", "opencode", "mimocode"]
        else:
            # Standard order as configured
            return list(self._providers)

        ordered: list[LLMProvider] = []
        by_name = {p.name: p for p in self._providers}
        for name in cheap_order:
            if name in by_name:
                ordered.append(by_name[name])

        # Add any remaining providers not in the order
        for p in self._providers:
            if p not in ordered:
                ordered.append(p)

        return ordered

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

    async def generate_batch(
        self,
        prompts: list[str],
        system_prompt: str = "You are a helpful assistant.",
        batch_size: int = 10,
    ) -> list[Optional[str]]:
        """Generate text for multiple prompts, batching them into single LLM calls.

        Combines up to ``batch_size`` prompts into a single request to reduce
        API calls and cost.  Falls back to individual calls when the batch
        response cannot be parsed.

        Args:
            prompts: List of user prompts.
            system_prompt: Shared system prompt for all prompts.
            batch_size: Maximum number of prompts per LLM call.

        Returns:
            List of responses aligned with the input prompts.
        """
        results: list[Optional[str]] = [None] * len(prompts)

        for start in range(0, len(prompts), batch_size):
            chunk = prompts[start : start + batch_size]
            if len(chunk) == 1:
                results[start] = await self.generate_text(chunk[0], system_prompt)
                continue

            # Build a batch prompt that asks the LLM to respond to N prompts at once
            numbered = "\n".join(f"[{i + 1}] {p}" for i, p in enumerate(chunk))
            batch_user = (
                f"Respond to each of the following {len(chunk)} items. "
                f"Return your responses as a JSON array of strings, one per item, "
                f'in the same order. Example: ["response 1", "response 2", ...]\n\n'
                f"{numbered}"
            )

            raw = await self.generate_text(batch_user, system_prompt)
            if raw:
                try:
                    import json

                    start_idx = raw.find("[")
                    end_idx = raw.rfind("]") + 1
                    parsed = json.loads(raw[start_idx:end_idx])
                    if isinstance(parsed, list) and len(parsed) == len(chunk):
                        for i, val in enumerate(parsed):
                            results[start + i] = str(val) if val is not None else None
                        continue
                except (json.JSONDecodeError, ValueError):
                    pass

            # Fallback: individual calls
            for i, prompt in enumerate(chunk):
                results[start + i] = await self.generate_text(prompt, system_prompt)

        return results
