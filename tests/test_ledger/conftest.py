"""Fixtures de teste para o Salesforce Feature Evolution Ledger (SFEL)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

# ── Fixtures de diretório de releases fictícias ─────────────────────────


def _write_meta(
    releases_dir: Path,
    slug: str,
    release_id: int,
    name: str,
    categories: list[dict[str, Any]],
    total_features: int | None = None,
) -> Path:
    """Escreve um arquivo .meta.json fictício.

    Args:
        releases_dir: Raiz das releases.
        slug: Identificador da release.
        release_id: ID numérico da release.
        name: Nome exibido.
        categories: Lista de dicts ``{"name": ..., "count": ...}``.
        total_features: Total de features. Se None, soma os counts.

    Returns:
        Path do arquivo escrito.
    """
    if total_features is None:
        total_features = sum(c["count"] for c in categories)
    meta = {
        "name": name,
        "release_id": release_id,
        "slug": slug,
        "total_features": total_features,
        "categories": categories,
        "generated_at": "2026-01-01T00:00:00+00:00",
        "source": "test_fixture",
    }
    meta_path = releases_dir / slug / ".meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return meta_path


def _write_md(
    releases_dir: Path,
    slug: str,
    category: str,
    features: list[str],
) -> Path:
    """Escreve um arquivo markdown fictício com features bullet.

    Args:
        releases_dir: Raiz das releases.
        slug: Identificador da release.
        category: Nome da categoria (título ##).
        features: Lista de nomes de features para bullet points.

    Returns:
        Path do arquivo escrito.
    """
    lines: list[str] = [
        f"# {category}",
        "",
        f"## {category}",
        "",
    ]
    for feat in features:
        lines.append(f"- {feat}")
    lines.append("")
    md_path = releases_dir / slug / f"{category.lower().replace(' ', '_')}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


@pytest.fixture
def releases_dir_fake(tmp_path: Path) -> Path:
    """Cria uma estrutura de releases fictícia com três releases.

    Layout:
        tmp_path/
        ├── spring_26/
        │   ├── .meta.json        (release_id=261, 2 categorias, 4 features)
        │   └── plataforma.md     (2 features: Flow Builder, Apex Enhancements)
        │   └── desenvolvimento.md (2 features: LWC TypeScript, Apex Debug)
        ├── summer_26/
        │   ├── .meta.json        (release_id=262, 2 categorias, 4 features)
        │   └── plataforma.md     (2 features: Flow Builder, Apex Enhancements)
        │   └── desenvolvimento.md (2 features: LWC TypeScript, Apex Debug Plus)
        └── winter_26/
            ├── .meta.json        (release_id=263, 2 categorias, 2 features)
            └── plataforma.md     (2 features: Flow Orchestrator, Apex New)

    Devolve o Path da raiz.
    """
    base = tmp_path / "releases"
    base.mkdir(parents=True, exist_ok=True)

    # spring_26
    _write_meta(
        base,
        "spring_26",
        261,
        "Spring '26",
        [
            {"name": "Plataforma", "count": 2},
            {"name": "Desenvolvimento", "count": 2},
        ],
        total_features=4,
    )
    _write_md(
        base,
        "spring_26",
        "Plataforma",
        [
            "Flow Builder",
            "Apex Enhancements",
        ],
    )
    _write_md(
        base,
        "spring_26",
        "Desenvolvimento",
        [
            "LWC TypeScript",
            "Apex Debug",
        ],
    )

    # summer_26
    _write_meta(
        base,
        "summer_26",
        262,
        "Summer '26",
        [
            {"name": "Plataforma", "count": 2},
            {"name": "Desenvolvimento", "count": 2},
        ],
        total_features=4,
    )
    _write_md(
        base,
        "summer_26",
        "Plataforma",
        [
            "Flow Builder",
            "Apex Enhancements",
        ],
    )
    _write_md(
        base,
        "summer_26",
        "Desenvolvimento",
        [
            "LWC TypeScript",
            "Apex Debug Plus",
        ],
    )

    # winter_26
    _write_meta(
        base,
        "winter_26",
        263,
        "Winter '26",
        [
            {"name": "Plataforma", "count": 2},
            {"name": "Segurança", "count": 0},
        ],
        total_features=2,
    )
    _write_md(
        base,
        "winter_26",
        "Plataforma",
        [
            "Flow Orchestrator",
            "Apex New",
        ],
    )

    return base


@pytest.fixture
def releases_dir_fake_current_only(tmp_path: Path) -> Path:
    """Cria apenas uma release com features (para testar born-only).

    Layout:
        tmp_path/releases/
        └── summer_26/
            ├── .meta.json
            └── plataforma.md  (2 features)
    """
    base = tmp_path / "releases"
    base.mkdir(parents=True, exist_ok=True)
    _write_meta(
        base,
        "summer_26",
        262,
        "Summer '26",
        [{"name": "Plataforma", "count": 2}],
        total_features=2,
    )
    _write_md(
        base,
        "summer_26",
        "Plataforma",
        [
            "Flow Builder",
            "Apex Enhancements",
        ],
    )
    return base


@pytest.fixture
def releases_dir_fake_previous_only(tmp_path: Path) -> Path:
    """Cria apenas uma release anterior com features (para testar removed-only).

    Layout:
        tmp_path/releases/
        └── spring_26/
            ├── .meta.json
            └── plataforma.md  (2 features)
    """
    base = tmp_path / "releases"
    base.mkdir(parents=True, exist_ok=True)
    _write_meta(
        base,
        "spring_26",
        261,
        "Spring '26",
        [{"name": "Plataforma", "count": 2}],
        total_features=2,
    )
    _write_md(
        base,
        "spring_26",
        "Plataforma",
        [
            "Legacy Flow",
            "Deprecated Apex",
        ],
    )
    return base
