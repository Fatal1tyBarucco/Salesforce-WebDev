"""Tests for scraper.py exponential backoff with jitter and null-safety."""

import asyncio
from unittest.mock import AsyncMock, patch

from src.config import RETRY_BASE_DELAY_SECONDS
from src.scraper import SalesforceReleaseScraper, calculate_jittered_delay

# ============================================================
# calculate_jittered_delay tests
# ============================================================


def test_calculate_jittered_delay_returns_float() -> None:
    result = calculate_jittered_delay(2.0, 0)
    assert isinstance(result, float)


def test_calculate_jittered_delay_attempt_0() -> None:
    base = 2.0
    attempt = 0
    with patch("src.scraper.random.uniform", return_value=0.0):
        result = calculate_jittered_delay(base, attempt)
    assert result == base * (2**attempt)  # 2.0


def test_calculate_jittered_delay_attempt_1() -> None:
    base = 2.0
    attempt = 1
    with patch("src.scraper.random.uniform", return_value=0.0):
        result = calculate_jittered_delay(base, attempt)
    assert result == base * (2**attempt)  # 4.0


def test_calculate_jittered_delay_attempt_2() -> None:
    base = 2.0
    attempt = 2
    with patch("src.scraper.random.uniform", return_value=0.0):
        result = calculate_jittered_delay(base, attempt)
    assert result == base * (2**attempt)  # 8.0


def test_calculate_jittered_delay_with_jitter() -> None:
    base = 2.0
    attempt = 1
    with patch("src.scraper.random.uniform", return_value=1.5):
        result = calculate_jittered_delay(base, attempt)
    assert result == 4.0 + 1.5  # 5.5


def test_calculate_jittered_delay_jitter_adds_randomness() -> None:
    """Verify jitter actually varies across calls."""
    base = 2.0
    attempt = 1
    delays = set()
    for _ in range(50):
        delays.add(calculate_jittered_delay(base, attempt))
    # With uniform jitter, we should get many distinct values
    assert len(delays) > 1


def test_calculate_jittered_delay_min_bound() -> None:
    """Delay should always be >= exponential_delay + 0."""
    base = 2.0
    for attempt in range(5):
        with patch("src.scraper.random.uniform", return_value=0.0):
            result = calculate_jittered_delay(base, attempt)
        assert result == base * (2**attempt)


def test_calculate_jittered_delay_max_bound() -> None:
    """Delay should always be <= exponential_delay + base_delay."""
    base = 2.0
    for attempt in range(5):
        with patch("src.scraper.random.uniform", return_value=base):
            result = calculate_jittered_delay(base, attempt)
        assert result == base * (2**attempt) + base


# ============================================================
# fetch_page_raw_text uses jittered backoff
# ============================================================


def test_fetch_page_raw_text_uses_jittered_delay() -> None:
    """Verify fetch_page_raw_text calls calculate_jittered_delay instead of ** operator."""
    import hashlib

    from src.scraper import CACHE_DIR

    scraper = SalesforceReleaseScraper()
    url = f"https://example.com/jitter_test_{id(scraper)}"
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{url_hash}.txt"
    if cache_file.exists():
        cache_file.unlink()

    with patch.object(scraper, "_fetch_with_playwright", new_callable=AsyncMock) as mock:
        with patch.object(scraper, "_ensure_browser", new_callable=AsyncMock, return_value=True):
            with patch("src.scraper.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                mock.return_value = "x" * 10  # below MIN_RAW_TEXT_LENGTH
                asyncio.run(scraper.fetch_page_raw_text(url))
    mock_sleep.assert_called()
    delay_arg = mock_sleep.call_args[0][0]
    assert delay_arg >= RETRY_BASE_DELAY_SECONDS * 2
    if cache_file.exists():
        cache_file.unlink()


# ============================================================
# Null-safety: _expand_toc_nodes and _extract_toc_from_page
# ============================================================


def test_expand_toc_nodes_handles_none_nodes() -> None:
    """_expand_toc_nodes should handle query_selector_all returning empty list."""
    scraper = SalesforceReleaseScraper()
    mock_page = AsyncMock()
    mock_page.query_selector_all = AsyncMock(return_value=[])

    # Should not raise
    asyncio.run(scraper._expand_toc_nodes(mock_page))
    mock_page.query_selector_all.assert_called_once()


def test_expand_toc_nodes_click_exception() -> None:
    """_expand_toc_nodes should silently handle click exceptions."""
    scraper = SalesforceReleaseScraper()
    mock_page = AsyncMock()
    mock_node = AsyncMock()
    mock_node.click = AsyncMock(side_effect=Exception("stale element"))
    mock_page.query_selector_all = AsyncMock(return_value=[mock_node])

    # Should not raise
    asyncio.run(scraper._expand_toc_nodes(mock_page))


def test_extract_toc_from_page_no_selector_found() -> None:
    """_extract_toc_from_page returns full page HTML when no ToC selector matches."""
    scraper = SalesforceReleaseScraper()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=None)
    mock_page.content = AsyncMock(return_value="<html>full page</html>")

    with patch.object(scraper, "_expand_toc_nodes", new_callable=AsyncMock):
        result = asyncio.run(scraper._extract_toc_from_page("https://example.com", mock_page))
    assert result == "<html>full page</html>"


def test_extract_toc_from_page_selector_too_small() -> None:
    """_extract_toc_from_page falls back when ToC HTML is too small."""
    from src.scraper import MIN_TOC_HTML_SIZE

    scraper = SalesforceReleaseScraper()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    mock_element = AsyncMock()
    mock_element.inner_html = AsyncMock(return_value="x" * (MIN_TOC_HTML_SIZE - 1))

    # First selector returns small HTML, rest return None
    call_count = 0

    async def fake_query_selector(sel: str) -> object:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_element
        return None

    mock_page.query_selector = fake_query_selector
    mock_page.content = AsyncMock(return_value="<html>full page</html>")

    with patch.object(scraper, "_expand_toc_nodes", new_callable=AsyncMock):
        result = asyncio.run(scraper._extract_toc_from_page("https://example.com", mock_page))
    assert result == "<html>full page</html>"


def test_extract_toc_from_page_success() -> None:
    """_extract_toc_from_page returns ToC HTML when selector matches with enough content."""
    from src.scraper import MIN_TOC_HTML_SIZE

    scraper = SalesforceReleaseScraper()
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()

    toc_html = "x" * (MIN_TOC_HTML_SIZE + 1)
    mock_element = AsyncMock()
    mock_element.inner_html = AsyncMock(return_value=toc_html)
    mock_page.query_selector = AsyncMock(return_value=mock_element)

    with patch.object(scraper, "_expand_toc_nodes", new_callable=AsyncMock):
        result = asyncio.run(scraper._extract_toc_from_page("https://example.com", mock_page))
    assert result == toc_html
