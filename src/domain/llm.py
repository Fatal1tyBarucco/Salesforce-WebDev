"""Domain models and ports for LLM services.

This module defines the core abstractions (ports) for LLM operations,
independent of any specific provider implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENROUTER = "XXXXopenrouterXXXX"
    OPENCODE = "opencode"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    OLLAMA = "ollama"


class LLMModel(str, Enum):
    """Known model identifiers."""

    # OpenRouter free
    OPENROUTER_FREE = "openrouter/free"
    GEMMA_4_31B = "google/gemma-4-31b-it:free"
    LLAMA_4_SCOUT = "XXmeta-llama/llama-4-scout:freeXX"
    QWEN_3_CODER = "qwen/qwen-3-coder:free"
    MISTRAL_NEMO = "mistralai/mistral-nemo:free"
    DEEPSEEK_CHAT_V3 = "deepseek/deepseek-chat-v3:free"
    CLAUDE_3_HAIKU = "anthropic/claude-3-haiku:free"

    # OpenCode
    GEMINI_36_FLASH = "gemini-3.6-flash"
    LING_3_FLASH = "ling-3.0-flash-free"
    LING_3_TINY = "ling-3.0-tiny-free"
    NEMOTRON_3_ULTRA = "nemotron-3-ultra-free"

    # Gemini direct
    GEMINI_36_FLASH_DIRECT = "gemini-3.6-flash"

    # Anthropic
    CLAUDE_3_HAIKU_ANTHROPIC = "claude-3-haiku-20240307"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"

    # Mistral
    MISTRAL_NEMO_DIRECT = "mistral-nemo"

    # Ollama (local)
    LLAMA_3_1_8B = "llama3.1:8b"
    MISTRAL_7B = "mistral:7b"


@dataclass(frozen=True)
class ProviderConfig:
    """Configuration for a single LLM provider."""

    name: LLMProvider
    api_key_env: str
    base_url: str = ""
    default_model: LLMModel = LLMModel.OPENROUTER_FREE
    fallback_models: tuple[LLMModel, ...] = ()
    timeout_seconds: int = 60
    max_retries: int = 3
    rate_limit_rps: float = 10.0


# Default provider chain (ordered by priority)
DEFAULT_PROVIDER_CHAIN: tuple[ProviderConfig, ...] = (
    ProviderConfig(
        name=LLMProvider.OPENROUTER,
        api_key_env="OPENROUTER_API_KEY",
        base_url="https://openrouter.ai/api/v1",
        default_model=LLMModel.OPENROUTER_FREE,
        fallback_models=(
            LLMModel.GEMMA_4_31B,
            LLMModel.LLAMA_4_SCOUT,
            LLMModel.QWEN_3_CODER,
            LLMModel.MISTRAL_NEMO,
            LLMModel.DEEPSEEK_CHAT_V3,
            LLMModel.CLAUDE_3_HAIKU,
        ),
        rate_limit_rps=20.0,
    ),
    ProviderConfig(
        name=LLMProvider.OPENCODE,
        api_key_env="OPENCODE_API_KEY",
        base_url="https://opencode.ai/zen/v1",
        default_model=LLMModel.GEMINI_36_FLASH,
        fallback_models=(
            LLMModel.LING_3_FLASH,
            LLMModel.LING_3_TINY,
            LLMModel.NEMOTRON_3_ULTRA,
        ),
        rate_limit_rps=10.0,
    ),
    ProviderConfig(
        name=LLMProvider.GEMINI,
        api_key_env="GOOGLE_API_KEY",
        default_model=LLMModel.GEMINI_36_FLASH_DIRECT,
        rate_limit_rps=2.0,  # Free tier: ~20 req/day
    ),
)


class LLMUsage(BaseModel):
    """Token usage and cost tracking for an LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    provider: str = ""
    model: str = ""

    def add(self, other: LLMUsage) -> LLMUsage:
        """Combine two usage records."""
        return LLMUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            estimated_cost_usd=self.estimated_cost_usd + other.estimated_cost_usd,
            provider=self.provider or other.provider,
            model=self.model or other.model,
        )


class LLMResponse(BaseModel):
    """Structured response from an LLM call.

    Mutable Pydantic model (``cached`` is updated by the client on cache hits)
    and JSON-serializable, which the cache adapters rely on.
    """

    content: str
    usage: LLMUsage
    provider: LLMProvider
    model: str
    finish_reason: str = "stop"
    cached: bool = False
    correlation_id: str = ""


class LLMPrompt(BaseModel):
    """Structured prompt with metadata for caching and evaluation."""

    system: str = ""
    user: str
    temperature: float = 0.7
    max_tokens: int | None = 1000
    response_format: dict[str, Any] | None = None
    metadata: dict[str, str] = Field(default_factory=dict)

    def cache_key(self) -> str:
        """Generate deterministic cache key for this prompt."""
        import hashlib
        import json

        data = {
            "system": self.system,
            "user": self.user,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "response_format": self.response_format,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


class LLMError(Exception):
    """Base exception for LLM errors."""

    def __init__(
        self,
        message: str,
        provider: LLMProvider | str = "",
        model: str = "",
        status_code: int | None = None,
        retryable: bool = True,
    ):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.status_code = status_code
        self.retryable = retryable


class LLMRateLimitError(LLMError):
    """Rate limit / quota exceeded error."""

    def __init__(
        self,
        message: str,
        provider: LLMProvider | str = "",
        model: str = "",
        retry_after: int | None = None,
    ):
        super().__init__(message, provider, model, status_code=429, retryable=True)
        self.retry_after = retry_after


class LLMAuthError(LLMError):
    """Authentication / authorization error."""

    def __init__(self, message: str, provider: LLMProvider | str = "", model: str = ""):
        super().__init__(message, provider, model, status_code=401, retryable=False)


class LLMModelUnavailableError(LLMError):
    """Model not available / unsupported error."""

    def __init__(self, message: str, provider: LLMProvider | str = "", model: str = ""):
        super().__init__(message, provider, model, status_code=403, retryable=False)


class LLMPort(ABC):
    """Abstract port for LLM operations (provider-agnostic)."""

    @abstractmethod
    async def generate(self, prompt: LLMPrompt) -> LLMResponse:
        """Generate a completion for the given prompt."""
        ...

    @abstractmethod
    async def generate_structured(self, prompt: LLMPrompt, schema: type[BaseModel]) -> BaseModel:
        """Generate a structured response validated against a Pydantic schema."""
        ...

    @abstractmethod
    def get_usage_stats(self) -> dict[str, Any]:
        """Get aggregated usage statistics."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the LLM service is available."""
        ...


class LLMCachePort(ABC):
    """Abstract port for semantic/exact LLM response caching."""

    @abstractmethod
    async def get(self, key: str) -> LLMResponse | None:
        """Get cached response by key."""
        ...

    @abstractmethod
    async def set(self, key: str, response: LLMResponse, ttl_seconds: int = 3600) -> None:
        """Cache a response with TTL."""
        ...

    @abstractmethod
    async def get_semantic(self, prompt: LLMPrompt, threshold: float = 0.95) -> LLMResponse | None:
        """Get semantically similar cached response (embedding-based)."""
        ...

    @abstractmethod
    async def set_semantic(self, prompt: LLMPrompt, response: LLMResponse) -> None:
        """Cache response with semantic embedding."""
        ...


class LLMRateLimiterPort(ABC):
    """Abstract port for adaptive rate limiting."""

    @abstractmethod
    async def acquire(self, provider: LLMProvider, tokens: int = 1) -> None:
        """Acquire permission to make a request."""
        ...

    @abstractmethod
    async def record_success(self, provider: LLMProvider) -> None:
        """Record successful request (may increase limits)."""
        ...

    @abstractmethod
    async def record_failure(self, provider: LLMProvider, error: LLMError) -> None:
        """Record failed request (may decrease limits)."""
        ...

    @abstractmethod
    def get_current_limit(self, provider: LLMProvider) -> float:
        """Get current effective rate limit (RPS)."""
        ...


class LLMObservabilityPort(ABC):
    """Abstract port for structured logging and metrics."""

    @abstractmethod
    def log_llm_call(
        self,
        provider: LLMProvider,
        model: str,
        prompt: LLMPrompt,
        response: LLMResponse,
        correlation_id: str,
    ) -> None:
        """Log an LLM call with full context."""
        ...

    @abstractmethod
    def log_fallback(
        self,
        from_provider: LLMProvider,
        to_provider: LLMProvider,
        error: LLMError,
        correlation_id: str,
    ) -> None:
        """Log a fallback event."""
        ...

    @abstractmethod
    def record_metrics(
        self,
        provider: LLMProvider,
        model: str,
        latency_ms: int,
        tokens: int,
        cost: float,
        success: bool,
    ) -> None:
        """Record metrics for observability."""
        ...
