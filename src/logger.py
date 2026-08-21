"""Logging configuration and utilities for Salesforce WebDev."""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from typing import Any, Optional

__all__ = [
    "CorrelationFilter",
    "JSONFormatter",
    "TextFormatter",
    "get_correlation_id",
    "new_correlation_id",
    "setup_logger",
    "setup_logging",
    "get_logger",
    "_setup_sentry",
]


class CorrelationFilter(logging.Filter):
    """Injects correlation ID into log records."""

    def __init__(self, name: str = "") -> None:
        super().__init__(name)
        self.correlation_id: str = ""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self.correlation_id
        return True


_global_correlation_filter = CorrelationFilter()


class JSONFormatter(logging.Formatter):
    """JSON log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        cid = getattr(record, "correlation_id", "")
        if cid:
            data["correlation_id"] = cid
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data)


class TextFormatter(logging.Formatter):
    """Text log formatter with optional correlation ID prefix."""

    def format(self, record: logging.LogRecord) -> str:
        cid = getattr(record, "correlation_id", "")
        prefix = f"[{cid[:8]}] " if cid else ""
        formatted = super().format(record)
        if prefix:
            return f"{prefix}{formatted}"
        return formatted


def new_correlation_id() -> str:
    """Generate a new correlation ID for request tracing."""
    cid = uuid.uuid4().hex[:12]
    _global_correlation_filter.correlation_id = cid
    return cid


def get_correlation_id() -> str:
    """Get the current correlation ID."""
    return _global_correlation_filter.correlation_id


def _setup_sentry(dsn: Optional[str] = None) -> None:
    """Optionally initialize Sentry integration if DSN is provided."""
    if dsn:
        try:
            import sentry_sdk

            sentry_sdk.init(dsn=dsn)
        except ImportError:
            pass


def setup_logging(
    level: Optional[int | str] = None,
    json_format: bool = False,
    log_file: Optional[str] = None,
    sentry_dsn: Optional[str] = None,
) -> logging.Logger:
    """Configure application-wide logging settings."""
    if level is None:
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        level_val = getattr(logging, log_level_str, logging.INFO)
    elif isinstance(level, str):
        level_val = getattr(logging, level.upper(), logging.INFO)
    else:
        level_val = level

    root = logging.getLogger()
    root.setLevel(level_val)
    root.handlers.clear()

    formatter: logging.Formatter = (
        JSONFormatter()
        if json_format
        else TextFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(_global_correlation_filter)
    root.addHandler(handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_global_correlation_filter)
        root.addHandler(file_handler)

    if sentry_dsn:
        _setup_sentry(sentry_dsn)

    return root


def setup_logger(
    name: str = "salesforce_webdev",
    level: Optional[int] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up and configure a named logger instance."""
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
        stream_handler.addFilter(_global_correlation_filter)
        logger.addHandler(stream_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            file_handler.addFilter(_global_correlation_filter)
            logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "salesforce_webdev") -> logging.Logger:
    """Get an existing logger or create a new one with default settings."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
