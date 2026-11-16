"""Testes de caracterização de src/release_docs.py — docs por release e metadados.

Congela em `tests/golden/release_docs/`:
- `category_files.json`: texto exato dos .md por categoria gerados por
  `_generate_release_files()` nos idiomas pt_BR e en_US;
- `meta_history.json`: `.meta.json` e `releases/history.json` produzidos por
  `_update_readme_single()` na primeira e na segunda execução (versão bump);
- `naming.json`: mapeamento release_id → nome/slug, slug de categoria e emoji.

RELEASES_DIR é redirecionado via monkeypatch para tmp_path — nenhum arquivo do
repositório é escrito. Regenerar goldens:
CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_release_docs.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from freezegun import freeze_time

from src import release_docs
from src.generator import MarkdownGenerator
from src.parser import FeatureImpactCategory, FeatureImpactParser
from tests.factories import make_feature_impact_text, make_release
from tests.test_characterization_golden import FROZEN_TIMESTAMP, assert_matches_golden_json

CATEGORIA_NAMES: list[str] = [
    "Análise de dados",
    "Segurança, identidade e privacidade",
    "Integrações do Salesforce para Slack",
    "Outros produtos e serviços do Salesforce",
    "Vendas",
    "Agentforce",
]


def _parse_categories() -> list[FeatureImpactCategory]:
    """Categorias reais obtidas pelo mesmo caminho do pipeline (factory → parser)."""
    return FeatureImpactParser().parse_text(make_feature_impact_text())


def _relative_map(paths: list[Path], base: Path) -> dict[str, str]:
    return {str(p.relative_to(base)): p.read_text(encoding="utf-8") for p in paths}


async def test_generate_release_files_match_golden(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Congela os .md por categoria (toggle, tabela, Trailhead, rodapé) em 2 idiomas."""
    releases_dir = tmp_path / "releases"
    monkeypatch.setattr(release_docs, "RELEASES_DIR", str(releases_dir))

    release = make_release(name="Summer '26", release_id=262, slug="summer_26")
    categories = _parse_categories()
    generator = MarkdownGenerator(base_dir=str(releases_dir))

    # translator=None de propósito: a tradução en_US passa pelo LLM
    # (TranslatorService.translate_feature) e não é determinística.
    pt_paths = await release_docs._generate_release_files(
        release, categories, generator, None, "pt_BR"
    )
    en_paths = await release_docs._generate_release_files(
        release, categories, generator, None, "en_US"
    )

    payload = {
        "pt_BR": _relative_map(pt_paths, releases_dir),
        "en_US": _relative_map(en_paths, releases_dir),
    }
    assert_matches_golden_json(payload, "release_docs/category_files.json")


def test_update_readme_single_meta_and_history_match_golden(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Congela .meta.json e history.json na 1ª e 2ª execução (bump de versão)."""
    releases_dir = tmp_path / "releases"
    monkeypatch.setattr(release_docs, "RELEASES_DIR", str(releases_dir))

    release = make_release(name="Summer '26", release_id=262, slug="summer_26")
    categories = _parse_categories()
    # Em produção process_single_release() cria o diretório antes; aqui o teste
    # replica essa pré-condição.
    (releases_dir / release.slug).mkdir(parents=True, exist_ok=True)
    meta_path = releases_dir / release.slug / ".meta.json"
    history_path = releases_dir / "history.json"

    with freeze_time(FROZEN_TIMESTAMP):
        release_docs._update_readme_single(release, categories)
        first_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        first_history = json.loads(history_path.read_text(encoding="utf-8"))

        release_docs._update_readme_single(release, categories)
        second_meta = json.loads(meta_path.read_text(encoding="utf-8"))
        second_history = json.loads(history_path.read_text(encoding="utf-8"))

    payload = {
        "first_run": {"meta": first_meta, "history": first_history},
        "second_run": {"meta": second_meta, "history": second_history},
    }
    assert_matches_golden_json(payload, "release_docs/meta_history.json")


def test_release_naming_helpers_match_golden() -> None:
    """Congela naming de release (id→nome/slug), slug de categoria e emoji."""
    release_ids = [248, 250, 254, 256, 258, 260, 262, 264, 266, 268, 270, 300]
    payload = {
        "release_ids": [
            {
                "release_id": rid,
                "name": release_docs._build_release_name(rid),
                "slug": release_docs._build_release_slug(rid),
            }
            for rid in release_ids
        ],
        "category_slugs": {name: release_docs._slugify_category(name) for name in CATEGORIA_NAMES},
        "release_emojis": {
            name: release_docs._get_release_emoji(name)
            for name in ["Spring '26", "Summer '26", "Winter '27", "Unknown Season"]
        },
    }
    assert_matches_golden_json(payload, "release_docs/naming.json")
