"""Type stub for openai package.

The openai package may not be installed in all environments (it is an
optional dependency gated by a runtime ImportError). This stub satisfies
mypy strict mode without requiring the package at typecheck time.

Only the symbols actually used in this project are declared here.
"""

from __future__ import annotations

from typing import Any

class _Message:
    """Minimal stub for a chat message."""

    content: str | None

class _Choice:
    """Minimal stub for a single chat completion choice."""

    message: _Message

class _ChatCompletion:
    """Minimal stub for a chat completion response."""

    choices: list[_Choice]

class _Completions:
    """Minimal stub for openai client.chat.completions namespace.

    In the real openai package this is a lazily-loaded module proxy.
    We model it as a class whose instances expose ``create(...)``.
    """

    def create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float,
        max_tokens: int | None = ...,
        **kwargs: Any,
    ) -> _ChatCompletion: ...

class _Chat:
    """Minimal stub for openai client.chat namespace.

    In the real openai package ``client.chat`` is a proxy object
    (not the class itself). We therefore treat ``completions`` as
    an instance attribute of ``_Chat``, which is what ``client.chat``
    resolves to at runtime.
    """

    completions: _Completions

class OpenAI:
    """Minimal stub for openai.OpenAI client.

    Covers only the surface used in src/llm_service._generate_openai_compatible:
    instantiation with api_key, base_url, timeout, max_retries,
    and the chain ``client.chat.completions.create(...)``.
    """

    def __init__(
        self,
        api_key: str | None = ...,
        base_url: str | None = ...,
        timeout: float | None = ...,
        max_retries: int | None = ...,
        **kwargs: Any,
    ) -> None: ...

    chat: _Chat

# Re-export the symbols that the real openai package exposes at module level.
OpenAI = OpenAI
