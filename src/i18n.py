"""Internationalization support for release notes pipeline."""

from __future__ import annotations

LOCALIZATION_MAP: dict[str, dict[str, str]] = {
    "pt_BR": {
        "resources": "Recursos",
        "category_count": "recursos",
        "users_header": "Usuários",
        "admins_header": "Admins/Devs",
        "config_header": "Config",
        "contact_header": "Contato",
        "docs_header": "Docs",
        "empty_category": "Nenhum recurso nesta categoria",
        "trailhead_section": "Módulos Trailhead Relacionados",
        "trailhead_empty": "Nenhum módulo específico encontrado para",
        "toggle_english": "🇺🇸 English",
        "toggle_portuguese": "🇧🇷 Português",
    },
    "en_US": {
        "resources": "Features",
        "category_count": "features",
        "users_header": "Users",
        "admins_header": "Admins/Devs",
        "config_header": "Config",
        "contact_header": "Contact",
        "docs_header": "Docs",
        "empty_category": "No features in this category",
        "trailhead_section": "Related Trailhead Modules",
        "trailhead_empty": "No specific modules found for",
        "toggle_english": "🇺🇸 English",
        "toggle_portuguese": "🇧🇷 Português",
    },
}


def detect_locale(request_headers: dict[str, str]) -> str:
    """Detect user locale from HTTP request headers."""
    accept_language = request_headers.get("Accept-Language", "")
    return get_user_locale(accept_language)


def get_user_locale(accept_language: str) -> str:
    """Parse Accept-Language header and return 'pt_BR' or 'en_US'."""
    if not accept_language:
        return "pt_BR"
    for lang_entry in accept_language.split(","):
        lang = lang_entry.split(";")[0].strip().lower()
        if lang.startswith("en"):
            return "en_US"
        if lang.startswith("pt"):
            return "pt_BR"
    return "pt_BR"


def generate_toggle_html(current_locale: str, file_slug: str, release_slug: str) -> str:
    """Generate inline HTML language toggle button."""
    other_locale = "en_US" if current_locale == "pt_BR" else "pt_BR"
    other_label = (
        LOCALIZATION_MAP[other_locale]["toggle_english"]
        if other_locale == "en_US"
        else LOCALIZATION_MAP[other_locale]["toggle_portuguese"]
    )
    current_label = (
        LOCALIZATION_MAP[current_locale]["toggle_portuguese"]
        if current_locale == "pt_BR"
        else LOCALIZATION_MAP[current_locale]["toggle_english"]
    )

    return (
        f'<div style="padding:8px 12px;margin-bottom:16px;'
        f"border:1px solid #d0d7de;border-radius:6px;"
        f'background:#f6f8fa;font-family:system-ui,sans-serif;font-size:14px;">'
        f"<strong>Idioma:</strong> "
        f'<a href="../{current_locale}/{file_slug}.md" '
        f'style="text-decoration:none;font-weight:bold;">{current_label}</a>'
        f" &nbsp;|&nbsp; "
        f'<a href="../{other_locale}/{file_slug}.md" '
        f'style="text-decoration:none;">{other_label}</a>'
        f"</div>"
    )
