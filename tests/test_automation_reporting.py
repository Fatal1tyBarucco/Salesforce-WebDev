"""Tests for src/automation/reporting.py — 100% coverage target."""

from unittest.mock import AsyncMock

import pytest


class TestGenerateAISummaryReport:
    """generate_ai_summary_report: LLM-powered release summary."""

    @pytest.mark.asyncio
    async def test_no_highlights_no_risks(self) -> None:
        from src.automation.models import ReleaseComparison
        from src.automation.reporting import generate_ai_summary_report

        mock_llm = AsyncMock()
        mock_llm.generate_text.return_value = None

        comp = ReleaseComparison(
            current_name="Summer '26",
            previous_name="Spring '26",
            new_categories=[],
            removed_categories=[],
            changed_categories=[],
        )

        result = await generate_ai_summary_report(mock_llm, comp, [], None, None)
        assert "Nenhum destaque" in result or "Nenhuma" in result


class TestGenerateLegacyAISummary:
    """_generate_legacy_ai_summary: rule-based summary with removed categories."""

    @pytest.mark.asyncio
    async def test_removed_categories_in_risk_areas(self) -> None:
        from src.automation.models import Regression, ReleaseComparison
        from src.automation.reporting import _generate_legacy_ai_summary

        comp = ReleaseComparison(
            current_name="New",
            previous_name="Old",
            new_categories=["Cat1"],
            removed_categories=["Cat2", "Cat3"],
            changed_categories=[("Cat4", 10, 15)],
        )
        regs = [Regression("Cat4", 10, 5, -5)]

        summary = _generate_legacy_ai_summary(comp, regs, None, None)
        assert len(summary.risk_areas) > 0
        assert "removidas" in summary.risk_areas[0]
