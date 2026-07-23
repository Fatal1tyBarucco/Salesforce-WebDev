"""Structured logging with correlation IDs for the release notes pipeline."""

import json
import logging
import sys
import uuid
import warnings


class CorrelationFilter(logging.Filter):
    """Injects correlation_id into every log record."""

    def __init__(self) -> None:
        super().__init__()
        self._correlation_id: str = ""

    @property
    def correlation_id(self) -> str:
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value: str) -> None:
        self._correlation_id = value

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self._correlation_id
        return True


class JSONFormatter(logging.Formatter):
    """Structured JSON log formatter for machine-readable output."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, object] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        cid = getattr(record, "correlation_id", "")
        if cid:
            log_entry["correlation_id"] = cid
        if record.exc_info and record.exc_info[0]:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Human-readable formatter with correlation ID prefix."""

    def format(self, record: logging.LogRecord) -> str:
        prefix = ""
        cid = getattr(record, "correlation_id", "")
        if cid:
            prefix = f"[{cid[:8]}] "
        return f"{self.formatTime(record)} - {prefix}{record.name} - {record.levelname} - {record.getMessage()}"


_correlation_filter = CorrelationFilter()


def setup_logging(*, json_format: bool = False) -> None:
    """Configure structured logging with correlation IDs."""
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="bs4")

    formatter: logging.Formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)
    root.addFilter(_correlation_filter)

    # Optional Sentry integration (requires sentry-sdk)
    _setup_sentry()


def new_correlation_id() -> str:
    """Generate a new correlation ID and set it as the active one."""
    cid = uuid.uuid4().hex[:12]
    _correlation_filter.correlation_id = cid
    return cid


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return _correlation_filter.correlation_id


def _setup_sentry() -> None:
    """Initialize Sentry if SENTRY_DSN is configured.

    Requires ``sentry-sdk`` to be installed.  Silently skips if not available.
    """
    import os

    dsn = os.environ.get("SENTRY_DSN", "")
    if not dsn:
        return

    try:
        import sentry_sdk  # type: ignore[import-not-found]

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        )
        logging.getLogger(__name__).info("Sentry error tracking initialized")
    except ImportError:
        logging.getLogger(__name__).debug("sentry-sdk not installed, skipping Sentry integration")
