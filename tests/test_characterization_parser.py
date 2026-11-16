"""Testes de caracterização do parser — ToC, Feature Impact e resumos de artigo.

Congela, em `tests/golden/parser/*.json`, a estrutura de dados produzida hoje
por `ReleaseNotesParser` e `FeatureImpactParser` a partir de fixtures HTML/texto
(sem rede, 100% determinístico). Diferente de `tests/test_snapshot.py` (syrupy,
fragmentos pontuais), aqui o contrato congelado é o JSON completo de saída.

Regenerar goldens: CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_parser.py
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from bs4 import BeautifulSoup

from src.parser import (
    FeatureImpactCategory,
    FeatureImpactEntry,
    FeatureImpactParser,
    ReleaseNotesParser,
)
from tests.factories import make_feature_impact_text, make_toc_html
from tests.test_characterization_golden import assert_matches_golden_json

# Fixture rico, no formato do DOM real do portal Salesforce Help:
# - li SEM data-is-link dentro de div (como o portal) — nó vira container
# - id com hífen (rn_field-service) passa pela sanitização de _get_node_id
# - slug excluído (rn_change_log em EXCLUDED_NODE_SLUGS) sai da árvore
# - data-is-link="true" COM filhos é tratado como container (regra do parser)
# - label por title / span.tree-item-label / div[role=label] / fallback get_text
# - aria-level ausente no filho de "flow" cai no default 1
RICH_TOC_HTML: str = """
<html><body>
<nav class="toc-container">
  <ul class="tree">
    <li role="treeitem" aria-level="1" id="rn_root">
      <ul>
        <li role="treeitem" aria-level="2" id="rn_development" title="Desenvolvimento">
          <ul>
            <li role="treeitem" aria-level="3" id="rn_development_leaf" data-is-link="true">
              <a href="/s/articleView?id=release-notes.rn_apex_overview.htm">Apex Overview</a>
            </li>
            <li role="treeitem" aria-level="3" id="rn_field-service" data-is-link="true">
              <a href="https://help.salesforce.com/s/articleView?id=service.htm">Field Service</a>
            </li>
          </ul>
        </li>
        <li role="treeitem" aria-level="2" id="rn_change_log">
          <span class="tree-item-label">Change Log</span>
        </li>
        <li role="treeitem" aria-level="2" id="rn_flow">
          <div class="slds-tree__item">
            <div role="label">Fluxo</div>
            <a href="/flow">Flow Container</a>
          </div>
          <ul>
            <li role="treeitem" id="rn_flow_article" data-is-link="true">
              <a href="/flow/article1">Flow Article 1</a>
            </li>
          </ul>
        </li>
        <li role="treeitem" aria-level="2" id="rn_platform" data-is-link="true">
          <a href="/platform">Platform Leaf</a>
          <ul>
            <li role="treeitem" aria-level="3" id="rn_platform_child" data-is-link="true">
              <a href="/platform/child">Platform Child</a>
            </li>
          </ul>
        </li>
      </ul>
    </li>
  </ul>
</nav>
</body></html>
"""

# Texto de Feature Impact montado à mão para exercitar caminhos que a factory
# make_feature_impact_text() não alcança: descrição explícita de categoria,
# header de tabela, entrada parcial (confiança 0.7), subcategoria, seção
# duplicada (merge) e linha de uma coluna (confiança 0.5).
CRAFTED_FEATURE_IMPACT_TEXT: str = "\n".join(
    [
        "Desenvolvimento",
        "Categoria de desenvolvimento de aplicações e automações.",
        "RECURSO\tATIVADO PARA USUÁRIOS\tADMINS/DEVS\tCONFIG\tCONTATO",
        "Recurso Um\tYes\tYes\tNo\tNo",
        "Recurso Parcial\tYes\tNo",
        "Fluxos",
        "Recurso Dois\tYes\tNo\tYes\tNo",
        "Agentforce",
        "RECURSO\tATIVADO PARA USUÁRIOS\tADMINS/DEVS\tCONFIG\tCONTATO",
        "Recurso Agente\tYes\tYes\tYes\tNo",
        "Total de Recursos: 4",
        "Desenvolvimento",
        "Recurso Extra\tYes\tNo\tNo\tYes",
    ]
)

CRAFTED_LINK_MAP: dict[str, str] = {
    "Recurso Um": "https://help.salesforce.com/s/articleView?id=recurso_um.htm"
}

ARTICLE_SUMMARY_CASES: dict[str, str] = {
    "why_section_pt": (
        "<html><body><h2>Por Que Essa Alteração É Importante</h2>"
        "<p>  Esta alteração   acelera   a automação.  </p></body></html>"
    ),
    "why_section_en": (
        "<html><body><h3>Why</h3><p>Why this change matters for admins.</p></body></html>"
    ),
    "first_long_paragraph_in_content": (
        "<html><body><div class='content'><p>curto</p><p>"
        + "Parágrafo informativo com mais de cinquenta caracteres. " * 2
        + "</p></div></body></html>"
    ),
    "fallback_when_no_content": "<html><body><p>tiny</p></body></html>",
}


def _topic_tree_payload(html: str) -> list[dict[str, Any]]:
    """Extrai a árvore de tópicos de um HTML e serializa como dicts."""
    soup = BeautifulSoup(html, "html.parser")
    topics = ReleaseNotesParser().extract_topic_tree(soup)
    return [asdict(topic) for topic in topics]


def _entry_payload(entry: FeatureImpactEntry) -> dict[str, Any]:
    return {
        "name": entry.name,
        "available_users": entry.available_users,
        "available_admins": entry.available_admins,
        "requires_config": entry.requires_config,
        "contact_sf": entry.contact_sf,
        "confidence": entry.confidence,
        "docs_url": entry.docs_url,
    }


def _category_payload(category: FeatureImpactCategory) -> dict[str, Any]:
    return {
        "name": category.name,
        "description": category.description,
        "entries": [_entry_payload(e) for e in category.entries],
        "subcategories": {
            sub_name: [_entry_payload(e) for e in sub_entries]
            for sub_name, sub_entries in category.subcategories.items()
        },
        "avg_confidence": category.avg_confidence,
        "total_features": category.total_features,
    }


def _parse_payload(text: str, link_map: dict[str, str] | None = None) -> dict[str, Any]:
    parser = FeatureImpactParser()
    categories = parser.parse_text(text, link_map=link_map)
    return {
        "categories": [_category_payload(c) for c in categories],
        "parse_stats": parser.parse_stats(),
        "classification_quality": parser.classification_quality(categories),
    }


def test_topic_tree_extraction_matches_golden() -> None:
    """Congela a árvore extraída do DOM: exclusões, slugs, URLs e fallbacks."""
    payload = {
        "rich_fixture": _topic_tree_payload(RICH_TOC_HTML),
        "factory_toc_html": _topic_tree_payload(make_toc_html()),
        "missing_container": _topic_tree_payload("<html><body><p>sem toc</p></body></html>"),
    }
    assert_matches_golden_json(payload, "parser/toc_trees.json")


def test_extract_article_summary_matches_golden() -> None:
    """Congela o texto de resumo de artigo (seção "Por que", parágrafo, fallback)."""
    results = {
        name: ReleaseNotesParser().extract_article_summary(BeautifulSoup(html, "html.parser"))
        for name, html in ARTICLE_SUMMARY_CASES.items()
    }
    assert_matches_golden_json(results, "parser/article_summary.json")


def test_feature_impact_factory_text_matches_golden() -> None:
    """Congela parse_text() sobre a factory make_feature_impact_text(), com e sem link_map."""
    text = make_feature_impact_text()
    link_map = {"Vendas Feature 2": "https://help.salesforce.com/s/articleView?id=vendas2.htm"}
    payload = {
        "without_link_map": _parse_payload(text),
        "with_link_map": _parse_payload(text, link_map),
    }
    assert_matches_golden_json(payload, "parser/feature_impact_factory.json")


def test_feature_impact_crafted_text_matches_golden() -> None:
    """Congela subcategoria, seção duplicada (merge), flags parciais e confianças."""
    payload = _parse_payload(CRAFTED_FEATURE_IMPACT_TEXT, CRAFTED_LINK_MAP)
    assert_matches_golden_json(payload, "parser/feature_impact_crafted.json")
