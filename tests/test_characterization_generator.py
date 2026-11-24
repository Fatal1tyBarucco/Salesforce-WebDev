"""Testes de caracterização do MarkdownGenerator — arquivos .md por tópico.

Congela em `tests/golden/generator/topic_files.json` o texto exato que
`MarkdownGenerator.generate()` escreve hoje (header com data congelada,
corpo por artigo, mensagem de "sem conteúdo"), além do resultado de
`list_generated_releases()` e do cabeçalho com badges.

Todos os arquivos são escritos em tmp_path; nenhum arquivo do repositório é
tocado. Regenerar goldens:
CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_generator.py
"""

from __future__ import annotations

from pathlib import Path

from freezegun import freeze_time

from src.config import TopicNode
from src.generator import MarkdownGenerator
from tests.factories import make_release, make_topic_node, make_topic_tree
from tests.test_characterization_golden import (
    FROZEN_TIMESTAMP,
    assert_matches_golden_json,
)

SOURCE_URL: str = (
    "https://help.salesforce.com/s/articleView?"
    "id=release-notes.rn_release_notes.htm&release=262&type=5&language=pt_BR"
)


def _build_topic_tree() -> list[TopicNode]:
    """Árvore cobrindo: artigos aninhados, nó vazio e artigo com summary."""
    tree: list[TopicNode] = make_topic_tree(categories=["Desenvolvimento"], articles_per_category=2)
    tree.append(
        make_topic_node(
            slug="rn_vazio",
            display_name="Vazio",
            level=2,
            url="",
        )
    )
    tree.append(
        make_topic_node(
            slug="rn_com_resumo",
            display_name="Com Resumo",
            level=2,
            url="",
            articles=[
                {
                    "title": "Artigo com resumo",
                    "url": "https://help.salesforce.com/s/articleView?id=resumo.htm",
                    "summary": "Resumo do artigo congelado para caracterização.",
                }
            ],
        )
    )
    return tree


def test_generate_topic_files_match_golden(tmp_path: Path) -> None:
    """Congela o conteúdo dos .md gerados por release (com relógio congelado)."""
    base_dir = tmp_path / "releases"
    release = make_release(name="Summer '26", release_id=262, slug="summer_26")
    generator = MarkdownGenerator(base_dir=str(base_dir))

    with freeze_time(FROZEN_TIMESTAMP):
        written = generator.generate(release, _build_topic_tree(), SOURCE_URL)

    files: dict[str, str] = {path.name: path.read_text(encoding="utf-8") for path in written}
    payload = {
        "files": files,
        "list_generated_releases": generator.list_generated_releases(),
        "release_header_with_badges": generator.generate_release_header_with_badges(
            release, total_features=42, category_count=3
        ),
    }
    assert_matches_golden_json(payload, "generator/topic_files.json")
