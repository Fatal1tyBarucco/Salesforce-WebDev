"""Profile-based notification filtering."""

from __future__ import annotations

from typing import Any

from .models import FilteredNotification, UserProfile

USER_PROFILES: dict[str, dict[str, Any]] = {
    "admin": {
        "name": "Administrador",
        "relevant_categories": [
            "Security",
            "Segurança, identidade e privacidade",
            "Compliance",
            "Data Governance",
            "Data 360",
            "User Management",
            "Authentication",
        ],
        "keywords": ["admin", "security", "compliance", "governance", "permission", "auth"],
        "priority_boost": ["Security", "Compliance"],
    },
    "developer": {
        "name": "Desenvolvedor",
        "relevant_categories": [
            "Development",
            "Desenvolvimento",
            "API",
            "Integration",
            "Apex",
            "LWC",
            "Flow",
            "Lightning Platform",
        ],
        "keywords": ["api", "code", "development", "integration", "apex", "lwc", "flow"],
        "priority_boost": ["Development", "API", "Integration"],
    },
    "architect": {
        "name": "Arquiteto",
        "relevant_categories": [
            "Architecture",
            "Platform",
            "Performance",
            "Scalability",
            "Infrastructure",
            "Data Architecture",
            "Integration Architecture",
        ],
        "keywords": ["architecture", "platform", "performance", "scalability", "design"],
        "priority_boost": ["Architecture", "Platform", "Performance"],
    },
    "business": {
        "name": "Usuário de Negócios",
        "relevant_categories": [
            "Sales",
            "Marketing",
            "Service",
            "Commerce",
            "Analytics",
            "Reports",
            "Dashboards",
        ],
        "keywords": ["sales", "marketing", "service", "commerce", "analytics", "report"],
        "priority_boost": ["Sales", "Marketing", "Service"],
    },
}


async def filter_features_for_profile(
    profile_type: str,
    categories: list[dict[str, Any]],
) -> UserProfile:
    """Filter features based on user profile relevance."""
    profile_config = USER_PROFILES.get(profile_type, USER_PROFILES["business"])

    relevant_categories = []
    priority_features: list[str] = []

    for cat in categories:
        cat_name = cat.get("name", "")
        count = cat.get("count", 0)

        is_relevant = any(kw.lower() in cat_name.lower() for kw in profile_config["keywords"])
        if cat_name in profile_config["priority_boost"]:
            is_relevant = True
            priority_features.append(f"{cat_name} ({count} recursos)")

        if is_relevant:
            relevant_categories.append(cat_name)

    total_categories = len(categories) if categories else 1
    relevance_score = len(relevant_categories) / total_categories

    return UserProfile(
        profile_type=profile_type,
        name=profile_config["name"],
        relevant_categories=relevant_categories,
        filtered_features=[],
        priority_features=priority_features,
        relevance_score=round(relevance_score, 2),
    )


async def generate_filtered_notification(
    load_meta_fn: Any,
    slug: str,
    profile_type: str,
) -> FilteredNotification:
    """Generate a filtered notification for a specific user profile."""
    meta = load_meta_fn(slug)
    if not meta:
        return FilteredNotification(
            profile=UserProfile(profile_type, "Unknown", [], [], [], 0.0),
            total_features=0,
            relevant_count=0,
            priority_count=0,
            summary="Release não encontrada.",
        )

    categories = meta.get("categories", [])
    total_features = sum(c.get("count", 0) for c in categories)
    profile = await filter_features_for_profile(profile_type, categories)

    if profile.relevance_score > 0.5:
        summary = f"Alta relevância para {profile.name}: {len(profile.relevant_categories)} categorias relevantes ({profile.relevance_score:.0%} do total)"
    elif profile.relevance_score > 0.2:
        summary = f"Relevância moderada para {profile.name}: {len(profile.relevant_categories)} categorias relevantes"
    else:
        summary = (
            f"Baixa relevância para {profile.name}: poucas categorias alinhadas com seu perfil"
        )

    return FilteredNotification(
        profile=profile,
        total_features=total_features,
        relevant_count=len(profile.relevant_categories),
        priority_count=len(profile.priority_features),
        summary=summary,
    )


async def generate_filtered_notification_report(
    load_meta_fn: Any,
    slug: str,
    profile_type: str,
) -> str:
    """Generate a formatted filtered notification report in Markdown."""
    notification = await generate_filtered_notification(load_meta_fn, slug, profile_type)

    lines = [
        "# Notificação Filtrada por Perfil\n",
        f"## Perfil: {notification.profile.name}\n",
        f"**Relevância:** {notification.profile.relevance_score:.0%}\n",
        f"*{notification.summary}*\n",
        "## 📊 Resumo\n",
        f"- **Total de recursos:** {notification.total_features}",
        f"- **Categorias relevantes:** {notification.relevant_count}",
        f"- **Categorias prioritárias:** {notification.priority_count}",
        "",
    ]

    if notification.profile.priority_features:
        lines.append("## 🔴 Prioridade Alta\n")
        for feature in notification.profile.priority_features:
            lines.append(f"- {feature}")
        lines.append("")

    if notification.profile.relevant_categories:
        lines.append("## 📋 Categorias Relevantes\n")
        for cat in notification.profile.relevant_categories:
            lines.append(f"- {cat}")
        lines.append("")

    lines.extend(["---", "*Notificação gerada automaticamente pelo módulo de AI Automation*"])
    return "\n".join(lines)
