"""
config.py — Configuração central do pipeline de Release Notes.

A abordagem agora é baseada em descoberta dinâmica via árvore de navegação
do portal Salesforce Help. Não é necessário definir tópicos manualmente.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

TopicContentMap = dict[str, list[str]]

# ---------------------------------------------------------------------------
# Constantes Globais
# ---------------------------------------------------------------------------

PT_BR_PARAM: Final[str] = "&language=pt_BR"

BASE_URL: Final[str] = (
    "https://help.salesforce.com/s/articleView"
    "?id=release-notes.salesforce_release_notes.htm"
    "&release={release_id}"
    "&type=5"
    f"{PT_BR_PARAM}"
)

REQUEST_TIMEOUT_SECONDS: Final[int] = 30
MAX_RETRY_ATTEMPTS: Final[int] = 5
RETRY_BASE_DELAY_SECONDS: Final[float] = 2.0  # backoff exponencial: 2^n
RELEASES_DIR: Final[str] = "releases"
README_PATH: Final[str] = "README.md"
README_INDEX_START_MARKER: Final[str] = "<!-- RELEASE_INDEX_START -->"
README_INDEX_END_MARKER: Final[str] = "<!-- RELEASE_INDEX_END -->"

USER_AGENT: Final[str] = (
    "Mozilla/5.0 (compatible; SalesforceReleaseBot/1.0; "
    "+https://github.com/Fatal1tyBarucco/Salesforce-WebDev)"
)

# ---------------------------------------------------------------------------
# IDs de itens a excluir da extração (não são conteúdo de release notes)
# ---------------------------------------------------------------------------

EXCLUDED_TOPIC_IDS: Final[set[str]] = {
    "rn_features_released_monthly",  # notas mensais (separado)
    "rn_change_log_rn_change_log",  # log de mudanças
    "rn_feature_impact",  # "como e quando os recursos ficam disponíveis"
    "rn_previous_release_notes",  # notas de versão anteriores
    "rn_compliance_docs",  # documentação legal
    "salesforce_release_notes",  # root item (nivel 1)
}

# ---------------------------------------------------------------------------
# Mapeamento de Releases Conhecidas
# release_id corresponde ao parâmetro ?release= da URL oficial do Salesforce.
# Padrão de numeração: incrementos de 2 por release (Summer=x6, Winter=x8, Spring=x0).
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ReleaseInfo:
    """Metadados imutáveis de uma release do Salesforce."""

    name: str  # Ex: "Summer '26"
    release_id: int  # Ex: 262
    slug: str  # Ex: "summer_26" — usado como nome de diretório


KNOWN_RELEASES: list[ReleaseInfo] = [
    ReleaseInfo(name="Spring '25", release_id=254, slug="spring_25"),
    ReleaseInfo(name="Summer '25", release_id=256, slug="summer_25"),
    ReleaseInfo(name="Winter '26", release_id=258, slug="winter_26"),
    ReleaseInfo(name="Spring '26", release_id=260, slug="spring_26"),
    ReleaseInfo(name="Summer '26", release_id=262, slug="summer_26"),
]

# ---------------------------------------------------------------------------
# Modelo de Tópico Dinâmico
# Representa um nó da árvore de navegação do Salesforce Help.
# Construído pelo parser a partir do DOM da página de release notes.
# ---------------------------------------------------------------------------


@dataclass
class TopicNode:
    """
    Nó dinâmico da árvore de tópicos do Salesforce Help.

    Atributos:
        node_id     : ID do <li> sem o sufixo '_leaf' (ex: 'rn_development')
        display_name: Texto do link/título do tópico (ex: 'Desenvolvimento')
        level       : Profundidade na árvore (2=categoria, 3=subcategoria, 4+=artigo)
        url         : URL completa do artigo/índice no Salesforce Help
        children    : Nós filhos (subcategorias e artigos)
        articles    : Artigos com scraping completo (título, url, resumo)
        is_leaf     : True se o nó é um artigo (data-is-link="true")
    """

    node_id: str
    display_name: str
    level: int
    url: str
    children: list[TopicNode] = field(default_factory=list)
    articles: list[dict[str, str]] = field(default_factory=list)
    is_leaf: bool = False

    @property
    def slug(self) -> str:
        """Slug normalizado para uso como nome de arquivo."""
        # Remove prefixo 'rn_' e substitui caracteres inválidos
        raw = self.node_id.replace("rn_", "", 1).replace("-", "_")
        return raw[:64]  # limita comprimento


# ---------------------------------------------------------------------------
# Compatibilidade Retroativa — mantida para não quebrar testes existentes
# ---------------------------------------------------------------------------


# MONITORED_TOPICS é mantido vazio para compatibilidade de imports legados.
# O novo fluxo usa TopicNode (descoberta dinâmica via árvore do portal).
@dataclass(frozen=True)
class TopicConfig:
    """
    [LEGADO] Configuração estática de um tópico.

    Mantida apenas para compatibilidade com testes existentes.
    O novo pipeline usa TopicNode com descoberta dinâmica.
    """

    slug: str
    display_name: str
    keywords: list[str] = field(default_factory=list)


MONITORED_TOPICS: list[TopicConfig] = []
