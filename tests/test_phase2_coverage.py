"""Tests for coverage gaps: exceptions, github_ops, content edge cases, reporting."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlparse

import pytest

# ── exceptions.py ──────────────────────────────────────────────────


class TestExceptionHierarchy:
    """Verify custom exception hierarchy is importable and usable."""

    def test_exceptions_importable(self) -> None:
        from src.exceptions import (
            BrowserError,
            ConfigError,
            ExportError,
            GitHubError,
            LLMError,
            LLMProviderExhausted,
            NotificationError,
            ParserError,
            PipelineError,
            RateLimitError,
            ScraperError,
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
        from src.exceptions import BrowserError, PipelineError, ScraperError

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
        from src.automation.content import load_content_cache, save_content_cache
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
        from src.automation.models import ReleaseComparison
        from src.automation.reporting import generate_diff_report

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
        from src.automation.models import ReleaseComparison
        from src.automation.reporting import generate_regression_report

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


class TestLLMServiceResilience:
    """Test LLM service error handling (modern API)."""

    def test_empty_prompt_raises_value_error(self) -> None:
        from src.llm_service import LLMService

        svc = LLMService(api_key="k")
        with pytest.raises(ValueError):
            svc.generate_completion("")

    def test_no_key_returns_mock(self) -> None:
        from src.llm_service import LLMService

        svc = LLMService(api_key=None, provider="none")
        out = svc.generate_completion("anything")
        assert out.startswith("[Mock LLM Response]")

    def test_unsupported_provider_falls_back(self) -> None:
        from src.llm_service import LLMService

        svc = LLMService(api_key="k", provider="nope")
        # Unknown provider triggers auto-detect; with a key it picks the
        # first provider whose env var is set, or 'none' if none match.
        assert svc.provider in ("gemini", "opencode", "openrouter", "none")

    def test_generate_completion_propagates_errors(self) -> None:
        from src.llm_service import LLMService

        svc = LLMService(api_key="k", provider="openrouter")
        with patch("openai.OpenAI", side_effect=RuntimeError("boom")):
            with pytest.raises(RuntimeError):
                svc.generate_completion("x")


# ── LLM Service provider chain coverage ────────────────────────────


class TestLLMProviderChain:
    """Tests for the multi-provider fallback chain."""

    def test_find_provider_config_valid(self) -> None:
        from src.llm_service import LLMService

        cfg = LLMService._find_provider_config("gemini")
        assert cfg is not None
        assert cfg.name == "gemini"

    def test_find_provider_config_invalid(self) -> None:
        from src.llm_service import LLMService

        cfg = LLMService._find_provider_config("nonexistent")
        assert cfg is None

    def test_switch_to_next_provider_no_fallback(self, monkeypatch) -> None:
        from src.llm_service import LLMService

        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENCODE_API_KEY", raising=False)
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        svc = LLMService(api_key=None, provider="none")
        # No providers available -> switch returns False
        assert svc._switch_to_next_provider() is False

    def test_dispatch_unsupported_provider(self) -> None:
        from src.llm_service import LLMService

        svc = LLMService(api_key="k", provider="gemini")
        svc.provider = "unknown_provider"
        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            svc._dispatch_to_provider("hi", None, 0.7, 100)

    def test_openai_compatible_all_models_fail(self, monkeypatch) -> None:
        from unittest.mock import MagicMock, patch

        from src.llm_service import LLMService

        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = RuntimeError("boom")
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter")
            with pytest.raises(RuntimeError):
                svc._generate_openai_compatible("hi", None, 0.7, 100)

    def test_openai_compatible_fallback_model(self, monkeypatch) -> None:
        from unittest.mock import MagicMock, patch

        from src.llm_service import LLMService

        fake_choice = MagicMock()
        fake_choice.message.content = "fallback result"
        fake_resp = MagicMock()
        fake_resp.choices = [fake_choice]
        fake_client = MagicMock()
        # First model fails, second succeeds
        fake_client.chat.completions.create.side_effect = [
            RuntimeError("model unavailable"),
            fake_resp,
        ]
        with patch("openai.OpenAI", return_value=fake_client):
            svc = LLMService(api_key="k", provider="openrouter")
            out = svc._generate_openai_compatible("hi", None, 0.7, 100)
            assert out == "fallback result"


# ── Automation Service edge cases ──────────────────────────────────


class TestAutomationServiceEdges:
    """Test automation service wrapper methods."""

    def test_generate_dynamic_badge_via_service(self) -> None:
        import re

        from src.automation.service import AIAutomationService

        service = AIAutomationService()
        badge = service.generate_dynamic_badge("Summer '26", 100)
        assert "Summer" in badge
        # O resultado é Markdown: ![label](url). Extrai a primeira URL.
        urls = re.findall(r"https?://[^\s)]+", badge)
        assert len(urls) >= 1
        host = urlparse(urls[0]).hostname
        assert host is not None
        assert host == "img.shields.io" or host.endswith(".shields.io")
