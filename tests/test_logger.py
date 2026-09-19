"""Tests for src/logger.py — 100% coverage target."""

import json
import logging
import sys
from unittest.mock import MagicMock, patch


class TestSetupSentry:
    """_setup_sentry: optional Sentry SDK initialization."""

    def test_no_op_when_dsn_missing(self) -> None:
        from src.logger import _setup_sentry

        with patch.dict("os.environ", {}, clear=False):
            monkeypatch_dsn = patch.dict("os.environ", {"SENTRY_DSN": ""}, clear=False)
            monkeypatch_dsn.start()
            try:
                _setup_sentry()  # Should return early without raising
            finally:
                monkeypatch_dsn.stop()

    def test_no_op_when_sdk_missing(self) -> None:
        from src.logger import _setup_sentry

        with (
            patch.dict("os.environ", {"SENTRY_DSN": "https://example@sentry.io/123"}, clear=False),
            patch.dict(sys.modules, {"sentry_sdk": None}),
        ):
            _setup_sentry()  # Should handle ImportError gracefully

    def test_initializes_sdk_when_available(self) -> None:
        from src.logger import _setup_sentry

        mock_sdk = MagicMock()
        with (
            patch.dict(
                "os.environ",
                {
                    "SENTRY_DSN": "https://example@sentry.io/123",
                    "SENTRY_TRACES_SAMPLE_RATE": "0.2",
                    "SENTRY_ENVIRONMENT": "test",
                },
                clear=False,
            ),
            patch.dict(sys.modules, {"sentry_sdk": mock_sdk}),
        ):
            _setup_sentry()
            mock_sdk.init.assert_called_once()


class TestSetupLogging:
    """setup_logging: JSON vs text format."""

    def test_json_format(self) -> None:
        from src.logger import setup_logging

        setup_logging(json_format=True)

    def test_text_format(self) -> None:
        from src.logger import setup_logging

        setup_logging(json_format=False)


class TestCorrelationId:
    """Correlation ID generation and filter."""

    def test_new_correlation_id_returns_string(self) -> None:
        from src.logger import get_correlation_id, new_correlation_id

        cid = new_correlation_id()
        assert isinstance(cid, str)
        assert len(cid) > 0
        assert get_correlation_id() == cid

    def test_correlation_filter(self) -> None:
        from src.logger import CorrelationFilter

        f = CorrelationFilter()
        assert f.correlation_id == ""
        f.correlation_id = "test-123"
        assert f.correlation_id == "test-123"


class TestFormatters:
    """JSONFormatter and TextFormatter: log record → string."""

    def test_json_formatter(self) -> None:
        from src.logger import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["message"] == "test message"

    def test_text_formatter(self) -> None:
        from src.logger import TextFormatter

        formatter = TextFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="warning msg",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        assert "warning msg" in result


class TestGetLogger:
    """get_logger: existing logger vs setup path."""

    def test_creates_new_logger_when_no_handlers(self) -> None:
        from src.logger import get_logger

        logger = get_logger("test_new_logger_no_handlers")
        assert logger.name == "test_new_logger_no_handlers"
        assert len(logger.handlers) > 0
        # Cleanup
        for h in list(logger.handlers):
            logger.removeHandler(h)

    def test_returns_existing_logger(self) -> None:
        from src.logger import get_logger

        name = "test_existing_logger_handlers"
        logger = logging.getLogger(name)
        logger.addHandler(logging.StreamHandler(sys.stdout))
        result = get_logger(name)
        assert result is logger


class TestJSONFormatterWithExtras:
    """JSONFormatter with correlation_id and exception info."""

    def test_with_cid_and_exception(self) -> None:
        from src.logger import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="error msg",
            args=(),
            exc_info=(ValueError, ValueError("boom"), None),
        )
        record.correlation_id = "abc123def456"
        result = formatter.format(record)
        parsed = json.loads(result)
        assert parsed["correlation_id"] == "abc123def456"
        assert "exception" in parsed
        assert "boom" in parsed["exception"]

    def test_without_cid_no_exception(self) -> None:
        from src.logger import JSONFormatter

        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )
        result = formatter.format(record)
        parsed = json.loads(result)
        assert "correlation_id" not in parsed
        assert "exception" not in parsed


class TestSetupSentryEdgeCases:
    """_setup_sentry edge cases."""

    def test_invalid_traces_sample_rate(self) -> None:
        from src.logger import _setup_sentry

        with (
            patch.dict(
                "os.environ",
                {
                    "SENTRY_DSN": "https://example@sentry.io/123",
                    "SENTRY_TRACES_SAMPLE_RATE": "not_a_number",
                    "SENTRY_ENVIRONMENT": "",
                },
                clear=False,
            ),
            patch.dict(sys.modules, {"sentry_sdk": MagicMock()}),
        ):
            _setup_sentry()  # Should not raise on invalid float


class TestSetupLoggerWithFile:
    """setup_logger with log_file parameter."""

    def test_with_log_file(self) -> None:
        from src.logger import setup_logger

        import os
        import tempfile
        import uuid

        tmp = tempfile.mktemp(suffix=".log")
        logger = setup_logger("test_with_file_" + uuid.uuid4().hex, log_file=tmp)
        assert len(logger.handlers) >= 2  # stream + file
        for h in list(logger.handlers):
            logger.removeHandler(h)
        if os.path.exists(tmp):
            os.remove(tmp)
