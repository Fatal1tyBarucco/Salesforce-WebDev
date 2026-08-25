"""Tests to cover uncovered lines across multiple modules.

Targets:
- src/automation/badge.py (51% → ~95%)
- src/llm_service.py (77% → ~95%)
- src/orchestrator.py (79% → ~95%)
- src/health.py (83% → ~95%)
- src/cache_manager.py (92% → ~100%)
"""

import asyncio
import json
import logging
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.llm_service import LLMService

# ── badge.py tests ──────────────────────────────────────────────


class TestBadgeCoverage:
    """Cover badge.py lines 60-61, 74-89, 102-118."""

    def test_generate_dynamic_badge(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_dynamic_badge

        result = generate_dynamic_badge("Summer '26", 42)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_latest_release_badge_no_dir(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path / "nonexistent"):
            result = get_latest_release_badge()
            assert result == "N/A"

    def test_get_latest_release_badge_empty_dir(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()
        with patch("src.automation.badge._get_releases_dir", return_value=releases_dir):
            result = get_latest_release_badge()
            assert result == "N/A"

    def test_get_latest_release_badge_with_meta(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        releases_dir = tmp_path / "releases"
        rel_dir = releases_dir / "summer_26"
        rel_dir.mkdir(parents=True)
        meta = {"name": "Summer '26", "release_id": 42, "categories": []}
        (rel_dir / ".meta.json").write_text(json.dumps(meta))

        with patch("src.automation.badge._get_releases_dir", return_value=releases_dir):
            result = get_latest_release_badge()
            assert result == "Summer '26"

    def test_get_latest_release_badge_corrupt_json(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        releases_dir = tmp_path / "releases"
        rel_dir = releases_dir / "summer_26"
        rel_dir.mkdir(parents=True)
        (rel_dir / ".meta.json").write_text("not json")

        with patch("src.automation.badge._get_releases_dir", return_value=releases_dir):
            result = get_latest_release_badge()
            assert result == "N/A"

    def test_get_latest_release_badge_picks_highest_id(self, tmp_path: Path) -> None:
        from src.automation.badge import get_latest_release_badge

        releases_dir = tmp_path / "releases"
        for slug, rid, name in [("summer_25", 1, "Summer '25"), ("summer_26", 5, "Summer '26")]:
            d = releases_dir / slug
            d.mkdir(parents=True)
            (d / ".meta.json").write_text(json.dumps({"name": name, "release_id": rid}))

        with patch("src.automation.badge._get_releases_dir", return_value=releases_dir):
            result = get_latest_release_badge()
            assert result == "Summer '26"

    def test_generate_release_header_badges_no_meta(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_release_header_badges

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_release_header_badges("nonexistent")
            assert result == ""

    def test_generate_release_header_badges_with_meta(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_release_header_badges

        slug = "summer_26"
        d = tmp_path / slug
        d.mkdir()
        meta = {
            "name": "Summer '26",
            "categories": [{"name": "Security", "count": 10}, {"name": "AI", "count": 5}],
        }
        (d / ".meta.json").write_text(json.dumps(meta))

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_release_header_badges(slug)
            assert isinstance(result, str)

    def test_generate_release_header_badges_corrupt_json(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_release_header_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text("{bad json")

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_release_header_badges("summer_26")
            assert result == ""

    def test_generate_category_badges_no_meta(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_category_badges("nonexistent", "Security")
            assert result == ""

    def test_generate_category_badges_found(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        meta = {"categories": [{"name": "Security", "count": 10}]}
        (d / ".meta.json").write_text(json.dumps(meta))

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_category_badges("summer_26", "Security")
            assert isinstance(result, str)

    def test_generate_category_badges_not_found(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        meta = {"categories": [{"name": "Security", "count": 10}]}
        (d / ".meta.json").write_text(json.dumps(meta))

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_category_badges("summer_26", "NonExistent")
            assert result == ""

    def test_generate_category_badges_corrupt_json(self, tmp_path: Path) -> None:
        from src.automation.badge import generate_category_badges

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text("not json")

        with patch("src.automation.badge._get_releases_dir", return_value=tmp_path):
            result = generate_category_badges("summer_26", "Security")
            assert isinstance(result, str)


# ── llm_service.py tests (modern API) ──────────────────────────


class TestLLMServiceCoverage:
    """Cover llm_service.py uncovered lines (modern API)."""

    def test_empty_prompt_raises(self) -> None:
        svc = LLMService(api_key="k")
        with pytest.raises(ValueError):
            svc.generate_completion("")

    def test_whitespace_prompt_raises(self) -> None:
        svc = LLMService(api_key="k")
        with pytest.raises(ValueError):
            svc.generate_completion("   ")

    def test_mock_openai_no_key(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = svc.generate_completion("hello")
        assert out.startswith("[Mock OpenAI Response]")

    def test_mock_gemini_no_key(self) -> None:
        svc = LLMService(api_key=None, provider="gemini")
        out = svc.generate_completion("hello")
        assert out.startswith("[Mock Gemini Response]")

    def test_unsupported_provider(self) -> None:
        svc = LLMService(api_key="k", provider="banana")
        with pytest.raises(ValueError):
            svc.generate_completion("hi")

    def test_generate_text_alias(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = asyncio.run(svc.generate_text("x"))
        assert out.startswith("[Mock")

    def test_classify_text_with_categories(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = asyncio.run(svc.classify_text("text", categories=["A", "B"]))
        assert out.startswith("[Mock")

    def test_classify_text_no_categories(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = asyncio.run(svc.classify_text("text"))
        assert out.startswith("[Mock")

    def test_summarize(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = svc.summarize("long text")
        assert out.startswith("[Mock")

    @pytest.mark.asyncio
    async def test_summarize_release_notes(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = await svc.summarize_release_notes("notes")
        assert out.startswith("[Mock")

    @pytest.mark.asyncio
    async def test_enrich_feature(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = await svc.enrich_feature({"name": "x"})
        assert out["enriched"] is True
        assert "details" in out

    @pytest.mark.asyncio
    async def test_enrich_feature_with_context(self) -> None:
        svc = LLMService(api_key=None, provider="openai")
        out = await svc.enrich_feature({"name": "x"}, context="ctx")
        assert out["enriched"] is True

    @pytest.mark.asyncio
    async def test_async_context_manager(self) -> None:
        async with LLMService(api_key="k") as svc:
            assert isinstance(svc, LLMService)

    def test_generate_openai_with_client(self) -> None:
        from unittest.mock import MagicMock

        from openai import OpenAI  # noqa: F401

        fake_choice = MagicMock()
        fake_choice.message.content = "result"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_resp
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openai")
            out = svc.generate_completion("hi", system_instruction="sys")
        assert out == "result"

    def test_generate_gemini_with_client(self, monkeypatch) -> None:
        from unittest.mock import MagicMock

        import src.llm_service as ls

        fake_resp = MagicMock()
        fake_resp.text = "gemini-result"
        fake_model = MagicMock()
        fake_model.generate_content.return_value = fake_resp
        fake_client = MagicMock()
        fake_client.models = fake_model
        fake_genai = MagicMock()
        fake_genai.Client.return_value = fake_client
        monkeypatch.setattr(ls, "genai", fake_genai)
        svc = LLMService(api_key="k", provider="gemini")
        out = svc.generate_completion("hi", system_instruction="sys")
        assert out == "gemini-result"


# ── health.py tests ─────────────────────────────────────────────


class TestHealthCoverage:
    """Cover health.py uncovered lines."""

    def test_health_state_init(self) -> None:
        from src.health import HealthState

        state = HealthState()
        assert state.last_run_status == "idle"
        assert state.last_run_time == ""
        assert state.uptime_seconds >= 0
        assert state.metrics["pipeline_runs_total"] == 0

    def test_health_state_inc_metric(self) -> None:
        from src.health import HealthState

        state = HealthState()
        state.inc_metric("pipeline_runs_total", 5)
        assert state.metrics["pipeline_runs_total"] == 5

    def test_health_state_set_pipeline_status_completed(self) -> None:
        from src.health import HealthState

        state = HealthState()
        state.set_pipeline_status("completed")
        assert state.last_run_status == "completed"
        assert state.last_run_time != ""
        assert state.metrics["pipeline_runs_total"] == 1

    def test_health_state_set_pipeline_status_errors(self) -> None:
        from src.health import HealthState

        state = HealthState()
        state.set_pipeline_status("completed_with_errors")
        assert state.metrics["pipeline_failures_total"] == 1

    def test_health_state_record_run_duration(self) -> None:
        from src.health import HealthState

        state = HealthState()
        state.record_run_duration(42.5)
        assert state._last_run_duration == 42.5

    def test_health_state_set_release_feature_count(self) -> None:
        from src.health import HealthState

        state = HealthState()
        state.set_release_feature_count("summer_26", 100)

    def test_health_state_metrics_copy(self) -> None:
        from src.health import HealthState

        state = HealthState()
        m = state.metrics
        m["pipeline_runs_total"] = 999
        assert state.metrics["pipeline_runs_total"] == 0

    def test_module_level_functions(self) -> None:
        from src.health import (
            inc_metric,
            record_run_duration,
            set_pipeline_status,
            set_release_feature_count,
        )

        inc_metric("test_metric", 1)
        set_pipeline_status("running")
        record_run_duration(10.0)
        set_release_feature_count("test", 5)

    def test_get_health_data(self, tmp_path: Path) -> None:
        from src.health import HealthState, _get_health_data

        state = HealthState()
        with patch("src.health.RELEASES_DIR", str(tmp_path)):
            data = _get_health_data(state)
        assert data["status"] == "healthy"
        assert data["version"] == "3.1.0"
        assert data["pipeline_status"] == "idle"

    def test_get_health_data_with_releases(self, tmp_path: Path) -> None:
        from src.health import HealthState, _get_health_data

        d = tmp_path / "summer_26"
        d.mkdir()
        meta = {"total_features": 42, "categories": []}
        (d / ".meta.json").write_text(json.dumps(meta))

        state = HealthState()
        with patch("src.health.RELEASES_DIR", str(tmp_path)):
            data = _get_health_data(state)
        assert data["releases_processed"] == 1
        assert data["total_features"] == 42

    def test_get_health_data_corrupt_meta(self, tmp_path: Path) -> None:
        from src.health import HealthState, _get_health_data

        d = tmp_path / "summer_26"
        d.mkdir()
        (d / ".meta.json").write_text("not json")

        state = HealthState()
        with patch("src.health.RELEASES_DIR", str(tmp_path)):
            data = _get_health_data(state)
        assert data["releases_processed"] == 1

    def test_fallback_metrics_text(self) -> None:
        from src.health import HealthHandler

        text = HealthHandler._fallback_metrics_text()
        assert "pipeline_runs_total" in text
        assert "pipeline_failures_total" in text
        assert "features_processed_total" in text
        assert "scraper_requests_total" in text
        assert "scraper_failures_total" in text
        assert "pipeline_uptime_seconds" in text


# ── cache_manager.py tests ──────────────────────────────────────


class TestCacheManagerCoverage:
    """Cover cache_manager.py remaining uncovered lines."""

    def test_compute_file_hash(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        f = tmp_path / "test.txt"
        f.write_text("hello world")
        h = CacheManager.compute_file_hash(f)
        assert len(h) == 32

    def test_get_content_hash_exists(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        f = tmp_path / "test.txt"
        f.write_text("content")
        h = cache.get_content_hash(f)
        assert h is not None

    def test_get_content_hash_not_exists(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        h = cache.get_content_hash(tmp_path / "nonexistent.txt")
        assert h is None

    def test_is_content_unchanged(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        f = tmp_path / "test.txt"
        f.write_text("content")
        h = cache.get_content_hash(f)
        assert cache.is_content_unchanged(f, h) is True
        assert cache.is_content_unchanged(f, "wrong_hash") is False

    def test_is_content_unchanged_nonexistent(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        assert cache.is_content_unchanged(tmp_path / "nope", "hash") is False

    def test_save_and_load_content_cache(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        cache_file = tmp_path / "content_cache.json"
        data = {"file1.md": "abc123", "file2.md": "def456"}
        cache.save_content_cache(cache_file, data)
        loaded = cache.load_content_cache(cache_file)
        assert loaded == data

    def test_load_content_cache_nonexistent(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        result = cache.load_content_cache(tmp_path / "nope.json")
        assert result == {}

    def test_load_content_cache_corrupt(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        f = tmp_path / "corrupt.json"
        f.write_text("not json")
        result = cache.load_content_cache(f)
        assert result == {}

    def test_load_content_cache_old_format(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        f = tmp_path / "old.json"
        data = {"file.md": {"content_hash": "abc123", "extra": "data"}}
        f.write_text(json.dumps(data))
        result = cache.load_content_cache(f)
        assert result == {"file.md": "abc123"}

    def test_stats_repr(self) -> None:
        from src.cache_manager import CacheStats

        stats = CacheStats(hits=10, misses=2, evictions=1)
        r = repr(stats)
        assert "hits=10" in r
        assert "misses=2" in r

    def test_stats_total(self) -> None:
        from src.cache_manager import CacheStats

        stats = CacheStats(hits=8, misses=2)
        assert stats.total == 10

    def test_stats_hit_rate_zero(self) -> None:
        from src.cache_manager import CacheStats

        stats = CacheStats()
        assert stats.hit_rate == 0.0


# ── orchestrator.py tests ───────────────────────────────────────


class TestOrchestratorCoverage:
    """Cover orchestrator.py uncovered lines."""

    def test_pipeline_result_dataclass(self) -> None:
        from src.orchestrator import PipelineResult

        r = PipelineResult(releases_processed=[], errors=[], status="running")
        assert r.status == "running"

    def test_orchestrator_init(self) -> None:
        from src.orchestrator import PipelineOrchestrator

        config = MagicMock()
        config.event_bus = None
        with patch("src.orchestrator.get_event_bus") as mock_bus:
            PipelineOrchestrator(config)
            assert mock_bus.called

    @pytest.mark.asyncio
    async def test_detect_releases_with_filter(self) -> None:
        from src.orchestrator import PipelineOrchestrator

        release_info = MagicMock()
        release_info.slug = "summer_26"

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = "summer_26"
        config.known_releases = [release_info]

        orch = PipelineOrchestrator(config)
        result = await orch._detect_releases(MagicMock())
        assert len(result) == 1
        assert result[0].slug == "summer_26"

    @pytest.mark.asyncio
    async def test_detect_releases_filter_not_found(self) -> None:
        from src.orchestrator import PipelineOrchestrator

        release_info = MagicMock()
        release_info.slug = "summer_26"

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = "nonexistent"
        config.known_releases = [release_info]

        orch = PipelineOrchestrator(config)
        result = await orch._detect_releases(MagicMock())
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_detect_releases_no_filter_new_release(self) -> None:
        from src.orchestrator import PipelineOrchestrator

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = None
        config.known_releases = None

        mock_release = MagicMock()
        mock_release.slug = "summer_26"

        orch = PipelineOrchestrator(config)
        with patch(
            "src.main.detect_new_release", new_callable=AsyncMock, return_value=mock_release
        ):
            result = await orch._detect_releases(MagicMock())
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_detect_releases_no_filter_no_new(self) -> None:
        from src.orchestrator import PipelineOrchestrator

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()
        config.release_filter = None
        config.known_releases = None

        orch = PipelineOrchestrator(config)
        with patch("src.main.detect_new_release", new_callable=AsyncMock, return_value=None):
            result = await orch._detect_releases(MagicMock())
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_run_ai_reports_no_llm(self) -> None:
        from src.orchestrator import PipelineOrchestrator, PipelineResult

        config = MagicMock()
        config.event_bus = MagicMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")

        with patch("src.release_docs.update_readme_all", new_callable=AsyncMock):
            await orch._run_ai_reports([], None, result)
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_run_ai_reports_success(self) -> None:
        from src.orchestrator import PipelineOrchestrator, PipelineResult

        config = MagicMock()
        config.event_bus = MagicMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")
        mock_llm = MagicMock()

        with (
            patch("src.release_docs.update_readme_all", new_callable=AsyncMock),
            patch("src.main.generate_ai_reports_async", new_callable=AsyncMock),
        ):
            await orch._run_ai_reports([MagicMock()], mock_llm, result)
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_run_ai_reports_error(self) -> None:
        from src.exceptions import LLMError
        from src.orchestrator import PipelineOrchestrator, PipelineResult

        config = MagicMock()
        config.event_bus = MagicMock()
        config.event_bus.emit = AsyncMock()

        orch = PipelineOrchestrator(config)
        result = PipelineResult(releases_processed=[], errors=[], status="running")
        mock_llm = MagicMock()

        with (
            patch("src.release_docs.update_readme_all", new_callable=AsyncMock),
            patch(
                "src.main.generate_ai_reports_async",
                new_callable=AsyncMock,
                side_effect=LLMError("fail"),
            ),
        ):
            await orch._run_ai_reports([MagicMock()], mock_llm, result)
        assert result.status == "completed_with_errors"
        assert len(result.errors) == 1


# ── logger.py tests ─────────────────────────────────────────────


class TestLoggerCoverage:
    """Cover logger.py uncovered lines (sentry setup)."""

    def test_setup_sentry_no_dsn(self) -> None:
        from src.logger import _setup_sentry

        with patch.dict("os.environ", {}, clear=False):
            # Should not raise, just return early
            _setup_sentry()

    def test_setup_sentry_with_dsn_no_sdk(self) -> None:
        from src.logger import _setup_sentry

        with (
            patch.dict("os.environ", {"SENTRY_DSN": "https://example@sentry.io/123"}, clear=False),
            patch.dict("sys.modules", {"sentry_sdk": None}),
        ):
            # Should handle ImportError gracefully
            _setup_sentry()

    def test_setup_sentry_with_dsn_and_sdk(self) -> None:
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
            patch.dict("sys.modules", {"sentry_sdk": mock_sdk}),
        ):
            _setup_sentry()
            mock_sdk.init.assert_called_once()

    def test_setup_logging_json(self) -> None:
        from src.logger import setup_logging

        setup_logging(json_format=True)

    def test_setup_logging_text(self) -> None:
        from src.logger import setup_logging

        setup_logging(json_format=False)

    def test_new_correlation_id(self) -> None:
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


# ── health.py HTTP handler tests ────────────────────────────────


class TestHealthHandlerCoverage:
    """Cover health.py HTTP handler and start_health_server lines."""

    def _make_handler(self, path: str) -> MagicMock:
        """Create a mock HealthHandler with the given path."""
        from src.health import HealthHandler

        handler = HealthHandler.__new__(HealthHandler)
        handler.path = path
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.wfile = MagicMock()
        handler.wfile.write = MagicMock()
        return handler

    def test_health_handler_do_get_health(self) -> None:
        handler = self._make_handler("/health")
        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_health_handler_do_get_ready(self) -> None:
        handler = self._make_handler("/ready")
        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_health_handler_do_get_metrics(self) -> None:
        handler = self._make_handler("/metrics")
        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_health_handler_do_get_not_found(self) -> None:
        handler = self._make_handler("/unknown")
        handler.do_GET()
        handler.send_response.assert_called_with(404)

    def test_health_handler_do_get_root(self) -> None:
        handler = self._make_handler("/")
        handler.do_GET()
        handler.send_response.assert_called_with(200)

    def test_start_health_server(self) -> None:
        from src.health import start_health_server

        server = start_health_server(port=18765)
        assert server is not None
        server.shutdown()


# ── automation/impact.py tests ──────────────────────────────────


class TestImpactCoverage:
    """Cover automation/impact.py uncovered lines."""

    @pytest.mark.asyncio
    async def test_calculate_category_impact_scores_insufficient_data(self, tmp_path: Path) -> None:
        from src.automation.impact import calculate_category_impact_scores

        def load_meta_fn(slug: str) -> dict | None:
            return {"categories": [{"name": "Security", "count": 10}]}

        releases_dir = tmp_path / "releases"
        releases_dir.mkdir()
        (releases_dir / "summer_25").mkdir()

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert result == []

    @pytest.mark.asyncio
    async def test_calculate_category_impact_scores_growth(self, tmp_path: Path) -> None:
        from src.automation.impact import calculate_category_impact_scores

        call_count = 0

        def load_meta_fn(slug: str) -> dict | None:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return {"release_id": call_count, "categories": [{"name": "Security", "count": 10}]}
            return {"release_id": call_count, "categories": [{"name": "Security", "count": 60}]}

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert len(result) == 1
        assert result[0].category == "Security"
        assert result[0].trend == "crescimento"

    @pytest.mark.asyncio
    async def test_calculate_category_impact_scores_decline(self, tmp_path: Path) -> None:
        from src.automation.impact import calculate_category_impact_scores

        call_count = 0

        def load_meta_fn(slug: str) -> dict | None:
            nonlocal call_count
            call_count += 1
            counts = [60, 30, 10]
            return {
                "release_id": call_count,
                "categories": [{"name": "AI", "count": counts[call_count - 1]}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert len(result) == 1
        assert result[0].trend == "declínio"

    @pytest.mark.asyncio
    async def test_calculate_category_impact_scores_stable(self, tmp_path: Path) -> None:
        from src.automation.impact import calculate_category_impact_scores

        call_count = 0

        def load_meta_fn(slug: str) -> dict | None:
            nonlocal call_count
            call_count += 1
            return {
                "release_id": call_count,
                "categories": [{"name": "AI", "count": 50 + call_count}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert len(result) == 1
        assert result[0].trend == "estável"

    @pytest.mark.asyncio
    async def test_calculate_category_impact_scores_high_volatility(self, tmp_path: Path) -> None:
        from src.automation.impact import calculate_category_impact_scores

        call_count = 0

        def load_meta_fn(slug: str) -> dict | None:
            nonlocal call_count
            call_count += 1
            counts = [10, 100, 10, 100]
            return {
                "release_id": call_count,
                "categories": [{"name": "Security", "count": counts[call_count - 1]}],
            }

        releases_dir = tmp_path / "releases"
        for s in ["s24", "s25", "s26", "s27"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert len(result) == 1
        assert result[0].risk_score > 20
        assert "significativa" in result[0].prediction

    @pytest.mark.asyncio
    async def test_calculate_category_impact_scores_empty_categories(self, tmp_path: Path) -> None:
        from src.automation.impact import calculate_category_impact_scores

        def load_meta_fn(slug: str) -> dict | None:
            return {"categories": []}

        releases_dir = tmp_path / "releases"
        for s in ["s25", "s26"]:
            (releases_dir / s).mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await calculate_category_impact_scores(load_meta_fn)
        assert result == []

    @pytest.mark.asyncio
    async def test_load_all_release_metas_no_dir(self) -> None:
        from src.automation.impact import _load_all_release_metas

        def load_meta_fn(slug: str) -> dict | None:
            return {"categories": [{"name": "X", "count": 1}]}

        with patch("src.config.RELEASES_DIR", "/nonexistent/path"):
            result = await _load_all_release_metas(load_meta_fn)
        assert result == []

    @pytest.mark.asyncio
    async def test_load_all_release_metas_with_data(self, tmp_path: Path) -> None:
        from src.automation.impact import _load_all_release_metas

        def load_meta_fn(slug: str) -> dict | None:
            return {"release_id": 1, "categories": [{"name": "X", "count": 5}]}

        releases_dir = tmp_path / "releases"
        (releases_dir / "summer_25").mkdir(parents=True)
        (releases_dir / "summer_26").mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await _load_all_release_metas(load_meta_fn)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_load_all_release_metas_returns_none(self, tmp_path: Path) -> None:
        from src.automation.impact import _load_all_release_metas

        def load_meta_fn(slug: str) -> dict | None:
            return None

        releases_dir = tmp_path / "releases"
        (releases_dir / "summer_25").mkdir(parents=True)

        with patch("src.config.RELEASES_DIR", str(releases_dir)):
            result = await _load_all_release_metas(load_meta_fn)
        assert result == []


# ── circuit_breaker.py tests ────────────────────────────────────


class TestCircuitBreakerCoverage:
    """Cover circuit_breaker.py remaining lines."""

    def test_reset(self) -> None:
        from src.circuit_breaker import CircuitBreaker

        cb = CircuitBreaker(threshold=3, cooldown=60)
        cb.record_failure()
        cb.record_failure()
        assert cb._failures == 2
        cb.reset()
        assert cb._failures == 0
        assert cb._opened_at == 0.0

    def test_repr_closed(self) -> None:
        from src.circuit_breaker import CircuitBreaker

        cb = CircuitBreaker(threshold=3, cooldown=60)
        r = repr(cb)
        assert "CLOSED" in r
        assert "failures=0" in r

    def test_repr_open(self) -> None:
        from src.circuit_breaker import CircuitBreaker

        cb = CircuitBreaker(threshold=1, cooldown=60)
        cb.record_failure()
        r = repr(cb)
        assert "OPEN" in r


# ── cache_manager.py edge case tests ────────────────────────────


class TestCacheManagerEdgeCases:
    """Cover cache_manager.py remaining lines."""

    def test_invalidate_nonexistent(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        cache.invalidate("nonexistent_key")

    def test_invalidate_namespace_empty(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        count = cache.invalidate_namespace("nonexistent_ns")
        assert count == 0

    def test_invalidate_namespace_with_entries(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache")
        cache.set("k1", "v1", namespace="test_ns")
        cache.set("k2", "v2", namespace="test_ns")
        count = cache.invalidate_namespace("test_ns")
        assert count == 2
        assert cache.get("k1", namespace="test_ns") is None

    def test_get_expired_entry(self, tmp_path: Path) -> None:
        from src.cache_manager import CacheManager

        cache = CacheManager(tmp_path / "cache", ttl_seconds=1)
        cache.set("key", "value", ttl=0)
        import time as time_mod

        time_mod.sleep(0.01)
        result = cache.get("key")
        assert result is None
        assert cache.stats.evictions == 1
