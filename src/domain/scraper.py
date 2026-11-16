"""Domain models and ports for Salesforce scraper."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ScraperErrorCode(str, Enum):
    """Standardized error codes for scraper failures."""

    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    SELECTOR_NOT_FOUND = "selector_not_found"
    INSUFFICIENT_CONTENT = "insufficient_content"
    RATE_LIMITED = "rate_limited"
    CIRCUIT_OPEN = "circuit_open"
    BROWSER_CRASH = "browser_crash"
    LAYOUT_CHANGED = "layout_changed"
    PDF_DOWNLOAD_FAILED = "pdf_download_failed"


class ScraperError(Exception):
    """Base exception for scraper errors with structured context."""

    def __init__(
        self,
        message: str,
        code: ScraperErrorCode = ScraperErrorCode.NETWORK_ERROR,
        url: str = "",
        selector: str = "",
        attempt: int = 0,
        retryable: bool = True,
        original_error: Exception | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.url = url
        self.selector = selector
        self.attempt = attempt
        self.retryable = retryable
        self.original_error = original_error


@dataclass(frozen=True)
class ScraperConfig:
    """Configuration for scraper behavior."""

    # Timeouts
    navigation_timeout_seconds: int = 30
    selector_timeout_seconds: int = 15
    content_wait_seconds: float = 5.0
    scroll_wait_seconds: float = 1.0
    toc_expand_wait_seconds: float = 0.3

    # Retry policy
    max_retry_attempts: int = 3
    base_retry_delay_seconds: float = 2.0
    max_retry_delay_seconds: float = 60.0
    retry_jitter: bool = True

    # Content validation
    min_valid_content_size: int = 1000
    min_toc_html_size: int = 100
    min_raw_text_length: int = 500

    # Rate limiting
    rate_limit_rps: float = 2.0
    rate_limit_burst: int = 5

    # Circuit breaker
    circuit_breaker_threshold: int = 3
    circuit_breaker_cooldown_seconds: int = 60

    # Browser
    headless: bool = True
    browser_args: tuple[str, ...] = ("--no-sandbox", "--disable-dev-shm-usage")

    # Cache
    cache_ttl_seconds: int = 7 * 24 * 3600  # 7 days
    cache_dir: Path = Path("cache")


@dataclass(frozen=True)
class SelectorContract:
    """Contract for CSS selectors with validation."""

    name: str
    selectors: tuple[str, ...]
    min_matches: int = 1
    required: bool = True
    description: str = ""

    def validate(self, html: str) -> tuple[bool, str | None]:
        """Validate that at least one selector matches in HTML."""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        for selector in self.selectors:
            matches = soup.select(selector)
            if len(matches) >= self.min_matches:
                return True, None
        return False, f"No selector matched for {self.name}: {self.selectors}"


# Default selector contracts for Salesforce Help
DEFAULT_SELECTOR_CONTRACTS: tuple[SelectorContract, ...] = (
    SelectorContract(
        name="content",
        selectors=(
            "article",
            "#articleViewContent",
            ".release-notes-content",
            "div.content",
            ".slds-card__body",
            "main",
        ),
        required=True,
        description="Main content area of release notes page",
    ),
    SelectorContract(
        name="toc",
        selectors=(".toc-container", "ul.tree", '[role="tree"]', "nav.toc"),
        required=True,
        description="Table of contents navigation tree",
    ),
    SelectorContract(
        name="feature_impact_table",
        selectors=("table", "[role=table]", ".feature-impact-table"),
        required=False,
        description="Feature impact table with links",
    ),
    SelectorContract(
        name="pdf_button",
        selectors=("button[title='Open PDF']", "button:has-text('PDF')", "[aria-label*='PDF']"),
        required=False,
        description="PDF download button",
    ),
)


@dataclass
class ScrapedContent:
    """Result of a successful scrape operation."""

    url: str
    html: str
    text: str
    toc_html: str | None = None
    features_with_links: list[dict[str, str]] = field(default_factory=list)
    pdf_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""

    def validate(self) -> tuple[bool, list[str]]:
        """Validate scraped content meets minimum requirements."""
        errors = []
        if len(self.html) < 1000:
            errors.append(f"HTML too small: {len(self.html)} bytes")
        if len(self.text) < 500:
            errors.append(f"Text too small: {len(self.text)} chars")
        return len(errors) == 0, errors


@dataclass
class ScraperMetrics:
    """Metrics collected during scraping."""

    url: str
    attempt: int
    success: bool
    latency_ms: int
    content_size: int
    error_code: ScraperErrorCode | None = None
    selector_used: str | None = None
    cache_hit: bool = False
    circuit_breaker_state: str = "closed"
    correlation_id: str = ""


class ScraperPort(ABC):
    """Abstract port for scraping operations."""

    @abstractmethod
    async def fetch_html(self, url: str, *, expand_toc: bool = True) -> str | None:
        """Fetch fully rendered HTML from URL."""
        ...

    @abstractmethod
    async def fetch_text(self, url: str) -> str | None:
        """Fetch extracted text content from URL."""
        ...

    @abstractmethod
    async def fetch_toc(self, url: str) -> str | None:
        """Fetch table of contents HTML from URL."""
        ...

    @abstractmethod
    async def fetch_features_with_links(self, url: str) -> list[dict[str, str]]:
        """Fetch feature names and their documentation links."""
        ...

    @abstractmethod
    async def download_pdf(self, page_url: str, dest: Path) -> bool:
        """Download PDF from page (via button click or direct URL)."""
        ...

    @abstractmethod
    async def fetch_multiple(self, urls: list[str], max_concurrent: int = 5) -> list[str | None]:
        """Fetch multiple URLs concurrently."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if scraper is functional."""
        ...


class ScraperCachePort(ABC):
    """Abstract port for scraper caching."""

    @abstractmethod
    async def get(self, url: str) -> str | None:
        """Get cached content by URL."""
        ...

    @abstractmethod
    async def set(self, url: str, content: str, ttl_seconds: int | None = None) -> None:
        """Cache content with TTL."""
        ...

    @abstractmethod
    async def invalidate(self, url: str) -> None:
        """Invalidate cache for URL."""
        ...


class ScraperObservabilityPort(ABC):
    """Abstract port for scraper observability."""

    @abstractmethod
    def log_scrape_attempt(self, metrics: ScraperMetrics) -> None:
        """Log a scrape attempt with full metrics."""
        ...

    @abstractmethod
    def log_layout_change(self, url: str, failed_selectors: list[str], correlation_id: str) -> None:
        """Log detected layout change."""
        ...

    @abstractmethod
    def record_metrics(self, metrics: ScraperMetrics) -> None:
        """Record metrics for observability."""
        ...
