"""Logging configuration and utility functions."""

import logging
import os
import sys
from typing import Optional


def setup_logger(
    name: Optional[str] = None,
    level: Optional[int] = None,
) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: Name of the logger. Defaults to 'app'.
        level: Logging level. Defaults to INFO or environment variable LOG_LEVEL.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger_name = name or "app"
    logger = logging.getLogger(logger_name)

    if level is None:
        env_level = os.getenv("LOG_LEVEL", "INFO").upper()
        level = getattr(logging, env_level, logging.INFO)

    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with default setup.

    Args:
        name: Name of the logger.

    Returns:
        logging.Logger: Logger instance.
    """
    return setup_logger(name=name)


logger = get_logger("app")
