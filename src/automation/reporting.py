"""Report generation: changelog, diff, regression, AI summary.

Refactored (Phase 1): uses CTO persona prompts, Pydantic-validated outputs,
and visual Markdown generators for stakeholder-ready reports.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from ..ai.generators.markdown import MarkdownGenerator
from ..ai.prompts.reporting import (
    build_ai_summary_prompt,
    build_changelog_prompt,
    build_diff_report_prompt,
    build_regression_report_prompt,
    build_reporting_system_prompt,
    parse_report_response,
)
from ..ai.prompts.validation import ReportOutput
from .models import AISummary, QualityMetrics, Regression, ReleaseComparison


def _get_releases_dir() -> "Path":  # type: ignore[name-defined]  # type: ignore[override]  # noqa: F821
    from pathlib import Path

    from ..config import RELEASES_DIR

    return Path(RELEASES_DIR)


async def generate_changelog(
    llm: Any,
    load_meta_fn: Any,
) -> str:
    """Generate an intelligent CHANGELOG.md from release metadata.

    Uses CTO persona with structured prompts and Pydantic validation.
    """
    releases_dir = _get_releases_dir()
    if not releases_dir.exists():
        return "# Changelog\n\nNo releases found.\n"

    metas = []
    for d in releases_dir.iterdir():
        meta = load_meta_fn(d.name)
        if meta:
            total = sum(c.get("count", 0) for c in meta.get("categories", []))
            if total > 0:
                metas.append(meta)

    metas.sort(key=lambda m: m.get("release_id", 0), reverse=True)
    if not metas:
        return "# Changelog\n\nNo releases found.\n"

    system_prompt = build_reporting_system_prompt()
    user_prompt = build_changelog_prompt(metas)

    result: str | None = await llm.generate_text(user_prompt, system_prompt)
    if result:
        return str(result)

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


async def generate_regression_report(
    llm: Any,
    comparison: ReleaseComparison,
    regressions: list[Regression],
) -> str:
    """Generate an intelligent regression report between two releases.

    Uses CTO persona with structured prompts.
    """
    system_prompt = build_reporting_system_prompt()
    comparison_dict: dict[str, Any] = vars(comparison)
    regressions_list: list[dict[str, Any]] = [vars(r) for r in regressions]
    user_prompt = build_regression_report_prompt(
        comparison_data=comparison_dict,
        regressions_data=regressions_list,
    )

    result: str | None = await llm.generate_text(user_prompt, system_prompt)
    if result:
        return str(result)

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


async def generate_diff_report(
    llm: Any,
    load_meta_fn: Any,
    comparison: ReleaseComparison,
    current_slug: str,
    previous_slug: str,
) -> str:
    """Generate an intelligent visual diff report between two releases.

    Uses CTO persona with structured prompts.
    """
    current = load_meta_fn(current_slug)
    previous = load_meta_fn(previous_slug)

    current_cats = {c["name"]: c["count"] for c in current.get("categories", [])} if current else {}
    previous_cats = (
        {c["name"]: c["count"] for c in previous.get("categories", [])} if previous else {}
    )
    all_names = sorted(set(current_cats) | set(previous_cats))

    diff_data = []
    for name in all_names:
        prev = previous_cats.get(name, 0)
        curr = current_cats.get(name, 0)
        diff_data.append(
            {"category": name, "previous": prev, "current": curr, "delta": curr - prev}
        )

    system_prompt = build_reporting_system_prompt()
    user_prompt = build_diff_report_prompt(diff_data)

    result: str | None = await llm.generate_text(user_prompt, system_prompt)
    if result:
        return str(result)

    lines = [
        f"# Diff: {comparison.previous_name} → {comparison.current_name}\n",
        "| Categoria | Anterior | Atual | Delta |",
        "| :--- | :---: | :---: | :---: |",
    ]
    for name in all_names:
        prev = previous_cats.get(name, 0)
        curr = current_cats.get(name, 0)
        diff = curr - prev
        delta = f"📈 +{diff}" if diff > 0 else (f"📉 {diff}" if diff < 0 else "—")
        lines.append(f"| {name} | {prev} | {curr} | {delta} |")

    prev_total = sum(previous_cats.values())
    curr_total = sum(current_cats.values())
    total_diff = curr_total - prev_total
    lines.append(
        f"| **TOTAL** | **{prev_total}** | **{curr_total}** | **{'+' if total_diff > 0 else ''}{total_diff}** |"
    )
    return "\n".join(lines)


async def generate_ai_summary(
    llm: Any,
    comparison: ReleaseComparison,
    regressions: list[Regression],
    current_metrics: Optional[QualityMetrics],
    previous_metrics: Optional[QualityMetrics],
) -> AISummary:
    """Generate an intelligent natural language summary of release differences.

    Uses CTO persona with structured prompts and Pydantic validation.
    """
    analysis_data = {
        "comparison": vars(comparison),
        "regressions": [vars(r) for r in regressions],
        "current_metrics": vars(current_metrics) if current_metrics else None,
        "previous_metrics": vars(previous_metrics) if previous_metrics else None,
    }

    system_prompt = build_reporting_system_prompt()
    user_prompt = build_ai_summary_prompt(analysis_data)

    result_text = await llm.generate_text(user_prompt, system_prompt)
    if not result_text:
        return _generate_legacy_ai_summary(
            comparison, regressions, current_metrics, previous_metrics
        )

    # Try Pydantic validation first
    validated = parse_report_response(result_text)
    if validated:
        return AISummary(
            headline=validated.headline,
            highlights=validated.highlights,
            risk_areas=validated.risk_areas,
            overall_trend=validated.trend,
        )

    # Fallback to legacy JSON parsing
    try:
        start_idx = result_text.find("{")
        end_idx = result_text.rfind("}") + 1
        data = json.loads(result_text[start_idx:end_idx])
        return AISummary(
            headline=data.get("headline", "Resumo da Release"),
            highlights=data.get("highlights", []),
            risk_areas=data.get("risk_areas", []),
            overall_trend=data.get("overall_trend", "indeterminado"),
        )
    except (ValueError, IndexError):
        return _generate_legacy_ai_summary(
            comparison, regressions, current_metrics, previous_metrics
        )


def _generate_legacy_ai_summary(
    comparison: ReleaseComparison,
    regressions: list[Regression],
    current_metrics: Optional[QualityMetrics],
    previous_metrics: Optional[QualityMetrics],
) -> AISummary:
    """Legacy heuristic-based summary generation for fallback."""
    total_changes = (
        len(comparison.new_categories)
        + len(comparison.removed_categories)
        + len(comparison.changed_categories)
    )
    if total_changes == 0:
        headline = f"{comparison.current_name} — sem alterações significativas em relação a {comparison.previous_name}"
    else:
        headline = f"{comparison.current_name} traz {total_changes} alterações em relação a {comparison.previous_name}"

    highlights: list[str] = []
    if comparison.new_categories:
        highlights.append(
            f"{len(comparison.new_categories)} novas categorias adicionadas: "
            + ", ".join(comparison.new_categories[:3])
        )

    risk_areas: list[str] = []
    if comparison.removed_categories:
        risk_areas.append(f"{len(comparison.removed_categories)} categorias removidas")
    if regressions:
        risk_areas.append(f"{len(regressions)} categorias com regressão")

    overall_trend = "estável"
    if current_metrics and previous_metrics:
        growth_pct = (
            (current_metrics.total_features - previous_metrics.total_features)
            / max(previous_metrics.total_features, 1)
        ) * 100
        if growth_pct > 5:
            overall_trend = "crescimento"
        elif growth_pct < -5:
            overall_trend = "declínio"

    return AISummary(
        headline=headline,
        highlights=highlights,
        risk_areas=risk_areas,
        overall_trend=overall_trend,
    )


async def generate_ai_summary_report(
    llm: Any,
    comparison: ReleaseComparison,
    regressions: list[Regression],
    current_metrics: Optional[QualityMetrics],
    previous_metrics: Optional[QualityMetrics],
) -> str:
    """Generate a formatted AI summary report in Markdown.

    Uses MarkdownGenerator for visual formatting with impact indicators.
    """
    summary = await generate_ai_summary(
        llm, comparison, regressions, current_metrics, previous_metrics
    )

    # Build a ReportOutput for the visual generator
    valid_trends = ("crescimento", "estável", "declínio")
    trend_val = summary.overall_trend if summary.overall_trend in valid_trends else "estável"
    report = ReportOutput(
        headline=summary.headline,
        highlights=summary.highlights if summary.highlights else ["Nenhum destaque significativo"],
        risk_areas=(
            summary.risk_areas if summary.risk_areas else ["Nenhuma área de risco identificada"]
        ),
        recommendation="Revisar as mudanças e planejar adoção conforme prioridade.",
        trend=trend_val,  # type: ignore[arg-type]
    )

    return MarkdownGenerator.report_section(report)
