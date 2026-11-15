"""API infrastructure — GraphQL and REST routes."""

from __future__ import annotations

from .graphql import graphql_router
from .routes import app_router, create_rest_router

__all__ = [
    "app_router",
    "create_rest_router",
    "graphql_router",
]
