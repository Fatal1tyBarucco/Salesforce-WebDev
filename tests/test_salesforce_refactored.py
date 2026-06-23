"""Tests for TrailheadMappingService — externalized Trailhead mappings."""

import json
from pathlib import Path

import pytest

from src.salesforce import TRAILHEAD_BASE_URL, TrailheadMappingService, TrailheadModule


@pytest.fixture
def valid_json(tmp_path: Path) -> Path:
    data = {
        "Automação": [
            {"title": "Flow Builder Basics", "url": "/content/learn/modules/flow-basics"},
        ],
        "Vendas": [
            {
                "title": "Sales Cloud for Sales Reps",
                "url": "/content/learn/modules/sales_cloud_for_sales_reps",
            },
        ],
    }
    p = tmp_path / "trailhead.json"
    p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return p


@pytest.fixture
def service(valid_json: Path) -> TrailheadMappingService:
    return TrailheadMappingService(config_path=valid_json)


def test_load_categories_from_json(service: TrailheadMappingService) -> None:
    cats = service.categories
    assert "Automação" in cats
    assert "Vendas" in cats
    assert len(cats) == 2


def test_search_returns_trailhead_modules(service: TrailheadMappingService) -> None:
    modules = service.search("Automação")
    assert len(modules) == 1
    assert isinstance(modules[0], TrailheadModule)
    assert modules[0].title == "Flow Builder Basics"
    assert modules[0].url == TRAILHEAD_BASE_URL + "/content/learn/modules/flow-basics"


def test_search_partial_match(service: TrailheadMappingService) -> None:
    modules = service.search("venda")
    assert len(modules) == 1
    assert modules[0].title == "Sales Cloud for Sales Reps"


def test_search_no_match(service: TrailheadMappingService) -> None:
    modules = service.search("NonExistentCategory123")
    assert modules == []


def test_search_respects_max_results(tmp_path: Path) -> None:
    data = {
        "Big": [{"title": f"Mod {i}", "url": f"/m{i}"} for i in range(10)],
    }
    p = tmp_path / "t.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    modules = svc.search("Big", max_results=3)
    assert len(modules) == 3


def test_search_prepends_base_url(tmp_path: Path) -> None:
    data = {"X": [{"title": "T", "url": "/content/learn/x"}]}
    p = tmp_path / "t.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    modules = svc.search("X")
    assert modules[0].url.startswith("https://trailhead.salesforce.com")


def test_search_does_not_double_prefix(tmp_path: Path) -> None:
    full_url = "https://trailhead.salesforce.com/content/learn/y"
    data = {"Y": [{"title": "T", "url": full_url}]}
    p = tmp_path / "t.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    modules = svc.search("Y")
    assert modules[0].url == full_url


def test_invalid_json_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("NOT JSON", encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    with pytest.raises(ValueError, match="Invalid JSON"):
        _ = svc.categories


def test_missing_file_uses_default(tmp_path: Path) -> None:
    svc = TrailheadMappingService(config_path=tmp_path / "nonexistent.json")
    cats = svc.categories
    assert "Automação" in cats


def test_invalid_structure_raises(tmp_path: Path) -> None:
    data = "not a dict"
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    with pytest.raises(ValueError, match="must be a JSON object"):
        _ = svc.categories


def test_invalid_module_entry_raises(tmp_path: Path) -> None:
    data = {"Cat": ["not a dict"]}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    with pytest.raises(ValueError, match="must be an object"):
        _ = svc.categories


def test_missing_title_field_raises(tmp_path: Path) -> None:
    data = {"Cat": [{"url": "/x"}]}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    with pytest.raises(ValueError, match="title"):
        _ = svc.categories


def test_missing_url_field_raises(tmp_path: Path) -> None:
    data = {"Cat": [{"title": "T"}]}
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    with pytest.raises(ValueError, match="url"):
        _ = svc.categories


def test_categories_cached_property(service: TrailheadMappingService) -> None:
    c1 = service.categories
    c2 = service.categories
    assert c1 is c2


def test_default_config_path_loads_real_data() -> None:
    svc = TrailheadMappingService()
    cats = svc.categories
    assert len(cats) > 20
    assert "Agentforce" in cats


def test_search_exact_vs_partial_priority(tmp_path: Path) -> None:
    data = {
        "Commerce": [{"title": "Exact", "url": "/exact"}],
        "Commerce Cloud": [{"title": "Partial", "url": "/partial"}],
    }
    p = tmp_path / "t.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    modules = svc.search("Commerce")
    assert modules[0].title == "Exact"


def test_search_case_insensitive(tmp_path: Path) -> None:
    data = {"Agentforce": [{"title": "A", "url": "/a"}]}
    p = tmp_path / "t.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    svc = TrailheadMappingService(config_path=p)
    modules = svc.search("agentforce")
    assert len(modules) == 1
