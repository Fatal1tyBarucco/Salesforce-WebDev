"""LLM Service module with multi-provider fallback chain.

Provider priority:
  1. Google Gemini (primary — user has Google AI Plus subscription)
  2. OpenCode (secondary — free tier)
  3. OpenRouter free models (tertiary — free tier fallback)

OpenAI support has been removed (no credits allocated).
"""

import logging
import os
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

# Free models on OpenRouter that work without credits
_OPENROUTER_FREE_MODELS = [
    "google/gemma-3-1b-it:free",
    "meta-llama/llama-4-scout:free",
    "deepseek/deepseek-r1-0528:free",
]


@dataclass
class _ProviderConfig:
    """Internal provider configuration."""

    name: str
    api_key_env: str
    base_url: str = ""
    default_model: str = ""
    fallback_models: list[str] = field(default_factory=list)


# Ordered by priority (first = preferred)
_PROVIDER_CHAIN: list[_ProviderConfig] = [
    _ProviderConfig(
        name="gemini",
        api_key_env="GOOGLE_API_KEY",
        default_model="gemini-3.6-flash",
    ),
    _ProviderConfig(
        name="opencode",
        api_key_env="OPENCODE_API_KEY",
        base_url="https://opencode-ai.serper.dev/v1",
        default_model="google/gemini-3.6-flash",
    ),
    _ProviderConfig(
        name="openrouter",
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        default_model="google/gemma-3-1b-it:free",
        fallback_models=_OPENROUTER_FREE_MODELS,
    ),
]


class LLMService:
    """Service class for handling interactions with Large Language Models.

    Supports multiple providers with automatic fallback:
      1. Google Gemini (primary)
      2. OpenCode (secondary)
      3. OpenRouter free models (tertiary)
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
            return self._dispatch_to_provider(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as err:
            logger.error(
                "Provider=%s failed: %s. Attempting fallback...",
                self.provider,
                err,
            )
            if self._switch_to_next_provider():
                return self._dispatch_to_provider(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            raise

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
        elif self.provider in ("opencode", "openrouter"):
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
        if genai is None:
            raise ImportError("google.genai package not available")

        client = genai.Client(api_key=self.api_key)
        full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt

        response = client.models.generate_content(
            model=self.model_name,
            contents=full_prompt,
        )

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
        )
        messages: list[dict[str, Any]] = []

        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})

        messages.append({"role": "user", "content": prompt})

        # Try primary model, then fallback models
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
                logger.warning("Model %s failed: %s", model, err)
                last_error = err
                continue

        raise last_error or RuntimeError("All models failed")

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
