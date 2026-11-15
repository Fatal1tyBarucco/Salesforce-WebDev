"""Tests for src/models/release.py, src/models/feature.py and src/models/classification.py to reach 95% coverage."""

from __future__ import annotations

from src.models.classification import (
    Audience,
    ClassificationResult,
    ClassifiedFeature,
    FeatureType,
    ImpactLevel,
    Priority,
)
from src.models.feature import (
    Feature,
    FeatureCategory,
    FeatureImpact,
    FeatureImpactCategory,
    FeatureStatus,
)
from src.models.release import ReleaseCategory, ReleaseMetadata, build_release_info


class TestReleaseCategory:
    """Tests for ReleaseCategory model."""

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields."""
        cat = ReleaseCategory(name="Test", count=5, features=("feat1", "feat2"))
        result = cat.to_dict()

        assert result["name"] == "Test"
        assert result["count"] == 5
        assert result["features"] == ["feat1", "feat2"]

    def test_from_dict(self) -> None:
        """from_dict should deserialize all fields."""
        data = {"name": "Test", "count": 3, "features": ["a", "b"]}
        cat = ReleaseCategory.from_dict(data)

        assert cat.name == "Test"
        assert cat.count == 3
        assert cat.features == ("a", "b")

    def test_from_dict_with_missing_optional(self) -> None:
        """from_dict should handle missing optional fields."""
        data = {"name": "Test"}
        cat = ReleaseCategory.from_dict(data)

        assert cat.name == "Test"
        assert cat.count == 0
        assert cat.features == ()


class TestReleaseMetadata:
    """Tests for ReleaseMetadata model."""

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields including categories."""
        cat = ReleaseCategory(name="Cat1", count=2, features=("f1",))
        meta = ReleaseMetadata(
            release_id=262,
            slug="summer_26",
            name="Summer '26",
            version="1.0",
            date="2024-06-01",
            total_features=10,
            avg_confidence=0.85,
            categories=(cat,),
        )
        result = meta.to_dict()

        assert result["release_id"] == 262
        assert result["slug"] == "summer_26"
        assert result["name"] == "Summer '26"
        assert result["version"] == "1.0"
        assert result["date"] == "2024-06-01"
        assert result["total_features"] == 10
        assert result["avg_confidence"] == 0.85
        assert len(result["categories"]) == 1
        assert result["categories"][0]["name"] == "Cat1"

    def test_from_dict(self) -> None:
        """from_dict should deserialize all fields."""
        data = {
            "release_id": 262,
            "slug": "summer_26",
            "name": "Summer '26",
            "version": "1.0",
            "date": "2024-06-01",
            "total_features": 10,
            "avg_confidence": 0.85,
            "generated_at": "2024-06-01T00:00:00",
            "categories": [{"name": "Cat1", "count": 2, "features": ["f1"]}],
        }
        meta = ReleaseMetadata.from_dict(data)

        assert meta.release_id == 262
        assert meta.slug == "summer_26"
        assert meta.name == "Summer '26"
        assert meta.version == "1.0"
        assert meta.date == "2024-06-01"
        assert meta.total_features == 10
        assert meta.avg_confidence == 0.85
        assert len(meta.categories) == 1
        assert meta.categories[0].name == "Cat1"

    def test_from_dict_with_missing_optional(self) -> None:
        """from_dict should handle missing optional fields."""
        data = {
            "release_id": 262,
            "slug": "summer_26",
            "name": "Summer '26",
        }
        meta = ReleaseMetadata.from_dict(data)

        assert meta.release_id == 262
        assert meta.slug == "summer_26"
        assert meta.name == "Summer '26"
        assert meta.version == ""
        assert meta.date == ""
        assert meta.total_features == 0
        assert meta.avg_confidence == 0.0
        assert meta.categories == ()


class TestBuildReleaseInfo:
    """Tests for build_release_info function (from src.models.release)."""

    def test_winter_release(self) -> None:
        """Should build winter release correctly."""
        # release_id=1 -> Winter '00 (year=2000, season_idx=1%4=1 -> winter)
        meta = build_release_info(1)
        assert meta.release_id == 1
        assert meta.slug == "winter_'00"
        assert meta.name == "Winter '00"

    def test_spring_release(self) -> None:
        """Should build spring release correctly."""
        # release_id=2 -> Spring '00
        meta = build_release_info(2)
        assert meta.release_id == 2
        assert meta.slug == "spring_'00"
        assert meta.name == "Spring '00"

    def test_summer_release(self) -> None:
        """Should build summer release correctly."""
        # release_id=3 -> Summer '00
        meta = build_release_info(3)
        assert meta.release_id == 3
        assert meta.slug == "summer_'00"
        assert meta.name == "Summer '00"

    def test_autumn_release(self) -> None:
        """Should build autumn release correctly."""
        # release_id=4 -> Autumn '01 (year = 2000 + 4//4 = 2001)
        meta = build_release_info(4)
        assert meta.release_id == 4
        assert meta.slug == "autumn_'01"
        assert meta.name == "Autumn '01"

    def test_next_year_winter(self) -> None:
        """Should handle year rollover."""
        # release_id=5 -> Winter '01 (year = 2000 + 5//4 = 2001, season_idx=5%4=1)
        meta = build_release_info(5)
        assert meta.release_id == 5
        assert meta.slug == "winter_'01"
        assert meta.name == "Winter '01"


class TestFeatureEnums:
    """Tests for Feature enums."""

    def test_feature_impact_values(self) -> None:
        """FeatureImpact enum should have correct values."""
        assert FeatureImpact.HIGH.value == "high"
        assert FeatureImpact.MEDIUM.value == "medium"
        assert FeatureImpact.LOW.value == "low"

    def test_feature_status_values(self) -> None:
        """FeatureStatus enum should have correct values."""
        assert FeatureStatus.RAW.value == "raw"
        assert FeatureStatus.CLASSIFIED.value == "classified"
        assert FeatureStatus.ENRICHED.value == "enriched"
        assert FeatureStatus.TRANSLATED.value == "translated"
        assert FeatureStatus.PUBLISHED.value == "published"


class TestFeature:
    """Tests for Feature model."""

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields."""
        feat = Feature(
            name="Test Feature",
            description="Description",
            category="Test Category",
            raw_text="Raw text",
            status=FeatureStatus.CLASSIFIED,
            locale="en_US",
            source_url="https://example.com",
        )
        result = feat.to_dict()

        assert result["name"] == "Test Feature"
        assert result["description"] == "Description"
        assert result["category"] == "Test Category"
        assert result["raw_text"] == "Raw text"
        assert result["status"] == "classified"
        assert result["locale"] == "en_US"
        assert result["source_url"] == "https://example.com"

    def test_from_dict(self) -> None:
        """from_dict should deserialize all fields."""
        data = {
            "name": "Test Feature",
            "description": "Description",
            "category": "Test Category",
            "raw_text": "Raw text",
            "status": "enriched",
            "locale": "en_US",
            "source_url": "https://example.com",
        }
        feat = Feature.from_dict(data)

        assert feat.name == "Test Feature"
        assert feat.description == "Description"
        assert feat.category == "Test Category"
        assert feat.raw_text == "Raw text"
        assert feat.status == FeatureStatus.ENRICHED
        assert feat.locale == "en_US"
        assert feat.source_url == "https://example.com"

    def test_from_dict_with_defaults(self) -> None:
        """from_dict should use defaults for missing fields."""
        data = {"name": "Test Feature"}
        feat = Feature.from_dict(data)

        assert feat.name == "Test Feature"
        assert feat.description == ""
        assert feat.category == ""
        assert feat.raw_text == ""
        assert feat.status == FeatureStatus.RAW
        assert feat.locale == "pt_BR"
        assert feat.source_url == ""


class TestFeatureCategory:
    """Tests for FeatureCategory model."""

    def test_post_init_sets_total_count(self) -> None:
        """__post_init__ should set total_count from features length."""
        feat1 = Feature(name="Feature 1")
        feat2 = Feature(name="Feature 2")
        cat = FeatureCategory(name="Test", features=(feat1, feat2))

        assert cat.total_count == 2

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields."""
        feat = Feature(name="Feature 1")
        cat = FeatureCategory(name="Test", features=(feat,), locale="en_US")

        result = cat.to_dict()

        assert result["name"] == "Test"
        assert result["locale"] == "en_US"
        assert result["total_count"] == 1
        assert len(result["features"]) == 1
        assert result["features"][0]["name"] == "Feature 1"

    def test_from_dict(self) -> None:
        """from_dict should deserialize all fields."""
        data = {
            "name": "Test",
            "locale": "en_US",
            "features": [{"name": "Feature 1", "description": "Desc", "status": "raw"}],
        }
        cat = FeatureCategory.from_dict(data)

        assert cat.name == "Test"
        assert cat.locale == "en_US"
        assert len(cat.features) == 1
        assert cat.features[0].name == "Feature 1"
        assert cat.total_count == 1


class TestFeatureImpactCategory:
    """Tests for FeatureImpactCategory model."""

    def test_to_dict(self) -> None:
        """to_dict should serialize all fields."""
        cat = FeatureImpactCategory(
            name="Security",
            impact=FeatureImpact.HIGH,
            features=("feat1", "feat2"),
            confidence=0.9,
        )
        result = cat.to_dict()

        assert result["name"] == "Security"
        assert result["impact"] == "high"
        assert result["features"] == ["feat1", "feat2"]
        assert result["confidence"] == 0.9

    def test_from_dict(self) -> None:
        """from_dict should deserialize all fields."""
        data = {
            "name": "Security",
            "impact": "high",
            "features": ["feat1", "feat2"],
            "confidence": 0.9,
        }
        cat = FeatureImpactCategory.from_dict(data)

        assert cat.name == "Security"
        assert cat.impact == FeatureImpact.HIGH
        assert cat.features == ("feat1", "feat2")
        assert cat.confidence == 0.9

    def test_from_dict_with_defaults(self) -> None:
        """from_dict should use defaults for missing fields."""
        data = {"name": "Security", "impact": "medium"}
        cat = FeatureImpactCategory.from_dict(data)

        assert cat.name == "Security"
        assert cat.impact == FeatureImpact.MEDIUM
        assert cat.features == ()
        assert cat.confidence == 0.0


class TestFeatureAdditionalCoverage:
    """Additional tests for Feature model to reach 100% coverage."""

    def test_to_dict_covers_all_fields(self) -> None:
        """Line 49: to_dict return statement."""
        feat = Feature(
            name="Test Feature",
            description="Description",
            category="Test Category",
            raw_text="Raw text",
            status=FeatureStatus.CLASSIFIED,
            locale="en_US",
            source_url="https://example.com",
        )
        result = feat.to_dict()

        assert result["name"] == "Test Feature"
        assert result["description"] == "Description"
        assert result["category"] == "Test Category"
        assert result["raw_text"] == "Raw text"
        assert result["status"] == "classified"
        assert result["locale"] == "en_US"
        assert result["source_url"] == "https://example.com"

    def test_from_dict_covers_all_fields(self) -> None:
        """Line 62: from_dict return statement."""
        data = {
            "name": "Test Feature",
            "description": "Description",
            "category": "Test Category",
            "raw_text": "Raw text",
            "status": "enriched",
            "locale": "en_US",
            "source_url": "https://example.com",
        }
        feat = Feature.from_dict(data)

        assert feat.name == "Test Feature"
        assert feat.description == "Description"
        assert feat.category == "Test Category"
        assert feat.raw_text == "Raw text"
        assert feat.status == FeatureStatus.ENRICHED
        assert feat.locale == "en_US"
        assert feat.source_url == "https://example.com"


class TestFeatureCategoryAdditionalCoverage:
    """Additional tests for FeatureCategory model to reach 100% coverage."""

    def test_post_init_sets_total_count_line_83(self) -> None:
        """Line 83: __post_init__ sets total_count."""
        feat1 = Feature(name="Feature 1")
        feat2 = Feature(name="Feature 2")
        cat = FeatureCategory(name="Test", features=(feat1, feat2))

        assert cat.total_count == 2

    def test_to_dict_covers_return_line_87(self) -> None:
        """Line 87: to_dict return statement."""
        feat = Feature(name="Feature 1")
        cat = FeatureCategory(name="Test", features=(feat,), locale="en_US")

        result = cat.to_dict()

        assert result["name"] == "Test"
        assert result["locale"] == "en_US"
        assert result["total_count"] == 1
        assert len(result["features"]) == 1
        assert result["features"][0]["name"] == "Feature 1"

    def test_from_dict_covers_return_line_97_98(self) -> None:
        """Lines 97-98: from_dict return statement."""
        data = {
            "name": "Test",
            "locale": "en_US",
            "features": [{"name": "Feature 1", "description": "Desc", "status": "raw"}],
        }
        cat = FeatureCategory.from_dict(data)

        assert cat.name == "Test"
        assert cat.locale == "en_US"
        assert len(cat.features) == 1
        assert cat.features[0].name == "Feature 1"
        assert cat.total_count == 1


class TestFeatureImpactCategoryAdditionalCoverage:
    """Additional tests for FeatureImpactCategory model to reach 100% coverage."""

    def test_to_dict_covers_return_line_116(self) -> None:
        """Line 116: to_dict return statement."""
        cat = FeatureImpactCategory(
            name="Security",
            impact=FeatureImpact.HIGH,
            features=("feat1", "feat2"),
            confidence=0.9,
        )
        result = cat.to_dict()

        assert result["name"] == "Security"
        assert result["impact"] == "high"
        assert result["features"] == ["feat1", "feat2"]
        assert result["confidence"] == 0.9

    def test_from_dict_covers_return_line_126(self) -> None:
        """Line 126: from_dict return statement."""
        data = {
            "name": "Security",
            "impact": "high",
            "features": ["feat1", "feat2"],
            "confidence": 0.9,
        }
        cat = FeatureImpactCategory.from_dict(data)

        assert cat.name == "Security"
        assert cat.impact == FeatureImpact.HIGH
        assert cat.features == ("feat1", "feat2")
        assert cat.confidence == 0.9


class TestClassifiedFeature:
    """Tests for ClassifiedFeature model (from src.models.classification)."""

    def test_to_dict_covers_return_line_67(self) -> None:
        """Line 67: to_dict return statement."""
        feat = ClassifiedFeature(
            name="Test Feature",
            impact=ImpactLevel.HIGH,
            feature_type=FeatureType.NEW_FEATURE,
            confidence=0.95,
            keywords_matched=("security", "api"),
            audience=Audience.ADMINS,
            priority=Priority.CRITICAL,
            justification="Critical security update",
        )
        result = feat.to_dict()

        assert result["name"] == "Test Feature"
        assert result["impact"] == "high"
        assert result["type"] == "new_feature"
        assert result["confidence"] == 0.95
        assert result["keywords_matched"] == ["security", "api"]
        assert result["audience"] == "admins"
        assert result["priority"] == "crítica"
        assert result["justification"] == "Critical security update"

    def test_from_dict_covers_return_line_81(self) -> None:
        """Line 81: from_dict return statement."""
        data = {
            "name": "Test Feature",
            "impact": "high",
            "type": "new_feature",
            "confidence": 0.95,
            "keywords_matched": ["security", "api"],
            "audience": "admins",
            "priority": "crítica",
            "justification": "Critical security update",
        }
        feat = ClassifiedFeature.from_dict(data)

        assert feat.name == "Test Feature"
        assert feat.impact == ImpactLevel.HIGH
        assert feat.feature_type == FeatureType.NEW_FEATURE
        assert feat.confidence == 0.95
        assert feat.keywords_matched == ("security", "api")
        assert feat.audience == Audience.ADMINS
        assert feat.priority == Priority.CRITICAL
        assert feat.justification == "Critical security update"

    def test_from_dict_with_optional_none(self) -> None:
        """from_dict should handle missing optional fields."""
        data = {
            "name": "Test Feature",
            "impact": "medium",
            "type": "improvement",
            "confidence": 0.5,
        }
        feat = ClassifiedFeature.from_dict(data)

        assert feat.name == "Test Feature"
        assert feat.impact == ImpactLevel.MEDIUM
        assert feat.feature_type == FeatureType.IMPROVEMENT
        assert feat.confidence == 0.5
        assert feat.keywords_matched == ()
        assert feat.audience is None
        assert feat.priority is None
        assert feat.justification == ""


class TestClassificationResult:
    """Tests for ClassificationResult model (from src.models.classification)."""

    def test_to_dict_covers_return_line_105(self) -> None:
        """Line 105: to_dict return statement."""
        feat = ClassifiedFeature(
            name="Test Feature",
            impact=ImpactLevel.HIGH,
            feature_type=FeatureType.NEW_FEATURE,
            confidence=0.95,
        )
        result = ClassificationResult(
            release_slug="summer_26",
            total_features=10,
            by_impact={"high": 3, "medium": 5, "low": 2},
            by_type={"new_feature": 5, "improvement": 3, "bug_fix": 2},
            features=(feat,),
        )
        out = result.to_dict()

        assert out["release_slug"] == "summer_26"
        assert out["total_features"] == 10
        assert out["by_impact"] == {"high": 3, "medium": 5, "low": 2}
        assert out["by_type"] == {"new_feature": 5, "improvement": 3, "bug_fix": 2}
        assert len(out["features"]) == 1
        assert out["features"][0]["name"] == "Test Feature"
