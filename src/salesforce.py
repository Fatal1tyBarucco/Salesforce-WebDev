"""Salesforce integration for release notes.

Provides Trailhead module linking, org limits cross-reference,
and sandbox deployment readiness checking.

Uses a curated mapping of feature categories to Trailhead modules,
since the Trailhead public API is no longer available.
"""

from __future__ import annotations

import functools

import json
import logging
from .exceptions import ConfigError
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

TRAILHEAD_BASE_URL = "https://trailhead.salesforce.com"
_DEFAULT_TRAILHEAD_JSON = Path(__file__).resolve().parent / "trailhead.json"


def _get_trailhead_service() -> TrailheadMappingService:
    """Return a cached TrailheadMappingService instance (lazy singleton via lru_cache)."""
    return _get_trailhead_service_cached()


@functools.lru_cache(maxsize=1)
def _get_trailhead_service_cached() -> TrailheadMappingService:
    """Create and cache the TrailheadMappingService instance."""
    return TrailheadMappingService()


@dataclass
class TrailheadModule:
    """A Trailhead learning module."""

    title: str
    url: str
    module_type: str = ""
    estimated_time: str = ""
    points: int = 0


class TrailheadMappingService:
    """Dynamic loader for Trailhead category-to-module mappings from JSON."""

    def __init__(self, config_path: Path | None = None) -> None:
        self._config_path = config_path or _DEFAULT_TRAILHEAD_JSON
        self._categories: dict[str, list[dict[str, str]]] | None = None

    @property
    def categories(self) -> dict[str, list[dict[str, str]]]:
        if self._categories is None:
            self._categories = self._load_categories()
        return self._categories

    def _load_categories(self) -> dict[str, list[dict[str, str]]]:
        if not self._config_path.exists():
            raise ConfigError(f"Trailhead config not found at {self._config_path}")

        raw = self._config_path.read_text(encoding="utf-8")
        try:
            data: Any = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {self._config_path}: {exc}") from exc

        if not isinstance(data, dict):
            raise ConfigError(f"Trailhead config must be a JSON object, got {type(data).__name__}")

        validated: dict[str, list[dict[str, str]]] = {}
        for category, modules in data.items():
            if not isinstance(modules, list):
                raise ConfigError(
                    f"Category '{category}' must map to a list, got {type(modules).__name__}"
                )
            entries: list[dict[str, str]] = []
            for entry in modules:
                if not isinstance(entry, dict):
                    raise ConfigError(
                        f"Module entry in '{category}' must be an object, got {type(entry).__name__}"
                    )
                if "title" not in entry:
                    raise ConfigError(
                        f"Module entry in '{category}' missing required 'title' field"
                    )
                if "url" not in entry:
                    raise ConfigError(f"Module entry in '{category}' missing required 'url' field")
                entry_dict: dict[str, str] = {
                    "title": str(entry["title"]),
                    "url": str(entry["url"]),
                }
                if "type" in entry:
                    entry_dict["type"] = str(entry["type"])
                if "estimated_time" in entry:
                    entry_dict["estimated_time"] = str(entry["estimated_time"])
                if "points" in entry:
                    entry_dict["points"] = str(entry["points"])
                entries.append(entry_dict)
            validated[category] = entries

        return validated

    def search(self, query: str, max_results: int = 5) -> list[TrailheadModule]:
        """Search Trailhead modules matching *query* (exact first, then partial)."""
        cats = self.categories

        # Exact match
        modules_data = cats.get(query, [])

        # Partial match (substring in either direction, case-insensitive)
        if not modules_data:
            query_lower = query.lower()
            for key, value in cats.items():
                if query_lower in key.lower() or key.lower() in query_lower:
                    modules_data = value
                    break

        result: list[TrailheadModule] = []
        for item in modules_data[:max_results]:
            url = item["url"]
            if not url.startswith("http"):
                url = TRAILHEAD_BASE_URL + url
            result.append(
                TrailheadModule(
                    title=item["title"],
                    url=url,
                    module_type=item.get("type", "module"),
                    estimated_time=item.get("estimated_time", ""),
                    points=int(item.get("points", 0) or 0),
                )
            )

        return result


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
    return _get_trailhead_service().search(query, max_results)


def get_release_trailhead_url(release_slug: str) -> str:
    """Get the Trailhead release highlights URL for a release.

    Pattern: https://trailhead.salesforce.com/content/learn/modules/{slug}-release-highlights
    Example: summer_26 -> summer-26-release-highlights
    """
    slug_dash = release_slug.replace("_", "-")
    return f"{TRAILHEAD_BASE_URL}/content/learn/modules/{slug_dash}-release-highlights"


def get_release_resources(release_slug: str) -> dict[str, list[dict[str, str]]]:
    """Get all Trailhead resources for a release.

    Returns a dict with categories of resources:
    - modules: Trailhead learning modules
    - community: Trailblazer Community posts
    - topics: Community topics
    """
    slug_dash = release_slug.replace("_", "-")
    year = slug_dash.split("-")[1] if "-" in slug_dash else ""  # e.g., "26"

    resources: dict[str, list[dict[str, str]]] = {
        "modules": [
            {
                "title": f"Summer '{year} Release Highlights",
                "url": f"{TRAILHEAD_BASE_URL}/content/learn/modules/{slug_dash}-release-highlights",
            },
            {
                "title": f"Summer '{year} Release Highlights (Português)",
                "url": f"{TRAILHEAD_BASE_URL}/pt-BR/content/learn/modules/{slug_dash}-release-highlights",
            },
        ],
        "community": [
            {
                "title": f"Trailblazer Community: Summer '{year} Release",
                "url": f"{TRAILHEAD_BASE_URL}/trailblazer-community/feed/0D5KX00000jAFbF0AW",
            },
            {
                "title": "Release Notes Discussion",
                "url": f"{TRAILHEAD_BASE_URL}/trailblazer-community/feed/0D5KX00000mmKV30AM",
            },
            {
                "title": "Release Feedback Thread",
                "url": f"{TRAILHEAD_BASE_URL}/trailblazer-community/feed/0D5KX00000mmbwr0AA",
            },
        ],
        "topics": [
            {
                "title": "Release Matrix",
                "url": f"{TRAILHEAD_BASE_URL}/trailblazer-community/topics/releasematrixpost",
            },
        ],
    }

    return resources


def generate_release_resources_section(release_slug: str, release_name: str) -> str:
    """Generate a markdown section with all Trailhead resources for a release.

    This section is included in each release's .md files.
    """
    resources = get_release_resources(release_slug)

    lines = ["## 🔗 Trailhead & Recursos\n"]

    # Modules section
    if resources.get("modules"):
        lines.append("### Módulos Trailhead\n")
        for mod in resources["modules"]:
            lines.append(f"- [{mod['title']}]({mod['url']})")
        lines.append("")

    # Community section
    if resources.get("community"):
        lines.append("### Comunidade Trailblazer\n")
        for post in resources["community"]:
            lines.append(f"- [{post['title']}]({post['url']})")
        lines.append("")

    # Topics section
    if resources.get("topics"):
        lines.append("### Tópicos\n")
        for topic in resources["topics"]:
            lines.append(f"- [{topic['title']}]({topic['url']})")
        lines.append("")

    return "\n".join(lines)


def generate_category_trailhead_section(
    category_name: str, release_slug: str, locale: str = "pt_BR"
) -> str:
    """Generate Trailhead section with category-specific modules.

    Args:
        category_name: The category name (e.g., "Agentforce")
        release_slug: The release slug (e.g., "summer_26")
        locale: Locale for section headers (default: "pt_BR")

    Returns:
        Markdown section with relevant Trailhead modules.
    """
    from .i18n import LOCALIZATION_MAP

    i18n = LOCALIZATION_MAP[locale]
    service = _get_trailhead_service()
    modules = service.search(category_name, max_results=5)

    lines = [f"## 🎓 {i18n['trailhead_section']}\n"]

    if modules:
        for module in modules:
            time_points = f" — {module.estimated_time}" if module.estimated_time else ""
            points = f" | {module.points} pts" if module.points else ""
            lines.append(f"- [{module.title}]({module.url}){time_points}{points}")
    else:
        lines.append(f"- {i18n['trailhead_empty']} {category_name}")

    lines.append("")
    return "\n".join(lines)


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
