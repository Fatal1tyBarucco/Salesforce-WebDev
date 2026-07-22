"""Type stubs for google.genai (Google Generative AI SDK).

Covers the subset used in this project:
  - Client (sync + async model access)
"""

from __future__ import annotations

from typing import Any

from . import types as types

class _AsyncModels:
    """Async interface for model operations."""
    async def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: Any = ...,
    ) -> GenerateContentResponse: ...

class _Models:
    """Sync interface for model operations."""
    def generate_content(
        self,
        *,
        model: str,
        contents: str,
        config: Any = ...,
    ) -> GenerateContentResponse: ...

class Client:
    """Google Generative AI client."""
    def __init__(self, *, api_key: str = ...) -> None: ...
    @property
    def aio(self) -> _AsyncAioClient: ...
    @property
    def models(self) -> _Models: ...

class _AsyncAioClient:
    """Async sub-client accessed via client.aio."""
    @property
    def models(self) -> _AsyncModels: ...

class GenerateContentResponse:
    """Response from generate_content."""
    @property
    def text(self) -> str: ...
