"""AI-powered automation features for release notes pipeline.

Provides:
- Release comparison between versions
- Regression detection
- Quality metrics generation
- Changelog generation
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import RELEASES_DIR


@dataclass
class ReleaseComparison:
    """Comparison between two releases."""

    current_name: str
    previous_name: str
    new_categories: list[str]
    removed_categories: list[str]
    changed_categories: list[tuple[str, int, int]]  # (name, prev_count, curr_count)


@dataclass
class Regression:
    """Detected regression in a category."""

    category: str
    previous_count: int
    current_count: int
    change: int


@dataclass
class QualityMetrics:
    """Quality metrics for a release."""

    total_features: int
    total_categories: int
    avg_features_per_category: float
    largest_category: tuple[str, int]
    smallest_category: tuple[str, int]


def load_release_meta(slug: str) -> Any:
    """Load .meta.json for a release."""
    meta_path = Path(RELEASES_DIR) / slug / ".meta.json"
    if not meta_path.exists():
        return None
    result: Any = json.loads(meta_path.read_text(encoding="utf-8"))
    return result


def compare_releases(current_slug: str, previous_slug: str) -> ReleaseComparison:
    """Compare two releases and identify differences."""
    current = load_release_meta(current_slug)
    previous = load_release_meta(previous_slug)

    if not current or not previous:
        return ReleaseComparison(
            current_name=current_slug if current else "unknown",
            previous_name=previous_slug if previous else "unknown",
            new_categories=[],
            removed_categories=[],
            changed_categories=[],
        )

    current_cats = {c["name"]: c["count"] for c in current.get("categories", [])}
    previous_cats = {c["name"]: c["count"] for c in previous.get("categories", [])}

    new_cats = [name for name in current_cats if name not in previous_cats]
    removed_cats = [name for name in previous_cats if name not in current_cats]
    changed = [
        (name, previous_cats[name], current_cats[name])
        for name in current_cats
        if name in previous_cats and current_cats[name] != previous_cats[name]
    ]

    return ReleaseComparison(
        current_name=current.get("name", current_slug),
        previous_name=previous.get("name", previous_slug),
        new_categories=new_cats,
        removed_categories=removed_cats,
        changed_categories=changed,
    )


def detect_regressions(current_slug: str, previous_slug: str) -> list[Regression]:
    """Detect features that lost resources between releases."""
    current = load_release_meta(current_slug)
    previous = load_release_meta(previous_slug)

    if not current or not previous:
        return []

    current_cats = {c["name"]: c["count"] for c in current.get("categories", [])}
    previous_cats = {c["name"]: c["count"] for c in previous.get("categories", [])}

    regressions = []
    for name in current_cats:
        if name in previous_cats and current_cats[name] < previous_cats[name]:
            regressions.append(
                Regression(
                    category=name,
                    previous_count=previous_cats[name],
                    current_count=current_cats[name],
                    change=current_cats[name] - previous_cats[name],
                )
            )

    return sorted(regressions, key=lambda r: r.change)


def calculate_quality_metrics(slug: str) -> QualityMetrics | None:
    """Calculate quality metrics for a release."""
    meta = load_release_meta(slug)
    if not meta:
        return None

    categories = meta.get("categories", [])
    counts = [c["count"] for c in categories]

    if not counts:
        return QualityMetrics(
            total_features=0,
            total_categories=0,
            avg_features_per_category=0.0,
            largest_category=("none", 0),
            smallest_category=("none", 0),
        )

    total = sum(counts)
    avg = total / len(counts)

    largest = max(categories, key=lambda c: c["count"])
    smallest = min(categories, key=lambda c: c["count"])

    return QualityMetrics(
        total_features=total,
        total_categories=len(categories),
        avg_features_per_category=avg,
        largest_category=(largest["name"], largest["count"]),
        smallest_category=(smallest["name"], smallest["count"]),
    )


def generate_changelog() -> str:
    """Generate a CHANGELOG.md from release metadata."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return "# Changelog\n\nNo releases found.\n"

    metas = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            metas.append(json.loads(meta_path.read_text(encoding="utf-8")))

    metas.sort(key=lambda m: m.get("release_id", 0), reverse=True)

    lines = ["# Changelog\n"]

    for meta in metas:
        name = meta.get("name", "Unknown")
        categories = meta.get("categories", [])
        total = sum(c.get("count", 0) for c in categories)

        lines.append(f"## {name}\n")
        lines.append(f"**{total} recursos** em {len(categories)} categorias\n")

        for cat in categories:
            count = cat.get("count", 0)
            if count > 0:
                lines.append(f"- **{cat['name']}**: {count} recursos")

        lines.append("")

    return "\n".join(lines)


def generate_regression_report(current_slug: str, previous_slug: str) -> str:
    """Generate a regression report between two releases."""
    comparison = compare_releases(current_slug, previous_slug)
    regressions = detect_regressions(current_slug, previous_slug)

    lines = [
        "# Relatório de Regressões\n",
        f"**Comparação:** {comparison.previous_name} → {comparison.current_name}\n",
    ]

    if comparison.new_categories:
        lines.append("## 📈 Novas Categorias\n")
        for cat in comparison.new_categories:
            lines.append(f"- {cat}")
        lines.append("")

    if comparison.removed_categories:
        lines.append("## 📉 Categorias Removidas\n")
        for cat in comparison.removed_categories:
            lines.append(f"- {cat}")
        lines.append("")

    if comparison.changed_categories:
        lines.append("## 🔄 Categorias Alteradas\n")
        for name, prev, curr in comparison.changed_categories:
            diff = curr - prev
            arrow = "📈" if diff > 0 else "📉"
            lines.append(f"- {arrow} **{name}**: {prev} → {curr} ({diff:+d})")
        lines.append("")

    if regressions:
        lines.append("## ⚠️ Regressões Detectadas\n")
        for reg in regressions:
            lines.append(
                f"- **{reg.category}**: {reg.previous_count} → {reg.current_count} ({reg.change:+d})"
            )
        lines.append("")
    else:
        lines.append("## ✅ Nenhuma Regressão Detectada\n")

    return "\n".join(lines)


def generate_quality_report() -> str:
    """Generate a quality report for all releases."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return "# Relatório de Qualidade\n\nNenhuma release encontrada.\n"

    lines = ["# Relatório de Qualidade\n"]

    for d in sorted(releases_dir.iterdir()):
        if not d.is_dir():
            continue

        meta = load_release_meta(d.name)
        if not meta:
            continue

        name = meta.get("name", d.name)
        metrics = calculate_quality_metrics(d.name)

        if not metrics:
            continue

        lines.append(f"## {name}\n")
        lines.append(f"- **Total de recursos:** {metrics.total_features}")
        lines.append(f"- **Total de categorias:** {metrics.total_categories}")
        lines.append(f"- **Média por categoria:** {metrics.avg_features_per_category:.1f}")
        lines.append(
            f"- **Maior categoria:** {metrics.largest_category[0]} ({metrics.largest_category[1]})"
        )
        lines.append(
            f"- **Menor categoria:** {metrics.smallest_category[0]} ({metrics.smallest_category[1]})"
        )
        lines.append("")

    return "\n".join(lines)
