"""Integration tests for all AI features working together."""

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

from src.ai_automation import (
    generate_ai_summary,
    generate_ai_summary_report,
    calculate_category_impact_scores,
    predict_next_release_impact,
    generate_impact_prediction_report,
    triage_release,
    generate_triage_report,
    analyze_content_changes,
    generate_deduplication_report,
    generate_filtered_notification,
    generate_filtered_notification_report,
    compare_releases,
    detect_regressions,
    calculate_quality_metrics,
    generate_changelog,
    generate_regression_report,
    generate_quality_report,
)


def test_full_ai_pipeline_integration(tmp_path: Path) -> None:
    """Integration test: all AI features working together."""
    prev_meta = {
        "name": "Winter '26",
        "slug": "winter_26",
        "release_id": 258,
        "categories": [
            {"name": "Salesforce geral", "count": 15},
            {"name": "Agentforce", "count": 5},
            {"name": "Automação", "count": 30},
            {"name": "Commerce", "count": 45},
            {"name": "Service Cloud", "count": 60},
        ],
    }
    curr_meta = {
        "name": "Summer '26",
        "slug": "summer_26",
        "release_id": 260,
        "categories": [
            {"name": "Salesforce geral", "count": 25},
            {"name": "Agentforce", "count": 40},
            {"name": "Automação", "count": 35},
            {"name": "Commerce", "count": 50},
            {"name": "Desenvolvimento", "count": 70},
        ],
    }
    prev_dir = tmp_path / "winter_26"
    curr_dir = tmp_path / "summer_26"
    prev_dir.mkdir()
    curr_dir.mkdir()
    (prev_dir / ".meta.json").write_text(json.dumps(prev_meta))
    (curr_dir / ".meta.json").write_text(json.dumps(curr_meta))
    (curr_dir / "salesforce_geral.md").write_text("# Salesforce Geral\nContent here.")
    (curr_dir / "agentforce.md").write_text("# Agentforce\nNew features.")

    with patch("src.ai_automation.RELEASES_DIR", str(tmp_path)):
        # Feature 1: AI Summary
        summary = asyncio.run(generate_ai_summary("summer_26", "winter_26"))
        assert summary.headline is not None
        assert summary.overall_trend == "crescimento"

        summary_report = asyncio.run(generate_ai_summary_report("summer_26", "winter_26"))
        assert "Resumo Inteligente" in summary_report

        # Feature 2: Predictive Impact Scoring
        r1_meta = {
            "name": "Spring '26",
            "slug": "spring_26",
            "release_id": 256,
            "categories": [
                {"name": "Salesforce geral", "count": 20},
                {"name": "Agentforce", "count": 10},
                {"name": "Automação", "count": 35},
                {"name": "Commerce", "count": 50},
                {"name": "Desenvolvimento", "count": 70},
            ],
        }
        r1_dir = tmp_path / "spring_26"
        r1_dir.mkdir()
        (r1_dir / ".meta.json").write_text(json.dumps(r1_meta))

        scores = asyncio.run(calculate_category_impact_scores())
        assert len(scores) > 0

        prediction = asyncio.run(predict_next_release_impact())
        assert prediction.overall_risk_level in ["alto", "moderado", "baixo", "indeterminado"]

        prediction_report = asyncio.run(generate_impact_prediction_report())
        assert "Previsão de Impacto" in prediction_report

        # Feature 3: Automated Alert Triage
        triage = asyncio.run(triage_release("summer_26"))
        assert triage.risk_level in ["mínimo", "baixo", "moderado", "alto"]
        assert 0 <= triage.risk_score <= 100
        assert len(triage.suggested_actions) > 0

        triage_report = asyncio.run(generate_triage_report("summer_26"))
        assert "Triage Automatizado" in triage_report

        # Feature 4: Content Deduplication
        result1 = asyncio.run(analyze_content_changes("summer_26"))
        assert len(result1.new_files) > 0

        result2 = asyncio.run(analyze_content_changes("summer_26"))
        assert len(result2.unchanged_files) > 0

        dedup_report = asyncio.run(generate_deduplication_report("summer_26"))
        assert "Deduplicação de Conteúdo" in dedup_report

        # Feature 5: Smart Notification Filtering
        for profile_type in ["admin", "developer", "architect", "business"]:
            notification = asyncio.run(generate_filtered_notification("summer_26", profile_type))
            assert notification.total_features > 0

        admin_notification = asyncio.run(generate_filtered_notification("summer_26", "admin"))
        assert admin_notification.profile.profile_type == "admin"

        filter_report = asyncio.run(generate_filtered_notification_report("summer_26", "admin"))
        assert "Notificação Filtrada" in filter_report

        # Cross-feature verification
        comparison = asyncio.run(compare_releases("summer_26", "winter_26"))
        assert comparison.current_name == "Summer '26"
        assert len(comparison.new_categories) > 0

        regressions = asyncio.run(detect_regressions("summer_26", "winter_26"))
        assert len(regressions) >= 0

        metrics = asyncio.run(calculate_quality_metrics("summer_26"))
        assert metrics is not None
        assert metrics.total_features > 0

        changelog = asyncio.run(generate_changelog())
        assert "Summer '26" in changelog
        assert "Winter '26" in changelog

        regression_report = asyncio.run(generate_regression_report("summer_26", "winter_26"))
        assert "Summer '26" in regression_report

        quality_report = asyncio.run(generate_quality_report())
        assert "Qualidade" in quality_report


def test_ai_features_with_missing_data() -> None:
    """Test all AI features handle missing data gracefully."""
    with patch("src.ai_automation.RELEASES_DIR", "/nonexistent"):
        summary = asyncio.run(generate_ai_summary("missing", "missing"))
        assert summary.headline is not None

        scores = asyncio.run(calculate_category_impact_scores())
        assert scores == []

        prediction = asyncio.run(predict_next_release_impact())
        assert prediction.overall_risk_level == "indeterminado"

        triage = asyncio.run(triage_release("missing"))
        assert triage.risk_level == "desconhecido"

        result = asyncio.run(analyze_content_changes("missing"))
        assert result.cache_hit_rate == 0.0

        notification = asyncio.run(generate_filtered_notification("missing", "admin"))
        assert notification.total_features == 0
