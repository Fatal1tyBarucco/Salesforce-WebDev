"""Logging configuration and utilities for Salesforce WebDev."""

from __future__ import annotations

import json
import logging
import os
import sys
import traceback
import uuid
from typing import Optional


def setup_logger(
    name: str = "salesforce_webdev",
    level: Optional[int] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up and configure a logger instance."""
    if level is None:
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "salesforce_webdev") -> logging.Logger:
    """Get an existing logger or create a new one with default settings."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


def new_correlation_id() -> str:
    """Generate a new correlation ID for request tracing (12-char hex)."""
    cid = uuid.uuid4().hex[:12]
    try:
        _filter.correlation_id = cid  # type: ignore[attr-defined]
    except NameError:
        pass
    return cid


def get_correlation_id() -> str:
    """Return current correlation id."""
    try:
        return _filter.correlation_id  # type: ignore[attr-defined]
    except NameError:
        return ""


class CorrelationFilter(logging.Filter):
    """Filter that injects correlation_id."""

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.correlation_id: str = ""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        record.correlation_id = self.correlation_id  # type: ignore[attr-defined]
        return True


class JSONFormatter(logging.Formatter):
    """JSON formatter."""

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, object] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        cid = getattr(record, "correlation_id", "")
        if cid:
            data["correlation_id"] = cid
        if record.exc_info and record.exc_info[0] is not None:
            data["exception"] = "".join(traceback.format_exception(*record.exc_info))
        return json.dumps(data)


class TextFormatter(logging.Formatter):
    """Text formatter with optional correlation id prefix."""

    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None) -> None:
        super().__init__(
            fmt or "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt or "%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        cid = getattr(record, "correlation_id", "")
        if cid:
            return f"[{cid[:8]}] {base}"
        return base


_filter = CorrelationFilter()


def setup_logging(
    level: object = None, json_format: bool = False, log_file: object = None
) -> logging.Logger:
    """Configure root logger. Clears existing handlers."""
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.INFO)
    handler: logging.Handler = logging.StreamHandler(sys.stdout)
    fmt: logging.Formatter
    if json_format:
        fmt = JSONFormatter()
    else:
        fmt = TextFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    handler.setFormatter(fmt)
    handler.addFilter(_filter)
    root.addHandler(handler)
    if isinstance(log_file, str) and log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(fmt)
        fh.addFilter(_filter)
        root.addHandler(fh)
    return root


def _setup_sentry(dsn: Optional[str] = None) -> None:
    """Initialize Sentry if a DSN is configured."""
    if dsn is None:
        dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return
    try:
        import sentry_sdk
    except ImportError:
        return
    init_kwargs: dict[str, object] = {"dsn": dsn}
    traces = os.getenv("SENTRY_TRACES_SAMPLE_RATE")
    if traces:
        try:
            init_kwargs["traces_sample_rate"] = float(traces)
        except ValueError:
            pass
    env = os.getenv("SENTRY_ENVIRONMENT")
    if env:
        init_kwargs["environment"] = env
    sentry_sdk.init(**init_kwargs)
