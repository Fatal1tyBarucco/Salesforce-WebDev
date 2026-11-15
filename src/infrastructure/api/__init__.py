"""API infrastructure — GraphQL and REST routes."""

from __future__ import annotations

from typing import Any

from .routes import app_router, create_rest_router

__all__ = [
    "app_router",
    "create_rest_router",
    "graphql_router",
]


def __getattr__(name: str) -> Any:
    """Expose ``graphql_router`` lazily (PEP 562).

    Importing the package must not require the optional ``strawberry-graphql``
    dependency — only accessing ``graphql_router`` does.
    """
    if name == "graphql_router":
        from .graphql import graphql_router

        return graphql_router
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")