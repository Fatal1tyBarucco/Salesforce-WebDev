"""Tests for src/logger.py — 100% coverage."""

import json
import logging
from unittest.mock import patch

from src.logger import (
    CorrelationFilter,
    JSONFormatter,
    TextFormatter,
    get_correlation_id,
    new_correlation_id,
    setup_logging,
)


class TestCorrelationFilter:
    """Tests for CorrelationFilter class."""

    def test_init_sets_empty_correlation_id(self) -> None:
        """CorrelationFilter.__init__ sets empty correlation_id."""
        f = CorrelationFilter()
        assert f.correlation_id == ""

    def test_correlation_id_setter(self) -> None:
        """CorrelationFilter.correlation_id setter works."""
        f = CorrelationFilter()
        f.correlation_id = "abc123"
        assert f.correlation_id == "abc123"

    def test_filter_injects_correlation_id(self) -> None:
        """CorrelationFilter.filter injects correlation_id into record."""
        f = CorrelationFilter()
        f.correlation_id = "test-id"
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        assert f.filter(record) is True
        assert record.correlation_id == "test-id"

    def test_filter_returns_true(self) -> None:
        """CorrelationFilter.filter always returns True."""
        f = CorrelationFilter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "msg", (), None)
        assert f.filter(record) is True


class TestJSONFormatter:
    """Tests for JSONFormatter class."""

    def test_format_basic(self) -> None:
        """JSONFormatter.format produces valid JSON with required fields."""
        fmt = JSONFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "hello", (), None)
        result = fmt.format(record)
        data = json.loads(result)
        assert data["level"] == "INFO"
        assert data["logger"] == "mylogger"
        assert data["message"] == "hello"
        assert "timestamp" in data

    def test_format_with_correlation_id(self) -> None:
        """JSONFormatter.format includes correlation_id when present."""
        fmt = JSONFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "hello", (), None)
        record.correlation_id = "abc123"
        result = fmt.format(record)
        data = json.loads(result)
        assert data["correlation_id"] == "abc123"

    def test_format_without_correlation_id(self) -> None:
        """JSONFormatter.format omits correlation_id when empty."""
        fmt = JSONFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "hello", (), None)
        record.correlation_id = ""
        result = fmt.format(record)
        data = json.loads(result)
        assert "correlation_id" not in data

    def test_format_with_exception(self) -> None:
        """JSONFormatter.format includes exception info."""
        fmt = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
        record = logging.LogRecord("mylogger", logging.ERROR, "test.py", 10, "error", (), exc_info)
        result = fmt.format(record)
        data = json.loads(result)
        assert "exception" in data
        assert "ValueError" in data["exception"]

    def test_format_no_exception_field(self) -> None:
        """JSONFormatter.format omits exception when exc_info is None."""
        fmt = JSONFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "ok", (), None)
        result = fmt.format(record)
        data = json.loads(result)
        assert "exception" not in data


class TestTextFormatter:
    """Tests for TextFormatter class."""

    def test_format_basic(self) -> None:
        """TextFormatter.format produces human-readable output."""
        fmt = TextFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "hello", (), None)
        result = fmt.format(record)
        assert "mylogger" in result
        assert "INFO" in result
        assert "hello" in result

    def test_format_with_correlation_id(self) -> None:
        """TextFormatter.format includes correlation ID prefix."""
        fmt = TextFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "hello", (), None)
        record.correlation_id = "abcdefgh1234"
        result = fmt.format(record)
        assert "[abcdefgh" in result

    def test_format_without_correlation_id(self) -> None:
        """TextFormatter.format omits prefix when no correlation_id."""
        fmt = TextFormatter()
        record = logging.LogRecord("mylogger", logging.INFO, "test.py", 10, "hello", (), None)
        record.correlation_id = ""
        result = fmt.format(record)
        assert "[" not in result.split(" - ")[0]


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_default(self) -> None:
        """setup_logging() configures TextFormatter by default."""
        setup_logging()
        root = logging.getLogger()
        assert root.level == logging.INFO
        assert len(root.handlers) >= 1

    def test_setup_logging_json_format(self) -> None:
        """setup_logging(json_format=True) uses JSONFormatter."""
        setup_logging(json_format=True)
        root = logging.getLogger()
        handler = root.handlers[-1]
        assert isinstance(handler.formatter, JSONFormatter)

    def test_setup_logging_clears_handlers(self) -> None:
        """setup_logging clears existing handlers."""
        root = logging.getLogger()
        root.addHandler(logging.StreamHandler())
        initial_count = len(root.handlers)
        setup_logging()
        # Should have cleared and added exactly 1
        assert len(root.handlers) == 1


class TestCorrelationId:
    """Tests for new_correlation_id and get_correlation_id."""

    def test_new_correlation_id_returns_hex(self) -> None:
        """new_correlation_id returns a 12-char hex string."""
        cid = new_correlation_id()
        assert len(cid) == 12
        assert all(c in "0123456789abcdef" for c in cid)

    def test_new_correlation_id_sets_global(self) -> None:
        """new_correlation_id sets the global correlation filter."""
        cid = new_correlation_id()
        assert get_correlation_id() == cid

    def test_get_correlation_id_returns_current(self) -> None:
        """get_correlation_id returns the current correlation ID."""
        cid = new_correlation_id()
        assert get_correlation_id() == cid
