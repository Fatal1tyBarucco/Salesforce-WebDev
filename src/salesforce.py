"""Salesforce integration for release notes.

Provides Trailhead module linking, org limits cross-reference,
and sandbox deployment readiness checking.

Uses Salesforce Trailhead public API for module search (no auth required).
Org limits and sandbox checks use Salesforce REST API (requires OAuth).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

TRAILHEAD_SEARCH_URL = "https://trailhead.salesforce.com/api/v2/trailhead/search?q={query}"
TRAILHEAD_BASE_URL = "https://trailhead.salesforce.com"


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

    Uses the public Trailhead search API (no authentication required).
    """
    encoded_query = quote(query)
    url = TRAILHEAD_SEARCH_URL.format(query=encoded_query)

    try:
        req = Request(
            url, headers={"Accept": "application/json", "User-Agent": "SalesforceReleaseBot/1.0"}
        )
        with urlopen(req, timeout=15) as resp:
            data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError) as e:
        logger.warning("Trailhead search failed for '%s': %s", query, e)
        return []

    modules: list[TrailheadModule] = []
    for item in data.get("results", [])[:max_results]:
        modules.append(
            TrailheadModule(
                title=item.get("title", ""),
                url=TRAILHEAD_BASE_URL + item.get("url", ""),
                module_type=item.get("type", ""),
                estimated_time=item.get("estimatedTime", ""),
                points=item.get("points", 0),
            )
        )

    return modules


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
