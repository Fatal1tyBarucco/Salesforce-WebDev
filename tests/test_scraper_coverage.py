"""Tests for src/scraper.py — coverage for non-browser paths."""

import asyncio
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.circuit_breaker import CircuitBreaker
from src.limiters.rate_limiter import RateLimiter
from src.scraper import (
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
    def test_acquire_positive_interval(self) -> None:
        rl = RateLimiter(min_interval=0.1)
        asyncio.run(rl.acquire())
        # Should not block

    def test_acquire_respects_interval(self) -> None:
        rl = RateLimiter(min_interval=0.05)

        async def run() -> float:
            await rl.acquire()
            start = time.monotonic()
            await rl.acquire()
            return time.monotonic() - start

        elapsed = asyncio.run(run())
        assert elapsed >= 0.05


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
        from src.scraper import MIN_RAW_TEXT_LENGTH, SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = "x" * (MIN_RAW_TEXT_LENGTH + 100)
        scraper._circuit_breaker = MagicMock()
        scraper._circuit_breaker.is_open = False

        result = asyncio.run(scraper.fetch_page_raw_text("http://test.com"))
        assert result == "x" * (MIN_RAW_TEXT_LENGTH + 100)

    def test_ensure_browser_no_playwright(self) -> None:
        """_ensure_browser returns False when playwright fails to start."""
        from unittest.mock import patch

        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = None
        scraper._playwright = None

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.start.side_effect = OSError("playwright not available")
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


class TestCircuitBreakerIntegration:
    """Circuit breaker open paths in scraper methods."""

    def test_fetch_page_circuit_breaker_open(self) -> None:
        """fetch_page returns None when circuit breaker is open."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = CircuitBreaker(threshold=1, cooldown=60)
        scraper._circuit_breaker.record_failure()  # Trip the circuit

        result = asyncio.run(scraper.fetch_page("https://example.com"))
        assert result is None

    def test_fetch_features_with_links_circuit_breaker_open(self) -> None:
        """fetch_features_with_links returns [] when circuit breaker is open."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._circuit_breaker = CircuitBreaker(threshold=1, cooldown=60)
        scraper._circuit_breaker.record_failure()  # Trip the circuit

        result = asyncio.run(scraper.fetch_features_with_links("https://example.com"))
        assert result == []


class TestRateLimiterEdgeCases:
    """Edge cases for RateLimiter."""

    def test_invalid_min_interval_raises(self) -> None:
        """RateLimiter rejects non-positive min_interval."""
        with pytest.raises(ValueError, match="must be positive"):
            RateLimiter(min_interval=0)

    def test_negative_min_interval_raises(self) -> None:
        """RateLimiter rejects negative min_interval."""
        with pytest.raises(ValueError, match="must be positive"):
            RateLimiter(min_interval=-1.0)


class TestFetchPageRawTextResilience:
    """Test fetch_page_raw_text retry/loop paths through the circuit breaker."""

    def test_success_records_success_and_caches(self) -> None:
        """Successful fetch caches content and resets failure counter."""
        from src.scraper import MIN_RAW_TEXT_LENGTH, SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = CircuitBreaker(threshold=3, cooldown=60)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._ensure_browser = AsyncMock(return_value=True)
        scraper._fetch_with_playwright = AsyncMock(return_value="x" * (MIN_RAW_TEXT_LENGTH + 100))

        content = "x" * (MIN_RAW_TEXT_LENGTH + 100)
        result = asyncio.run(scraper.fetch_page_raw_text("https://example.com"))
        assert result == content
        scraper._cache.set.assert_called_once()
        assert scraper._circuit_breaker.failure_count == 0

    def test_browser_unavailable_all_attempts_fail(self) -> None:
        """All retries exhausted when browser cannot be recovered."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = CircuitBreaker(threshold=3, cooldown=60)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._ensure_browser = AsyncMock(return_value=False)

        result = asyncio.run(scraper.fetch_page_raw_text("https://example.com"))
        assert result is None
        assert scraper._circuit_breaker.failure_count == 0  # No failures recorded (browser issue)

    def test_exception_records_failure(self) -> None:
        """Exception during fetch records a circuit breaker failure."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = CircuitBreaker(threshold=3, cooldown=60)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._ensure_browser = AsyncMock(return_value=True)
        scraper._fetch_with_playwright = AsyncMock(side_effect=TimeoutError("timeout"))

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = asyncio.run(scraper.fetch_page_raw_text("https://example.com"))
        assert result is None
        assert scraper._circuit_breaker.failure_count > 0


class TestFetchFeaturesWithLinksResilience:
    """Test fetch_features_with_links retry paths."""

    def test_success_returns_features(self) -> None:
        """Successful extraction returns features and records success."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = CircuitBreaker(threshold=3, cooldown=60)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._ensure_browser = AsyncMock(return_value=True)
        # HTML with a <tr> containing a feature name — matches Strategy 1
        html = "<html><body><table><tr><td>TestFeature</td></tr></table></body></html>"
        scraper._fetch_with_playwright = AsyncMock(return_value=html)

        result = asyncio.run(scraper.fetch_features_with_links("https://example.com"))
        assert len(result) == 1
        assert result[0]["name"] == "TestFeature"
        assert scraper._circuit_breaker.failure_count == 0

    def test_empty_html_retries_and_fails(self) -> None:
        """No features found in empty HTML exhausts retries and returns []."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._circuit_breaker = CircuitBreaker(threshold=3, cooldown=60)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._ensure_browser = AsyncMock(return_value=True)
        scraper._fetch_with_playwright = AsyncMock(return_value="<html><body></body></html>")

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = asyncio.run(scraper.fetch_features_with_links("https://example.com"))
        assert result == []


class TestScraperCleanupAndConcurrency:
    """Test __aexit__ cleanup and fetch_multiple_raw_text paths."""

    def test_aexit_closes_browser_and_playwright(self) -> None:
        """__aexit__ closes browser and stops playwright when both exist."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = MagicMock()
        scraper._browser.close = AsyncMock()
        scraper._playwright = MagicMock()
        scraper._playwright.stop = AsyncMock()

        asyncio.run(scraper.__aexit__(None, None, None))
        scraper._browser.close.assert_called_once()
        scraper._playwright.stop.assert_called_once()

    def test_aexit_none_browser_and_playwright(self) -> None:
        """__aexit__ handles None browser and playwright gracefully."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = None
        scraper._playwright = None

        asyncio.run(scraper.__aexit__(None, None, None))  # Should not raise

    def test_fetch_multiple_raw_text(self) -> None:
        """fetch_multiple_raw_text concurrently fetches from multiple URLs."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._circuit_breaker = CircuitBreaker(threshold=3, cooldown=60)
        scraper._cache = MagicMock()
        scraper._cache.get.return_value = None
        scraper._ensure_browser = AsyncMock(return_value=False)

        with patch("asyncio.sleep", new_callable=AsyncMock):
            results = asyncio.run(
                scraper.fetch_multiple_raw_text(
                    ["https://a.com", "https://b.com"], max_concurrent=2
                )
            )
        assert len(results) == 2
        assert results[0] is None  # Browser unavailable → None


class TestEnsureBrowserInitialStartup:
    """Test _ensure_browser initial startup path (playwright starts fresh)."""

    def test_initial_startup_starts_playwright(self) -> None:
        """_ensure_browser starts playwright when _playwright is None and _browser is None."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = None
        scraper._playwright = None

        mock_browser = MagicMock()
        mock_browser.is_connected.return_value = True
        mock_pw = MagicMock()
        mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_pw.stop = AsyncMock()

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_pw)
            result = asyncio.run(scraper._ensure_browser())
        assert result is True
        assert scraper._playwright is mock_pw
        assert scraper._browser is mock_browser


class TestExecFetch:
    """Test _exec_fetch method paths."""

    def test_exec_fetch_returns_body_text(self) -> None:
        """_exec_fetch with return_text=True returns body inner text."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._rate_limiter = RateLimiter(min_interval=0.01)
        scraper._expand_toc_nodes = AsyncMock()

        page = MagicMock()
        page.goto = AsyncMock()
        page.wait_for_selector = AsyncMock()
        page.evaluate = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        page.inner_text = AsyncMock(return_value="Body text content")

        result = asyncio.run(scraper._exec_fetch("https://example.com", page, return_text=True))
        assert result == "Body text content"


class TestDownloadPdfButton:
    """Test download_pdf_from_button paths."""

    def test_button_not_found_with_browser(self) -> None:
        """Existing browser, PDF button not found → returns False, closes context only."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = MagicMock()
        scraper._playwright = MagicMock()

        mock_context = MagicMock()
        mock_context.new_page = AsyncMock(return_value=MagicMock())
        mock_context.close = AsyncMock()
        scraper._browser.new_context = AsyncMock(return_value=mock_context)

        mock_page = mock_context.new_page.return_value
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=TimeoutError("no button"))

        dest = Path("/tmp/test_pdf_browser.pdf")

        result = asyncio.run(scraper.download_pdf_from_button("https://example.com", dest))
        assert result is False
        mock_context.close.assert_awaited_once()

    def test_button_not_found_no_browser(self) -> None:
        """No browser, PDF button not found → returns False, closes browser + playwright."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = None
        scraper._playwright = None

        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_context = MagicMock()
        mock_context.new_page = AsyncMock(return_value=MagicMock())
        mock_context.close = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)

        mock_page = mock_context.new_page.return_value
        mock_page.goto = AsyncMock()
        mock_page.wait_for_selector = AsyncMock(side_effect=TimeoutError("no button"))

        mock_pw = MagicMock()
        mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_pw.stop = AsyncMock()

        dest = Path("/tmp/test_pdf_no_browser.pdf")

        with patch("src.scraper.async_playwright") as mock_ap:
            mock_ap.return_value.start = AsyncMock(return_value=mock_pw)
            result = asyncio.run(scraper.download_pdf_from_button("https://example.com", dest))
        assert result is False
        mock_context.close.assert_awaited_once()
        mock_browser.close.assert_awaited_once()
        mock_pw.stop.assert_awaited_once()


class TestEnsureBrowserRelaunch:
    """Test _ensure_browser relaunch path."""

    def test_relaunch_when_browser_crashed(self) -> None:
        """Relaunch browser when existing one is disconnected."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = MagicMock()
        scraper._browser.is_connected.return_value = False
        scraper._playwright = MagicMock()
        scraper._playwright.chromium.launch = AsyncMock(return_value=MagicMock())

        result = asyncio.run(scraper._ensure_browser())
        assert result is True

    def test_relaunch_failure_returns_false(self) -> None:
        """Returns False when browser relaunch fails."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = None
        scraper._playwright = MagicMock()
        scraper._playwright.chromium.launch = AsyncMock(side_effect=OSError("launch failed"))

        result = asyncio.run(scraper._ensure_browser())
        assert result is False


class TestExtractFeaturesFromHtmlEdgeCases:
    """Edge cases for _is_allowed_salesforce_href and Strategy 3."""

    def test_no_hostname_skipped(self) -> None:
        """Links with http:// but no host are rejected by _is_allowed_salesforce_href."""
        from src.scraper import SalesforceReleaseScraper

        # "http://" has scheme http but hostname None
        html = """
        <table>
            <tr>
                <td>Bare HTTP Feature</td>
                <td><a href="http://">Docs</a></td>
            </tr>
        </table>
        """
        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert len(features) == 1
        assert features[0]["docs_url"] == ""  # _is_allowed_salesforce_href returned False

    def test_strategy3_short_name_skipped(self) -> None:
        """Strategy 3: anchors with release-notes but short name are skipped."""
        from src.scraper import SalesforceReleaseScraper

        html = '<a href="https://help.salesforce.com/release-notes.test.htm">AB</a>'
        features = SalesforceReleaseScraper._extract_features_from_html(html)
        assert features == []


class TestDownloadPdfButtonException:
    """download_pdf_from_button outer exception handler."""

    def test_exception_returns_false(self) -> None:
        """download_pdf_from_button catches exception and returns False."""
        from src.scraper import SalesforceReleaseScraper

        scraper = SalesforceReleaseScraper.__new__(SalesforceReleaseScraper)
        scraper._browser = MagicMock()
        scraper._playwright = MagicMock()

        mock_context = MagicMock()
        mock_context.new_page = AsyncMock(return_value=MagicMock())
        mock_context.close = AsyncMock()
        scraper._browser.new_context = AsyncMock(return_value=mock_context)

        mock_page = mock_context.new_page.return_value
        mock_page.goto = AsyncMock(side_effect=OSError("network error"))

        dest = Path("/tmp/test_pdf_exc.pdf")

        result = asyncio.run(scraper.download_pdf_from_button("https://example.com", dest))
        assert result is False
