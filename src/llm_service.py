"""LLM Service module with multi-provider fallback chain.

Provider priority:
  1. OpenCode (primary — free tier)
  2. OpenRouter free models (secondary — free tier)
  3. Google Gemini (last resort — protects the free tier 20 req/day quota)

Each provider loops through its models before moving to the next provider.
Groq is also supported via explicit provider="groq" (free tier retired
2026-08-16, paid opt-in only).
"""

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Self

from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import google.genai as _genai_module

    genai = _genai_module
except ImportError:  # pragma: no cover
    genai = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

LLM_CALL_TIMEOUT_S = int(os.environ.get("LLM_CALL_TIMEOUT_S") or 60)


@dataclass
class _ProviderConfig:
    """Internal provider configuration."""

    name: str
    api_key_env: str
    base_url: str = ""
    default_model: str = ""
    fallback_models: list[str] = field(default_factory=list)


# Ordered by priority (first = preferred).
# Gemini is LAST: free tier caps at ~20 req/day, so we protect that quota
# and only fall back to it after exhausting OpenCode/OpenRouter pools.
_PROVIDER_CHAIN: list[_ProviderConfig] = [
    _ProviderConfig(
        name="opencode",
        api_key_env="OPENCODE_API_KEY",
        base_url="https://opencode.ai/zen/v1",
        default_model="gemini-3.6-flash",
        fallback_models=[
            "deepseek-v4-flash-free",
            "mimo-v2.5-free",
            "hy3-free",
            "nemotron-3-ultra-free",
            "laguna-s-2.1-free",
        ],
    ),
    _ProviderConfig(
        name="openrouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        default_model="openrouter/auto",
        fallback_models=[
            "google/gemma-4-31b-it:free",
            "meta-llama/llama-4-scout:free",
            "qwen/qwen-3-coder:free",
            "mistralai/mistral-nemo:free",
            "deepseek/deepseek-chat-v3:free",
            "anthropic/claude-3-haiku:free",
        ],
    ),
    _ProviderConfig(
        name="gemini",
        api_key_env="GOOGLE_API_KEY",
        default_model="gemini-3.6-flash",
    ),
    _ProviderConfig(
        # Groq: free tier retired 2026-08-16. Kept here so users with paid
        # credentials can opt in via provider="groq". Excluded from auto-detect
        # below via _find_provider_config fallback handling.
        name="groq",
        api_key_env="GROQ_API_KEY",
        base_url="https://api.groq.com/openai/v1",
        default_model="llama-3.3-70b-versatile",
        fallback_models=[
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
        ],
    ),
]


class LLMService:
    """Service class for handling interactions with Large Language Models.

    Supports multiple providers with automatic fallback:
      1. OpenCode (primary, free tier)
      2. OpenRouter free models (secondary, free tier)
      3. Google Gemini (tertiary, free tier 20 req/day protected)

    Each provider loops through its models before moving to the next.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        provider: str | None = None,
    ) -> None:
        """Initialize the LLM Service.

        Args:
            api_key: Optional API key override. If None, resolved from env.
            model_name: Model override. If None, uses provider default.
            provider: Provider override. If None, auto-detects from available keys.
        """
        self._provider_chain = list(_PROVIDER_CHAIN)
        self._active_provider: _ProviderConfig | None = None
        self._tried_providers: set[str] = set()

        if provider:
            # Explicit provider requested
            cfg = self._find_provider_config(provider)
            if cfg:
                resolved_key = api_key or os.getenv(cfg.api_key_env, "")
                if resolved_key:
                    self._active_provider = cfg
                    self.api_key = resolved_key
                    self.model_name = model_name or cfg.default_model
                    self.provider = cfg.name
                    return
            # Fallback: try auto-detect below

        # Auto-detect: find first provider with a valid API key
        for cfg in self._provider_chain:
            if cfg.name == "groq":
                continue  # Groq free tier retired 2026-08-16; skip in auto-detect
            resolved_key = api_key or os.getenv(cfg.api_key_env, "")
            if resolved_key:
                self._active_provider = cfg
                self.api_key = resolved_key
                self.model_name = model_name or cfg.default_model
                self.provider = cfg.name
                return

        # No provider available — will return mock responses
        self.api_key = ""
        self.model_name = model_name or "mock"
        self.provider = "none"
        self._active_provider = None
        logger.warning("No LLM API key configured. Service will return mock responses.")

    @staticmethod
    def _find_provider_config(name: str) -> _ProviderConfig | None:
        """Find a provider config by name."""
        name_lower = name.lower()
        for cfg in _PROVIDER_CHAIN:
            if cfg.name == name_lower:
                return cfg
        return None

    def _next_fallback_provider(self) -> _ProviderConfig | None:
        """Get the next untried provider from the chain."""
        for cfg in self._provider_chain:
            if cfg.name not in self._tried_providers:
                key = os.getenv(cfg.api_key_env, "")
                if key:
                    return cfg
        return None

    def _switch_to_next_provider(self) -> bool:
        """Switch to the next available fallback provider. Returns True if switched."""
        self._tried_providers.add(self.provider)
        next_cfg = self._next_fallback_provider()
        if next_cfg:
            self._active_provider = next_cfg
            self.api_key = os.getenv(next_cfg.api_key_env, "")
            self.model_name = next_cfg.default_model
            self.provider = next_cfg.name
            logger.info(
                "Switching to fallback provider=%s, model=%s",
                self.provider,
                self.model_name,
            )
            return True
        return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_completion(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = 1000,
    ) -> str:
        """Generate text completion using the configured LLM provider.

        Automatically falls back to the next provider in the chain on failure.

        Args:
            prompt: The input user prompt.
            system_instruction: Optional system prompt to guide behavior.
            temperature: Sampling temperature for output generation.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated string response from the model.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        if self.provider == "none":
            logger.warning("No LLM provider available, returning mock response.")
            return f"[Mock LLM Response] Prompt: {prompt[:50]}..."

        logger.info(
            "Generating completion using provider=%s, model=%s",
            self.provider,
            self.model_name,
        )

        try:
            result = self._dispatch_to_provider(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            # Success clears the blacklist so transient failures on one call
            # don't permanently skip providers for the rest of a long run.
            self._tried_providers.clear()
            return result
        except Exception as err:
            logger.error(
                "Provider=%s failed: %s. Attempting fallback...",
                self.provider,
                err,
            )
            last_err: Exception = err
            while self._switch_to_next_provider():
                try:
                    return self._dispatch_to_provider(
                        prompt=prompt,
                        system_instruction=system_instruction,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                except Exception as next_err:
                    logger.error(
                        "Fallback provider=%s failed: %s. Continuing chain...",
                        self.provider,
                        next_err,
                    )
                    last_err = next_err
            raise last_err

    def _dispatch_to_provider(
        self,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Dispatch the request to the currently active provider."""
        if self.provider == "gemini":
            return self._generate_gemini(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        elif self.provider in ("groq", "opencode", "openrouter"):
            return self._generate_openai_compatible(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _generate_gemini(
        self,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Generate response via Google Gemini API."""
        import concurrent.futures

        if genai is None:
            raise ImportError("google.genai package not available")

        client = genai.Client(api_key=self.api_key)
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        def _gen() -> Any:
            return client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            future = ex.submit(_gen)
            try:
                response = future.result(timeout=LLM_CALL_TIMEOUT_S)
            except concurrent.futures.TimeoutError:
                future.cancel()
                raise RuntimeError(f"Gemini call timed out after {LLM_CALL_TIMEOUT_S}s")

        return response.text.strip() if response.text else ""

    def _generate_openai_compatible(
        self,
        prompt: str,
        system_instruction: str | None,
        temperature: float,
        max_tokens: int | None,
    ) -> str:
        """Generate response via OpenAI-compatible API (OpenCode, OpenRouter)."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package required for OpenAI-compatible providers")

        assert self._active_provider is not None
        client = OpenAI(
            api_key=self.api_key,
            base_url=self._active_provider.base_url,
            timeout=LLM_CALL_TIMEOUT_S,
            max_retries=0,
        )
        messages: list[dict[str, Any]] = []

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        messages.append({"role": "user", "content": prompt})

        models_to_try = [self.model_name] + self._active_provider.fallback_models
        last_error: Exception | None = None

        for model in models_to_try:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,  # type: ignore[arg-type]
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content
                return content.strip() if content else ""
            except Exception as err:
                err_str = str(err)
                # 403 may mean the model slug exists but isn't accessible via API (e.g.
                # "only available on agentic harnesses") — skip without retry
                is_forbidden = "403" in err_str or "inaccessible" in err_str.lower()
                if is_forbidden:
                    logger.warning("Model %s permanently inaccessible (403), skipping.", model)
                    last_error = err
                    continue
                # 401 from OpenRouter usually means the model slug is no longer
                # available on the free tier ("not supported"). Skip without
                # retry to avoid wasting the next model's quota.
                is_unsupported = "401" in err_str and (
                    "not supported" in err_str.lower() or "modelerror" in err_str.lower()
                )
                if is_unsupported:
                    logger.warning("Model %s unsupported (401), skipping.", model)
                    last_error = err
                    continue
                # 429 = rate limit or quota exceeded — back off and retry up to 3 times
                is_rate_limit = (
                    "429" in err_str
                    or "rate limit" in err_str.lower()
                    or "quota exceeded" in err_str.lower()
                )
                if is_rate_limit:
                    if models_to_try.index(model) < len(models_to_try) - 1:
                        backoff = min(30, 2 ** (3 - models_to_try.index(model)))
                        logger.warning(
                            "Model %s hit rate limit (429), backing off %ds before retry.",
                            model,
                            backoff,
                        )
                        time.sleep(backoff)
                        last_error = err
                        continue
                    else:
                        last_error = err
                        continue
                logger.warning("Model %s failed: %s", model, err)
                last_error = err
                continue

        # All models exhausted — raise so caller switches to the next provider
        if last_error:
            raise last_error
        # Unreachable: every exception path above sets last_error. Kept as defensive
        # fallback in case a future refactoring introduces a non-exception exit.
        raise RuntimeError(f"All models failed for provider {self.provider}")  # pragma: no cover

    async def generate_text(
        self,
        prompt: str,
        system_instruction: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = 1000,
    ) -> str:
        """Alias for generate_completion (async-compatible wrapper)."""
        return self.generate_completion(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def classify_text(
        self,
        text: str,
        categories: list[str] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Alias for generate_completion for classification tasks."""
        prompt = text
        if categories:
            prompt = "Classify into: " + ", ".join(categories) + "\n\n" + text
        return self.generate_completion(
            prompt=prompt,
            system_instruction=system_prompt,
        )

    def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize given text content using LLM.

        Args:
            text: The text content to summarize.
            max_length: Target word/token length for summary.

        Returns:
            Summarized string output.
        """
        system_prompt = (
            f"You are a concise summarizer. Summarize the text in under {max_length} words."
        )
        return self.generate_completion(prompt=text, system_instruction=system_prompt)

    async def summarize_release_notes(self, notes: str, max_length: int = 200) -> str:
        """Summarize release notes content using the LLM."""
        return self.summarize(text=notes, max_length=max_length)

    async def enrich_feature(
        self, feature: dict[str, Any], context: str | None = None
    ) -> dict[str, Any]:
        """Enrich a feature dictionary with additional LLM-derived details."""
        prompt = f"Enrich the following feature:\n{feature}"
        if context:
            prompt += f"\n\nContext:\n{context}"
        details = self.generate_completion(prompt=prompt)
        enriched = dict(feature)
        enriched["details"] = details
        enriched["enriched"] = True
        return enriched

    async def __aenter__(self) -> Self:
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        """Exit async context."""
        return
