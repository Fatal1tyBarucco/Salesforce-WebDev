"""Tests for src/scraper.py — coverage for non-browser paths."""

import asyncio
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.scraper import (
    CircuitBreaker,
    RateLimiter,
    calculate_jittered_delay,
    is_rate_limited_response,
)


class TestIsRateLimitedResponse:
    def test_429(self) -> None:
        assert is_rate_limited_response(429) is True

    def test_200(self) -> None:
        assert is_rate_limited_response(200) is False

    def test_none(self) -> None:
        assert is_rate_limited_response(None) is False

    def test_string_code(self) -> None:
        assert is_rate_limited_response("429") is True


class TestCalculateJitteredDelay:
    def test_first_attempt(self) -> None:
        delay = calculate_jittered_delay(1.0, 1)
        assert 1.0 <= delay <= 3.0  # base + jitter

    def test_exponential_growth(self) -> None:
        d1 = calculate_jittered_delay(1.0, 1)
        d3 = calculate_jittered_delay(1.0, 3)
        assert d3 > d1


class TestCircuitBreaker:
    def test_initially_closed(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=10)
        assert cb.is_open is False

    def test_trips_after_threshold(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=10)
        for _ in range(3):
            cb.record_failure()
        assert cb.is_open is True

    def test_resets_after_cooldown(self) -> None:
        cb = CircuitBreaker(threshold=2, cooldown=0)
        cb.record_failure()
        cb.record_failure()
        time.sleep(0.01)
        assert cb.is_open is False

    def test_success_resets(self) -> None:
        cb = CircuitBreaker(threshold=3, cooldown=10)
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        assert cb.failure_count == 0

    def test_failure_count(self) -> None:
        cb = CircuitBreaker(threshold=5, cooldown=10)
        assert cb.failure_count == 0
        cb.record_failure()
        assert cb.failure_count == 1

    def test_cooldown_timer_reset(self) -> None:
        """When cooldown expired, timer resets on next failure."""
        cb = CircuitBreaker(threshold=2, cooldown=0)
        cb.record_failure()
        cb.record_failure()
        # Cooldown expired (0s)
        time.sleep(0.01)
        cb.record_failure()  # Should reset timer
        assert cb.failure_count == 3


class TestRateLimiter:
    def test_acquire(self) -> None:
        rl = RateLimiter(min_interval=0)
        asyncio.run(rl.acquire())
        # Should not block

    def test_acquire_respects_interval(self) -> None:
        rl = RateLimiter(min_interval=0.01)
        asyncio.run(rl.acquire())
        start = time.monotonic()
        asyncio.run(rl.acquire())
        elapsed = time.monotonic() - start
        assert elapsed >= 0.01


class TestScraperAsyncMethods:
    """Tests for scraper async methods with mocked browser."""

    def test_fetch_page_raw_text_circuit_breaker_open(self) -> None:
        """fetch_page_raw_text returns None when circuit breaker is open."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = MagicMock()
        scraper._circuit_breaker.is_open = True

        result = asyncio.run(scraper.fetch_page_raw_text("http://test.com"))
        assert result is None

    def test_fetch_page_raw_text_cached(self) -> None:
        """fetch_page_raw_text returns cached content."""
        from src.scraper import SalesforceReleaseScraper, MIN_RAW_TEXT_LENGTH

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = "x" * (MIN_RAW_TEXT_LENGTH + 100)
        scraper._circuit_breaker = MagicMock()
        scraper._circuit_breaker.is_open = False

        result = asyncio.run(scraper.fetch_page_raw_text("http://test.com"))
        assert result == "x" * (MIN_RAW_TEXT_LENGTH + 100)

    def test_ensure_browser_no_playwright(self) -> None:
        """_ensure_browser returns False when no playwright."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = None
        scraper._playwright = None

        result = asyncio.run(scraper._ensure_browser())
        assert result is False

    def test_ensure_browser_already_connected(self) -> None:
        """_ensure_browser returns True when browser already connected."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = MagicMock()
        scraper._browser.is_connected.return_value = True

        result = asyncio.run(scraper._ensure_browser())
        assert result is True

    def test_download_pdf_success(self, tmp_path: Path) -> None:
        """download_pdf downloads file successfully."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        dest = tmp_path / "test.pdf"

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"x" * 2000  # > MIN_VALID_CONTENT_SIZE

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = asyncio.run(scraper.download_pdf("http://test.com/file.pdf", dest))
            assert result is True

    def test_download_pdf_too_small(self, tmp_path: Path) -> None:
        """download_pdf returns False when file too small."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        dest = tmp_path / "small.pdf"

        mock_resp = MagicMock()
        mock_resp.read.return_value = b"tiny"

        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = asyncio.run(scraper.download_pdf("http://test.com/file.pdf", dest))
            assert result is False

    def test_download_pdf_error(self, tmp_path: Path) -> None:
        """download_pdf returns False on error."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        dest = tmp_path / "err.pdf"

        with patch("urllib.request.urlopen", side_effect=TimeoutError("timeout")):
            result = asyncio.run(scraper.download_pdf("http://test.com/file.pdf", dest))
            assert result is False

    def test_download_pdf_from_button_existing_file(self, tmp_path: Path) -> None:
        """download_pdf_from_button skips if file already exists."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        dest = tmp_path / "existing.pdf"
        dest.write_bytes(b"x" * 2000)

        result = asyncio.run(scraper.download_pdf_from_button("http://test.com", dest))
        assert result is True
