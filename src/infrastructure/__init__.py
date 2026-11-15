"""Infrastructure layer — adapters for external systems.

This layer implements the domain interfaces (adapters) using concrete
technologies: Playwright, BeautifulSoup, OpenAI/Google GenAI, GitHub API, etc.
"""

from __future__ import annotations

from src.core.classification.service import ClassificationAdapter
from src.core.enrichment.service import EnrichmentAdapter

from .api.routes import (
    create_rest_router,
)
from .github import (
    GitHubOperationsAdapter,
)
from .llm import (
    GeminiLLMAdapter,
    HeuristicClassificationAdapter,
    OpenRouterClassificationAdapter,
    OpenRouterEnrichmentAdapter,
    OpenRouterLLMAdapter,
)
from .messaging import (
    NotificationAdapter,
)
from .parsing import (
    BeautifulSoupParsingAdapter,
    ParsingAdapter,
)
from .scraping import (
    PlaywrightScrapingAdapter,
    ScrapingAdapter,
)
from .storage import (
    FileSystemStorageAdapter,
    StorageAdapter,
)

__all__ = [
    "BeautifulSoupParsingAdapter",
    # LLM
    "ClassificationAdapter",
    "EnrichmentAdapter",
    "FileSystemStorageAdapter",
    "GeminiLLMAdapter",
    # GitHub
    "GitHubOperationsAdapter",
    "HeuristicClassificationAdapter",
    # Messaging
    "NotificationAdapter",
    "OpenRouterClassificationAdapter",
    "OpenRouterEnrichmentAdapter",
    "OpenRouterLLMAdapter",
    # Parsing
    "ParsingAdapter",
    "PlaywrightScrapingAdapter",
    # Scraping
    "ScrapingAdapter",
    # Storage
    "StorageAdapter",
    # API
    "create_rest_router",
]
