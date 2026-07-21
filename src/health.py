"""Lightweight health check and status endpoint.

Provides a simple HTTP server for monitoring pipeline health.
No external dependencies — uses stdlib http.server.
"""

import json
import logging
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread

from .config import RELEASES_DIR

logger = logging.getLogger(__name__)


class HealthState:
    """Thread-safe pipeline health state and metrics.

    Replaces module-level global variables with an encapsulated,
    injectable state container.
    """

    def __init__(self) -> None:
        self._pipeline_start_time: float = time.monotonic()
        self._last_run_status: str = "idle"
        self._last_run_time: str = ""
        self._metrics: dict[str, float] = {
            "pipeline_runs_total": 0,
            "pipeline_failures_total": 0,
            "features_processed_total": 0,
            "scraper_requests_total": 0,
            "scraper_failures_total": 0,
            "circuit_breaker_trips_total": 0,
        }

    def inc_metric(self, name: str, value: float = 1.0) -> None:
        """Increment a counter metric."""
        self._metrics[name] = self._metrics.get(name, 0) + value

    def set_pipeline_status(self, status: str) -> None:
        """Update the pipeline status."""
        self._last_run_status = status
        self._last_run_time = datetime.now(tz=timezone.utc).isoformat()
        if status == "completed":
            self.inc_metric("pipeline_runs_total")
        elif status == "completed_with_errors":
            self.inc_metric("pipeline_failures_total")

    @property
    def last_run_status(self) -> str:
        """Return the current pipeline status."""
        return self._last_run_status

    @property
    def last_run_time(self) -> str:
        """Return the last run timestamp."""
        return self._last_run_time

    @property
    def uptime_seconds(self) -> float:
        """Return uptime in seconds."""
        return time.monotonic() - self._pipeline_start_time

    @property
    def metrics(self) -> dict[str, float]:
        """Return a copy of current metrics."""
        return dict(self._metrics)


# Module-level instance for backward compatibility
_health_state = HealthState()


def inc_metric(name: str, value: float = 1.0) -> None:
    """Increment a counter metric (delegates to module HealthState)."""
    _health_state.inc_metric(name, value)


def set_pipeline_status(status: str) -> None:
    """Update the global pipeline status (delegates to module HealthState)."""
    _health_state.set_pipeline_status(status)


def _get_health_data(state: HealthState | None = None) -> dict[str, object]:
    """Build health check response data.

    Args:
        state: HealthState instance. Uses module-level default if None.

    Returns:
        Dictionary with health check fields.
    """
    if state is None:
        state = _health_state

    releases_dir = Path(RELEASES_DIR)
    release_count = 0
    total_features = 0
    if releases_dir.exists():
        for d in releases_dir.iterdir():
            if d.is_dir():
                meta_path = d / ".meta.json"
                if meta_path.exists():
                    release_count += 1
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                        total_features += meta.get("total_features", 0)
                    except (json.JSONDecodeError, OSError) as e:
                        logger.warning("Ignorando .meta.json corrompido: %s", e)

    return {
        "status": "healthy",
        "uptime_seconds": round(state.uptime_seconds, 1),
        "pipeline_status": state.last_run_status,
        "last_run": state.last_run_time,
        "releases_processed": release_count,
        "total_features": total_features,
        "version": "3.0.0",
    }


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints."""

    def do_GET(self) -> None:
        if self.path == "/health" or self.path == "/":
            data = _get_health_data()
            self._respond(200, data)
        elif self.path == "/ready":
            data = {"status": "ready"}
            self._respond(200, data)
        elif self.path == "/metrics":
            self._respond_metrics()
        else:
            self._respond(404, {"error": "not found"})

    def _respond_metrics(self) -> None:
        """Return Prometheus-compatible plain text metrics."""
        metrics = _health_state.metrics
        lines = [
            "# HELP pipeline_runs_total Total pipeline runs",
            "# TYPE pipeline_runs_total counter",
            f"pipeline_runs_total {metrics.get('pipeline_runs_total', 0)}",
            "",
            "# HELP pipeline_failures_total Total pipeline failures",
            "# TYPE pipeline_failures_total counter",
            f"pipeline_failures_total {metrics.get('pipeline_failures_total', 0)}",
            "",
            "# HELP features_processed_total Total features processed",
            "# TYPE features_processed_total counter",
            f"features_processed_total {metrics.get('features_processed_total', 0)}",
            "",
            "# HELP scraper_requests_total Total scraper requests",
            "# TYPE scraper_requests_total counter",
            f"scraper_requests_total {metrics.get('scraper_requests_total', 0)}",
            "",
            "# HELP scraper_failures_total Total scraper failures",
            "# TYPE scraper_failures_total counter",
            f"scraper_failures_total {metrics.get('scraper_failures_total', 0)}",
            "",
            "# HELP pipeline_uptime_seconds Pipeline uptime in seconds",
            "# TYPE pipeline_uptime_seconds gauge",
            f"pipeline_uptime_seconds {round(_health_state.uptime_seconds, 1)}",
            "",
        ]
        body = "\n".join(lines).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; version=0.0.4")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _respond(self, code: int, data: dict[str, object]) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        logger.debug("Health server: %s", format % args)


def start_health_server(port: int = 8080) -> HTTPServer:
    """Start health check HTTP server in a background thread."""
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    logger.info("Health check server started on port %d", port)
    return server
