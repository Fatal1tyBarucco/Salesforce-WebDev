"""
config.py — Configuração central do pipeline de Release Notes.

Tópicos são descobertos dinamicamente a partir da árvore de navegação
do Salesforce Help (não mais hardcoded).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

# ---------------------------------------------------------------------------
# Constantes Globais
# ---------------------------------------------------------------------------

PT_BR_PARAM: Final[str] = "&language=pt_BR"
EN_PARAM: Final[str] = "&language=en"

LANGUAGE_PARAMS: Final[dict[str, str]] = {
    "pt-BR": PT_BR_PARAM,
    "en": EN_PARAM,
}

BASE_URL: Final[str] = (
    "https://help.salesforce.com/s/articleView"
    "?id=release-notes.salesforce_release_notes.htm"
    "&release={release_id}"
    "&type=5"
    f"{PT_BR_PARAM}"
)

FEATURE_IMPACT_URL: Final[str] = (
    "https://help.salesforce.com/s/articleView"
    "?id=release-notes.rn_feature_impact.htm"
    "&release={release_id}"
    "&type=5"
    f"{PT_BR_PARAM}"
)

PDF_URL_TEMPLATE: Final[str] = (
    "https://www.salesforce.com/en-us/wp-content/uploads/sites/4/"
    "documents/PDF/release-in-a-box-{season}-{year_short}-v{version}.pdf"
)

REQUEST_TIMEOUT_SECONDS: Final[int] = 30
MAX_RETRY_ATTEMPTS: Final[int] = 5
RETRY_BASE_DELAY_SECONDS: Final[float] = 2.0  # backoff exponencial: 2^n
MAX_CONCURRENT_PAGES: Final[int] = 4
ARTICLE_FETCH_TIMEOUT_SECONDS: Final[int] = 45
RELEASES_DIR: Final[str] = "releases"
README_PATH: Final[str] = "README.md"
README_INDEX_START_MARKER: Final[str] = "<!-- RELEASE_INDEX_START -->"
README_INDEX_END_MARKER: Final[str] = "<!-- RELEASE_INDEX_END -->"

USER_AGENT: Final[str] = (
    "Mozilla/5.0 (compatible; SalesforceReleaseBot/1.0; "
    "+https://github.com/Fatal1tyBarucco/Salesforce-WebDev)"
)

# Slugs de nós da árvore de navegação que devem ser ignorados
# (não contêm artigos de release notes relevantes)
# NOTA: os slugs são derivados dos IDs removendo o prefixo "rn_"
EXCLUDED_NODE_SLUGS: Final[frozenset[str]] = frozenset(
    {
        "features_released_monthly",
        "change_log",
        "feature_impact",
        "previous_release_notes",
    }
)

# Mapeamento de nomes de categorias pt_BR → slug em inglês
ENGLISH_CATEGORY_SLUGS: Final[dict[str, str]] = {
    "Agentforce": "agentforce",
    "Análise de dados": "data-analysis",
    "Automação": "automation",
    "Commerce": "commerce",
    "Personalização": "customization",
    "Data 360": "data-360",
    "Desenvolvimento": "development",
    "Experience Cloud": "experience-cloud",
    "Field Service": "field-service",
    "Hyperforce": "hyperforce",
    "Setores": "industries",
    "Marketing": "marketing",
    "MuleSoft": "mulesoft",
    "Aplicativo móvel": "mobile-app",
    "OmniStudio": "omnistudio",
    "Partner Cloud": "partner-cloud",
    "Gerenciamento de receita": "revenue-management",
    "Vendas": "sales",
    "Integrações do Salesforce para Slack": "salesforce-slack-integrations",
    "Segurança, identidade e privacidade": "security-identity-privacy",
    "Serviço": "service",
    "Outros produtos e serviços do Salesforce": "other-salesforce-products",
    "Documentação legal": "legal-documentation",
    "Salesforce geral": "salesforce-general",
}

# Mapeamento de nomes de categorias pt_BR → nome em inglês
ENGLISH_CATEGORY_NAMES: Final[dict[str, str]] = {
    "Agentforce": "Agentforce",
    "Análise de dados": "Data Analysis",
    "Automação": "Automation",
    "Commerce": "Commerce",
    "Personalização": "Customization",
    "Data 360": "Data 360",
    "Desenvolvimento": "Development",
    "Experience Cloud": "Experience Cloud",
    "Field Service": "Field Service",
    "Hyperforce": "Hyperforce",
    "Setores": "Industries",
    "Marketing": "Marketing",
    "MuleSoft": "MuleSoft",
    "Aplicativo móvel": "Mobile App",
    "OmniStudio": "OmniStudio",
    "Partner Cloud": "Partner Cloud",
    "Gerenciamento de receita": "Revenue Management",
    "Vendas": "Sales",
    "Integrações do Salesforce para Slack": "Salesforce Slack Integrations",
    "Segurança, identidade e privacidade": "Security, Identity & Privacy",
    "Serviço": "Service",
    "Outros produtos e serviços do Salesforce": "Other Salesforce Products",
    "Documentação legal": "Legal Documentation",
    "Salesforce geral": "Salesforce General",
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


def build_release_info(release_id: int) -> ReleaseInfo:
    SEASONS = ("Spring", "Summer", "Winter")
    BASE_ID = 254
    BASE_YEAR = 25

    step = (release_id - BASE_ID) // 2
    season = SEASONS[step % 3]
    year = BASE_YEAR + step // 3
    if season == "Winter":
        year += 1

    year_short = str(year)
    name = f"{season} '{year_short}"
    slug = f"{season.lower()}_{year_short}"
    return ReleaseInfo(name=name, release_id=release_id, slug=slug)


def _id_to_season(release_id: int) -> str:
    SEASONS = ("Spring", "Summer", "Winter")
    BASE_ID = 254
    step = (release_id - BASE_ID) // 2
    return SEASONS[step % 3]


# ---------------------------------------------------------------------------
# TopicNode — nó dinâmico da árvore de navegação do Salesforce Help.
# Extraído diretamente do DOM (li[role="treeitem"]) em vez de keywords
# estáticas. A árvore completa é construída pelo parser.
# ---------------------------------------------------------------------------


@dataclass
class TopicNode:
    """Nó da árvore de navegação extraída do portal Salesforce Help."""

    slug: str  # ID do nó sem prefixo, ex: "rn_development"
    display_name: str  # Texto legível do label, ex: "Desenvolvimento"
    level: int  # aria-level no DOM (2 = categoria principal, 3+ = subcategorias)
    url: str  # URL completa (vazia para nós container)
    children: list[TopicNode] = field(default_factory=list)
    articles: list[dict[str, str]] = field(default_factory=list)

    def is_leaf(self) -> bool:
        """True se o nó não tem filhos (é artigo ou subsem filhos)."""
        return len(self.children) == 0

    def all_articles(self) -> list[dict[str, str]]:
        """Retorna todos os artigos recursivamente (filhos + netos)."""
        result: list[dict[str, str]] = list(self.articles)
        for child in self.children:
            result.extend(child.all_articles())
        return result

    def topic_file_slug(self) -> str:
        """Slug usado como nome do arquivo .md para este tópico."""
        return self.slug
