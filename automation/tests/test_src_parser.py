"""Testes para src/parser.py — Extração dinâmica de árvore de tópicos."""

from bs4 import BeautifulSoup
from src.parser import ReleaseNotesParser
from src.config import TopicNode

# ---------------------------------------------------------------------------
# HTML de exemplo com estrutura de árvore do Salesforce Help (ToC)
# ---------------------------------------------------------------------------

SAMPLE_TOC_HTML = """
<html>
<body>
<ul class="tree">
  <!-- Root level 1 -->
  <li title="Notas de versão do Salesforce Winter '26"
      id="salesforce_release_notes_leaf"
      role="treeitem" aria-level="1">
    <div class="slds-tree__item">
      <a role="presentation"
         href="https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&amp;release=258&amp;type=5">
        Notas de versão do Salesforce Winter '26
      </a>
    </div>
    <ul>
      <!-- Categoria principal - nível 2 -->
      <li title="Desenvolvimento"
          id="rn_development_leaf"
          role="treeitem" aria-level="2">
        <div class="slds-tree__item">
          <a role="presentation"
             href="https://help.salesforce.com/s/articleView?id=release-notes.rn_development.htm&amp;release=258&amp;type=5">
            Desenvolvimento
          </a>
        </div>
        <ul>
          <!-- Subcategoria - nível 3 -->
          <li title="Apex"
              id="rn_apex_leaf"
              role="treeitem" aria-level="3">
            <div class="slds-tree__item">
              <a role="presentation"
                 href="https://help.salesforce.com/s/articleView?id=release-notes.rn_apex.htm&amp;release=258&amp;type=5">
                Apex
              </a>
            </div>
            <ul>
              <!-- Artigo - nível 4 com data-is-link -->
              <li title="Nova funcionalidade de Apex Triggers"
                  id="rn_apex_triggers_leaf"
                  role="treeitem" aria-level="4"
                  data-is-link="true">
                <div class="slds-tree__item">
                  <a role="presentation"
                     href="/s/articleView?id=release-notes.rn_apex_triggers.htm&amp;release=258&amp;type=5">
                    Nova funcionalidade de Apex Triggers
                  </a>
                </div>
              </li>
              <!-- Artigo 2 - nível 4 -->
              <li title="Melhorias no SOQL"
                  id="rn_apex_soql_leaf"
                  role="treeitem" aria-level="4"
                  data-is-link="true">
                <div class="slds-tree__item">
                  <a role="presentation"
                     href="/s/articleView?id=release-notes.rn_apex_soql.htm&amp;release=258&amp;type=5">
                    Melhorias no SOQL
                  </a>
                </div>
              </li>
            </ul>
          </li>
          <!-- Subcategoria LWC - nível 3 -->
          <li title="Componentes do Lightning"
              id="rn_lc_leaf"
              role="treeitem" aria-level="3">
            <div class="slds-tree__item">
              <a role="presentation"
                 href="https://help.salesforce.com/s/articleView?id=release-notes.rn_lc.htm&amp;release=258&amp;type=5">
                Componentes do Lightning
              </a>
            </div>
            <ul>
              <li title="LWC Dynamic Forms"
                  id="rn_lc_dynamic_forms_leaf"
                  role="treeitem" aria-level="4"
                  data-is-link="true">
                <div class="slds-tree__item">
                  <a role="presentation"
                     href="/s/articleView?id=release-notes.rn_lc_dynamic.htm&amp;release=258&amp;type=5">
                    LWC Dynamic Forms
                  </a>
                </div>
              </li>
            </ul>
          </li>
        </ul>
      </li>
      <!-- Categoria Segurança - nível 2 -->
      <li title="Segurança, identidade e privacidade"
          id="rn_security_leaf"
          role="treeitem" aria-level="2">
        <div class="slds-tree__item">
          <a role="presentation"
             href="https://help.salesforce.com/s/articleView?id=release-notes.rn_security.htm&amp;release=258&amp;type=5">
            Segurança, identidade e privacidade
          </a>
        </div>
        <ul>
          <li title="Melhorias no OAuth 2.0"
              id="rn_security_oauth_leaf"
              role="treeitem" aria-level="3"
              data-is-link="true">
            <div class="slds-tree__item">
              <a role="presentation"
                 href="/s/articleView?id=release-notes.rn_security_oauth.htm&amp;release=258&amp;type=5">
                Melhorias no OAuth 2.0
              </a>
            </div>
          </li>
        </ul>
      </li>
      <!-- Item excluído - deve ser filtrado -->
      <li title="Notas da versão mensais"
          id="rn_features_released_monthly_leaf"
          role="treeitem" aria-level="2"
          data-is-link="true">
        <div class="slds-tree__item">
          <a role="presentation"
             href="/s/articleView?id=release-notes.rn_features_released_monthly.htm&amp;release=258&amp;type=5">
            Notas da versão mensais
          </a>
        </div>
      </li>
    </ul>
  </li>
</ul>
</body>
</html>
"""

SAMPLE_ARTICLE_HTML = """
<html>
<body>
  <article>
    <h1>Nova funcionalidade de Apex Triggers</h1>
    <h2>Por que essa alteração é importante</h2>
    <p>Os triggers agora executam de forma assíncrona em contextos específicos,
       melhorando a escalabilidade das automações Apex.</p>
    <h2>Como usar</h2>
    <p>Adicione a anotação @future para triggers que processam grandes volumes.</p>
  </article>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Testes: extract_topic_tree
# ---------------------------------------------------------------------------


def test_extract_topic_tree_returns_level2_categories() -> None:
    """Deve retornar apenas categorias de nível 2 (sem o root de nível 1)."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup(SAMPLE_TOC_HTML, "html.parser")

    tree = parser.extract_topic_tree(soup, "Winter '26", 258)

    # Deve encontrar pelo menos 2 categorias (Desenvolvimento e Segurança)
    # "Notas da versão mensais" deve ser excluído (EXCLUDED_TOPIC_IDS)
    slugs = [node.node_id for node in tree]
    assert "rn_development" in slugs
    assert "rn_security" in slugs
    assert "rn_features_released_monthly" not in slugs


def test_extract_topic_tree_builds_hierarchy() -> None:
    """Deve construir a hierarquia correta de filhos."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup(SAMPLE_TOC_HTML, "html.parser")

    tree = parser.extract_topic_tree(soup, "Winter '26", 258)

    # Encontra o nó "Desenvolvimento"
    dev_node = next((n for n in tree if n.node_id == "rn_development"), None)
    assert dev_node is not None
    assert dev_node.level == 2
    assert dev_node.display_name == "Desenvolvimento"

    # Deve ter filhos (Apex e Componentes do Lightning)
    assert len(dev_node.children) >= 2
    child_ids = [c.node_id for c in dev_node.children]
    assert "rn_apex" in child_ids
    assert "rn_lc" in child_ids


def test_extract_topic_tree_identifies_leaf_articles() -> None:
    """Deve marcar corretamente os artigos folha (data-is-link='true')."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup(SAMPLE_TOC_HTML, "html.parser")

    tree = parser.extract_topic_tree(soup, "Winter '26", 258)

    dev_node = next((n for n in tree if n.node_id == "rn_development"), None)
    assert dev_node is not None

    apex_node = next((c for c in dev_node.children if c.node_id == "rn_apex"), None)
    assert apex_node is not None
    assert len(apex_node.children) == 2

    # Os artigos de nível 4 devem ser marcados como folhas
    for article_node in apex_node.children:
        assert article_node.is_leaf is True
        assert article_node.level == 4


def test_extract_topic_tree_empty_html() -> None:
    """Deve retornar lista vazia para HTML sem treeitems."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup("<html><body><p>No tree here</p></body></html>", "html.parser")

    tree = parser.extract_topic_tree(soup, "Winter '26", 258)
    assert tree == []


def test_extract_topic_tree_url_normalization() -> None:
    """Deve normalizar URLs relativas para URLs completas com os parâmetros corretos."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup(SAMPLE_TOC_HTML, "html.parser")

    tree = parser.extract_topic_tree(soup, "Winter '26", 258)

    # O artigo de Apex triggers tem URL relativa — deve ser normalizada
    dev_node = next((n for n in tree if n.node_id == "rn_development"), None)
    assert dev_node is not None

    apex_node = next((c for c in dev_node.children if c.node_id == "rn_apex"), None)
    assert apex_node is not None

    trigger_node = apex_node.children[0]
    assert trigger_node.url.startswith("https://help.salesforce.com")
    assert "language=pt_BR" in trigger_node.url
    assert "release=258" in trigger_node.url


def test_extract_topic_tree_node_slug_property() -> None:
    """O property slug deve retornar versão normalizada do node_id."""
    node = TopicNode(
        node_id="rn_development",
        display_name="Desenvolvimento",
        level=2,
        url="https://example.com",
    )
    assert node.slug == "development"


# ---------------------------------------------------------------------------
# Testes: extract_article_summary
# ---------------------------------------------------------------------------


def test_extract_article_summary_finds_why_section() -> None:
    """Deve extrair o texto da seção 'Por que essa alteração é importante'."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup(SAMPLE_ARTICLE_HTML, "html.parser")

    summary = parser.extract_article_summary(soup)
    assert "assíncrona" in summary or "escalabilidade" in summary


def test_extract_article_summary_fallback_to_first_paragraph() -> None:
    """Deve retornar o primeiro parágrafo significativo quando não há seção 'Por que'."""
    parser = ReleaseNotesParser()

    html = """
    <html><body>
      <article>
        <h1>Feature X</h1>
        <p>Short</p>
        <p>Este é um parágrafo suficientemente longo para ser considerado como resumo do artigo.</p>
      </article>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    summary = parser.extract_article_summary(soup)
    assert "suficientemente longo" in summary


def test_extract_article_summary_no_content() -> None:
    """Deve retornar mensagem padrão quando não há conteúdo adequado."""
    parser = ReleaseNotesParser()
    soup = BeautifulSoup("<html><body><p>ok</p></body></html>", "html.parser")

    summary = parser.extract_article_summary(soup)
    assert summary == "Resumo não disponível para este artigo."


# ---------------------------------------------------------------------------
# Testes: build_topic_content_map
# ---------------------------------------------------------------------------


def test_build_topic_content_map_generates_markdown() -> None:
    """Deve gerar mapa de conteúdo Markdown a partir da árvore de TopicNode."""
    parser = ReleaseNotesParser()

    # Monta árvore simples com artigos
    apex_node = TopicNode(
        node_id="rn_apex",
        display_name="Apex",
        level=3,
        url="https://help.salesforce.com/rn_apex",
    )
    apex_node.articles = [
        {
            "title": "Nova Funcionalidade Apex",
            "summary": "Resumo da nova funcionalidade.",
            "url": "https://help.salesforce.com/rn_apex_feature",
        }
    ]

    dev_node = TopicNode(
        node_id="rn_development",
        display_name="Desenvolvimento",
        level=2,
        url="https://help.salesforce.com/rn_development",
        children=[apex_node],
    )

    content_map = parser.build_topic_content_map([dev_node], "Winter '26")

    assert "development" in content_map
    lines = "\n".join(content_map["development"])
    assert "## Desenvolvimento — Winter '26" in lines
    assert "### Apex" in lines
    assert "Nova Funcionalidade Apex" in lines
    assert "Resumo da nova funcionalidade." in lines


def test_build_topic_content_map_excludes_empty_topics() -> None:
    """Não deve incluir tópicos sem artigos no mapa de conteúdo."""
    parser = ReleaseNotesParser()

    empty_node = TopicNode(
        node_id="rn_empty",
        display_name="Tópico Vazio",
        level=2,
        url="https://help.salesforce.com/rn_empty",
    )

    content_map = parser.build_topic_content_map([empty_node], "Winter '26")
    assert "empty" not in content_map


# ---------------------------------------------------------------------------
# Testes: _clean_text (utilitário interno)
# ---------------------------------------------------------------------------


def test_clean_text_removes_extra_whitespace() -> None:
    """Deve remover espaços extras e normalizar."""
    result = ReleaseNotesParser._clean_text("  Hello   World  ")
    assert result == "Hello World"


def test_clean_text_returns_empty_for_short_text() -> None:
    """Deve retornar string vazia para textos menores que 3 caracteres."""
    assert ReleaseNotesParser._clean_text("ab") == ""
    assert ReleaseNotesParser._clean_text("") == ""
