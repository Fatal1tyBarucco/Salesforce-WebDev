"""Tests for coverage gaps: exceptions, github_ops, content edge cases, reporting."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import openai

import pytest

# ── exceptions.py ──────────────────────────────────────────────────


class TestExceptionHierarchy:
    """Verify custom exception hierarchy is importable and usable."""

    def test_exceptions_importable(self) -> None:
        from src.exceptions import (
            PipelineError,
            ScraperError,
            BrowserError,
            RateLimitError,
            ParserError,
            LLMError,
            LLMProviderExhausted,
            ConfigError,
            ExportError,
            NotificationError,
            GitHubError,
        )

        # All should be Exception subclasses
        assert issubclass(PipelineError, Exception)
        assert issubclass(ScraperError, PipelineError)
        assert issubclass(BrowserError, ScraperError)
        assert issubclass(RateLimitError, ScraperError)
        assert issubclass(ParserError, PipelineError)
        assert issubclass(LLMError, PipelineError)
        assert issubclass(LLMProviderExhausted, LLMError)
        assert issubclass(ConfigError, PipelineError)
        assert issubclass(ExportError, PipelineError)
        assert issubclass(NotificationError, PipelineError)
        assert issubclass(GitHubError, PipelineError)

    def test_exceptions_carry_message(self) -> None:
        from src.exceptions import PipelineError, ScraperError

        e = PipelineError("pipeline broke")
        assert str(e) == "pipeline broke"

        e2 = ScraperError("scrape failed")
        assert str(e2) == "scrape failed"
        assert isinstance(e2, PipelineError)

    def test_exceptions_catch_hierarchy(self) -> None:
        from src.exceptions import BrowserError, ScraperError, PipelineError

        with pytest.raises(PipelineError):
            raise BrowserError("browser died")

        with pytest.raises(ScraperError):
            raise BrowserError("browser died")


# ── github_ops.py ──────────────────────────────────────────────────


class TestGitHubOps:
    """Test GitHub issue creation via CLI."""

    @pytest.mark.asyncio
    async def test_create_issue_success(self, tmp_path: Path) -> None:
        from src.automation.github_ops import create_github_issue

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "https://github.com/org/repo/issues/42\n"

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            url = await create_github_issue("Summer '26", 100, 5)

        assert url == "https://github.com/org/repo/issues/42"
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "gh"
        assert "Release: Summer '26" in call_args

    @pytest.mark.asyncio
    async def test_create_issue_failure(self) -> None:
        from src.automation.github_ops import create_github_issue

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch("subprocess.run", return_value=mock_result):
            url = await create_github_issue("Test", 10, 2)

        assert url is None

    @pytest.mark.asyncio
    async def test_create_issue_exception(self) -> None:
        from src.automation.github_ops import create_github_issue

        with patch("subprocess.run", side_effect=FileNotFoundError("gh not found")):
            url = await create_github_issue("Test", 10, 2)

        assert url is None


# ── content.py edge cases ──────────────────────────────────────────


class TestContentEdgeCases:
    """Test content deduplication edge cases."""

    def test_load_content_cache_corrupt(self, tmp_path: Path) -> None:
        from src.automation.content import load_content_cache

        cache_path = tmp_path / "corrupt.json"
        cache_path.write_text("not valid json {{{", encoding="utf-8")
        result = load_content_cache(cache_path)
        assert result == {}

    def test_load_content_cache_missing(self, tmp_path: Path) -> None:
        from src.automation.content import load_content_cache

        result = load_content_cache(tmp_path / "nope.json")
        assert result == {}

    def test_save_and_load_roundtrip(self, tmp_path: Path) -> None:
        from src.automation.content import save_content_cache, load_content_cache
        from src.automation.models import ContentHash

        cache_path = tmp_path / "cache.json"
        cache = {
            "file.md": ContentHash(
                file_path="file.md",
                content_hash="abc123",
                size_bytes=100,
                last_modified=1234567890.0,
            )
        }
        save_content_cache(cache_path, cache)
        loaded = load_content_cache(cache_path)
        assert "file.md" in loaded
        assert loaded["file.md"].content_hash == "abc123"

    @pytest.mark.asyncio
    async def test_get_content_hash_nonexistent(self) -> None:
        from src.automation.content import get_content_hash

        result = await get_content_hash("/nonexistent/file.txt")
        assert result is None

    @pytest.mark.asyncio
    async def test_is_content_unchanged_nonexistent(self) -> None:
        from src.automation.content import is_content_unchanged

        result = await is_content_unchanged("/nonexistent/file.txt", "abc")
        assert result is False

    @pytest.mark.asyncio
    async def test_analyze_content_nonexistent_release(self) -> None:
        from src.automation.content import analyze_content_changes

        result = await analyze_content_changes("nonexistent_release_slug")
        assert result.unchanged_files == []
        assert result.changed_files == []
        assert result.new_files == []
        assert result.cache_hit_rate == 0.0

    @pytest.mark.asyncio
    async def test_analyze_content_new_files(self, tmp_path: Path) -> None:
        from src.automation.content import analyze_content_changes

        release_dir = tmp_path / "test_release"
        release_dir.mkdir()
        (release_dir / "feature.md").write_text("# Feature\nContent here", encoding="utf-8")

        with patch("src.automation.content._get_releases_dir", return_value=tmp_path):
            result = await analyze_content_changes("test_release")

        assert len(result.new_files) == 1
        assert result.cache_hit_rate == 0.0

    @pytest.mark.asyncio
    async def test_analyze_content_unchanged_files(self, tmp_path: Path) -> None:
        from src.automation.content import analyze_content_changes

        release_dir = tmp_path / "test_release"
        release_dir.mkdir()
        (release_dir / "feature.md").write_text("# Feature\nContent here", encoding="utf-8")

        with patch("src.automation.content._get_releases_dir", return_value=tmp_path):
            # First run — all new
            await analyze_content_changes("test_release")
            # Second run — all unchanged
            result = await analyze_content_changes("test_release")

        assert len(result.unchanged_files) == 1
        assert len(result.new_files) == 0
        assert result.cache_hit_rate == 1.0

    @pytest.mark.asyncio
    async def test_generate_deduplication_report_all_types(self, tmp_path: Path) -> None:
        from src.automation.content import generate_deduplication_report
        from src.automation.models import DeduplicationResult

        with patch(
            "src.automation.content.analyze_content_changes",
            return_value=DeduplicationResult(
                unchanged_files=["unchanged.md"],
                changed_files=["changed.md"],
                new_files=["new.md"],
                removed_files=["removed.md"],
                total_savings_bytes=500,
                cache_hit_rate=0.5,
            ),
        ):
            report = await generate_deduplication_report("test_release")

        assert "Inalterados" in report
        assert "Alterados" in report
        assert "Novos" in report
        assert "Removidos" in report
        assert "500" in report


# ── reporting.py edge cases ────────────────────────────────────────


class TestReportingEdgeCases:
    """Test report generation edge cases."""

    @pytest.mark.asyncio
    async def test_generate_changelog_no_releases_dir(self, tmp_path: Path) -> None:
        from src.automation.reporting import generate_changelog

        with patch(
            "src.automation.reporting._get_releases_dir", return_value=tmp_path / "nonexistent"
        ):
            report = await generate_changelog(llm=None, load_meta_fn=lambda slug: None)
        assert "No releases found" in report

    @pytest.mark.asyncio
    async def test_generate_changelog_empty_metas(self, tmp_path: Path) -> None:
        from src.automation.reporting import generate_changelog

        (tmp_path / "release1").mkdir()
        with patch("src.automation.reporting._get_releases_dir", return_value=tmp_path):
            report = await generate_changelog(llm=None, load_meta_fn=lambda slug: None)
        assert "No releases found" in report

    @pytest.mark.asyncio
    async def test_generate_diff_report_no_meta(self) -> None:
        from src.automation.reporting import generate_diff_report
        from src.automation.models import ReleaseComparison

        comparison = ReleaseComparison(
            current_name="Summer '26",
            previous_name="Spring '26",
            new_categories=[],
            removed_categories=[],
            changed_categories=[],
        )

        mock_llm = MagicMock()
        mock_llm.generate_text = AsyncMock(return_value=None)

        report = await generate_diff_report(
            llm=mock_llm,
            load_meta_fn=lambda slug: None,
            comparison=comparison,
            current_slug="summer_26",
            previous_slug="spring_26",
        )
        assert "Diff" in report or "Anterior" in report

    @pytest.mark.asyncio
    async def test_generate_regression_report_no_regressions(self) -> None:
        from src.automation.reporting import generate_regression_report
        from src.automation.models import ReleaseComparison

        comparison = ReleaseComparison(
            current_name="Summer '26",
            previous_name="Spring '26",
            new_categories=[],
            removed_categories=[],
            changed_categories=[],
        )

        mock_llm = MagicMock()
        mock_llm.generate_text = AsyncMock(return_value=None)

        report = await generate_regression_report(
            llm=mock_llm,
            comparison=comparison,
            regressions=[],
        )
        assert "Nenhuma Regressão" in report or "regress" in report.lower()


# ── api.py GraphQL edge cases ──────────────────────────────────────


class TestGraphQLFieldSelection:
    """Test GraphQL field selection and edge cases."""

    def test_graphql_select_fields_empty(self) -> None:
        from src.api import _select_graphql_fields

        data = {"name": "Test", "slug": "test"}
        result = _select_graphql_fields(data, [])
        # Empty fields returns full data (no filtering)
        assert result == data

    def test_graphql_select_fields_mapped(self) -> None:
        from src.api import _select_graphql_fields

        data = {"name": "Test", "total_features": 100}
        result = _select_graphql_fields(data, ["name", "totalFeatures"])
        assert result == {"name": "Test", "totalFeatures": 100}

    def test_graphql_select_fields_unknown(self) -> None:
        from src.api import _select_graphql_fields

        data = {"name": "Test"}
        result = _select_graphql_fields(data, ["unknownField"])
        assert result == {}

    def test_graphql_extract_fields_with_keywords(self) -> None:
        from src.api import _extract_requested_fields

        # The function works on already-stripped query (outer braces removed)
        query = "releases { name slug query mutation }"
        fields = _extract_requested_fields(query)
        assert "query" not in fields
        assert "mutation" not in fields
        assert "name" in fields
        assert "slug" in fields

    def test_graphql_extract_fields_no_braces(self) -> None:
        from src.api import _extract_requested_fields

        query = "releases"
        fields = _extract_requested_fields(query)
        assert fields == []

    def test_graphql_unknown_operation(self) -> None:
        from src.api import _execute_graphql

        result = _execute_graphql("{ unknown { field } }")
        assert "errors" in result

    def test_graphql_multiple_operations(self) -> None:
        from src.api import _execute_graphql

        result = _execute_graphql('{ releases { name } release(slug: "x") { name } }')
        assert "errors" in result

    def test_graphql_release_not_found(self, tmp_path: Path) -> None:
        from src.api import _execute_graphql

        with patch("src.api.KNOWN_RELEASES", []):
            result = _execute_graphql('{ release(slug: "nonexistent") { name } }')
        assert result.get("data", {}).get("release") is None
        assert "errors" in result

    def test_graphql_diff_not_found(self, tmp_path: Path) -> None:
        from src.api import _execute_graphql

        with patch("src.api.KNOWN_RELEASES", []):
            result = _execute_graphql(
                '{ diff(current: "nonexistent", previous: "also_nonexistent") { totalDelta } }'
            )
        assert "errors" in result


# ── LLM Service resilience ─────────────────────────────────────────


class TestLLMServiceResilience:
    """Test LLM service timeout and retry behavior."""

    def _make_service(self, providers: list | None = None) -> Any:
        from src.llm_service import LLMService, LLMProvider, CircuitBreakerConfig

        if providers is None:
            providers = [
                LLMProvider(
                    name="test",
                    api_key="sk-test",
                    base_url="http://localhost:1",
                    model="gpt-4o",
                    provider_type="openai",
                )
            ]
        with patch.dict(os.environ, {}, clear=True):
            service = LLMService(config=CircuitBreakerConfig(threshold=1, cooldown=0))
        service._providers = providers
        service._provider_states = {
            p.name: MagicMock(failures=0, circuit_open=False) for p in providers
        }
        service._client = None
        return service

    @pytest.mark.asyncio
    async def test_openai_timeout(self) -> None:
        service = self._make_service()
        with patch.object(
            service, "_call_provider", new=AsyncMock(side_effect=TimeoutError("timed out"))
        ):
            result = await service.generate_text("test", "test")
        assert result is None

    @pytest.mark.asyncio
    async def test_rate_limit_error_handled(self) -> None:
        from src.llm_service import ProviderState

        service = self._make_service()
        service._provider_states = {"test": ProviderState()}

        with patch("src.llm_service.openai.AsyncOpenAI") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=openai.RateLimitError(
                    message="rate limited",
                    response=MagicMock(status_code=429, headers={}),
                    body=None,
                )
            )
            mock_client_cls.return_value = mock_client
            result = await service.generate_text("test", "test")

        assert result is None

    @pytest.mark.asyncio
    async def test_auth_error_handled(self) -> None:
        from src.llm_service import ProviderState

        service = self._make_service()
        service._provider_states = {"test": ProviderState()}

        with patch("src.llm_service.openai.AsyncOpenAI") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create = AsyncMock(
                side_effect=openai.AuthenticationError(
                    message="auth failed",
                    response=MagicMock(status_code=401, headers={}),
                    body=None,
                )
            )
            mock_client_cls.return_value = mock_client
            result = await service.generate_text("test", "test")

        assert result is None


# ── Automation Service edge cases ──────────────────────────────────


class TestAutomationServiceEdges:
    """Test automation service wrapper methods."""

    def test_generate_dynamic_badge_via_service(self) -> None:
        from src.automation.service import AIAutomationService

        service = AIAutomationService()
        badge = service.generate_dynamic_badge("Summer '26", 100)
        assert "Summer" in badge
        assert "shields.io" in badge


# ── OpenAPI spec ───────────────────────────────────────────────────


class TestOpenAPISpec:
    """Test OpenAPI spec loading."""

    def test_spec_loads_valid_json(self) -> None:
        from src.api import _generate_openapi_spec

        spec = _generate_openapi_spec()
        assert spec["openapi"] == "3.0.3"
        assert "/releases" in spec["paths"]
        assert "/graphql" in spec["paths"]
        assert "Release" in spec["components"]["schemas"]

    def test_spec_has_all_endpoints(self) -> None:
        from src.api import _generate_openapi_spec

        spec = _generate_openapi_spec()
        paths = spec["paths"]
        assert "/releases" in paths
        assert "/releases/{slug}" in paths
        assert "/releases/{slug}/categories/{name}" in paths
        assert "/diff/{current}/{previous}" in paths
        assert "/graphql" in paths
