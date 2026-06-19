"""AI-powered automation features for release notes pipeline.

Provides:
- Release comparison between versions
- Regression detection
- Quality metrics generation
- Changelog generation
- GitHub Issue notifications
- Dynamic badge generation
"""

from __future__ import annotations

import json
import subprocess
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
    changed_categories: list[tuple[str, int, int]]


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


def create_github_issue(release_name: str, total_features: int, categories: int) -> str | None:
    """Create a GitHub Issue for a new release detection."""
    body = f"""## Nova Release Detectada: {release_name}

### Resumo
- **Total de recursos:** {total_features}
- **Categorias:** {categories}

### Detalhes
A automação detectou uma nova release do Salesforce e processou os dados automaticamente.

### Arquivos Gerados
- `releases/{release_name.lower().replace(' ', '_').replace("'", "")}/` — Diretório da release
- `CHANGELOG.md` — Changelog atualizado
- `QUALITY_REPORT.md` — Relatório de qualidade

---
*Gerado automaticamente pelo pipeline de Release Notes Intelligence*
"""
    try:
        result = subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                f"Release: {release_name}",
                "--body",
                body,
                "--label",
                "release",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def generate_dynamic_badge(release_name: str, total_features: int) -> str:
    """Generate a dynamic badge markdown for the latest release."""
    return f"![Latest Release](https://img.shields.io/badge/Última%20Release-{release_name.replace(' ', '%20')}-blue)"


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


def create_release_issue(slug: str) -> str:
    """Create a GitHub Issue body for a new release."""
    meta = load_release_meta(slug)
    if not meta:
        return ""

    name = meta.get("name", slug)
    categories = meta.get("categories", [])
    total = sum(c.get("count", 0) for c in categories)

    lines = [
        f"## 🚀 Nova Release: {name}",
        "",
        f"**{total} recursos** em **{len(categories)} categorias** detectados automaticamente.",
        "",
        "### Categorias",
        "",
    ]

    for cat in sorted(categories, key=lambda c: c.get("count", 0), reverse=True):
        count = cat.get("count", 0)
        if count > 0:
            lines.append(f"- **{cat['name']}**: {count} recursos")

    lines.extend(
        [
            "",
            "---",
            "*Issue criada automaticamente pelo pipeline de release notes.*",
        ]
    )

    return "\n".join(lines)


def get_latest_release_badge() -> str:
    """Get the latest release name for badge display."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return "N/A"

    latest = None
    latest_id = -1

    for d in releases_dir.iterdir():
        meta = load_release_meta(d.name)
        if meta and meta.get("release_id", 0) > latest_id:
            latest_id = meta.get("release_id", 0)
            latest = meta.get("name", d.name)

    return latest or "N/A"


@dataclass
class AISummary:
    """AI-generated summary of release comparison."""

    headline: str
    highlights: list[str]
    risk_areas: list[str]
    overall_trend: str


def generate_ai_summary(current_slug: str, previous_slug: str) -> AISummary:
    """Generate an intelligent natural language summary of release differences.

    Analyzes comparison data and produces a structured summary with:
    - Headline: one-line summary of the release
    - Highlights: key positive changes
    - Risk areas: potential concerns (regressions, removed categories)
    - Overall trend: growth, stable, or declining
    """
    comparison = compare_releases(current_slug, previous_slug)
    regressions = detect_regressions(current_slug, previous_slug)
    current_metrics = calculate_quality_metrics(current_slug)
    previous_metrics = calculate_quality_metrics(previous_slug)

    # Build headline
    total_changes = (
        len(comparison.new_categories)
        + len(comparison.removed_categories)
        + len(comparison.changed_categories)
    )
    if total_changes == 0:
        headline = f"{comparison.current_name} — sem alterações significativas em relação a {comparison.previous_name}"
    else:
        headline = (
            f"{comparison.current_name} traz {total_changes} alterações "
            f"em relação a {comparison.previous_name}"
        )

    # Build highlights
    highlights: list[str] = []
    if comparison.new_categories:
        highlights.append(
            f"{len(comparison.new_categories)} novas categorias adicionadas: "
            + ", ".join(comparison.new_categories[:3])
            + ("..." if len(comparison.new_categories) > 3 else "")
        )
    if comparison.changed_categories:
        growth = [c for c in comparison.changed_categories if c[2] > c[1]]
        if growth:
            top_grower = max(growth, key=lambda c: c[2] - c[1])
            highlights.append(
                f"Maior crescimento em '{top_grower[0]}': "
                f"{top_grower[1]} → {top_grower[2]} (+{top_grower[2] - top_grower[1]})"
            )
    if current_metrics and previous_metrics:
        diff = current_metrics.total_features - previous_metrics.total_features
        if diff > 0:
            highlights.append(
                f"Crescimento total de {diff} recursos "
                f"({previous_metrics.total_features} → {current_metrics.total_features})"
            )

    # Build risk areas
    risk_areas: list[str] = []
    if comparison.removed_categories:
        risk_areas.append(
            f"{len(comparison.removed_categories)} categorias removidas: "
            + ", ".join(comparison.removed_categories)
        )
    if regressions:
        total_loss = sum(r.change for r in regressions)
        risk_areas.append(
            f"{len(regressions)} categorias com regressão (perda total: {abs(total_loss)} recursos)"
        )

    # Determine overall trend
    if current_metrics and previous_metrics:
        growth_pct = (
            (current_metrics.total_features - previous_metrics.total_features)
            / max(previous_metrics.total_features, 1)
            * 100
        )
        if growth_pct > 5:
            overall_trend = "crescimento"
        elif growth_pct < -5:
            overall_trend = "declínio"
        else:
            overall_trend = "estável"
    else:
        overall_trend = "indeterminado"

    return AISummary(
        headline=headline,
        highlights=highlights,
        risk_areas=risk_areas,
        overall_trend=overall_trend,
    )


def generate_ai_summary_report(current_slug: str, previous_slug: str) -> str:
    """Generate a formatted AI summary report in Markdown."""
    summary = generate_ai_summary(current_slug, previous_slug)

    lines = [
        "# Resumo Inteligente da Release\n",
        f"## {summary.headline}\n",
        "## 📈 Destaques\n",
    ]

    for highlight in summary.highlights:
        lines.append(f"- {highlight}")

    if not summary.highlights:
        lines.append("- Nenhum destaque significativo")

    lines.append("")
    lines.append("## ⚠️ Áreas de Risco\n")

    for risk in summary.risk_areas:
        lines.append(f"- {risk}")

    if not summary.risk_areas:
        lines.append("- Nenhuma área de risco identificada")

    lines.extend(
        [
            "",
            f"## 📊 Tendência Geral: **{summary.overall_trend.upper()}**",
            "",
            "---",
            "*Relatório gerado automaticamente pelo módulo de AI Automation*",
        ]
    )

    return "\n".join(lines)


@dataclass
class CategoryImpactScore:
    """Impact score for a single category based on historical data."""

    category: str
    volatility: float
    trend: str
    risk_score: float
    prediction: str


@dataclass
class ImpactPrediction:
    """Predictive impact analysis for next release."""

    high_risk_categories: list[CategoryImpactScore]
    stable_categories: list[CategoryImpactScore]
    growing_categories: list[CategoryImpactScore]
    overall_risk_level: str
    summary: str


def _load_all_release_metas() -> list[dict[str, Any]]:
    """Load all release metadata sorted by release_id."""
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return []

    metas = []
    for d in releases_dir.iterdir():
        meta_path = d / ".meta.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            metas.append(meta)

    metas.sort(key=lambda m: m.get("release_id", 0))
    return metas


def calculate_category_impact_scores() -> list[CategoryImpactScore]:
    """Calculate impact scores for all categories based on historical data.

    Analyzes changes across all available releases to determine:
    - Volatility: how much a category changes between releases
    - Trend: whether the category is growing, stable, or declining
    - Risk score: likelihood of significant change in next release
    """
    metas = _load_all_release_metas()
    if len(metas) < 2:
        return []

    # Build category history: {category: [count_per_release]}
    category_history: dict[str, list[int]] = {}
    for meta in metas:
        current_cats = {c["name"]: c["count"] for c in meta.get("categories", [])}
        for name, count in current_cats.items():
            if name not in category_history:
                category_history[name] = []
            category_history[name].append(count)

    scores: list[CategoryImpactScore] = []
    for name, history in category_history.items():
        if len(history) < 2:
            continue

        # Calculate volatility (standard deviation of changes)
        changes = [history[i] - history[i - 1] for i in range(1, len(history))]
        if not changes:
            continue

        mean_change = sum(changes) / len(changes)
        variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
        volatility = variance ** 0.5

        # Determine trend
        if mean_change > 5:
            trend = "crescimento"
        elif mean_change < -5:
            trend = "declínio"
        else:
            trend = "estável"

        # Risk score: higher volatility + extreme trend = higher risk
        risk_score = volatility + abs(mean_change) * 0.5

        # Generate prediction
        if risk_score > 20:
            prediction = "Alta probabilidade de mudança significativa"
        elif risk_score > 10:
            prediction = "Mudança moderada esperada"
        elif risk_score > 5:
            prediction = "Mudança leve possível"
        else:
            prediction = "Provavelmente estável"

        scores.append(
            CategoryImpactScore(
                category=name,
                volatility=round(volatility, 2),
                trend=trend,
                risk_score=round(risk_score, 2),
                prediction=prediction,
            )
        )

    return sorted(scores, key=lambda s: s.risk_score, reverse=True)


def predict_next_release_impact() -> ImpactPrediction:
    """Predict which categories will have the most impact in the next release.

    Uses historical volatility and trend data to forecast:
    - High-risk categories likely to change significantly
    - Stable categories expected to remain consistent
    - Growing categories with upward momentum
    """
    scores = calculate_category_impact_scores()
    if not scores:
        return ImpactPrediction(
            high_risk_categories=[],
            stable_categories=[],
            growing_categories=[],
            overall_risk_level="indeterminado",
            summary="Dados insuficientes para previsão. Necessário pelo menos 2 releases.",
        )

    high_risk = [s for s in scores if s.risk_score > 15]
    growing = [s for s in scores if s.trend == "crescimento" and s.risk_score > 5]
    stable = [s for s in scores if s.trend == "estável" and s.risk_score <= 10]

    # Overall risk level
    avg_risk = sum(s.risk_score for s in scores) / len(scores)
    if avg_risk > 20:
        overall_risk = "alto"
    elif avg_risk > 10:
        overall_risk = "moderado"
    else:
        overall_risk = "baixo"

    # Build summary
    parts = []
    if high_risk:
        parts.append(
            f"{len(high_risk)} categorias de alto risco ({', '.join(s.category for s in high_risk[:3])})"
        )
    if growing:
        parts.append(f"{len(growing)} categorias em crescimento")
    if stable:
        parts.append(f"{len(stable)} categorias estáveis")

    summary = "Análise: " + "; ".join(parts) if parts else "Sem dados suficientes para análise."

    return ImpactPrediction(
        high_risk_categories=high_risk,
        stable_categories=stable,
        growing_categories=growing,
        overall_risk_level=overall_risk,
        summary=summary,
    )


def generate_impact_prediction_report() -> str:
    """Generate a formatted impact prediction report in Markdown."""
    prediction = predict_next_release_impact()

    lines = [
        "# Previsão de Impacto da Próxima Release\n",
        f"## Nível de Risco Geral: **{prediction.overall_risk_level.upper()}**\n",
        f"*{prediction.summary}*\n",
    ]

    if prediction.high_risk_categories:
        lines.append("## 🔴 Alto Risco\n")
        for cat in prediction.high_risk_categories:
            lines.append(
                f"- **{cat.category}** — Volatilidade: {cat.volatility:.1f}, "
                f"Tendência: {cat.trend}, Previsão: {cat.prediction}"
            )
        lines.append("")

    if prediction.growing_categories:
        lines.append("## 📈 Em Crescimento\n")
        for cat in prediction.growing_categories:
            lines.append(
                f"- **{cat.category}** — Volatilidade: {cat.volatility:.1f}, "
                f"Score: {cat.risk_score:.1f}"
            )
        lines.append("")

    if prediction.stable_categories:
        lines.append("## ✅ Estáveis\n")
        for cat in prediction.stable_categories:
            lines.append(f"- **{cat.category}** — Volatilidade: {cat.volatility:.1f}")
        lines.append("")

    if not prediction.high_risk_categories and not prediction.growing_categories:
        lines.append("## ℹ️ Sem categorias de alto risco ou em crescimento\n")

    lines.extend(
        [
            "---",
            "*Previsão gerada automaticamente pelo módulo de AI Automation*",
        ]
    )

    return "\n".join(lines)
