"""Scraper infrastructure adapters."""

from src.infrastructure.scraping.playwright_adapter import (
    PlaywrightScraperAdapter,
    SalesforceReleaseScraper,
    PlaywrightScrapingAdapter,  # Legacy compatibility wrapper
    CachedScrapingAdapter,  # Legacy compatibility wrapper
)
from src.infrastructure.scraping.cache_adapter import ScraperCacheAdapter
from src.infrastructure.scraping.rate_limiter import AsyncRateLimiter, RateLimitState
from src.infrastructure.scraping.observability import (
    ScraperObservabilityAdapter,
    configure_structlog,
)


# Legacy ScrapingAdapter base class for backwards compatibility with characterization tests
class ScrapingAdapter:
    """Legacy base class for scraping adapters."""

    @property
    def name(self) -> str:
        """Return the adapter name."""
        return "scraping_adapter"

    async def execute(self, url: str) -> str:
        """Execute scraping and return HTML."""
        raise NotImplementedError("Subclasses must implement execute method")


# Legacy aliases
PlaywrightScrapingAdapter = PlaywrightScrapingAdapter
CachedScrapingAdapter = CachedScrapingAdapter

__all__ = [
    # New names
    "PlaywrightScraperAdapter",
    "SalesforceReleaseScraper",
    "ScraperCacheAdapter",
    "AsyncRateLimiter",
    "RateLimitState",
    "ScraperObservabilityAdapter",
    "configure_structlog",
    # Legacy names (for characterization tests)
    "ScrapingAdapter",
    "PlaywrightScrapingAdapter",
    "CachedScrapingAdapter",
]
