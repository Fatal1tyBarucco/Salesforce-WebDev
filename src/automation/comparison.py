"""Release comparison and regression detection."""

from __future__ import annotations

import json
from typing import Any, Optional

from .models import QualityMetrics, ReleaseComparison, Regression


async def compare_releases(
    load_meta_fn: Any,
    current_slug: str,
    previous_slug: str,
) -> ReleaseComparison:
    """Compare two releases and identify differences."""
    current = load_meta_fn(current_slug)
    previous = load_meta_fn(previous_slug)

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


async def detect_regressions(
    load_meta_fn: Any,
    current_slug: str,
    previous_slug: str,
) -> list[Regression]:
    """Detect features that lost resources between releases."""
    current = load_meta_fn(current_slug)
    previous = load_meta_fn(previous_slug)

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


async def calculate_quality_metrics(
    load_meta_fn: Any,
    slug: str,
) -> Optional[QualityMetrics]:
    """Calculate quality metrics for a release."""
    meta = load_meta_fn(slug)
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


async def generate_quality_report(
    llm: Any,
    load_meta_fn: Any,
    calculate_metrics_fn: Any,
) -> str:
    """Generate an intelligent quality report for all releases."""
    from pathlib import Path

    from ..config import RELEASES_DIR

    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return "# Relatório de Qualidade\n\nNenhuma release encontrada.\n"

    all_metrics = []
    metas_loaded = []
    for d in releases_dir.iterdir():
        if not d.is_dir():
            continue
        meta = load_meta_fn(d.name)
        if not meta:
            continue
        metas_loaded.append((d, meta))

    metas_loaded.sort(key=lambda x: x[1].get("release_id", 0), reverse=True)

    for d, meta in metas_loaded:
        metrics = await calculate_metrics_fn(d.name)
        if metrics and metrics.total_features > 0:
            all_metrics.append({"name": meta.get("name", d.name), "metrics": vars(metrics)})

    if not all_metrics:
        return "# Relatório de Qualidade\n\nNenhuma release com dados encontrada.\n"

    system_prompt = (
        "You are an expert Salesforce Release Analyst. Analyze the quality metrics across multiple releases. "
        "Generate a Markdown report in Brazilian Portuguese that identifies trends in feature density, "
        "category distribution, and overall release quality."
    )
    user_prompt = f"Quality Metrics: {json.dumps(all_metrics)}"

    result = await llm.generate_text(user_prompt, system_prompt)
    if result:
        return result

    lines = ["# Relatório de Qualidade\n"]
    for item in all_metrics:
        name = item["name"]
        m = item["metrics"]
        lines.append(f"## {name}\n")
        lines.append(f"- **Total de recursos:** {m['total_features']}")
        lines.append(f"- **Total de categorias:** {m['total_categories']}")
        lines.append(f"- **Média por categoria:** {m['avg_features_per_category']:.1f}")
        lines.append(
            f"- **Maior categoria:** {m['largest_category'][0]} ({m['largest_category'][1]})"
        )
        lines.append(
            f"- **Menor categoria:** {m['smallest_category'][0]} ({m['smallest_category'][1]})"
        )
        lines.append("")
    return "\n".join(lines)
