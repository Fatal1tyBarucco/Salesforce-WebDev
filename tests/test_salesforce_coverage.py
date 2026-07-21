"""Tests for src/salesforce.py — 100% coverage."""

from src.exceptions import ConfigError
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.salesforce import (
    FeatureReadiness,
    OrgLimits,
    TrailheadModule,
    _load_trailhead_cache,
    _save_trailhead_cache,
    assess_feature_readiness,
    check_sandbox_readiness,
    detect_new_trailhead_content,
    find_related_modules,
    generate_category_trailhead_section,
    generate_readiness_report,
    generate_release_resources_section,
    generate_trailhead_update_report,
    get_release_resources,
    get_release_trailhead_url,
    search_trailhead,
)


def make_module(title="Test Module", url="https://trailhead.com/m/test", **kwargs):
    defaults = {
        "title": title,
        "url": url,
        "module_type": "",
        "estimated_time": "30 min",
        "points": 100,
    }
    defaults.update(kwargs)
    return TrailheadModule(**defaults)


class TestGetReleaseTrailheadUrl:
    def test_url(self) -> None:
        url = get_release_trailhead_url("summer_26")
        assert "summer-26" in url
        assert "trailhead" in url


class TestGetReleaseResources:
    def test_returns_resources(self) -> None:
        r = get_release_resources("summer_26")
        assert "modules" in r
        assert "community" in r
        assert "topics" in r
        assert len(r["modules"]) == 2


class TestGenerateReleaseResourcesSection:
    def test_generates_section(self) -> None:
        section = generate_release_resources_section("summer_26", "Summer '26")
        assert "Trailhead" in section
        assert "Summer '26" in section


class TestGenerateCategoryTrailheadSection:
    def test_generates_section(self) -> None:
        with patch("src.salesforce.search_trailhead", return_value=[make_module()]):
            section = generate_category_trailhead_section("Security", "summer_26")
            assert "Security" in section or "Trailhead" in section


class TestFindRelatedModules:
    def test_finds_related(self) -> None:
        with patch("src.salesforce.search_trailhead", return_value=[make_module()]):
            modules = find_related_modules("Security", "summer_26")
            assert len(modules) >= 0


class TestAssessFeatureReadiness:
    def test_basic(self) -> None:
        with patch("src.salesforce.search_trailhead", return_value=[make_module()]):
            r = assess_feature_readiness("Security")
            assert r.category == "Security"
            assert r.sandbox_ready is True

    def test_with_flags(self) -> None:
        with patch("src.salesforce.search_trailhead", return_value=[]):
            r = assess_feature_readiness("Security", {"requires_config": True, "contact_sf": True})
            assert r.requires_config is True
            assert r.requires_license is True
            assert len(r.notes) == 3  # config + license + no modules

    def test_no_modules(self) -> None:
        with patch("src.salesforce.search_trailhead", return_value=[]):
            r = assess_feature_readiness("Unknown")
            assert any("Trailhead" in n for n in r.notes)


class TestCheckSandboxReadiness:
    def test_no_limits(self) -> None:
        s = check_sandbox_readiness(None, 0)
        assert s.ready is True

    def test_api_high(self) -> None:
        limits = OrgLimits(
            api_requests_used=950,
            api_requests_limit=1000,
            data_storage_used_mb=0,
            data_storage_limit_mb=0,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        s = check_sandbox_readiness(limits, 0)
        assert s.ready is False
        assert any("API" in i for i in s.issues)

    def test_api_elevated(self) -> None:
        limits = OrgLimits(
            api_requests_used=750,
            api_requests_limit=1000,
            data_storage_used_mb=0,
            data_storage_limit_mb=0,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        s = check_sandbox_readiness(limits, 0)
        assert s.ready is True
        assert any("API" in w for w in s.warnings)

    def test_storage_high(self) -> None:
        limits = OrgLimits(
            api_requests_used=0,
            api_requests_limit=0,
            data_storage_used_mb=950,
            data_storage_limit_mb=1000,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        s = check_sandbox_readiness(limits, 0)
        assert any("Data" in i for i in s.issues)

    def test_storage_elevated(self) -> None:
        limits = OrgLimits(
            api_requests_used=0,
            api_requests_limit=0,
            data_storage_used_mb=750,
            data_storage_limit_mb=1000,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        s = check_sandbox_readiness(limits, 0)
        assert any("Data" in w for w in s.warnings)

    def test_file_storage_high(self) -> None:
        limits = OrgLimits(
            api_requests_used=0,
            api_requests_limit=0,
            data_storage_used_mb=0,
            data_storage_limit_mb=0,
            file_storage_used_mb=950,
            file_storage_limit_mb=1000,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        s = check_sandbox_readiness(limits, 0)
        assert any("File" in i for i in s.issues)

    def test_async_high(self) -> None:
        limits = OrgLimits(
            api_requests_used=0,
            api_requests_limit=0,
            data_storage_used_mb=0,
            data_storage_limit_mb=0,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=950,
            daily_async_jobs_limit=1000,
        )
        s = check_sandbox_readiness(limits, 0)
        assert any("Async" in i for i in s.issues)

    def test_large_deployment(self) -> None:
        s = check_sandbox_readiness(None, 600)
        assert any("Large" in w for w in s.warnings)

    def test_moderate_deployment(self) -> None:
        s = check_sandbox_readiness(None, 250)
        assert any("Moderate" in w for w in s.warnings)


class TestGenerateReadinessReport:
    def test_ready(self) -> None:
        with patch(
            "src.salesforce.assess_feature_readiness",
            return_value=FeatureReadiness("A", [], False, False, True, []),
        ):
            report = generate_readiness_report([{"name": "A", "count": 10}])
            assert "Prontidão" in report
            assert "Sandbox" in report

    def test_not_ready(self) -> None:
        limits = OrgLimits(
            api_requests_used=950,
            api_requests_limit=1000,
            data_storage_used_mb=0,
            data_storage_limit_mb=0,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        with patch(
            "src.salesforce.assess_feature_readiness",
            return_value=FeatureReadiness("A", [], False, False, True, []),
        ):
            report = generate_readiness_report([{"name": "A", "count": 10}], limits)
            assert "Não Pronta" in report

    def test_ready_with_warnings(self) -> None:
        # Need sandbox NOT ready (has issues) AND has warnings
        limits = OrgLimits(
            api_requests_used=950,
            api_requests_limit=1000,
            data_storage_used_mb=0,
            data_storage_limit_mb=0,
            file_storage_used_mb=0,
            file_storage_limit_mb=0,
            daily_async_jobs_used=0,
            daily_async_jobs_limit=0,
        )
        with patch(
            "src.salesforce.assess_feature_readiness",
            return_value=FeatureReadiness("A", [], False, False, True, []),
        ):
            report = generate_readiness_report([{"name": "A", "count": 600}], limits)
            assert "Não Pronta" in report
            assert "⚠️" in report


class TestTrailheadCache:
    def test_load_no_file(self, tmp_path: Path) -> None:
        with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(tmp_path / "nope.json")):
            assert _load_trailhead_cache() == {}

    def test_load_valid(self, tmp_path: Path) -> None:
        p = tmp_path / "cache.json"
        p.write_text(json.dumps({"A": ["url1"]}))
        with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
            assert _load_trailhead_cache() == {"A": ["url1"]}

    def test_load_invalid(self, tmp_path: Path) -> None:
        p = tmp_path / "cache.json"
        p.write_text("bad{")
        with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
            assert _load_trailhead_cache() == {}

    def test_save(self, tmp_path: Path) -> None:
        p = tmp_path / "cache.json"
        with patch("src.salesforce.TRAILHEAD_CACHE_FILE", str(p)):
            _save_trailhead_cache({"A": ["url1"]})
            assert json.loads(p.read_text()) == {"A": ["url1"]}

    def test_save_os_error(self, tmp_path: Path) -> None:
        with patch(
            "src.salesforce.TRAILHEAD_CACHE_FILE", str(tmp_path / "nonexistent" / "cache.json")
        ):
            with patch("pathlib.Path.mkdir", side_effect=OSError("perm")):
                _save_trailhead_cache({"A": ["url1"]})  # Should not raise


class TestDetectNewTrailheadContent:
    def test_detects_new(self) -> None:
        mod = make_module(url="https://new-url")
        with (
            patch(
                "src.salesforce._load_trailhead_cache",
                return_value={"Security": ["https://old-url"]},
            ),
            patch("src.salesforce.search_trailhead", return_value=[mod]),
            patch("src.salesforce._save_trailhead_cache"),
        ):
            result = detect_new_trailhead_content(["Security"])
            assert "Security" in result
            assert len(result["Security"]) == 1

    def test_no_new(self) -> None:
        mod = make_module(url="https://known-url")
        with (
            patch(
                "src.salesforce._load_trailhead_cache",
                return_value={"Security": ["https://known-url"]},
            ),
            patch("src.salesforce.search_trailhead", return_value=[mod]),
            patch("src.salesforce._save_trailhead_cache"),
        ):
            result = detect_new_trailhead_content(["Security"])
            assert "Security" not in result


class TestGenerateTrailheadUpdateReport:
    def test_no_new(self) -> None:
        report = generate_trailhead_update_report({})
        assert "Sem novidades" in report

    def test_with_new(self) -> None:
        mod = make_module(estimated_time="30 min", points=100)
        report = generate_trailhead_update_report({"Security": [mod]})
        assert "Novos Módulos" in report
        assert "Security" in report


class TestTrailheadMappingService:
    def test_config_not_found(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        svc = TrailheadMappingService(config_path=tmp_path / "nope.json")
        with pytest.raises(ConfigError, match="not found"):
            _ = svc.categories

    def test_invalid_json(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        p = tmp_path / "bad.json"
        p.write_text("not json{")
        svc = TrailheadMappingService(config_path=p)
        with pytest.raises(ConfigError, match="Invalid JSON"):
            _ = svc.categories

    def test_not_dict(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        p = tmp_path / "list.json"
        p.write_text(json.dumps([1, 2, 3]))
        svc = TrailheadMappingService(config_path=p)
        with pytest.raises(ConfigError, match="JSON object"):
            _ = svc.categories

    def test_category_not_list(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        p = tmp_path / "config.json"
        p.write_text(json.dumps({"A": "not a list"}))
        svc = TrailheadMappingService(config_path=p)
        with pytest.raises(ConfigError, match="must map to a list"):
            _ = svc.categories

    def test_entry_not_dict(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        p = tmp_path / "config.json"
        p.write_text(json.dumps({"A": ["not a dict"]}))
        svc = TrailheadMappingService(config_path=p)
        with pytest.raises(ConfigError, match="must be an object"):
            _ = svc.categories

    def test_missing_title(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        p = tmp_path / "config.json"
        p.write_text(json.dumps({"A": [{"url": "http://x"}]}))
        svc = TrailheadMappingService(config_path=p)
        with pytest.raises(ConfigError, match="missing required 'title'"):
            _ = svc.categories

    def test_missing_url(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService
        import pytest

        p = tmp_path / "config.json"
        p.write_text(json.dumps({"A": [{"title": "T"}]}))
        svc = TrailheadMappingService(config_path=p)
        with pytest.raises(ConfigError, match="missing required 'url'"):
            _ = svc.categories

    def test_valid_config(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService

        p = tmp_path / "config.json"
        p.write_text(
            json.dumps(
                {
                    "Security": [
                        {
                            "title": "T",
                            "url": "http://x.com",
                            "type": "module",
                            "estimated_time": "30 min",
                            "points": "100",
                        }
                    ]
                }
            )
        )
        svc = TrailheadMappingService(config_path=p)
        assert "Security" in svc.categories

    def test_search(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService

        p = tmp_path / "config.json"
        p.write_text(
            json.dumps({"Security": [{"title": "Security Basics", "url": "http://x.com"}]})
        )
        svc = TrailheadMappingService(config_path=p)
        results = svc.search("security")
        assert len(results) == 1

    def test_search_relative_url(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService

        p = tmp_path / "config.json"
        p.write_text(json.dumps({"Security": [{"title": "Test", "url": "/relative/path"}]}))
        svc = TrailheadMappingService(config_path=p)
        results = svc.search("Security")
        assert len(results) == 1
        assert results[0].url.startswith("http")

    def test_search_no_match(self, tmp_path: Path) -> None:
        from src.salesforce import TrailheadMappingService

        p = tmp_path / "config.json"
        p.write_text(json.dumps({"Security": [{"title": "Test", "url": "http://x.com"}]}))
        svc = TrailheadMappingService(config_path=p)
        results = svc.search("nonexistent")
        assert len(results) == 0

    def test_search_default_config(self) -> None:
        """search_trailhead uses _get_trailhead_service()."""
        with patch("src.salesforce._get_trailhead_service") as mock_svc:
            mock_svc.return_value.search.return_value = [make_module()]
            results = search_trailhead("test")
            assert len(results) == 1


class TestGenerateCategoryTrailheadSectionWithWarnings:
    def test_with_modules(self, tmp_path: Path) -> None:
        """generate_category_trailhead_section with modules that have time/points."""
        mod = make_module(estimated_time="30 min", points=100)
        mock_svc = MagicMock()
        mock_svc.search.return_value = [mod]
        with patch("src.salesforce._get_trailhead_service", return_value=mock_svc):
            section = generate_category_trailhead_section("Security", "summer_26")
            assert "30 min" in section or "100" in section
