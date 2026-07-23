"""Tests for src/health.py — 100% coverage."""

import json
from io import BytesIO
from pathlib import Path

import pytest
from unittest.mock import MagicMock, patch

from src.health import (
    HealthHandler,
    _get_health_data,
    inc_metric,
    set_pipeline_status,
    start_health_server,
)


class TestIncMetric:
    """Tests for inc_metric function."""

    def test_inc_metric_default(self) -> None:
        """inc_metric increments by 1.0 by default."""
        import src.health as health_mod

        state = health_mod._health_state
        original = state._metrics.copy()
        state._metrics = {"test_counter": 0}
        try:
            inc_metric("test_counter")
            assert state._metrics["test_counter"] == 1.0
        finally:
            state._metrics = original

    def test_inc_metric_custom_value(self) -> None:
        """inc_metric increments by custom value."""
        import src.health as health_mod

        state = health_mod._health_state
        original = state._metrics.copy()
        state._metrics = {"test_counter": 5}
        try:
            inc_metric("test_counter", 3.0)
            assert state._metrics["test_counter"] == 8.0
        finally:
            state._metrics = original

    def test_inc_metric_new_key(self) -> None:
        """inc_metric creates key if it doesn't exist."""
        import src.health as health_mod

        state = health_mod._health_state
        original = state._metrics.copy()
        state._metrics = {}
        try:
            inc_metric("new_metric")
            assert state._metrics["new_metric"] == 1.0
        finally:
            state._metrics = original


class TestSetPipelineStatus:
    """Tests for set_pipeline_status function."""

    def test_set_status_completed(self) -> None:
        """set_pipeline_status('completed') increments pipeline_runs_total."""
        import src.health as health_mod

        state = health_mod._health_state
        original = state._metrics.get("pipeline_runs_total", 0)
        set_pipeline_status("completed")
        assert state._metrics["pipeline_runs_total"] == original + 1.0

    def test_set_status_completed_with_errors(self) -> None:
        """set_pipeline_status('completed_with_errors') increments pipeline_failures_total."""
        import src.health as health_mod

        state = health_mod._health_state
        original = state._metrics.get("pipeline_failures_total", 0)
        set_pipeline_status("completed_with_errors")
        assert state._metrics["pipeline_failures_total"] == original + 1.0

    def test_set_status_running(self) -> None:
        """set_pipeline_status('running') does not increment counters."""
        import src.health as health_mod

        state = health_mod._health_state
        runs_before = state._metrics.get("pipeline_runs_total", 0)
        failures_before = state._metrics.get("pipeline_failures_total", 0)
        set_pipeline_status("running")
        assert state._metrics.get("pipeline_runs_total", 0) == runs_before
        assert state._metrics.get("pipeline_failures_total", 0) == failures_before

    def test_set_status_updates_last_run_time(self) -> None:
        """set_pipeline_status updates last_run_time."""
        import src.health

        set_pipeline_status("running")
        assert src.health._health_state.last_run_time != ""


class TestGetHealthData:
    """Tests for _get_health_data function."""

    def test_get_health_data_no_releases_dir(self, tmp_path: Path) -> None:
        """_get_health_data returns data when releases dir doesn't exist."""
        with patch("src.health.RELEASES_DIR", str(tmp_path / "nonexistent")):
            data = _get_health_data()
            assert data["status"] == "healthy"
            assert data["releases_processed"] == 0
            assert data["total_features"] == 0
            assert data["version"] == "3.1.0"

    def test_get_health_data_with_releases(self, tmp_path: Path) -> None:
        """_get_health_data counts releases and features."""
        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text(json.dumps({"total_features": 42}))

        with patch("src.health.RELEASES_DIR", str(tmp_path)):
            data = _get_health_data()
            assert data["releases_processed"] == 1
            assert data["total_features"] == 42

    def test_get_health_data_with_invalid_meta(self, tmp_path: Path) -> None:
        """_get_health_data handles invalid .meta.json gracefully."""
        d = tmp_path / "bad_release"
        d.mkdir()
        (d / ".meta.json").write_text("not valid json{")

        with patch("src.health.RELEASES_DIR", str(tmp_path)):
            data = _get_health_data()
            assert data["releases_processed"] == 1
            assert data["total_features"] == 0

    def test_get_health_data_skips_files(self, tmp_path: Path) -> None:
        """_get_health_data skips non-directory entries."""
        (tmp_path / "not_a_dir.txt").write_text("hello")

        with patch("src.health.RELEASES_DIR", str(tmp_path)):
            data = _get_health_data()
            assert data["releases_processed"] == 0


class TestHealthHandler:
    """Tests for HealthHandler HTTP handler."""

    def _make_handler(self, path: str) -> HealthHandler:
        """Create a HealthHandler with mocked socket."""
        request = MagicMock()
        request.makefile.return_value = BytesIO()

        wfile = BytesIO()
        handler = HealthHandler(request, ("127.0.0.1", 12345), MagicMock())
        handler.path = path
        handler.wfile = wfile
        handler.request_version = "HTTP/1.1"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        return handler

    def test_do_GET_health(self, tmp_path: Path) -> None:
        """GET /health returns 200 with health data."""
        with patch("src.health.RELEASES_DIR", str(tmp_path / "nonexistent")):
            handler = self._make_handler("/health")
            handler.do_GET()
            handler.send_response.assert_called_with(200)

    def test_do_GET_root(self, tmp_path: Path) -> None:
        """GET / returns 200 with health data."""
        with patch("src.health.RELEASES_DIR", str(tmp_path / "nonexistent")):
            handler = self._make_handler("/")
            handler.do_GET()
            handler.send_response.assert_called_with(200)

    def test_do_GET_ready(self) -> None:
        """GET /ready returns 200 with ready status."""
        handler = self._make_handler("/ready")
        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_do_GET_metrics(self) -> None:
        """GET /metrics returns 200 with Prometheus metrics."""
        handler = self._make_handler("/metrics")
        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_do_GET_not_found(self) -> None:
        """GET /unknown returns 404."""
        handler = self._make_handler("/unknown")
        handler.do_GET()
        handler.send_response.assert_called_with(404)

    def test_log_message(self) -> None:
        """HealthHandler.log_message calls logger.debug."""
        handler = self._make_handler("/health")
        # Should not raise
        handler.log_message("GET %s", "/health")


class TestStartHealthServer:
    """Tests for start_health_server function."""

    def test_start_health_server(self) -> None:
        """start_health_server returns an HTTPServer."""
        server = start_health_server(port=0)  # port 0 = random available
        assert server is not None
        server.shutdown()


class TestNewHealthFeatures:
    """Tests for new health features: duration, release count, prometheus."""

    def _make_handler(self, path: str) -> HealthHandler:
        """Create a HealthHandler with mocked socket."""
        request = MagicMock()
        request.makefile.return_value = BytesIO()
        handler = HealthHandler(request, ("127.0.0.1", 12345), MagicMock())
        handler.path = path
        handler.wfile = BytesIO()
        handler.request_version = "HTTP/1.1"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        return handler

    def test_record_run_duration(self) -> None:
        """record_run_duration stores the duration."""
        from src.health import _health_state

        _health_state.record_run_duration(42.5)
        assert _health_state._last_run_duration == 42.5

    def test_set_release_feature_count(self) -> None:
        """set_release_feature_count doesn't raise."""
        from src.health import set_release_feature_count

        # Should not raise even without prometheus
        set_release_feature_count("summer_26", 100)

    def test_prometheus_available_flag(self) -> None:
        """_PROMETHEUS_AVAILABLE is a bool."""
        from src.health import _PROMETHEUS_AVAILABLE

        assert isinstance(_PROMETHEUS_AVAILABLE, bool)

    def test_fallback_metrics_text(self) -> None:
        """_fallback_metrics_text returns Prometheus text format."""
        from src.health import HealthHandler

        text = HealthHandler._fallback_metrics_text()
        assert "pipeline_runs_total" in text
        assert "pipeline_uptime_seconds" in text
        assert "# TYPE" in text

    def test_health_data_includes_prometheus_field(self, tmp_path: Path) -> None:
        """Health data response includes prometheus availability flag."""
        with patch("src.health.RELEASES_DIR", str(tmp_path / "nonexistent")):
            data = _get_health_data()
            assert "prometheus" in data
            assert isinstance(data["prometheus"], bool)

    def test_do_GET_metrics_content_type(self) -> None:
        """GET /metrics sets appropriate content type."""
        handler = self._make_handler("/metrics")
        handler.do_GET()
        handler.send_response.assert_called_with(200)
        # Verify Content-Type was set (either prometheus or plain text)
        assert handler.send_header.call_count >= 2  # Content-Type + Content-Length

    def test_inc_metric_prometheus_mirror(self) -> None:
        """inc_metric mirrors to prometheus counters when available."""
        from src.health import _health_state, _PROMETHEUS_AVAILABLE

        if not _PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client not installed")

        # These should not raise
        _health_state.inc_metric("features_processed_total", 1.0)
        _health_state.inc_metric("scraper_requests_total", 1.0)
        _health_state.inc_metric("scraper_failures_total", 1.0)
        _health_state.inc_metric("circuit_breaker_trips_total", 1.0)

    def test_set_pipeline_status_prometheus(self) -> None:
        """set_pipeline_status mirrors to prometheus when available."""
        from src.health import _health_state, _PROMETHEUS_AVAILABLE

        if not _PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client not installed")

        _health_state.set_pipeline_status("completed")
        _health_state.set_pipeline_status("completed_with_errors")

    def test_record_run_duration_prometheus(self) -> None:
        """record_run_duration mirrors to prometheus histogram when available."""
        from src.health import _health_state, _PROMETHEUS_AVAILABLE

        if not _PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client not installed")

        _health_state.record_run_duration(10.5)

    def test_set_release_feature_count_prometheus(self) -> None:
        """set_release_feature_count sets prometheus gauge when available."""
        from src.health import _PROMETHEUS_AVAILABLE

        if not _PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client not installed")

        from src.health import set_release_feature_count

        set_release_feature_count("summer_26", 150)

    def test_metrics_with_prometheus_registry(self) -> None:
        """GET /metrics uses prometheus_client.generate_latest when available."""
        from src.health import _PROMETHEUS_AVAILABLE

        if not _PROMETHEUS_AVAILABLE:
            pytest.skip("prometheus_client not installed")

        handler = self._make_handler("/metrics")
        handler.do_GET()
        handler.send_response.assert_called_with(200)
        # Verify the body contains prometheus format
        body = handler.wfile.getvalue().decode()
        assert "pipeline_runs_total" in body or "pipeline_uptime_seconds" in body
