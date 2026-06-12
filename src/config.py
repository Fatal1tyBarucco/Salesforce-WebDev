"""
config.py — Configuração central do pipeline de Release Notes.

Adicionar novos tópicos ou releases aqui NÃO requer alterações no motor principal.
"""

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
# Tópicos Monitorados
# Para adicionar um novo tópico (ex: "data_cloud"), basta inserir um novo
# TopicConfig abaixo. Nenhuma outra alteração é necessária.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TopicConfig:
    """
    Configuração de um tópico de extração.

    Atributos:
        slug        : identificador único (nome do arquivo .md)
        display_name: título legível usado no Markdown gerado
        keywords    : termos de busca usados pelo parser para filtrar seções
    """

    slug: str
    display_name: str
    keywords: list[str] = field(default_factory=list)


MONITORED_TOPICS: list[TopicConfig] = [
    TopicConfig(
        slug="apex",
        display_name="Apex",
        keywords=[
            "apex",
            "trigger",
            "batch",
            "queueable",
            "schedulable",
            "anonymous",
            "governor limit",
            "soql",
            "sosl",
        ],
    ),
    TopicConfig(
        slug="lwc",
        display_name="Lightning Web Components (LWC)",
        keywords=[
            "lwc",
            "lightning web component",
            "lightning component",
            "aura",
            "wire",
            "lms",
            "lightning message service",
        ],
    ),
    TopicConfig(
        slug="flow",
        display_name="Flow & Automação",
        keywords=[
            "flow",
            "process builder",
            "workflow",
            "automation",
            "screen flow",
            "record-triggered",
            "scheduled flow",
        ],
    ),
    TopicConfig(
        slug="security",
        display_name="Segurança & Permissões",
        keywords=[
            "security",
            "permission",
            "shield",
            "encryption",
            "profile",
            "role",
            "sharing",
            "csp",
            "csrf",
            "oauth",
        ],
    ),
    TopicConfig(
        slug="integrations",
        display_name="Integrações & APIs",
        keywords=[
            "api",
            "rest",
            "soap",
            "bulk",
            "streaming",
            "platform event",
            "integration",
            "webhook",
            "named credential",
            "connected app",
        ],
    ),
    # -----------------------------------------------------------------------
    # Exemplo de extensão sem refatoração do motor:
    # TopicConfig(
    #     slug="data_cloud",
    #     display_name="Data Cloud",
    #     keywords=["data cloud", "cdp", "data stream", "calculated insight"],
    # ),
    # TopicConfig(
    #     slug="einstein_ai",
    #     display_name="Einstein AI & Agentforce",
    #     keywords=["einstein", "agentforce", "copilot", "prompt builder", "llm"],
    # ),
    # -----------------------------------------------------------------------
]
