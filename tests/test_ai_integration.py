"""Integration test for all 5 AI automation features.

Tests the complete workflow:
1. AI Summary generation
2. Predictive Release Impact Scoring
3. Automated Alert Triage
4. Content Deduplication & Caching
5. Smart Notification Filtering
"""

from pathlib import Path
import json
from unittest.mock import patch

from src.ai_automation import (
    compare_releases,
    detect_regressions,
    calculate_quality_metrics,
    generate_changelog,
    generate_regression_report,
    generate_quality_report,
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
)


def test_full_ai_pipeline_integration(tmp_path: Path) -> None:
    """End-to-end test of all 5 AI features with mock release data."""
    # Setup: Create two mock releases for comparison
    prev_meta = {
        "name": "Winter '26",
        "slug": "winter_26",
        "release_id": 258,
        "categories": [
            {"name": "Salesforce geral", "count": 25},
            {"name": "Agentforce", "count": 15},
            {"name": "Automação", "count": 45},
            {"name": "Commerce", "count": 60},
            {"name": "Desenvolvimento", "count": 80},
            {"name": "Segurança, identidade e privacidade", "count": 30},
        ],
    }

    curr_meta = {
        "name": "Summer '26",
        "slug": "summer_26",
        "release_id": 262,
        "categories": [
            {"name": "Salesforce geral", "count": 31},
            {"name": "Agentforce", "count": 19},
            {"name": "Automação", "count": 81},
            {"name": "Commerce", "count": 91},
            {"name": "Desenvolvimento", "count": 102},
            {"name": "Marketing", "count": 53},
            {"name": "Segurança, identidade e privacidade", "count": 44},
        ],
    }

    prev_dir = tmp_path / "winter_26"
    curr_dir = tmp_path / "summer_26"
    prev_dir.mkdir()
    curr_dir.mkdir()
    (prev_dir / ".meta.json").write_text(json.dumps(prev_meta))
    (curr_dir / ".meta.json").write_text(json.dumps(curr_meta))

    # Create content files for deduplication test
    (curr_dir / "salesforce_geral.md").write_text("# Salesforce Geral\nContent here.")
    (curr_dir / "agentforce.md").write_text("# Agentforce\nNew features.")

    with patch("src.ai_automation.RELEASES_DIR", str(tmp_path)):
        # ==========================================
        # Feature 1: AI Summary
        # ==========================================
        print("\n=== Feature 1: AI Summary ===")
        summary = generate_ai_summary("summer_26", "winter_26")
        assert summary.headline is not None
        assert len(summary.highlights) > 0
        assert summary.overall_trend == "crescimento"
        print(f"Headline: {summary.headline}")
        print(f"Highlights: {len(summary.highlights)}")
        print(f"Trend: {summary.overall_trend}")

        summary_report = generate_ai_summary_report("summer_26", "winter_26")
        assert "Resumo Inteligente" in summary_report
        print("AI Summary: PASSED")

        # ==========================================
        # Feature 2: Predictive Impact Scoring
        # ==========================================
        print("\n=== Feature 2: Predictive Impact Scoring ===")
        # Create a third release for historical analysis
        r1_meta = {
            "name": "Spring '26",
            "slug": "spring_26",
            "release_id": 260,
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

        scores = calculate_category_impact_scores()
        assert len(scores) > 0
        print(f"Categories scored: {len(scores)}")
        print(f"Top risk: {scores[0].category} (score: {scores[0].risk_score})")

        prediction = predict_next_release_impact()
        assert prediction.overall_risk_level in ["alto", "moderado", "baixo", "indeterminado"]
        print(f"Risk level: {prediction.overall_risk_level}")
        print(f"Summary: {prediction.summary}")

        prediction_report = generate_impact_prediction_report()
        assert "Previsão de Impacto" in prediction_report
        print("Predictive Scoring: PASSED")

        # ==========================================
        # Feature 3: Automated Alert Triage
        # ==========================================
        print("\n=== Feature 3: Automated Alert Triage ===")
        triage = triage_release("summer_26")
        assert triage.risk_level in ["mínimo", "baixo", "moderado", "alto"]
        assert 0 <= triage.risk_score <= 100
        assert len(triage.suggested_actions) > 0
        print(f"Risk: {triage.risk_level} (score: {triage.risk_score})")
        print(f"Priority: {triage.priority}")
        print(f"Actions: {len(triage.suggested_actions)}")

        triage_report = generate_triage_report("summer_26")
        assert "Triage Automatizado" in triage_report
        print("Alert Triage: PASSED")

        # ==========================================
        # Feature 4: Content Deduplication
        # ==========================================
        print("\n=== Feature 4: Content Deduplication ===")
        result1 = analyze_content_changes("summer_26")
        assert len(result1.new_files) > 0
        print(f"First run - New files: {len(result1.new_files)}")

        # Run again to test cache hit
        result2 = analyze_content_changes("summer_26")
        assert len(result2.unchanged_files) > 0
        print(f"Second run - Unchanged: {len(result2.unchanged_files)}")
        print(f"Cache hit rate: {result2.cache_hit_rate:.0%}")

        dedup_report = generate_deduplication_report("summer_26")
        assert "Deduplicação de Conteúdo" in dedup_report
        print("Content Deduplication: PASSED")

        # ==========================================
        # Feature 5: Smart Notification Filtering
        # ==========================================
        print("\n=== Feature 5: Smart Notification Filtering ===")
        # Test all profiles
        for profile_type in ["admin", "developer", "architect", "business"]:
            notification = generate_filtered_notification("summer_26", profile_type)
            assert notification.total_features > 0
            print(
                f"  {profile_type}: relevance={notification.profile.relevance_score:.0%}, "
                f"relevant={notification.relevant_count}"
            )

        # Test admin profile specifically
        admin_notification = generate_filtered_notification("summer_26", "admin")
        assert admin_notification.profile.profile_type == "admin"
        assert admin_notification.profile.name == "Administrador"

        # Test developer profile
        dev_notification = generate_filtered_notification("summer_26", "developer")
        assert dev_notification.profile.profile_type == "developer"

        # Generate report
        filter_report = generate_filtered_notification_report("summer_26", "admin")
        assert "Notificação Filtrada" in filter_report
        assert "Perfil" in filter_report
        print("Smart Filtering: PASSED")

        # ==========================================
        # Cross-feature verification
        # ==========================================
        print("\n=== Cross-Feature Verification ===")

        # Verify comparison data feeds into summary
        comparison = compare_releases("summer_26", "winter_26")
        assert comparison.current_name == "Summer '26"
        assert len(comparison.new_categories) > 0
        print(f"Comparison: {len(comparison.new_categories)} new categories")

        # Verify regression detection works with comparison data
        regressions = detect_regressions("summer_26", "winter_26")
        print(f"Regressions: {len(regressions)}")

        # Verify quality metrics work
        metrics = calculate_quality_metrics("summer_26")
        assert metrics is not None
        assert metrics.total_features > 0
        print(f"Metrics: {metrics.total_features} features, {metrics.total_categories} categories")

        # Verify changelog generation works
        changelog = generate_changelog()
        assert "Summer '26" in changelog
        assert "Winter '26" in changelog
        print("Changelog: Generated")

        # Verify regression report works
        regression_report = generate_regression_report("summer_26", "winter_26")
        assert "Summer '26" in regression_report
        print("Regression report: Generated")

        # Verify quality report works
        quality_report = generate_quality_report()
        assert "Qualidade" in quality_report
        print("Quality report: Generated")

        print("\n=== ALL 5 AI FEATURES PASSED ===")
        print("Integration test completed successfully!")


def test_ai_features_with_missing_data() -> None:
    """Test all AI features handle missing data gracefully."""
    with patch("src.ai_automation.RELEASES_DIR", "/nonexistent"):
        # Feature 1
        summary = generate_ai_summary("missing", "missing")
        assert "sem alterações" in summary.headline

        # Feature 2
        scores = calculate_category_impact_scores()
        assert scores == []

        prediction = predict_next_release_impact()
        assert prediction.overall_risk_level == "indeterminado"

        # Feature 3
        triage = triage_release("missing")
        assert triage.risk_level == "desconhecido"

        # Feature 4
        result = analyze_content_changes("missing")
        assert result.cache_hit_rate == 0.0

        # Feature 5
        notification = generate_filtered_notification("missing", "admin")
        assert notification.total_features == 0

        print("Missing data handling: PASSED")
