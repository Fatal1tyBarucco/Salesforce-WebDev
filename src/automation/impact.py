"""Impact prediction, category scoring, and triage."""

from __future__ import annotations

from typing import Any

from .models import CategoryImpactScore, ImpactPrediction, TriageResult


async def _load_all_release_metas(load_meta_fn: Any) -> list[dict[str, Any]]:
    """Load all release metadata sorted by release_id."""
    from pathlib import Path

    from ..config import RELEASES_DIR

    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return []

    metas = []
    for d in releases_dir.iterdir():
        meta = load_meta_fn(d.name)
        if meta:
            total = sum(c.get("count", 0) for c in meta.get("categories", []))
            if total > 0:
                metas.append(meta)

    metas.sort(key=lambda m: m.get("release_id", 0))
    return metas


async def calculate_category_impact_scores(
    load_meta_fn: Any,
) -> list[CategoryImpactScore]:
    """Calculate impact scores for all categories based on historical data."""
    metas = await _load_all_release_metas(load_meta_fn)
    if len(metas) < 2:
        return []

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

        changes = [history[i] - history[i - 1] for i in range(1, len(history))]
        if not changes:
            continue

        mean_change = sum(changes) / len(changes)
        variance = sum((c - mean_change) ** 2 for c in changes) / len(changes)
        volatility = variance**0.5

        if mean_change > 5:
            trend = "crescimento"
        elif mean_change < -5:
            trend = "declínio"
        else:
            trend = "estável"

        risk_score = volatility + abs(mean_change) * 0.5

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


async def predict_next_release_impact(
    load_meta_fn: Any,
) -> ImpactPrediction:
    """Predict which categories will have the most impact in the next release."""
    scores = await calculate_category_impact_scores(load_meta_fn)
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

    avg_risk = sum(s.risk_score for s in scores) / len(scores)
    if avg_risk > 20:
        overall_risk = "alto"
    elif avg_risk > 10:
        overall_risk = "moderado"
    else:
        overall_risk = "baixo"

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


async def generate_impact_prediction_report(
    load_meta_fn: Any,
) -> str:
    """Generate a formatted impact prediction report in Markdown."""
    prediction = await predict_next_release_impact(load_meta_fn)

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

    lines.extend(["---", "*Previsão gerada automaticamente pelo módulo de AI Automation*"])
    return "\n".join(lines)


async def triage_release(
    load_meta_fn: Any,
    slug: str,
) -> TriageResult:
    """Analyze a release and generate automated triage with risk assessment."""
    meta = load_meta_fn(slug)
    if not meta:
        return TriageResult(
            risk_level="desconhecido",
            risk_score=0,
            categories_at_risk=[],
            suggested_actions=["Verificar se a release existe no repositório"],
            priority="baixa",
            summary="Release não encontrada para análise.",
        )

    from .comparison import calculate_quality_metrics, compare_releases, detect_regressions

    metrics = await calculate_quality_metrics(load_meta_fn, slug)
    predictions = await predict_next_release_impact(load_meta_fn)

    risk_score = 0
    categories_at_risk: list[str] = []
    suggested_actions: list[str] = []

    if predictions.high_risk_categories:
        risk_score += len(predictions.high_risk_categories) * 10
        categories_at_risk.extend([c.category for c in predictions.high_risk_categories])
        suggested_actions.append(
            f"Monitorar de perto as {len(predictions.high_risk_categories)} categorias de alto risco"
        )

    all_metas = await _load_all_release_metas(load_meta_fn)
    all_slugs_by_id = [m.get("slug", "") for m in all_metas]
    if len(all_slugs_by_id) >= 2:
        prev_slugs = [s for s in all_slugs_by_id if s != slug]
        if prev_slugs:
            prev_slug = prev_slugs[-1]
            regressions = await detect_regressions(load_meta_fn, slug, prev_slug)
            if regressions:
                risk_score += len(regressions) * 15
                categories_at_risk.extend([r.category for r in regressions])
                suggested_actions.append(f"Investigar {len(regressions)} categorias com regressão")

    if metrics:
        if metrics.total_features > 2000:
            risk_score += 5
            suggested_actions.append("Release com alto volume de recursos — revisar changelog")
        if metrics.avg_features_per_category > 100:
            risk_score += 5
            suggested_actions.append("Categorias com média alta — verificar consistência")

    if len(all_slugs_by_id) >= 2:
        prev_slugs = [s for s in all_slugs_by_id if s != slug]
        if prev_slugs:
            prev_slug = prev_slugs[-1]
            comparison = await compare_releases(load_meta_fn, slug, prev_slug)
            if comparison.new_categories:
                risk_score += len(comparison.new_categories) * 3
                suggested_actions.append(
                    f"Documentar {len(comparison.new_categories)} novas categorias"
                )

    risk_score = min(risk_score, 100)

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

    if not suggested_actions:
        suggested_actions.append("Nenhuma ação específica necessária")

    name = meta.get("name", slug)
    total = metrics.total_features if metrics else 0
    summary = (
        f"Release {name} com {total} recursos analisada. "
        f"Nível de risco: {risk_level} (pontuação: {risk_score}/100). "
        f"Prioridade: {priority}."
    )

    return TriageResult(
        risk_level=risk_level,
        risk_score=risk_score,
        categories_at_risk=list(dict.fromkeys(categories_at_risk)),
        suggested_actions=suggested_actions,
        priority=priority,
        summary=summary,
    )


async def generate_triage_report(
    load_meta_fn: Any,
    slug: str,
) -> str:
    """Generate a formatted triage report in Markdown."""
    triage = await triage_release(load_meta_fn, slug)

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

    lines.extend(["---", "*Triage gerado automaticamente pelo módulo de AI Automation*"])
    return "\n".join(lines)
