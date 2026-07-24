"""Trailhead integration for suggesting relevant learning modules.

Maps release features to Trailhead modules and trails for
guided learning paths.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Trailhead module mapping (category → relevant modules)
# ---------------------------------------------------------------------------

_TRAILHEAD_MODULES: dict[str, list[dict[str, str]]] = {
    "agentforce": [
        {
            "title": "Get Started with Agentforce",
            "url": "https://trailhead.salesforce.com/content/learn/modules/get-started-with-agentforce",
            "duration": "45 min",
        },
        {
            "title": "Build Agents with Agentforce",
            "url": "https://trailhead.salesforce.com/content/learn/modules/agentforce-build-agents",
            "duration": "2 hrs",
        },
    ],
    "security": [
        {
            "title": "Security Specialist",
            "url": "https://trailhead.salesforce.com/content/learn/trails/force-com-security-specialist",
            "duration": "6 hrs",
        },
        {
            "title": "Data Security",
            "url": "https://trailhead.salesforce.com/content/learn/modules/data_security",
            "duration": "45 min",
        },
    ],
    "development": [
        {
            "title": "Apex Specialist",
            "url": "https://trailhead.salesforce.com/content/learn/trails/force_com_dev_intermediate",
            "duration": "8 hrs",
        },
        {
            "title": "Lightning Web Components",
            "url": "https://trailhead.salesforce.com/content/learn/trails/lightning-web-components",
            "duration": "6 hrs",
        },
    ],
    "automation": [
        {
            "title": "Process Automation Specialist",
            "url": "https://trailhead.salesforce.com/content/learn/trails/force_com_business_process_automation",
            "duration": "6 hrs",
        },
        {
            "title": "Flow Builder",
            "url": "https://trailhead.salesforce.com/content/learn/modules/flow-basics",
            "duration": "1 hr",
        },
    ],
    "data_360": [
        {
            "title": "Data Cloud",
            "url": "https://trailhead.salesforce.com/content/learn/modules/data-cloud-basics",
            "duration": "1 hr",
        },
    ],
    "sales": [
        {
            "title": "Sales Cloud",
            "url": "https://trailhead.salesforce.com/content/learn/modules/lex_migration_sales",
            "duration": "45 min",
        },
    ],
    "service": [
        {
            "title": "Service Cloud",
            "url": "https://trailhead.salesforce.com/content/learn/modules/service_cloud_basics",
            "duration": "45 min",
        },
    ],
    "marketing": [
        {
            "title": "Marketing Cloud",
            "url": "https://trailhead.salesforce.com/content/learn/modules/marketing-cloud-basics",
            "duration": "1 hr",
        },
    ],
    "experience_cloud": [
        {
            "title": "Experience Cloud Basics",
            "url": "https://trailhead.salesforce.com/content/learn/modules/comm_basics",
            "duration": "45 min",
        },
    ],
    "analytics": [
        {
            "title": "CRM Analytics",
            "url": "https://trailhead.salesforce.com/content/learn/modules/crm-analytics-basics",
            "duration": "1 hr",
        },
    ],
    "field_service": [
        {
            "title": "Field Service",
            "url": "https://trailhead.salesforce.com/content/learn/modules/field-service-basics",
            "duration": "45 min",
        },
    ],
}


@dataclass
class TrailheadModule:
    """A Trailhead learning module."""

    title: str
    url: str
    duration: str = ""
    relevance: str = ""  # Why this module is relevant


@dataclass
class TrailheadSuggestion:
    """Trailhead suggestion for a category."""

    category: str
    modules: list[TrailheadModule] = field(default_factory=list)


class TrailheadIntegration:
    """Suggests Trailhead modules based on release features.

    Maps release categories and features to relevant Trailhead
    learning paths for guided adoption.
    """

    def __init__(self) -> None:
        self._modules = _TRAILHEAD_MODULES

    def suggest_for_category(
        self,
        category_slug: str,
        category_name: str = "",
    ) -> TrailheadSuggestion:
        """Suggest Trailhead modules for a release category.

        Args:
            category_slug: Category slug (e.g. "agentforce").
            category_name: Human-readable category name.

        Returns:
            TrailheadSuggestion with relevant modules.
        """
        # Normalize slug
        normalized = category_slug.lower().replace("-", "_").replace(" ", "_")

        modules: list[TrailheadModule] = []

        # Direct match
        if normalized in self._modules:
            for mod in self._modules[normalized]:
                modules.append(
                    TrailheadModule(
                        title=mod["title"],
                        url=mod["url"],
                        duration=mod.get("duration", ""),
                        relevance=f"Módulo diretamente relacionado a {category_name or category_slug}",
                    )
                )

        # Partial matches
        for key, mods in self._modules.items():
            if key == normalized:
                continue
            if key in normalized or normalized in key:
                for mod in mods:
                    if not any(m.title == mod["title"] for m in modules):
                        modules.append(
                            TrailheadModule(
                                title=mod["title"],
                                url=mod["url"],
                                duration=mod.get("duration", ""),
                                relevance=f"Relacionado a {category_name or category_slug}",
                            )
                        )

        return TrailheadSuggestion(category=category_name or category_slug, modules=modules)

    def suggest_for_release(
        self,
        categories: list[dict[str, str]],
    ) -> list[TrailheadSuggestion]:
        """Suggest Trailhead modules for all categories in a release.

        Args:
            categories: List of dicts with 'name' and 'slug'.

        Returns:
            List of TrailheadSuggestion, one per category with matches.
        """
        suggestions: list[TrailheadSuggestion] = []

        for cat in categories:
            slug = cat.get("slug", cat.get("name", "").lower().replace(" ", "_"))
            name = cat.get("name", "")
            suggestion = self.suggest_for_category(slug, name)
            if suggestion.modules:
                suggestions.append(suggestion)

        return suggestions

    def generate_trailhead_section(
        self,
        categories: list[dict[str, str]],
    ) -> str:
        """Generate a Markdown section with Trailhead suggestions.

        Args:
            categories: List of dicts with 'name' and 'slug'.

        Returns:
            Markdown string with Trailhead section.
        """
        suggestions = self.suggest_for_release(categories)

        if not suggestions:
            return ""

        lines = [
            "## 🎓 Módulos Trailhead Recomendados\n",
            "Para aproveitar ao máximo as novidades desta release, "
            "confira os seguintes módulos no Trailhead:\n",
        ]

        for suggestion in suggestions:
            if not suggestion.modules:
                continue

            lines.append(f"### {suggestion.category}\n")
            for mod in suggestion.modules:
                duration = f" ⏱️ {mod.duration}" if mod.duration else ""
                lines.append(f"- [{mod.title}]({mod.url}){duration}")
            lines.append("")

        return "\n".join(lines)

    def get_available_categories(self) -> list[str]:
        """Get list of categories with Trailhead mappings.

        Returns:
            List of category slugs.
        """
        return list(self._modules.keys())
