#!/usr/bin/env python3
"""Explicit cache maintenance (ADR-011, R5/R8).

Runs a FULL expired-entry sweep (the lazy ``clear_expired()`` default only
touches namespaces used in the current session) and reports quarantine
backups. Cleans ONLY safely derivable runtime caches under ``cache/`` —
never touches ``releases/`` or any versioned artifact.

Usage::

    uv run python scripts/cache_maintenance.py --cache-dir cache

Stdlib-only; safe to run as a CI finalizer (best-effort, exit 0 on
degraded I/O so maintenance never fails a pipeline run).
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cache_manager import CacheManager
from src.config import CACHE_DIR

logger = logging.getLogger("cache_maintenance")


def main(argv: list[str] | None = None) -> int:
    """Run maintenance on the runtime cache directory.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        Process exit code (always 0 — maintenance is best-effort).
    """
    parser = argparse.ArgumentParser(description="Runtime cache maintenance (ADR-011)")
    parser.add_argument(
        "--cache-dir",
        default=CACHE_DIR,
        help="Runtime cache directory (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    cache_dir = Path(args.cache_dir)
    manager = CacheManager(cache_dir=cache_dir)
    report = manager.maintenance()
    manager.persist_stats()
    logger.info(
        "[CACHE] Maintenance complete: expired_removed=%d quarantine_copies=%d",
        report["expired_removed"],
        report["quarantine_copies"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
