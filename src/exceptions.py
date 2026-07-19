"""Custom exception hierarchy for the release notes pipeline.

Usage::

    from src.exceptions import PipelineError, ScraperError

    try:
        await scraper.fetch_page(url)
    except ScraperError as e:
        logger.error("Scraping failed: %s", e)
    except PipelineError as e:
        logger.error("Pipeline error: %s", e)
"""


class PipelineError(Exception):
    """Base exception for all pipeline errors."""


class ScraperError(PipelineError):
    """Error during web scraping or page fetching."""


class BrowserError(ScraperError):
    """Browser launch or connection error."""


class RateLimitError(ScraperError):
    """Rate limit exceeded by target site."""


class ParserError(PipelineError):
    """Error during content parsing."""


class LLMError(PipelineError):
    """Error during LLM API call."""


class LLMProviderExhausted(LLMError):
    """All LLM providers failed or circuit breaker tripped."""


class ConfigError(PipelineError):
    """Configuration or environment error."""


class ExportError(PipelineError):
    """Error during data export (JSON/CSV)."""


class NotificationError(PipelineError):
    """Error during notification delivery."""


class GitHubError(PipelineError):
    """Error during GitHub API interaction."""
