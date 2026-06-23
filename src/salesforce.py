"""Salesforce integration for release notes.

Provides Trailhead module linking, org limits cross-reference,
and sandbox deployment readiness checking.

Uses a curated mapping of feature categories to Trailhead modules,
since the Trailhead public API is no longer available.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

TRAILHEAD_BASE_URL = "https://trailhead.salesforce.com"

# Curated mapping of Salesforce feature categories to Trailhead modules
# Source: https://trailhead.salesforce.com/
TRAILHEAD_BY_CATEGORY: dict[str, list[dict[str, str]]] = {
    "Agentforce": [
        {"title": "Agentforce Basics", "url": "/content/learn/modules/agentforce-basics"},
        {
            "title": "Build an Agent with Agentforce",
            "url": "/content/learn/projects/build-an-agent-with-agentforce",
        },
        {
            "title": "Agentforce for Developers",
            "url": "/content/learn/modules/agentforce-for-developers",
        },
    ],
    "Análise de dados": [
        {"title": "Data Analysis with SOQL", "url": "/content/learn/modules/soql-for-admins"},
        {
            "title": "Reports & Dashboards for Lightning Experience",
            "url": "/content/learn/modules/reports_dashboards_lightning_experience",
        },
    ],
    "Automação": [
        {"title": "Flow Builder Basics", "url": "/content/learn/modules/flow-basics"},
        {
            "title": "Flow Builder Strategies",
            "url": "/content/learn/modules/flow-builder-strategies",
        },
        {"title": "Flow Builder Logic", "url": "/content/learn/modules/flow-builder-logic"},
    ],
    "Commerce": [
        {
            "title": "Commerce Cloud B2C Basics",
            "url": "/content/learn/modules/commerce-cloud-b2c-basics",
        },
        {
            "title": "B2B Commerce on Lightning Experience",
            "url": "/content/learn/modules/b2b-commerce-lightning",
        },
    ],
    "Personalização": [
        {"title": "Lightning App Builder", "url": "/content/learn/modules/lightning_app_builder"},
        {
            "title": "Customization Basics & Navigation",
            "url": "/content/learn/modules/customization_basics",
        },
    ],
    "Data 360": [
        {"title": "Data Cloud Basics", "url": "/content/learn/modules/data-cloud-basics"},
        {
            "title": "Data Cloud Ingestion and Transformation",
            "url": "/content/learn/modules/data-cloud-ingestion",
        },
    ],
    "Desenvolvimento": [
        {"title": "Apex Basics & Database", "url": "/content/learn/modules/apex_basics_database"},
        {
            "title": "Lightning Web Components Basics",
            "url": "/content/learn/modules/lex_aura_lwc_lgpd",
        },
        {"title": "Apex Triggers", "url": "/content/learn/modules/apex_triggers"},
        {
            "title": "Test Automation Strategies",
            "url": "/content/learn/modules/test_automation_strategies",
        },
    ],
    "Experience Cloud": [
        {
            "title": "Digital Experiences Basics",
            "url": "/content/learn/modules/digital_experiences",
        },
    ],
    "Field Service": [
        {
            "title": "Field Service Lightning Basics",
            "url": "/content/learn/modules/field-service-lightning-basics",
        },
        {
            "title": "Field Service Lightning Dispatch",
            "url": "/content/learn/modules/field-service-dispatch",
        },
    ],
    "Hyperforce": [
        {"title": "Hyperforce Basics", "url": "/content/learn/modules/hyperforce-basics"},
    ],
    "Setores": [
        {"title": "Industry Cloud Basics", "url": "/content/learn/modules/industry-cloud-basics"},
    ],
    "Marketing": [
        {
            "title": "Marketing Cloud Engagement Basics",
            "url": "/content/learn/modules/marketing-cloud-engagement-basics",
        },
        {
            "title": "Marketing Cloud Account Engagement Basics",
            "url": "/content/learn/modules/marketing-cloud-account-engagement-basics",
        },
    ],
    "MuleSoft": [
        {
            "title": "MuleSoft Composer Basics",
            "url": "/content/learn/modules/mulesoft-composer-basics",
        },
        {
            "title": "MuleSoft for Salesforce Integration",
            "url": "/content/learn/modules/mulesoft-for-salesforce-integration",
        },
    ],
    "Aplicativo móvel": [
        {
            "title": "Salesforce Mobile App Customization",
            "url": "/content/learn/modules/salesforce-mobile-app-customization",
        },
    ],
    "OmniStudio": [
        {"title": "OmniStudio Basics", "url": "/content/learn/modules/omnistudio-basics"},
    ],
    "Partner Cloud": [
        {"title": "Partner Cloud Basics", "url": "/content/learn/modules/partner-cloud-basics"},
    ],
    "Gerenciamento de receita": [
        {"title": "Revenue Cloud Basics", "url": "/content/learn/modules/revenue-cloud-basics"},
        {"title": "CPQ Basics", "url": "/content/learn/modules/cpq-basics"},
    ],
    "Vendas": [
        {
            "title": "Sales Cloud for Sales Reps",
            "url": "/content/learn/modules/sales_cloud_for_sales_reps",
        },
        {
            "title": "Opportunity Management Basics",
            "url": "/content/learn/modules/opportunity_management_basics",
        },
    ],
    "Integrações do Salesforce para Slack": [
        {
            "title": "Slack Basics for Salesforce",
            "url": "/content/learn/modules/slack-basics-for-salesforce",
        },
    ],
    "Segurança, identidade e privacidade": [
        {"title": "Security Basics", "url": "/content/learn/modules/security_basics"},
        {"title": "Identity Basics", "url": "/content/learn/modules/identity_basics"},
    ],
    "Serviço": [
        {
            "title": "Service Cloud for Lightning Experience",
            "url": "/content/learn/modules/service-cloud-lightning-experience",
        },
        {"title": "Case Management Basics", "url": "/content/learn/modules/case-management-basics"},
    ],
    "Outros produtos e serviços do Salesforce": [
        {
            "title": "Salesforce Platform App Builder",
            "url": "/content/learn/modules/platform-app-builder",
        },
    ],
}


@dataclass
class TrailheadModule:
    """A Trailhead learning module."""

    title: str
    url: str
    module_type: str = ""
    estimated_time: str = ""
    points: int = 0


@dataclass
class OrgLimits:
    """Salesforce org limits data."""

    api_requests_used: int = 0
    api_requests_limit: int = 0
    data_storage_used_mb: float = 0.0
    data_storage_limit_mb: float = 0.0
    file_storage_used_mb: float = 0.0
    file_storage_limit_mb: float = 0.0
    daily_async_jobs_used: int = 0
    daily_async_jobs_limit: int = 0


@dataclass
class SandboxStatus:
    """Sandbox deployment readiness status."""

    sandbox_name: str
    ready: bool
    issues: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    org_limits: OrgLimits | None = None


@dataclass
class FeatureReadiness:
    """Readiness assessment for a feature category."""

    category: str
    trailhead_modules: list[TrailheadModule]
    requires_config: bool = False
    requires_license: bool = False
    sandbox_ready: bool = True
    notes: list[str] = field(default_factory=list)


def search_trailhead(query: str, max_results: int = 5) -> list[TrailheadModule]:
    """Search Trailhead for modules matching a query.

    Uses curated mapping of Salesforce feature categories to Trailhead modules.
    Falls back to URL-based search if category not found in mapping.
    """
    # Direct lookup in curated mapping
    modules_data = TRAILHEAD_BY_CATEGORY.get(query, [])

    # If not found, try partial match
    if not modules_data:
        for key, value in TRAILHEAD_BY_CATEGORY.items():
            if query.lower() in key.lower() or key.lower() in query.lower():
                modules_data = value
                break

    modules: list[TrailheadModule] = []
    for item in modules_data[:max_results]:
        url = item.get("url", "")
        if not url.startswith("http"):
            url = TRAILHEAD_BASE_URL + url
        modules.append(
            TrailheadModule(
                title=item.get("title", ""),
                url=url,
                module_type=item.get("type", "module"),
                estimated_time=item.get("estimated_time", ""),
                points=int(item.get("points", 0) or 0),
            )
        )

    return modules


def get_release_trailhead_url(release_slug: str) -> str:
    """Get the Trailhead release highlights URL for a release.

    Pattern: https://trailhead.salesforce.com/content/learn/modules/{slug}-release-highlights
    Example: summer_26 -> summer-26-release-highlights
    """
    slug_dash = release_slug.replace("_", "-")
    return f"{TRAILHEAD_BASE_URL}/content/learn/modules/{slug_dash}-release-highlights"


def get_release_blog_url(release_slug: str) -> str:
    """Get the Salesforce blog post URL for a release.

    Pattern: https://www.salesforce.com/blog/platform-{slug}-release/
    Example: summer_26 -> summer-26-release
    """
    slug_dash = release_slug.replace("_", "-")
    return f"https://www.salesforce.com/blog/platform-{slug_dash}-release/"


def get_release_community_url(release_slug: str) -> str:
    """Get the Trailblazer Community feed URL for a release.

    This is a general link since community posts don't follow a fixed URL pattern.
    """
    return "https://trailhead.salesforce.com/trailblazer-community/feed"


def generate_release_resources_section(release_slug: str, release_name: str) -> str:
    """Generate a markdown section with Trailhead links for a release.

    This section is included at the top of each release's .md files.
    """
    trailhead_url = get_release_trailhead_url(release_slug)

    return f"""## 🔗 Trailhead

- [{release_name} Release Highlights]({trailhead_url})

"""


def find_related_modules(
    feature_categories: list[str],
    max_per_category: int = 3,
) -> dict[str, list[TrailheadModule]]:
    """Find Trailhead modules related to each feature category.

    Returns a dict mapping category name to list of related modules.
    """
    results: dict[str, list[TrailheadModule]] = {}
    for category in feature_categories:
        modules = search_trailhead(category, max_results=max_per_category)
        if modules:
            results[category] = modules
    return results


def assess_feature_readiness(
    category: str,
    availability_flags: dict[str, bool] | None = None,
) -> FeatureReadiness:
    """Assess readiness for deploying a feature category.

    Checks Trailhead availability, configuration requirements,
    and licensing needs based on availability flags from the
    feature impact table.
    """
    modules = search_trailhead(category, max_results=3)

    requires_config = False
    requires_license = False
    notes: list[str] = []

    if availability_flags:
        requires_config = availability_flags.get("requires_config", False)
        requires_license = availability_flags.get("contact_sf", False)

        if requires_config:
            notes.append("Requer configuração pelo administrador antes de ativar")
        if requires_license:
            notes.append("Entre em contato com a Salesforce para verificar licenciamento")

    if not modules:
        notes.append("Nenhum módulo Trailhead encontrado para esta categoria")

    return FeatureReadiness(
        category=category,
        trailhead_modules=modules,
        requires_config=requires_config,
        requires_license=requires_license,
        sandbox_ready=True,
        notes=notes,
    )


def check_sandbox_readiness(
    org_limits: OrgLimits | None = None,
    features_to_deploy: int = 0,
) -> SandboxStatus:
    """Check if a sandbox is ready for deployment.

    Evaluates org limits and feature count to determine readiness.
    """
    issues: list[str] = []
    warnings: list[str] = []

    if org_limits:
        # Check API limit
        if org_limits.api_requests_limit > 0:
            api_pct = org_limits.api_requests_used / org_limits.api_requests_limit
            if api_pct > 0.9:
                issues.append(f"API requests critically high: {api_pct:.0%} used")
            elif api_pct > 0.7:
                warnings.append(f"API requests elevated: {api_pct:.0%} used")

        # Check data storage
        if org_limits.data_storage_limit_mb > 0:
            storage_pct = org_limits.data_storage_used_mb / org_limits.data_storage_limit_mb
            if storage_pct > 0.9:
                issues.append(f"Data storage critically high: {storage_pct:.0%} used")
            elif storage_pct > 0.7:
                warnings.append(f"Data storage elevated: {storage_pct:.0%} used")

        # Check file storage
        if org_limits.file_storage_limit_mb > 0:
            file_pct = org_limits.file_storage_used_mb / org_limits.file_storage_limit_mb
            if file_pct > 0.9:
                issues.append(f"File storage critically high: {file_pct:.0%} used")

        # Check async jobs
        if org_limits.daily_async_jobs_limit > 0:
            async_pct = org_limits.daily_async_jobs_used / org_limits.daily_async_jobs_limit
            if async_pct > 0.9:
                issues.append(f"Async jobs critically high: {async_pct:.0%} used")

    if features_to_deploy > 500:
        warnings.append(
            f"Large deployment: {features_to_deploy} features. Consider staged rollout."
        )
    elif features_to_deploy > 200:
        notes_msg = f"Moderate deployment: {features_to_deploy} features"
        warnings.append(notes_msg)

    return SandboxStatus(
        sandbox_name="",
        ready=len(issues) == 0,
        issues=issues,
        warnings=warnings,
        org_limits=org_limits,
    )


def generate_readiness_report(
    categories: list[dict[str, Any]],
    org_limits: OrgLimits | None = None,
) -> str:
    """Generate a markdown readiness report for all categories."""
    lines = ["# 📋 Relatório de Prontidão de Deploy\n"]

    total_features = sum(c.get("count", 0) for c in categories)
    lines.append(f"**Total de features:** {total_features}\n")

    # Sandbox check
    sandbox = check_sandbox_readiness(org_limits, total_features)
    if sandbox.ready:
        lines.append("## ✅ Sandbox: Pronta\n")
    else:
        lines.append("## ❌ Sandbox: Não Pronta\n")
        for issue in sandbox.issues:
            lines.append(f"- ❌ {issue}")
        for warning in sandbox.warnings:
            lines.append(f"- ⚠️ {warning}")
        lines.append("")

    # Category readiness
    lines.append("## 📊 Prontidão por Categoria\n")
    lines.append("| Categoria | Features | Trailhead | Config | Licença |")
    lines.append("|-----------|----------|-----------|--------|---------|")

    for cat in categories:
        name = cat.get("name", "?")
        count = cat.get("count", 0)
        readiness = assess_feature_readiness(name)
        trailhead_icon = "✅" if readiness.trailhead_modules else "❌"
        config_icon = "⚠️" if readiness.requires_config else "✅"
        license_icon = "⚠️" if readiness.requires_license else "✅"
        lines.append(f"| {name} | {count} | {trailhead_icon} | {config_icon} | {license_icon} |")

    lines.append("")
    lines.append("---\n_Gerado automaticamente pelo pipeline de Release Notes_")

    return "\n".join(lines)


TRAILHEAD_CACHE_FILE = "notifications/trailhead_cache.json"


def _load_trailhead_cache() -> dict[str, list[str]]:
    """Load previously known Trailhead module URLs per category."""
    from pathlib import Path

    cache_path = Path(TRAILHEAD_CACHE_FILE)
    if not cache_path.exists():
        return {}
    try:
        data: dict[str, list[str]] = json.loads(cache_path.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, OSError):
        return {}


def _save_trailhead_cache(cache: dict[str, list[str]]) -> None:
    """Save Trailhead module URLs cache."""
    from pathlib import Path

    cache_path = Path(TRAILHEAD_CACHE_FILE)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        logger.warning("Failed to save Trailhead cache")


def detect_new_trailhead_content(
    categories: list[str],
    max_per_category: int = 5,
) -> dict[str, list[TrailheadModule]]:
    """Detect new Trailhead modules since last check.

    Searches Trailhead for each category, compares with cached URLs,
    and returns only newly discovered modules.

    Returns:
        Dict mapping category name to list of NEW modules not previously seen.
    """
    cache = _load_trailhead_cache()
    new_modules: dict[str, list[TrailheadModule]] = {}

    for category in categories:
        modules = search_trailhead(category, max_results=max_per_category)
        known_urls = set(cache.get(category, []))

        fresh = [m for m in modules if m.url not in known_urls]
        if fresh:
            new_modules[category] = fresh

        # Update cache with all current URLs
        cache[category] = [m.url for m in modules]

    _save_trailhead_cache(cache)
    return new_modules


def generate_trailhead_update_report(
    new_modules: dict[str, list[TrailheadModule]],
) -> str:
    """Generate a markdown report of newly discovered Trailhead content."""
    if not new_modules:
        return "## ✅ Trailhead — Sem novidades\n\nNenhum novo módulo encontrado desde a última verificação.\n"

    lines = ["## 🆕 Trailhead — Novos Módulos Detectados\n"]

    total = sum(len(mods) for mods in new_modules.values())
    lines.append(f"**{total} novos módulos** em {len(new_modules)} categorias:\n")

    for category, modules in sorted(new_modules.items()):
        lines.append(f"### {category}\n")
        for mod in modules:
            time_str = f" ({mod.estimated_time})" if mod.estimated_time else ""
            points_str = f" — {mod.points} pts" if mod.points else ""
            lines.append(f"- [{mod.title}]({mod.url}){time_str}{points_str}")
        lines.append("")

    lines.append("---\n_Gerado automaticamente pelo pipeline de Release Notes_")
    return "\n".join(lines)
