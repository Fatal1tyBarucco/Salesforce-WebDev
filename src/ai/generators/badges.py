"""Dynamic SVG badge generation for releases.

Generates shields.io-compatible badges and inline SVG badges
for release metadata, impact levels, and feature counts.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Badge color schemes
# ---------------------------------------------------------------------------

_IMPACT_COLORS: dict[str, tuple[str, str]] = {
    "alto": ("#E53935", "#FFFFFF"),  # Red bg, white text
    "médio": ("#FB8C00", "#FFFFFF"),  # Orange bg, white text
    "baixo": ("#43A047", "#FFFFFF"),  # Green bg, white text
    "high": ("#E53935", "#FFFFFF"),
    "medium": ("#FB8C00", "#FFFFFF"),
    "low": ("#43A047", "#FFFFFF"),
}

_STATUS_COLORS: dict[str, tuple[str, str]] = {
    "active": ("#43A047", "#FFFFFF"),
    "deprecated": ("#FB8C00", "#FFFFFF"),
    "removed": ("#E53935", "#FFFFFF"),
    "new": ("#1E88E5", "#FFFFFF"),
    "beta": ("#8E24AA", "#FFFFFF"),
    "ga": ("#43A047", "#FFFFFF"),
}

_RELEASE_COLORS: dict[str, tuple[str, str]] = {
    "spring": ("#4CAF50", "#FFFFFF"),  # Green
    "summer": ("#FF9800", "#FFFFFF"),  # Orange
    "winter": ("#2196F3", "#FFFFFF"),  # Blue
}


@dataclass
class Badge:
    """A single badge definition."""

    label: str
    message: str
    color: str = "#555555"
    label_color: str = "#555555"
    style: Literal["flat", "flat-square", "plastic", "for-the-badge"] = "flat"
    logo: str = ""

    def to_shields_url(self) -> str:
        """Generate a shields.io URL for this badge.

        Returns:
            shields.io badge URL string.
        """
        label_enc = self.label.replace(" ", "%20").replace("-", "--")
        message_enc = self.message.replace(" ", "%20").replace("-", "--")
        color_clean = self.color.lstrip("#")
        label_clean = self.label_color.lstrip("#")

        url = f"https://img.shields.io/badge/{label_enc}-{message_enc}-{color_clean}"
        params = [f"style={self.style}"]
        if label_clean != "555555":
            params.append(f"labelColor={label_clean}")
        if self.logo:
            params.append(f"logo={self.logo}")
        return f"{url}?{'&'.join(params)}"

    def to_markdown(self) -> str:
        """Generate a Markdown image tag for this badge.

        Returns:
            Markdown string with badge image.
        """
        return f"![{self.label}](https://img.shields.io/badge/{self.label.replace(' ', '%20')}-{self.message.replace(' ', '%20')}-{self.color.lstrip('#')}?style={self.style})"

    def to_html(self) -> str:
        """Generate an inline HTML badge (no external dependency).

        Returns:
            HTML string with styled badge.
        """
        safe_label = html.escape(self.label)
        safe_message = html.escape(self.message)
        return (
            f'<span style="background-color:{self.color};color:{self.label_color};'
            f"padding:2px 8px;border-radius:4px;font-size:0.85em;"
            f'font-weight:bold;margin-right:4px;">'
            f"{safe_label}: {safe_message}</span>"
        )


# ---------------------------------------------------------------------------
# Badge factories
# ---------------------------------------------------------------------------


def impact_badge(impact: str) -> Badge:
    """Create a badge for an impact level.

    Args:
        impact: Impact level (alto/médio/baixo or high/medium/low).

    Returns:
        Badge instance with appropriate colors.
    """
    bg, fg = _IMPACT_COLORS.get(impact.lower(), ("#9E9E9E", "#FFFFFF"))
    emoji = {"alto": "🔴", "médio": "🟡", "baixo": "🟢"}.get(impact.lower(), "⚪")
    return Badge(label="Impacto", message=f"{emoji} {impact}", color=bg, label_color=fg)


def feature_count_badge(count: int, total: int | None = None) -> Badge:
    """Create a badge for feature count.

    Args:
        count: Number of features.
        total: Optional total for context.

    Returns:
        Badge instance.
    """
    if total:
        message = f"{count}/{total}"
    else:
        message = str(count)

    if count > 100:
        color = "#E53935"
    elif count > 50:
        color = "#FB8C00"
    else:
        color = "#43A047"

    return Badge(label="Features", message=message, color=color, label_color="#FFFFFF")


def release_badge(release_name: str) -> Badge:
    """Create a badge for a release name.

    Args:
        release_name: Release name (e.g. "Summer '26").

    Returns:
        Badge instance with season-appropriate color.
    """
    season = release_name.split()[0].lower() if release_name else ""
    bg, fg = _RELEASE_COLORS.get(season, ("#555555", "#FFFFFF"))
    return Badge(label="Release", message=release_name, color=bg, label_color=fg)


def api_version_badge(version: str) -> Badge:
    """Create a badge for API version.

    Args:
        version: API version string (e.g. "v67.0").

    Returns:
        Badge instance.
    """
    return Badge(
        label="API", message=version, color="#1E88E5", label_color="#FFFFFF", logo="salesforce"
    )


def status_badge(status: str) -> Badge:
    """Create a badge for feature/product status.

    Args:
        status: Status string (active, deprecated, new, beta, ga).

    Returns:
        Badge instance.
    """
    bg, fg = _STATUS_COLORS.get(status.lower(), ("#9E9E9E", "#FFFFFF"))
    return Badge(label="Status", message=status, color=bg, label_color=fg)


def category_badge(name: str, count: int) -> Badge:
    """Create a badge for a release category with feature count.

    Args:
        name: Category name.
        count: Number of features in category.

    Returns:
        Badge instance.
    """
    if count > 100:
        color = "#E53935"
    elif count > 50:
        color = "#FB8C00"
    elif count > 20:
        color = "#1E88E5"
    else:
        color = "#43A047"

    return Badge(label=name, message=f"{count} recursos", color=color, label_color="#FFFFFF")


# ---------------------------------------------------------------------------
# Badge collections
# ---------------------------------------------------------------------------


def release_meta_badges(
    release_name: str,
    total_features: int,
    category_count: int,
    api_version: str = "",
) -> str:
    """Generate a row of badges for release metadata.

    Args:
        release_name: Release name.
        total_features: Total feature count.
        category_count: Number of categories.
        api_version: Optional API version.

    Returns:
        Markdown string with badge row.
    """
    badges = [
        release_badge(release_name),
        feature_count_badge(total_features),
        Badge(
            label="Categorias", message=str(category_count), color="#7B1FA2", label_color="#FFFFFF"
        ),
    ]
    if api_version:
        badges.append(api_version_badge(api_version))

    return " ".join(b.to_shields_url() for b in badges)


def category_header_badges(
    name: str, count: int, high: int = 0, medium: int = 0, low: int = 0
) -> str:
    """Generate badges for a category header.

    Args:
        name: Category name.
        count: Total feature count.
        high: High-impact count.
        medium: Medium-impact count.
        low: Low-impact count.

    Returns:
        Markdown string with category badges.
    """
    badges = [category_badge(name, count)]

    if high > 0:
        badges.append(
            Badge(label="Alto", message=str(high), color="#E53935", label_color="#FFFFFF")
        )
    if medium > 0:
        badges.append(
            Badge(label="Médio", message=str(medium), color="#FB8C00", label_color="#FFFFFF")
        )
    if low > 0:
        badges.append(
            Badge(label="Baixo", message=str(low), color="#43A047", label_color="#FFFFFF")
        )

    return " ".join(b.to_shields_url() for b in badges)
