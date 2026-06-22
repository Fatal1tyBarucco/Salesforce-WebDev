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

import hashlib
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
        if not changes:  # pragma: no cover — unreachable: len(history) >= 2 ensures changes
            continue

        mean_change = sum(changes) / len(changes)
        variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
        volatility = variance**0.5

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


@dataclass
class TriageResult:
    """Automated triage result for a release alert."""

    risk_level: str
    risk_score: int
    categories_at_risk: list[str]
    suggested_actions: list[str]
    priority: str
    summary: str


def triage_release(slug: str) -> TriageResult:
    """Analyze a release and generate automated triage with risk assessment.

    Evaluates:
    - Category volatility from historical data
    - Regression patterns
    - Feature count anomalies
    - Suggests specific actions based on findings
    """
    meta = load_release_meta(slug)
    if not meta:
        return TriageResult(
            risk_level="desconhecido",
            risk_score=0,
            categories_at_risk=[],
            suggested_actions=["Verificar se a release existe no repositório"],
            priority="baixa",
            summary="Release não encontrada para análise.",
        )

    metrics = calculate_quality_metrics(slug)
    predictions = predict_next_release_impact()

    risk_score = 0
    categories_at_risk: list[str] = []
    suggested_actions: list[str] = []

    # Check for high-risk categories in this release
    if predictions.high_risk_categories:
        risk_score += len(predictions.high_risk_categories) * 10
        categories_at_risk.extend([c.category for c in predictions.high_risk_categories])
        suggested_actions.append(
            f"Monitorar de perto as {len(predictions.high_risk_categories)} categorias de alto risco"
        )

    # Check for regressions
    all_slugs = sorted(
        [d.name for d in Path(RELEASES_DIR).iterdir() if d.is_dir()],
    )
    if len(all_slugs) >= 2:
        prev_slug = [s for s in all_slugs if s != slug]
        if prev_slug:
            regressions = detect_regressions(slug, prev_slug[0])
            if regressions:
                risk_score += len(regressions) * 15
                categories_at_risk.extend([r.category for r in regressions])
                suggested_actions.append(f"Investigar {len(regressions)} categorias com regressão")

    # Check for large feature count anomalies
    if metrics:
        if metrics.total_features > 2000:
            risk_score += 5
            suggested_actions.append("Release com alto volume de recursos — revisar changelog")
        if metrics.avg_features_per_category > 100:
            risk_score += 5
            suggested_actions.append("Categorias com média alta — verificar consistência")

    # Check for new categories
    if len(all_slugs) >= 2:
        prev_slug = [s for s in all_slugs if s != slug]
        if prev_slug:
            comparison = compare_releases(slug, prev_slug[0])
            if comparison.new_categories:
                risk_score += len(comparison.new_categories) * 3
                suggested_actions.append(
                    f"Documentar {len(comparison.new_categories)} novas categorias"
                )

    # Cap risk score at 100
    risk_score = min(risk_score, 100)

    # Determine risk level and priority
    if risk_score >= 50:
        risk_level = "alto"
        priority = "urgente"
    elif risk_score >= 25:
        risk_level = "moderado"
        priority = "alta"
    elif risk_score >= 10:
        risk_level = "baixo"
        priority = "normal"
    else:
        risk_level = "mínimo"
        priority = "baixa"

    # Add default actions if none generated
    if not suggested_actions:
        suggested_actions.append("Nenhuma ação específica necessária")

    # Build summary
    name = meta.get("name", slug)
    total = metrics.total_features if metrics else 0
    summary = (
        f"Release {name} com {total} recursos analisada. "
        f"Nível de risco: {risk_level} (pontuação: {risk_score}/100). "
        f"Prioridade: {priority}."
    )

    # Deduplicate categories
    categories_at_risk = list(dict.fromkeys(categories_at_risk))

    return TriageResult(
        risk_level=risk_level,
        risk_score=risk_score,
        categories_at_risk=categories_at_risk,
        suggested_actions=suggested_actions,
        priority=priority,
        summary=summary,
    )


def generate_triage_report(slug: str) -> str:
    """Generate a formatted triage report in Markdown."""
    triage = triage_release(slug)

    lines = [
        "# Relatório de Triage Automatizado\n",
        f"## Nível de Risco: **{triage.risk_level.upper()}** (Pontuação: {triage.risk_score}/100)\n",
        f"**Prioridade:** {triage.priority}\n",
        f"*{triage.summary}*\n",
    ]

    if triage.categories_at_risk:
        lines.append("## 🎯 Categorias em Risco\n")
        for cat in triage.categories_at_risk:
            lines.append(f"- {cat}")
        lines.append("")

    lines.append("## 📋 Ações Sugeridas\n")
    for action in triage.suggested_actions:
        lines.append(f"1. {action}")
    lines.append("")

    lines.extend(
        [
            "---",
            "*Triage gerado automaticamente pelo módulo de AI Automation*",
        ]
    )

    return "\n".join(lines)


@dataclass
class ContentHash:
    """Hash of a content file for deduplication."""

    file_path: str
    content_hash: str
    size_bytes: int
    last_modified: float


@dataclass
class DeduplicationResult:
    """Result of content deduplication analysis."""

    unchanged_files: list[str]
    changed_files: list[str]
    new_files: list[str]
    removed_files: list[str]
    total_savings_bytes: int
    cache_hit_rate: float


def _calculate_file_hash(file_path: Path) -> ContentHash:
    """Calculate MD5 hash of a file's content."""
    content = file_path.read_bytes()
    content_hash = hashlib.md5(content).hexdigest()
    stat = file_path.stat()
    return ContentHash(
        file_path=str(file_path),
        content_hash=content_hash,
        size_bytes=stat.st_size,
        last_modified=stat.st_mtime,
    )


def _load_content_cache(cache_path: Path) -> dict[str, ContentHash]:
    """Load content cache from file."""
    if not cache_path.exists():
        return {}
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        return {k: ContentHash(**v) for k, v in data.items()}
    except (json.JSONDecodeError, TypeError):
        return {}


def _save_content_cache(cache_path: Path, cache: dict[str, ContentHash]) -> None:
    """Save content cache to file."""
    data = {k: vars(v) for k, v in cache.items()}
    cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def analyze_content_changes(release_slug: str) -> DeduplicationResult:
    """Analyze content changes in a release directory.

    Compares current files against cached hashes to identify:
    - Unchanged files (same hash)
    - Changed files (different hash)
    - New files (not in cache)
    - Removed files (in cache but not on disk)
    """
    release_dir = Path(RELEASES_DIR) / release_slug
    cache_path = release_dir / ".content_cache.json"

    if not release_dir.exists():
        return DeduplicationResult(
            unchanged_files=[],
            changed_files=[],
            new_files=[],
            removed_files=[],
            total_savings_bytes=0,
            cache_hit_rate=0.0,
        )

    # Calculate current hashes
    current_hashes: dict[str, ContentHash] = {}
    for f in release_dir.iterdir():
        if f.is_file() and f.suffix == ".md":
            current_hashes[str(f)] = _calculate_file_hash(f)

    # Load cached hashes
    cached_hashes = _load_content_cache(cache_path)

    # Compare
    unchanged: list[str] = []
    changed: list[str] = []
    new: list[str] = []
    savings = 0

    for path, current in current_hashes.items():
        if path in cached_hashes:
            if current.content_hash == cached_hashes[path].content_hash:
                unchanged.append(path)
                savings += current.size_bytes
            else:
                changed.append(path)
        else:
            new.append(path)

    removed = [path for path in cached_hashes if path not in current_hashes]

    total = len(current_hashes)
    hit_rate = len(unchanged) / total if total > 0 else 0.0

    # Update cache
    _save_content_cache(cache_path, current_hashes)

    return DeduplicationResult(
        unchanged_files=unchanged,
        changed_files=changed,
        new_files=new,
        removed_files=removed,
        total_savings_bytes=savings,
        cache_hit_rate=round(hit_rate, 2),
    )


def get_content_hash(file_path: str) -> str | None:
    """Get the MD5 hash of a file's content."""
    path = Path(file_path)
    if not path.exists():
        return None
    content = path.read_bytes()
    return hashlib.md5(content).hexdigest()


def is_content_unchanged(file_path: str, expected_hash: str) -> bool:
    """Check if a file's content matches the expected hash."""
    current_hash = get_content_hash(file_path)
    return current_hash == expected_hash if current_hash else False


def generate_deduplication_report(release_slug: str) -> str:
    """Generate a formatted deduplication report in Markdown."""
    result = analyze_content_changes(release_slug)

    lines = [
        "# Relatório de Deduplicação de Conteúdo\n",
        f"## Release: {release_slug}\n",
        f"**Taxa de acerto do cache:** {result.cache_hit_rate:.0%}\n",
        f"**Economia total:** {result.total_savings_bytes:,} bytes\n",
    ]

    if result.unchanged_files:
        lines.append(f"## ✅ Arquivos Inalterados ({len(result.unchanged_files)})\n")
        for f in result.unchanged_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    if result.changed_files:
        lines.append(f"## 🔄 Arquivos Alterados ({len(result.changed_files)})\n")
        for f in result.changed_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    if result.new_files:
        lines.append(f"## 🆕 Arquivos Novos ({len(result.new_files)})\n")
        for f in result.new_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    if result.removed_files:
        lines.append(f"## 🗑️ Arquivos Removidos ({len(result.removed_files)})\n")
        for f in result.removed_files:
            lines.append(f"- `{Path(f).name}`")
        lines.append("")

    lines.extend(
        [
            "---",
            "*Relatório gerado automaticamente pelo módulo de AI Automation*",
        ]
    )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Smart Notification Filtering
# ---------------------------------------------------------------------------

# User profile definitions with category relevance mappings
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


@dataclass
class UserProfile:
    """User profile for notification filtering."""

    profile_type: str
    name: str
    relevant_categories: list[str]
    filtered_features: list[str]
    priority_features: list[str]
    relevance_score: float


@dataclass
class FilteredNotification:
    """Filtered notification for a specific user profile."""

    profile: UserProfile
    total_features: int
    relevant_count: int
    priority_count: int
    summary: str


def filter_features_for_profile(profile_type: str, categories: list[dict[str, Any]]) -> UserProfile:
    """Filter features based on user profile relevance.

    Analyzes feature categories and returns:
    - Which categories are relevant to the profile
    - Which features are high priority
    - Overall relevance score
    """
    if profile_type not in USER_PROFILES:
        profile_config = USER_PROFILES["business"]  # Default fallback
    else:
        profile_config = USER_PROFILES[profile_type]

    relevant_categories = []
    priority_features: list[str] = []

    for cat in categories:
        cat_name = cat.get("name", "")
        count = cat.get("count", 0)

        # Check if category matches profile keywords
        is_relevant = False
        for keyword in profile_config["keywords"]:
            if keyword.lower() in cat_name.lower():
                is_relevant = True
                break

        # Check if category is in priority boost list
        if cat_name in profile_config["priority_boost"]:
            is_relevant = True
            priority_features.append(f"{cat_name} ({count} recursos)")

        if is_relevant:
            relevant_categories.append(cat_name)

    # Calculate relevance score
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


def generate_filtered_notification(slug: str, profile_type: str) -> FilteredNotification:
    """Generate a filtered notification for a specific user profile.

    Filters release features based on profile relevance and
    generates a personalized summary.
    """
    meta = load_release_meta(slug)
    if not meta:
        return FilteredNotification(
            profile=UserProfile(
                profile_type=profile_type,
                name="Unknown",
                relevant_categories=[],
                filtered_features=[],
                priority_features=[],
                relevance_score=0.0,
            ),
            total_features=0,
            relevant_count=0,
            priority_count=0,
            summary="Release não encontrada.",
        )

    categories = meta.get("categories", [])
    total_features = sum(c.get("count", 0) for c in categories)

    profile = filter_features_for_profile(profile_type, categories)

    # Build summary
    if profile.relevance_score > 0.5:
        summary = (
            f"Alta relevância para {profile.name}: "
            f"{len(profile.relevant_categories)} categorias relevantes "
            f"({profile.relevance_score:.0%} do total)"
        )
    elif profile.relevance_score > 0.2:
        summary = (
            f"Relevância moderada para {profile.name}: "
            f"{len(profile.relevant_categories)} categorias relevantes"
        )
    else:
        summary = (
            f"Baixa relevância para {profile.name}: " f"poucas categorias alinhadas com seu perfil"
        )

    return FilteredNotification(
        profile=profile,
        total_features=total_features,
        relevant_count=len(profile.relevant_categories),
        priority_count=len(profile.priority_features),
        summary=summary,
    )


def generate_filtered_notification_report(slug: str, profile_type: str) -> str:
    """Generate a formatted filtered notification report in Markdown."""
    notification = generate_filtered_notification(slug, profile_type)

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

    lines.extend(
        [
            "---",
            "*Notificação gerada automaticamente pelo módulo de AI Automation*",
        ]
    )

    return "\n".join(lines)
