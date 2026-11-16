"""Unified LLM client implementing LLMPort with multi-provider fallback."""

from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Any

import structlog
from pydantic import BaseModel

from src.domain.llm import (
    DEFAULT_PROVIDER_CHAIN,
    LLMAuthError,
    LLMError,
    LLMModel,
    LLMModelUnavailableError,
    LLMPort,
    LLMPrompt,
    LLMProvider,
    LLMRateLimitError,
    LLMResponse,
    LLMUsage,
    ProviderConfig,
)
from src.infrastructure.llm_adapters.cache import LLMCacheAdapter
from src.infrastructure.llm_adapters.observability import LLMObservabilityAdapter
from src.infrastructure.llm_adapters.rate_limiter import AdaptiveRateLimiter

logger = structlog.get_logger(__name__)


def _env_model_override(cfg: ProviderConfig) -> str:
    """Resolve model for provider from env override."""
    override = os.getenv(f"{cfg.name.name.upper()}_MODEL", "").strip()
    return override or cfg.default_model.value


def _parse_usage_from_openai(response: Any, provider: LLMProvider, model: str) -> LLMUsage:
    """Parse usage from OpenAI-compatible response."""
    usage = getattr(response, "usage", None)
    if usage:
        prompt_tokens = getattr(usage, "prompt_tokens", 0)
        completion_tokens = getattr(usage, "completion_tokens", 0)
        total = prompt_tokens + completion_tokens
        cost = 0.0
        if "gpt-4" in model.lower() or "claude" in model.lower():
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
        elif "gpt-3.5" in model.lower():
            cost = (prompt_tokens * 0.0015 + completion_tokens * 0.002) / 1000
        return LLMUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            estimated_cost_usd=cost,
            provider=provider.value,
            model=model,
        )
    return LLMUsage(provider=provider.value, model=model)


def _parse_usage_from_gemini(response: Any, model: str) -> LLMUsage:
    """Parse usage from Gemini response."""
    usage = getattr(response, "usage_metadata", None)
    if usage:
        prompt_tokens = getattr(usage, "prompt_token_count", 0)
        completion_tokens = getattr(usage, "candidates_token_count", 0)
        total = prompt_tokens + completion_tokens
        return LLMUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total,
            estimated_cost_usd=0.0,
            provider=LLMProvider.GEMINI.value,
            model=model,
        )
    return LLMUsage(provider=LLMProvider.GEMINI.value, model=model)


class UnifiedLLMClient(LLMPort):
    """Unified LLM client with multi-provider fallback chain."""

    def __init__(
        self,
        provider_chain: tuple[ProviderConfig, ...] = DEFAULT_PROVIDER_CHAIN,
        cache: LLMCacheAdapter | None = None,
        rate_limiter: AdaptiveRateLimiter | None = None,
        observability: LLMObservabilityAdapter | None = None,
        default_timeout: int = 60,
    ) -> None:
        self._provider_chain = list(provider_chain)
        self._cache = cache or LLMCacheAdapter()
        self._rate_limiter = rate_limiter or AdaptiveRateLimiter()
        self._observability = observability or LLMObservabilityAdapter()
        self._default_timeout = default_timeout

        # Provider state
        self._active_provider: ProviderConfig | None = None
        self._tried_providers: set[LLMProvider] = set()
        self._clients: dict[LLMProvider, Any] = {}

        # Usage tracking
        self._total_usage = LLMUsage()
        self._call_count = 0

        # Auto-detect first available provider
        self._auto_detect_provider()

    def _auto_detect_provider(self) -> None:
        """Auto-detect first provider with valid API key."""
        for cfg in self._provider_chain:
            key = os.getenv(cfg.api_key_env, "")
            if key:
                self._active_provider = cfg
                logger.info("Auto-detected provider: %s", cfg.name.value)
                return

        logger.warning("No LLM API key configured. Service will return mock responses.")
        self._active_provider = None

    def _get_client(self, provider: LLMProvider) -> Any:
        """Get or create client for provider."""
        if provider in self._clients:
            return self._clients[provider]

        if not self._active_provider:
            return None

        cfg = self._active_provider
        key = os.getenv(cfg.api_key_env, "")

        if not key:
            return None

        if provider in (LLMProvider.OPENROUTER, LLMProvider.OPENCODE):
            from openai import OpenAI

            client: Any = OpenAI(
                api_key=key,
                base_url=cfg.base_url,
                timeout=cfg.timeout_seconds,
                max_retries=0,
            )
        elif provider == LLMProvider.GEMINI:
            try:
                from google import genai

                client = genai.Client(api_key=key)
            except ImportError:
                logger.warning("google.genai not available")
                return None
        else:
            return None

        self._clients[provider] = client
        return client

    def _next_fallback_provider(self) -> ProviderConfig | None:
        """Get next untried provider from chain."""
        for cfg in self._provider_chain:
            if cfg.name not in self._tried_providers:
                key = os.getenv(cfg.api_key_env, "")
                if key:
                    return cfg
        return None

    def _switch_to_next_provider(self) -> bool:
        """Switch to next available fallback provider."""
        if not self._active_provider:
            return False

        self._tried_providers.add(
            (self._active_provider.name if self._active_provider else LLMProvider.OPENROUTER)
            if self._active_provider
            else LLMProvider.OPENROUTER
        )
        next_cfg = self._next_fallback_provider()

        if next_cfg:
            self._active_provider = next_cfg
            logger.info("Switching to fallback provider: %s", next_cfg.name.value)
            return True
        return False

    def _reset_provider_chain(self) -> None:
        """Reset tried providers on success."""
        self._tried_providers.clear()

    async def generate(self, prompt: LLMPrompt) -> LLMResponse:
        """Generate completion for prompt with fallback chain."""
        correlation_id = uuid.uuid4().hex[:12]
        start_time = time.perf_counter()

        # Check cache first
        cache_key = prompt.cache_key()
        cached = await self._cache.get(cache_key)
        if cached:
            logger.info("cache_hit", correlation_id=correlation_id, key=cache_key)
            cached.cached = True
            self._observability.log_llm_call(
                cached.provider, cached.model, prompt, cached, correlation_id
            )
            return cached

        if not self._active_provider:
            # Return mock response
            return LLMResponse(
                content=f"[Mock] {prompt.user[:50]}...",
                usage=LLMUsage(provider="mock", model="mock"),
                provider=LLMProvider.OPENROUTER,
                model="mock",
            )

        # Acquire rate limit permission
        await self._rate_limiter.acquire(
            (self._active_provider.name if self._active_provider else LLMProvider.OPENROUTER)
            if self._active_provider
            else LLMProvider.OPENROUTER
        )

        try:
            response = await self._dispatch_with_fallback(prompt, correlation_id)
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Cache successful response
            await self._cache.set(prompt.cache_key(), response)

            # Record metrics
            self._total_usage = self._total_usage.add(response.usage)
            self._call_count += 1
            await self._rate_limiter.record_success(
                (self._active_provider.name if self._active_provider else LLMProvider.OPENROUTER)
                if self._active_provider
                else LLMProvider.OPENROUTER
            )
            self._reset_provider_chain()

            self._observability.record_metrics(
                provider=(
                    (
                        self._active_provider.name
                        if self._active_provider
                        else LLMProvider.OPENROUTER
                    )
                    if self._active_provider
                    else LLMProvider.OPENROUTER
                ).value,
                model=response.model,
                latency_ms=latency_ms,
                tokens=response.usage.total_tokens,
                cost=response.usage.estimated_cost_usd,
                success=True,
            )

            return response

        except LLMError as e:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            await self._rate_limiter.record_failure(
                (
                    (
                        self._active_provider.name
                        if self._active_provider
                        else LLMProvider.OPENROUTER
                    )
                    if self._active_provider
                    else LLMProvider.OPENROUTER
                ),
                e,
            )
            self._observability.record_metrics(
                provider=(
                    (
                        self._active_provider.name
                        if self._active_provider
                        else LLMProvider.OPENROUTER
                    )
                    if self._active_provider
                    else LLMProvider.OPENROUTER
                ).value,
                model=(
                    (
                        self._active_provider.default_model
                        if self._active_provider
                        else LLMModel.OPENROUTER_FREE
                    )
                    if self._active_provider
                    else LLMModel.OPENROUTER_FREE
                ).value,
                latency_ms=latency_ms,
                tokens=0,
                cost=0.0,
                success=False,
            )
            raise

    async def _dispatch_with_fallback(self, prompt: LLMPrompt, correlation_id: str) -> LLMResponse:
        """Dispatch to active provider with fallback chain."""
        while True:
            if not self._active_provider:
                raise LLMError("No provider available", retryable=False)

            provider = (
                (self._active_provider.name if self._active_provider else LLMProvider.OPENROUTER)
                if self._active_provider
                else LLMProvider.OPENROUTER
            )
            client = self._get_client(provider)

            if not client:
                logger.warning("No client for provider %s, trying fallback", provider.value)
                if not self._switch_to_next_provider():
                    raise LLMError("All providers exhausted", retryable=False)
                continue

            try:
                response = await self._call_provider(client, prompt)

                usage = self._parse_usage(
                    response,
                    provider,
                    (
                        (
                            self._active_provider.default_model
                            if self._active_provider
                            else LLMModel.OPENROUTER_FREE
                        )
                        if self._active_provider
                        else LLMModel.OPENROUTER_FREE
                    ).value,
                )

                return LLMResponse(
                    content=response.content if hasattr(response, "content") else str(response),
                    usage=usage,
                    provider=provider,
                    model=(
                        (
                            self._active_provider.default_model
                            if self._active_provider
                            else LLMModel.OPENROUTER_FREE
                        )
                        if self._active_provider
                        else LLMModel.OPENROUTER_FREE
                    ).value,
                )

            except (LLMRateLimitError, LLMAuthError, LLMModelUnavailableError) as e:
                logger.warning("Provider %s error: %s", provider.value, e)
                if not self._switch_to_next_provider():
                    raise e
                continue

            except Exception as e:
                logger.error("Provider %s unexpected error: %s", provider.value, e)
                if not self._switch_to_next_provider():
                    raise LLMError(str(e), provider=provider.value, retryable=True)
                continue

    async def _call_provider(self, client: Any, prompt: LLMPrompt) -> Any:
        """Call specific provider client."""
        provider = (
            (self._active_provider.name if self._active_provider else LLMProvider.OPENROUTER)
            if self._active_provider
            else LLMProvider.OPENROUTER
        )

        if provider in (LLMProvider.OPENROUTER, LLMProvider.OPENCODE):
            return await self._call_openai_compatible(client, prompt)
        elif provider == LLMProvider.GEMINI:
            return await self._call_gemini(client, prompt)
        else:
            raise LLMError(
                f"Unsupported provider: {provider}", provider=provider.value, retryable=False
            )

    async def _call_openai_compatible(self, client: Any, prompt: LLMPrompt) -> Any:
        """Call OpenAI-compatible API."""
        messages = []
        if prompt.system:
            messages.append({"role": "system", "content": prompt.system})
        messages.append({"role": "user", "content": prompt.user})

        kwargs = {
            "model": (
                (
                    (
                        _env_model_override(self._active_provider)
                        if self._active_provider
                        else LLMModel.OPENROUTER_FREE.value
                    )
                    if self._active_provider
                    else LLMModel.OPENROUTER_FREE.value
                )
                if self._active_provider
                else LLMModel.OPENROUTER_FREE.value
            ),
            "messages": messages,
            "temperature": prompt.temperature,
        }
        if prompt.max_tokens:
            kwargs["max_tokens"] = prompt.max_tokens
        if prompt.response_format:
            kwargs["response_format"] = prompt.response_format

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: client.chat.completions.create(**kwargs))

    async def _call_gemini(self, client: Any, prompt: LLMPrompt) -> Any:
        """Call Google Gemini API."""
        full_prompt = f"{prompt.system}\n\n{prompt.user}" if prompt.system else prompt.user

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=(
                    (
                        (
                            _env_model_override(self._active_provider)
                            if self._active_provider
                            else LLMModel.OPENROUTER_FREE.value
                        )
                        if self._active_provider
                        else LLMModel.OPENROUTER_FREE.value
                    )
                    if self._active_provider
                    else LLMModel.GEMINI_36_FLASH_DIRECT.value
                ),
                contents=full_prompt,
            ),
        )

    def _parse_usage(self, response: Any, provider: LLMProvider, model: str) -> LLMUsage:
        """Parse usage from provider response."""
        if provider in (LLMProvider.OPENROUTER, LLMProvider.OPENCODE):
            return _parse_usage_from_openai(response, provider, model)
        elif provider == LLMProvider.GEMINI:
            return _parse_usage_from_gemini(response, model)
        return LLMUsage(provider=provider.value, model=model)

    async def generate_structured(self, prompt: LLMPrompt, schema: type[BaseModel]) -> BaseModel:
        """Generate structured response validated against schema."""
        schema_prompt = LLMPrompt(
            system=prompt.system
            + "\n\nRespond ONLY with valid JSON matching this schema:\n"
            + json.dumps(schema.model_json_schema()),
            user=prompt.user,
            temperature=0.1,
            max_tokens=prompt.max_tokens,
            response_format={"type": "json_object"},
        )

        response = await self.generate(schema_prompt)

        try:
            data = json.loads(response.content)
            return schema.model_validate(data)
        except (json.JSONDecodeError, Exception) as e:
            logger.error("Failed to parse structured response: %s", e)
            raise LLMError(f"Invalid structured response: {e}", retryable=False)

    def get_usage_stats(self) -> dict[str, Any]:
        """Get aggregated usage statistics."""
        return {
            "total_calls": self._call_count,
            "total_tokens": self._total_usage.total_tokens,
            "total_cost_usd": self._total_usage.estimated_cost_usd,
            "prompt_tokens": self._total_usage.prompt_tokens,
            "completion_tokens": self._total_usage.completion_tokens,
            "active_provider": (
                (
                    (
                        self._active_provider.name
                        if self._active_provider
                        else LLMProvider.OPENROUTER
                    )
                    if self._active_provider
                    else LLMProvider.OPENROUTER
                ).value
                if self._active_provider
                else "none"
            ),
            "rate_limits": {
                p.name.value: self._rate_limiter.get_state(p.name) for p in self._provider_chain
            },
        }

    async def health_check(self) -> bool:
        """Check if LLM service is available."""
        if not self._active_provider:
            return False

        try:
            test_prompt = LLMPrompt(user="Health check", max_tokens=10)
            response = await self.generate(test_prompt)
            return len(response.content) > 0
        except Exception:
            return False


# Backwards compatibility
class LLMService:
    """Legacy LLMService wrapper for backwards compatibility."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._client = UnifiedLLMClient(*args, **kwargs)

    def generate_completion(self, prompt: str, **kwargs: Any) -> str:
        import asyncio

        return asyncio.run(self._client.generate(LLMPrompt(user=prompt, **kwargs))).content

    async def generate_text(self, prompt: str, **kwargs: Any) -> str:
        return (await self._client.generate(LLMPrompt(user=prompt, **kwargs))).content

    async def classify_text(self, text: str, **kwargs: Any) -> str:
        return await self.generate_text(f"Classify: {text}", **kwargs)

    def summarize(self, text: str, max_length: int = 200) -> str:
        import asyncio

        return asyncio.run(
            self._client.generate(
                LLMPrompt(user=f"Summarize in {max_length} words:\n{text}", max_tokens=max_length)
            )
        ).content
