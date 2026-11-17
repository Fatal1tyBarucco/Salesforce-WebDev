"""Scraper infrastructure adapters."""

from src.infrastructure.scraping.cache_adapter import ScraperCacheAdapter
from src.infrastructure.scraping.observability import (
    ScraperObservabilityAdapter,
    configure_structlog,
)
from src.infrastructure.scraping.playwright_adapter import (
    CachedScrapingAdapter,  # Legacy compatibility wrapper
    PlaywrightScraperAdapter,
    PlaywrightScrapingAdapter,  # Legacy compatibility wrapper
    SalesforceReleaseScraper,
)
from src.infrastructure.scraping.rate_limiter import AsyncRateLimiter, RateLimitState


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


__all__ = [
    "AsyncRateLimiter",
    "CachedScrapingAdapter",
    "PlaywrightScraperAdapter",
    "PlaywrightScrapingAdapter",
    "RateLimitState",
    "SalesforceReleaseScraper",
    "ScraperCacheAdapter",
    "ScraperObservabilityAdapter",
    "ScrapingAdapter",
    "configure_structlog",
]
