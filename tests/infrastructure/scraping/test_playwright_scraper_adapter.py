"""Tests for PlaywrightScraperAdapter.

Every test runs fully offline: the browser, the page, the cache, the rate
limiter and the observability adapter are replaced by test doubles, so no
network access and no real Chromium instance are involved.

The tests describe the *real* contract of
``src.infrastructure.scraping.playwright_adapter``:

* ``_ensure_browser`` starts Playwright through ``async_playwright().start()``
  and returns ``False`` when the launch fails;
* ``_exec_fetch`` navigates, waits for the content, optionally expands the
  TOC and returns either the HTML or the body text;
* ``fetch_html`` serves the cache first, opens the circuit breaker when it
  is tripped, retries up to ``max_retry_attempts`` and records metrics;
* ``download_pdf`` prefers the "Open PDF" button and falls back to a direct
  download of the linked ``.pdf`` file.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from playwright._impl._errors import Error as PlaywrightError
from playwright._impl._errors import TimeoutError as PlaywrightTimeout

from src.domain.scraper import (
    DEFAULT_SELECTOR_CONTRACTS,
    ScraperCachePort,
    ScraperConfig,
    ScraperError,
    ScraperErrorCode,
    ScraperObservabilityPort,
    SelectorContract,
)
from src.infrastructure.scraping.cache_adapter import ScraperCacheAdapter
from src.infrastructure.scraping.playwright_adapter import (
    PlaywrightScraperAdapter,
    SalesforceReleaseScraper,
    calculate_jittered_delay,
)

BIG_HTML = "<html><body>" + ("release notes content " * 100) + "</body></html>"
BIG_TEXT = "release notes text " * 100


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


def _make_page() -> MagicMock:
    """Build a page double with the async API used by the adapter."""
    page = MagicMock()
    page.goto = AsyncMock()
    page.content = AsyncMock(return_value="<html><body>full page</body></html>")
    page.inner_text = AsyncMock(return_value="body text")
    page.query_selector = AsyncMock(return_value=None)
    page.query_selector_all = AsyncMock(return_value=[])
    page.wait_for_selector = AsyncMock()
    page.wait_for_timeout = AsyncMock()
    page.evaluate = AsyncMock()
    page.click = AsyncMock()
    page.close = AsyncMock()
    return page


def _make_browser(page: MagicMock | None = None) -> MagicMock:
    """Build a browser double returning ``page`` for every new context."""
    browser = MagicMock()
    browser.is_connected = MagicMock(return_value=True)
    browser.close = AsyncMock()

    context = MagicMock()
    context.new_page = AsyncMock(return_value=page if page is not None else _make_page())
    context.close = AsyncMock()

    browser.new_context = AsyncMock(return_value=context)
    browser.new_page = AsyncMock(return_value=page if page is not None else _make_page())
    return browser


class _FakeDownload:
    """Stand-in for playwright's Download object."""

    def __init__(self, payload: bytes) -> None:
        self.payload = payload
        self.saved_to: list[str] = []

    async def save_as(self, path: str) -> None:
        """Write the fake payload to disk, like playwright does."""
        self.saved_to.append(path)
        Path(path).write_bytes(self.payload)


class _FakeDownloadInfo:
    """Stand-in for playwright's DownloadInfo (awaitable ``value``)."""

    def __init__(self, download: _FakeDownload) -> None:
        self._download = download

    @property
    def value(self):
        """Return the awaitable resolving to the download."""
        download = self._download

        async def _resolve() -> _FakeDownload:
            return download

        return _resolve()


class _FakeExpectDownload:
    """Stand-in for the async context manager returned by expect_download."""

    def __init__(self, info: _FakeDownloadInfo) -> None:
        self._info = info

    async def __aenter__(self) -> _FakeDownloadInfo:
        return self._info

    async def __aexit__(self, *exc_info: object) -> None:
        return None


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def config(tmp_path) -> ScraperConfig:
    """Create a fast, offline test configuration."""
    return ScraperConfig(
        headless=True,
        navigation_timeout_seconds=5,
        selector_timeout_seconds=2,
        content_wait_seconds=0.0,
        scroll_wait_seconds=0.0,
        toc_expand_wait_seconds=0.0,
        max_retry_attempts=2,
        base_retry_delay_seconds=0.1,
        max_retry_delay_seconds=1.0,
        min_valid_content_size=1000,
        min_toc_html_size=100,
        min_raw_text_length=500,
        cache_ttl_seconds=60,
        cache_dir=tmp_path / "cache",
    )


@pytest.fixture
def cache() -> AsyncMock:
    """Cache port double (miss by default)."""
    mock = AsyncMock(spec=ScraperCachePort)
    mock.get.return_value = None
    return mock


@pytest.fixture
def rate_limiter() -> AsyncMock:
    """Rate limiter double."""
    return AsyncMock()


@pytest.fixture
def observability() -> MagicMock:
    """Observability port double."""
    return MagicMock(spec=ScraperObservabilityPort)


@pytest.fixture
def adapter(config, cache, rate_limiter, observability) -> PlaywrightScraperAdapter:
    """Create the adapter with every collaborator injected."""
    return PlaywrightScraperAdapter(
        config=config,
        cache=cache,
        rate_limiter=rate_limiter,
        observability=observability,
    )


@pytest.fixture
def browser(adapter) -> MagicMock:
    """Attach a browser double to the adapter."""
    page = _make_page()
    mock_browser = _make_browser(page)
    adapter._browser = mock_browser
    return mock_browser


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCalculateJitteredDelay:
    """Tests for calculate_jittered_delay function."""

    def test_base_case(self):
        """Should calculate base delay correctly."""
        delay = calculate_jittered_delay(2.0, 0)
        assert 2.0 <= delay <= 4.0  # base + jitter (0-2)

    def test_exponential_backoff(self):
        """Should increase exponentially with attempts."""
        delay1 = calculate_jittered_delay(2.0, 0)
        delay2 = calculate_jittered_delay(2.0, 1)
        delay3 = calculate_jittered_delay(2.0, 2)

        assert delay2 > delay1
        assert delay3 > delay2

    def test_max_delay_cap(self):
        """Should cap at max_delay."""
        delay = calculate_jittered_delay(100.0, 5, max_delay=60.0)
        assert delay <= 60.0

    def test_returns_float(self):
        """Should return float."""
        delay = calculate_jittered_delay(2.0, 0)
        assert isinstance(delay, float)


class TestPlaywrightScraperAdapterConstruction:
    """Tests for the adapter construction."""

    def test_init_uses_the_injected_collaborators(self, adapter, config, cache, rate_limiter):
        """Should keep every injected collaborator."""
        assert adapter.config == config
        assert adapter.cache is cache
        assert adapter.rate_limiter is rate_limiter
        assert adapter.selector_contracts == DEFAULT_SELECTOR_CONTRACTS
        assert adapter._browser is None
        assert adapter._playwright is None

    def test_init_builds_default_collaborators(self, tmp_path):
        """Without injection the adapter builds its own collaborators."""
        adapter = PlaywrightScraperAdapter(
            config=ScraperConfig(cache_dir=tmp_path / "default-cache")
        )

        assert isinstance(adapter.cache, ScraperCacheAdapter)
        assert adapter.rate_limiter is not None
        assert adapter.observability is not None

    def test_init_accepts_custom_selector_contracts(self, config, cache, rate_limiter):
        """Should keep the given selector contracts."""
        contracts = (SelectorContract(name="content", selectors=("article",)),)

        adapter = PlaywrightScraperAdapter(
            config=config,
            selector_contracts=contracts,
            cache=cache,
            rate_limiter=rate_limiter,
        )

        assert adapter.selector_contracts == contracts

    def test_circuit_breaker_uses_the_configured_threshold(self, adapter):
        """Should build the circuit breaker from the configuration."""
        assert adapter._circuit_breaker.is_open is False


class TestPlaywrightScraperAdapterBrowserLifecycle:
    """Tests for the browser lifecycle."""

    @pytest.mark.asyncio
    async def test_ensure_browser_launches(self, adapter):
        """Should start playwright and launch chromium."""
        mock_browser = MagicMock()
        mock_browser.is_connected.return_value = True
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_context = MagicMock()
        mock_context.start = AsyncMock(return_value=mock_playwright)

        with patch(
            "src.infrastructure.scraping.playwright_adapter.async_playwright",
            return_value=mock_context,
        ):
            result = await adapter._ensure_browser()

        assert result is True
        assert adapter._browser is mock_browser
        assert adapter._playwright is mock_playwright
        mock_playwright.chromium.launch.assert_called_once_with(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @pytest.mark.asyncio
    async def test_ensure_browser_reuses_a_connected_browser(self, adapter):
        """Should not launch twice when the browser is already connected."""
        mock_browser = MagicMock()
        mock_browser.is_connected.return_value = True
        adapter._browser = mock_browser

        assert await adapter._ensure_browser() is True

    @pytest.mark.asyncio
    async def test_ensure_browser_relaunches_a_disconnected_browser(self, adapter):
        """A disconnected browser must be relaunched without restarting playwright."""
        mock_browser = MagicMock()
        mock_browser.is_connected.return_value = False
        new_browser = MagicMock()
        new_browser.is_connected.return_value = True

        mock_playwright = MagicMock()
        mock_playwright.chromium.launch = AsyncMock(return_value=new_browser)
        mock_context = MagicMock()
        mock_context.start = AsyncMock(return_value=mock_playwright)

        adapter._browser = mock_browser
        adapter._playwright = mock_playwright

        with patch(
            "src.infrastructure.scraping.playwright_adapter.async_playwright",
            return_value=mock_context,
        ):
            result = await adapter._ensure_browser()

        assert result is True
        assert adapter._browser is new_browser
        mock_context.start.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_browser_handles_os_error(self, adapter):
        """Should return False when the launch fails with an OSError."""
        mock_context = MagicMock()
        mock_context.start = AsyncMock(side_effect=OSError("Launch failed"))

        with patch(
            "src.infrastructure.scraping.playwright_adapter.async_playwright",
            return_value=mock_context,
        ):
            result = await adapter._ensure_browser()

        assert result is False

    @pytest.mark.asyncio
    async def test_ensure_browser_handles_playwright_error(self, adapter):
        """Should return False when playwright itself fails."""
        mock_context = MagicMock()
        mock_context.start = AsyncMock(side_effect=PlaywrightError("boom"))

        with patch(
            "src.infrastructure.scraping.playwright_adapter.async_playwright",
            return_value=mock_context,
        ):
            result = await adapter._ensure_browser()

        assert result is False

    @pytest.mark.asyncio
    async def test_close_browser(self, adapter):
        """Should close the browser and stop playwright."""
        mock_browser = MagicMock()
        mock_browser.close = AsyncMock()
        mock_playwright = MagicMock()
        mock_playwright.stop = AsyncMock()

        adapter._browser = mock_browser
        adapter._playwright = mock_playwright

        await adapter._close_browser()

        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
        assert adapter._browser is None
        assert adapter._playwright is None

    @pytest.mark.asyncio
    async def test_close_browser_without_browser(self, adapter):
        """Should be a no-op when nothing was launched."""
        await adapter._close_browser()

        assert adapter._browser is None
        assert adapter._playwright is None

    @pytest.mark.asyncio
    async def test_context_manager_opens_and_closes_the_browser(self, adapter):
        """The async context manager must open and close the browser."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)) as ensure,
            patch.object(adapter, "_close_browser", AsyncMock()) as close,
        ):
            async with adapter as scoped:
                assert scoped is adapter

        ensure.assert_called_once()
        close.assert_called_once()

    def test_get_correlation_id(self, adapter):
        """Should generate a unique 12 character correlation ID."""
        cid1 = adapter._get_correlation_id()
        cid2 = adapter._get_correlation_id()

        assert len(cid1) == 12
        assert cid1 != cid2
        assert int(cid1, 16) >= 0


class TestPlaywrightScraperAdapterPageHelpers:
    """Tests for the page helper methods."""

    @pytest.mark.asyncio
    async def test_wait_for_content(self, adapter):
        """Should wait for a selector, scroll down and pause."""
        page = _make_page()

        await adapter._wait_for_content(page, "test-cid")

        page.wait_for_selector.assert_called_once()
        page.evaluate.assert_called_once_with("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout.assert_called_once()

    @pytest.mark.asyncio
    async def test_wait_for_content_survives_a_selector_timeout(self, adapter):
        """A selector timeout must not abort the wait."""
        page = _make_page()
        page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("timeout"))

        await adapter._wait_for_content(page, "test-cid")

        page.evaluate.assert_called_once()
        page.wait_for_timeout.assert_called_once()

    @pytest.mark.asyncio
    async def test_expand_toc_without_collapsed_nodes(self, adapter):
        """Should expand nothing when there is no collapsed node."""
        page = _make_page()

        expanded = await adapter._expand_toc(page, "test-cid")

        assert expanded == 0
        page.query_selector_all.assert_called_once_with(
            'li[role="treeitem"][aria-expanded="false"]'
        )

    @pytest.mark.asyncio
    async def test_expand_toc_expands_visible_nodes(self, adapter):
        """Should expand visible nodes and skip invisible ones."""
        node1 = AsyncMock()
        node1.is_visible = AsyncMock(return_value=True)
        node1.bounding_box = AsyncMock(return_value={"x": 0, "y": 0})
        node1.scroll_into_view_if_needed = AsyncMock()
        node1.click = AsyncMock()

        node2 = AsyncMock()
        node2.is_visible = AsyncMock(return_value=False)

        page = _make_page()
        page.query_selector_all = AsyncMock(return_value=[node1, node2])

        expanded = await adapter._expand_toc(page, "test-cid")

        assert expanded == 1
        node1.scroll_into_view_if_needed.assert_called_once()
        node1.click.assert_called_once()
        node2.click.assert_not_called()

    @pytest.mark.asyncio
    async def test_expand_toc_skips_nodes_without_bounding_box(self, adapter):
        """A node without a bounding box cannot be clicked."""
        node = AsyncMock()
        node.is_visible = AsyncMock(return_value=True)
        node.bounding_box = AsyncMock(return_value=None)
        node.click = AsyncMock()

        page = _make_page()
        page.query_selector_all = AsyncMock(return_value=[node])

        expanded = await adapter._expand_toc(page, "test-cid")

        assert expanded == 0
        node.click.assert_not_called()

    @pytest.mark.asyncio
    async def test_expand_toc_handles_playwright_errors(self, adapter):
        """A playwright failure must not break the expansion."""
        page = _make_page()
        page.query_selector_all = AsyncMock(side_effect=PlaywrightError("boom"))

        assert await adapter._expand_toc(page, "test-cid") == 0

    @pytest.mark.asyncio
    async def test_expand_toc_handles_node_failures(self, adapter):
        """A failing node must be skipped instead of breaking the loop."""
        node = AsyncMock()
        node.is_visible = AsyncMock(return_value=True)
        node.bounding_box = AsyncMock(return_value={"x": 0, "y": 0})
        node.scroll_into_view_if_needed = AsyncMock()
        node.click = AsyncMock(side_effect=PlaywrightError("click failed"))

        page = _make_page()
        page.query_selector_all = AsyncMock(return_value=[node])

        assert await adapter._expand_toc(page, "test-cid") == 0

    @pytest.mark.asyncio
    async def test_find_working_selector_uses_the_cache(self, adapter):
        """Should reuse the selector cached for the contract."""
        page = _make_page()
        element = AsyncMock()
        page.query_selector = AsyncMock(return_value=element)

        contract = SelectorContract(name="test", selectors=("selector1", "selector2"))

        selector = await adapter._find_working_selector(page, contract)
        assert selector == "selector1"

        page.query_selector.reset_mock()
        page.query_selector.return_value = element

        selector = await adapter._find_working_selector(page, contract)
        assert selector == "selector1"
        page.query_selector.assert_called_once_with("selector1")

    @pytest.mark.asyncio
    async def test_find_working_selector_tries_multiple_selectors(self, adapter):
        """Should try every selector of the contract."""
        page = _make_page()
        page.query_selector = AsyncMock(side_effect=[None, AsyncMock()])

        contract = SelectorContract(name="test", selectors=("selector1", "selector2"))

        selector = await adapter._find_working_selector(page, contract)

        assert selector == "selector2"
        assert page.query_selector.call_count == 2

    @pytest.mark.asyncio
    async def test_find_working_selector_returns_none(self, adapter):
        """Should return None when no selector matches."""
        page = _make_page()
        page.query_selector = AsyncMock(return_value=None)

        contract = SelectorContract(name="test", selectors=("selector1", "selector2"))

        assert await adapter._find_working_selector(page, contract) is None

    @pytest.mark.asyncio
    async def test_extract_with_selectors(self, adapter):
        """Should extract the inner HTML of the matched element."""
        page = _make_page()
        element = AsyncMock()
        element.inner_html = AsyncMock(return_value=BIG_HTML)
        page.query_selector = AsyncMock(return_value=element)

        contract = SelectorContract(name="content", selectors=("selector1",))

        with patch.object(adapter, "_find_working_selector", AsyncMock(return_value="selector1")):
            html = await adapter._extract_with_selectors(page, contract)

        assert html == BIG_HTML
        element.inner_html.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_with_selectors_uses_the_toc_threshold(self, adapter):
        """The TOC contract is validated against min_toc_html_size."""
        page = _make_page()
        element = AsyncMock()
        element.inner_html = AsyncMock(return_value="<ul class='tree'>" + ("x" * 120) + "</ul>")
        page.query_selector = AsyncMock(return_value=element)

        contract = SelectorContract(name="toc", selectors=("selector1",))

        with patch.object(adapter, "_find_working_selector", AsyncMock(return_value="selector1")):
            html = await adapter._extract_with_selectors(page, contract)

        assert html is not None

    @pytest.mark.asyncio
    async def test_extract_with_selectors_returns_none_on_small_content(self, adapter):
        """Should return None for content below min_valid_content_size."""
        page = _make_page()
        element = AsyncMock()
        element.inner_html = AsyncMock(return_value="<div>X</div>")
        page.query_selector = AsyncMock(return_value=element)

        contract = SelectorContract(name="content", selectors=("selector1",))

        with patch.object(adapter, "_find_working_selector", AsyncMock(return_value="selector1")):
            html = await adapter._extract_with_selectors(page, contract)

        assert html is None

    @pytest.mark.asyncio
    async def test_find_working_selector_refetches_when_the_cached_selector_stops_working(
        self, adapter
    ):
        """A cached selector that no longer matches must be replaced."""
        page = _make_page()
        page.query_selector = AsyncMock(return_value=AsyncMock())

        contract = SelectorContract(name="test", selectors=("selector1", "selector2"))

        assert await adapter._find_working_selector(page, contract) == "selector1"

        page.query_selector = AsyncMock(side_effect=[None, None, AsyncMock()])

        assert await adapter._find_working_selector(page, contract) == "selector2"

    @pytest.mark.asyncio
    async def test_extract_with_selectors_returns_none_without_selector(self, adapter):
        """Should return None when no selector of the contract matches."""
        page = _make_page()
        page.query_selector = AsyncMock(return_value=None)

        contract = SelectorContract(name="content", selectors=("selector1",))

        assert await adapter._extract_with_selectors(page, contract) is None

    @pytest.mark.asyncio
    async def test_extract_with_selectors_returns_none_when_the_element_vanishes(self, adapter):
        """Should return None when the element disappears between the two lookups."""
        page = _make_page()
        page.query_selector = AsyncMock(return_value=None)

        contract = SelectorContract(name="content", selectors=("selector1",))

        with patch.object(adapter, "_find_working_selector", AsyncMock(return_value="selector1")):
            assert await adapter._extract_with_selectors(page, contract) is None

    def test_validate_content(self, adapter):
        """Should validate the content size."""
        assert adapter._validate_content("<html>Large content</html>" * 100, 100) is True
        assert adapter._validate_content("Small", 100) is False
        assert adapter._validate_content(None, 100) is False


class TestPlaywrightScraperAdapterLayoutValidation:
    """Tests for the layout change detection."""

    @pytest.mark.asyncio
    async def test_validate_layout_does_not_report_a_valid_layout(
        self, config, cache, rate_limiter
    ):
        """A page matching every required contract must not be reported."""
        contracts = (
            SelectorContract(name="content", selectors=("article",)),
            SelectorContract(name="toc", selectors=("ul.tree",)),
        )
        adapter = PlaywrightScraperAdapter(
            config=config,
            selector_contracts=contracts,
            cache=cache,
            rate_limiter=rate_limiter,
        )
        observability = MagicMock(spec=ScraperObservabilityPort)
        adapter.observability = observability

        html = "<html><body><article>content</article><ul class='tree'></ul></body></html>"
        await adapter._validate_layout("https://example.com", html, "test-cid")

        observability.log_layout_change.assert_not_called()

    @pytest.mark.asyncio
    async def test_validate_layout_reports_the_failed_contracts(self, config, cache, rate_limiter):
        """A missing required contract must be reported."""
        contracts = (
            SelectorContract(name="content", selectors=("article",)),
            SelectorContract(name="toc", selectors=("ul.tree",)),
        )
        adapter = PlaywrightScraperAdapter(
            config=config,
            selector_contracts=contracts,
            cache=cache,
            rate_limiter=rate_limiter,
        )
        observability = MagicMock(spec=ScraperObservabilityPort)
        adapter.observability = observability

        html = "<html><body><article>content</article></body></html>"
        await adapter._validate_layout("https://example.com", html, "test-cid")

        observability.log_layout_change.assert_called_once_with(
            "https://example.com", ["toc"], "test-cid"
        )

    @pytest.mark.asyncio
    async def test_validate_layout_ignores_optional_contracts(self, config, cache, rate_limiter):
        """Optional contracts must never be reported as a layout change."""
        contracts = (
            SelectorContract(name="content", selectors=("article",)),
            SelectorContract(name="pdf", selectors=("button.pdf",), required=False),
        )
        adapter = PlaywrightScraperAdapter(
            config=config,
            selector_contracts=contracts,
            cache=cache,
            rate_limiter=rate_limiter,
        )
        observability = MagicMock(spec=ScraperObservabilityPort)
        adapter.observability = observability

        html = "<html><body><article>content</article></body></html>"
        await adapter._validate_layout("https://example.com", html, "test-cid")

        observability.log_layout_change.assert_not_called()


class TestPlaywrightScraperAdapterExecFetch:
    """Tests for the low level fetch routine."""

    @pytest.mark.asyncio
    async def test_exec_fetch_returns_the_html(self, adapter, rate_limiter):
        """Should navigate and return the page HTML."""
        page = _make_page()
        page.content = AsyncMock(return_value="<html>Content</html>")

        with (
            patch.object(adapter, "_wait_for_content", AsyncMock()) as wait,
            patch.object(adapter, "_expand_toc", AsyncMock()) as expand,
        ):
            html = await adapter._exec_fetch(
                "https://example.com",
                page,
                expand_toc=True,
                return_text=False,
                correlation_id="test",
            )

        assert html == "<html>Content</html>"
        page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="domcontentloaded",
            timeout=adapter.config.navigation_timeout_seconds * 1000,
        )
        wait.assert_called_once()
        expand.assert_called_once()
        rate_limiter.acquire.assert_called_once()

    @pytest.mark.asyncio
    async def test_exec_fetch_returns_the_text(self, adapter):
        """Should return the body text when return_text is set."""
        page = _make_page()
        page.inner_text = AsyncMock(return_value="the body text")

        with (
            patch.object(adapter, "_wait_for_content", AsyncMock()),
            patch.object(adapter, "_expand_toc", AsyncMock()),
        ):
            text = await adapter._exec_fetch(
                "https://example.com",
                page,
                expand_toc=False,
                return_text=True,
                correlation_id="test",
            )

        assert text == "the body text"

    @pytest.mark.asyncio
    async def test_exec_fetch_does_not_expand_the_toc_when_not_requested(self, adapter):
        """The TOC expansion must be skipped when expand_toc is False."""
        page = _make_page()

        with (
            patch.object(adapter, "_wait_for_content", AsyncMock()),
            patch.object(adapter, "_expand_toc", AsyncMock()) as expand,
        ):
            await adapter._exec_fetch(
                "https://example.com",
                page,
                expand_toc=False,
                return_text=False,
                correlation_id="test",
            )

        expand.assert_not_called()

    @pytest.mark.asyncio
    async def test_exec_fetch_raises_on_timeout(self, adapter):
        """Should raise a ScraperError when the navigation times out."""
        page = _make_page()
        page.goto = AsyncMock(side_effect=PlaywrightTimeout("Timeout"))

        with pytest.raises(ScraperError) as exc_info:
            await adapter._exec_fetch("https://example.com", page, correlation_id="test")

        assert "Navigation failed" in str(exc_info.value)
        assert exc_info.value.code == ScraperErrorCode.TIMEOUT
        assert exc_info.value.url == "https://example.com"

    @pytest.mark.asyncio
    async def test_exec_fetch_raises_on_playwright_error(self, adapter):
        """Should raise a ScraperError on any playwright failure."""
        page = _make_page()
        page.goto = AsyncMock(side_effect=PlaywrightError("boom"))

        with pytest.raises(ScraperError) as exc_info:
            await adapter._exec_fetch("https://example.com", page, correlation_id="test")

        assert exc_info.value.code == ScraperErrorCode.TIMEOUT


class TestPlaywrightScraperAdapterFetchHtml:
    """Tests for the public fetch_html method."""

    @pytest.mark.asyncio
    async def test_fetch_html_success(self, adapter, browser, cache, observability):
        """Should return the HTML, cache it and record the metrics."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(return_value=BIG_HTML)) as exec_fetch,
            patch.object(adapter, "_validate_layout", AsyncMock()) as validate_layout,
        ):
            html = await adapter.fetch_html("https://example.com")

        assert html == BIG_HTML
        exec_fetch.assert_called_once()
        validate_layout.assert_called_once()
        cache.set.assert_called_once_with(
            "https://example.com", BIG_HTML, adapter.config.cache_ttl_seconds
        )
        observability.record_metrics.assert_called_once()
        metrics = observability.record_metrics.call_args.args[0]
        assert metrics.success is True
        assert metrics.content_size == len(BIG_HTML)
        assert metrics.attempt == 1

    @pytest.mark.asyncio
    async def test_fetch_html_cache_hit(self, adapter, cache, observability):
        """Should serve the cached content without touching the browser."""
        cache.get.return_value = BIG_HTML

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)) as ensure:
            html = await adapter.fetch_html("https://example.com")

        assert html == BIG_HTML
        ensure.assert_not_called()
        cache.get.assert_called_once_with("https://example.com")

        metrics = observability.record_metrics.call_args.args[0]
        assert metrics.cache_hit is True
        assert metrics.success is True

    @pytest.mark.asyncio
    async def test_fetch_html_ignores_an_invalid_cache_entry(self, adapter, cache, browser):
        """A cached entry below the minimum size must be refetched."""
        cache.get.return_value = "<html>too small</html>"

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(return_value=BIG_HTML)),
            patch.object(adapter, "_validate_layout", AsyncMock()),
        ):
            html = await adapter.fetch_html("https://example.com")

        assert html == BIG_HTML

    @pytest.mark.asyncio
    async def test_fetch_html_with_open_circuit_breaker(self, adapter, observability, cache):
        """Should return None and record the circuit breaker metric."""
        for _ in range(adapter.config.circuit_breaker_threshold):
            adapter._circuit_breaker.record_failure()

        assert adapter._circuit_breaker.is_open is True

        html = await adapter.fetch_html("https://example.com")

        assert html is None
        cache.get.assert_not_called()

        metrics = observability.record_metrics.call_args.args[0]
        assert metrics.success is False
        assert metrics.error_code == ScraperErrorCode.CIRCUIT_OPEN
        assert metrics.circuit_breaker_state == "open"

    @pytest.mark.asyncio
    async def test_fetch_html_retries_on_failure(self, adapter, browser):
        """Should retry after a transient playwright failure."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(
                adapter,
                "_exec_fetch",
                AsyncMock(side_effect=[PlaywrightError("boom"), BIG_HTML]),
            ) as exec_fetch,
            patch.object(adapter, "_validate_layout", AsyncMock()),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            html = await adapter.fetch_html("https://example.com")

        assert html == BIG_HTML
        assert exec_fetch.await_count == 2

    @pytest.mark.asyncio
    async def test_fetch_html_returns_none_after_all_attempts_fail(self, adapter, browser, cache):
        """Should give up after max_retry_attempts and return None."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(
                adapter, "_exec_fetch", AsyncMock(side_effect=PlaywrightError("boom"))
            ) as exec_fetch,
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            html = await adapter.fetch_html("https://example.com")

        assert html is None
        assert exec_fetch.await_count == adapter.config.max_retry_attempts
        cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_html_raises_non_retryable_errors(self, adapter, browser, observability):
        """A non retryable ScraperError must be propagated."""
        error = ScraperError(
            "insufficient content",
            code=ScraperErrorCode.INSUFFICIENT_CONTENT,
            url="https://example.com",
            retryable=False,
        )

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(side_effect=error)),
        ):
            with pytest.raises(ScraperError) as exc_info:
                await adapter.fetch_html("https://example.com")

        assert exc_info.value is error
        metrics = observability.record_metrics.call_args.args[0]
        assert metrics.error_code == ScraperErrorCode.INSUFFICIENT_CONTENT

    @pytest.mark.asyncio
    async def test_fetch_html_raises_on_the_last_attempt(self, adapter, browser, observability):
        """A retryable error is raised when the last attempt fails."""
        error = ScraperError("boom", code=ScraperErrorCode.TIMEOUT, url="https://example.com")

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(side_effect=error)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            with pytest.raises(ScraperError):
                await adapter.fetch_html("https://example.com")

        metrics = observability.record_metrics.call_args.args[0]
        assert metrics.attempt == adapter.config.max_retry_attempts

    @pytest.mark.asyncio
    async def test_fetch_html_fails_when_the_browser_cannot_start(self, adapter):
        """Should raise when the browser cannot be launched."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=False)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            with pytest.raises(ScraperError) as exc_info:
                await adapter.fetch_html("https://example.com")

        assert exc_info.value.code == ScraperErrorCode.BROWSER_CRASH

    @pytest.mark.asyncio
    async def test_fetch_html_raises_when_the_browser_object_is_missing(self, adapter):
        """A missing browser object must be reported as a browser crash."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            with pytest.raises(ScraperError) as exc_info:
                await adapter.fetch_html("https://example.com")

        assert exc_info.value.code == ScraperErrorCode.BROWSER_CRASH

    @pytest.mark.asyncio
    async def test_fetch_html_retries_when_the_content_is_insufficient(
        self, adapter, browser, cache
    ):
        """Content below the minimum size must not be accepted."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(return_value="<html>tiny</html>")),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            html = await adapter.fetch_html("https://example.com")

        assert html is None
        cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_html_closes_the_page_and_the_context(self, adapter, browser):
        """The page and the context must be closed after the fetch."""
        page = browser.new_context.return_value.new_page.return_value

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(return_value=BIG_HTML)),
            patch.object(adapter, "_validate_layout", AsyncMock()),
        ):
            await adapter.fetch_html("https://example.com")

        page.close.assert_called_once()
        browser.new_context.return_value.close.assert_called_once()


class TestPlaywrightScraperAdapterFetchText:
    """Tests for the public fetch_text method."""

    @pytest.mark.asyncio
    async def test_fetch_text_success(self, adapter, browser, cache):
        """Should return the text and cache it under the text key."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(return_value=BIG_TEXT)),
        ):
            text = await adapter.fetch_text("https://example.com")

        assert text == BIG_TEXT
        cache.get.assert_called_once_with("text:https://example.com")
        cache.set.assert_called_once_with(
            "text:https://example.com", BIG_TEXT, adapter.config.cache_ttl_seconds
        )

    @pytest.mark.asyncio
    async def test_fetch_text_cache_hit(self, adapter, cache):
        """Should serve the cached text without touching the browser."""
        cache.get.return_value = BIG_TEXT

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)) as ensure:
            text = await adapter.fetch_text("https://example.com")

        assert text == BIG_TEXT
        ensure.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_text_returns_none_when_too_short(self, adapter, browser, cache):
        """Should give up when the extracted text stays below the threshold."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_exec_fetch", AsyncMock(return_value="short")),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            text = await adapter.fetch_text("https://example.com")

        assert text is None
        cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_text_with_open_circuit_breaker(self, adapter, cache):
        """Should return None when the circuit breaker is open."""
        for _ in range(adapter.config.circuit_breaker_threshold):
            adapter._circuit_breaker.record_failure()

        text = await adapter.fetch_text("https://example.com")

        assert text is None
        cache.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_text_returns_none_without_browser(self, adapter, cache):
        """Should return None when the browser cannot be launched."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=False)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            assert await adapter.fetch_text("https://example.com") is None

        cache.set.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_text_returns_none_without_browser_object(self, adapter):
        """Should return None when the browser object is missing."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            assert await adapter.fetch_text("https://example.com") is None

    @pytest.mark.asyncio
    async def test_fetch_text_handles_playwright_errors(self, adapter, browser, cache):
        """A playwright failure must be retried and finally return None."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(
                adapter, "_exec_fetch", AsyncMock(side_effect=PlaywrightError("boom"))
            ) as exec_fetch,
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            assert await adapter.fetch_text("https://example.com") is None

        assert exec_fetch.await_count == adapter.config.max_retry_attempts
        cache.set.assert_not_called()


class TestPlaywrightScraperAdapterFetchToc:
    """Tests for the public fetch_toc method."""

    @pytest.mark.asyncio
    async def test_fetch_toc_success(self, adapter, browser):
        """Should return the TOC extracted with the selector contract."""
        toc_html = "<ul class='tree'>" + ("<li>item</li>" * 10) + "</ul>"

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_expand_toc", AsyncMock()),
            patch.object(
                adapter, "_extract_with_selectors", AsyncMock(return_value=toc_html)
            ) as extract,
        ):
            toc = await adapter.fetch_toc("https://example.com")

        assert toc == toc_html
        extract.assert_called_once()
        contract = extract.call_args.args[1]
        assert contract.name == "toc"

    @pytest.mark.asyncio
    async def test_fetch_toc_falls_back_to_the_full_page(self, adapter, browser):
        """Should return the whole page when no TOC container is found."""
        page = browser.new_context.return_value.new_page.return_value
        page.content = AsyncMock(return_value="<html>Full page</html>")

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch.object(adapter, "_expand_toc", AsyncMock()),
            patch.object(adapter, "_extract_with_selectors", AsyncMock(return_value=None)),
        ):
            toc = await adapter.fetch_toc("https://example.com")

        assert toc == "<html>Full page</html>"

    @pytest.mark.asyncio
    async def test_fetch_toc_with_open_circuit_breaker(self, adapter, browser):
        """Should return None when the circuit breaker is open."""
        for _ in range(adapter.config.circuit_breaker_threshold):
            adapter._circuit_breaker.record_failure()

        assert await adapter.fetch_toc("https://example.com") is None

    @pytest.mark.asyncio
    async def test_fetch_toc_returns_none_without_browser(self, adapter, browser):
        """Should return None when the browser cannot be launched."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=False)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            assert await adapter.fetch_toc("https://example.com") is None

    @pytest.mark.asyncio
    async def test_fetch_toc_returns_none_without_browser_object(self, adapter):
        """Should return None when the browser object is missing."""
        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            assert await adapter.fetch_toc("https://example.com") is None

    @pytest.mark.asyncio
    async def test_fetch_toc_handles_playwright_errors(self, adapter, browser):
        """A playwright failure must be retried and finally return None."""
        page = browser.new_context.return_value.new_page.return_value
        page.goto = AsyncMock(side_effect=PlaywrightError("boom"))

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch(
                "src.infrastructure.scraping.playwright_adapter.asyncio.sleep",
                new_callable=AsyncMock,
            ),
        ):
            assert await adapter.fetch_toc("https://example.com") is None


class TestPlaywrightScraperAdapterFeatures:
    """Tests for the feature extraction."""

    @pytest.mark.asyncio
    async def test_fetch_features_with_links(self, adapter):
        """Should extract the features and their documentation links."""
        html = """
        <html>
            <table>
                <tr><td>Feature 1</td><td><a href="/feature1">Link</a></td></tr>
                <tr><td>Feature 2</td><td></td></tr>
            </table>
        </html>
        """

        with patch.object(adapter, "fetch_html", AsyncMock(return_value=html)) as fetch_html:
            features = await adapter.fetch_features_with_links("https://example.com")

        fetch_html.assert_called_once_with("https://example.com", expand_toc=False)
        assert len(features) == 2
        assert features[0]["name"] == "Feature 1"
        assert features[0]["docs_url"] == "https://help.salesforce.com/feature1"
        assert features[1]["name"] == "Feature 2"
        assert features[1]["docs_url"] == ""

    @pytest.mark.asyncio
    async def test_fetch_features_with_links_returns_empty_list(self, adapter):
        """Should return an empty list when the page cannot be fetched."""
        with patch.object(adapter, "fetch_html", AsyncMock(return_value=None)):
            assert await adapter.fetch_features_with_links("https://example.com") == []

    @pytest.mark.asyncio
    async def test_fetch_features_with_links_with_open_circuit_breaker(self, adapter):
        """Should return an empty list when the circuit breaker is open."""
        for _ in range(adapter.config.circuit_breaker_threshold):
            adapter._circuit_breaker.record_failure()

        assert await adapter.fetch_features_with_links("https://example.com") == []

    def test_extract_features_ignores_foreign_hosts(self):
        """Links pointing outside salesforce.com must be dropped."""
        html = """
        <html><table>
            <tr><td>Foreign feature</td><td><a href="https://example.org/doc">Doc</a></td></tr>
        </table></html>
        """

        features = PlaywrightScraperAdapter._extract_features_from_html(html)

        assert features == [{"name": "Foreign feature", "docs_url": ""}]

    def test_extract_features_keeps_absolute_salesforce_links(self):
        """Absolute salesforce.com links must be preserved."""
        html = """
        <html><table>
            <tr>
                <td>Absolute feature</td>
                <td><a href="https://help.salesforce.com/doc">Doc</a></td>
            </tr>
        </table></html>
        """

        features = PlaywrightScraperAdapter._extract_features_from_html(html)

        assert features[0]["docs_url"] == "https://help.salesforce.com/doc"

    def test_extract_features_skips_rows_without_feature_names(self):
        """Rows without a usable name must be ignored."""
        html = """
        <html><table>
            <tr><th>Header</th></tr>
            <tr><td>ab</td></tr>
        </table></html>
        """

        assert PlaywrightScraperAdapter._extract_features_from_html(html) == []

    def test_extract_features_ignores_non_http_links(self):
        """Links with another scheme must be dropped."""
        html = """
        <html><table>
            <tr><td>Ftp feature</td><td><a href="ftp://files.salesforce.com/doc">Doc</a></td></tr>
            <tr><td>Hostless feature</td><td><a href="http://">Doc</a></td></tr>
        </table></html>
        """

        features = PlaywrightScraperAdapter._extract_features_from_html(html)

        assert features == [
            {"name": "Ftp feature", "docs_url": ""},
            {"name": "Hostless feature", "docs_url": ""},
        ]

    def test_extract_features_falls_back_to_the_list_items(self):
        """Pages without a table must be parsed through the list items."""
        html = """
        <html><ul>
            <li><a href="/release-notes/winter-26">Winter '26 release notes</a></li>
            <li><a href="/release-notes/summer-25">Summer '25 release notes</a></li>
        </ul></html>
        """

        features = PlaywrightScraperAdapter._extract_features_from_html(html)

        assert len(features) == 2
        assert features[0]["name"] == "Winter '26 release notes"
        assert features[0]["docs_url"] == "https://help.salesforce.com/release-notes/winter-26"

    def test_extract_features_deduplicates_by_name(self):
        """The same feature must not be reported twice."""
        html = """
        <html><table>
            <tr><td>Repeated feature</td><td><a href="/a">A</a></td></tr>
            <tr><td>Repeated feature</td><td><a href="/b">B</a></td></tr>
        </table></html>
        """

        features = PlaywrightScraperAdapter._extract_features_from_html(html)

        assert len(features) == 1


class TestPlaywrightScraperAdapterDownloadPdf:
    """Tests for the PDF download."""

    @pytest.mark.asyncio
    async def test_download_pdf_uses_the_button(self, adapter, browser, tmp_path):
        """Should save the download triggered by the PDF button."""
        page = browser.new_context.return_value.new_page.return_value
        download = _FakeDownload(b"%PDF" + b"0" * 2000)
        page.expect_download = MagicMock(
            return_value=_FakeExpectDownload(_FakeDownloadInfo(download))
        )

        dest = tmp_path / "release-notes.pdf"

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)):
            result = await adapter.download_pdf("https://example.com", dest)

        assert result is True
        assert dest.exists()
        assert download.saved_to == [str(dest)]

    @pytest.mark.asyncio
    async def test_download_pdf_skips_an_existing_file(self, adapter, tmp_path):
        """A valid file already on disk must not be downloaded again."""
        dest = tmp_path / "release-notes.pdf"
        dest.write_bytes(b"%PDF" + b"0" * 2000)

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)) as ensure:
            result = await adapter.download_pdf("https://example.com", dest)

        assert result is True
        ensure.assert_not_called()

    @pytest.mark.asyncio
    async def test_download_pdf_falls_back_to_the_direct_link(self, adapter, browser, tmp_path):
        """Should download the linked .pdf file when the button is missing."""
        page = browser.new_context.return_value.new_page.return_value
        page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("no button"))

        link = MagicMock()
        link.get_attribute = AsyncMock(return_value="/documents/release-notes/winter-26.pdf")
        page.query_selector_all = AsyncMock(return_value=[link])

        dest = tmp_path / "release-notes.pdf"
        response = MagicMock()
        response.read = MagicMock(return_value=b"%PDF" + b"0" * 2000)

        with (
            patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)),
            patch("urllib.request.urlopen", return_value=response) as urlopen,
        ):
            result = await adapter.download_pdf("https://example.com", dest)

        assert result is True
        assert dest.exists()
        urlopen.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_pdf_returns_false_without_links(self, adapter, browser, tmp_path):
        """Should return False when neither the button nor a link is available."""
        page = browser.new_context.return_value.new_page.return_value
        page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeout("no button"))
        page.query_selector_all = AsyncMock(return_value=[])

        dest = tmp_path / "release-notes.pdf"

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)):
            result = await adapter.download_pdf("https://example.com", dest)

        assert result is False
        assert not dest.exists()

    @pytest.mark.asyncio
    async def test_download_pdf_returns_false_without_browser(self, adapter, tmp_path):
        """Should return False when the browser cannot be launched."""
        dest = tmp_path / "release-notes.pdf"

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=False)):
            result = await adapter.download_pdf("https://example.com", dest)

        assert result is False

    @pytest.mark.asyncio
    async def test_download_pdf_returns_false_without_browser_object(self, adapter, tmp_path):
        """Should return False when the browser object is missing."""
        dest = tmp_path / "release-notes.pdf"

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)):
            result = await adapter.download_pdf("https://example.com", dest)

        assert result is False


class TestPlaywrightScraperAdapterFetchMultiple:
    """Tests for the concurrent fetch."""

    @pytest.mark.asyncio
    async def test_fetch_multiple(self, adapter):
        """Should return one result per URL, keeping the order."""
        with patch.object(
            adapter,
            "fetch_html",
            AsyncMock(side_effect=["<html>1</html>", "<html>2</html>", None]),
        ):
            results = await adapter.fetch_multiple(["url1", "url2", "url3"], max_concurrent=2)

        assert len(results) == 3
        assert results[0] == "<html>1</html>"
        assert results[1] == "<html>2</html>"
        assert results[2] is None

    @pytest.mark.asyncio
    async def test_fetch_multiple_with_no_urls(self, adapter):
        """Should return an empty list when there is nothing to fetch."""
        assert await adapter.fetch_multiple([]) == []


class TestPlaywrightScraperAdapterHealthCheck:
    """Tests for the health check."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, adapter, browser):
        """Should return True when the homepage can be loaded."""
        page = browser.new_page.return_value

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)):
            result = await adapter.health_check()

        assert result is True
        page.goto.assert_called_once()
        page.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_failure_without_browser(self, adapter):
        """Should return False when the browser cannot be launched."""
        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=False)):
            assert await adapter.health_check() is False

    @pytest.mark.asyncio
    async def test_health_check_failure_without_browser_object(self, adapter):
        """Should return False when the browser object is missing."""
        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)):
            assert await adapter.health_check() is False

    @pytest.mark.asyncio
    async def test_health_check_failure_on_error(self, adapter, browser):
        """Should return False when the navigation raises."""
        page = browser.new_page.return_value
        page.goto = AsyncMock(side_effect=PlaywrightError("boom"))

        with patch.object(adapter, "_ensure_browser", AsyncMock(return_value=True)):
            assert await adapter.health_check() is False


class TestSalesforceReleaseScraper:
    """Tests for backwards compatibility alias."""

    def test_alias_exists(self):
        """SalesforceReleaseScraper should be PlaywrightScraperAdapter."""
        assert SalesforceReleaseScraper is PlaywrightScraperAdapter

    def test_can_instantiate(self, tmp_path):
        """Should be able to instantiate."""
        scraper = SalesforceReleaseScraper(config=ScraperConfig(cache_dir=tmp_path / "cache"))
        assert isinstance(scraper, PlaywrightScraperAdapter)
