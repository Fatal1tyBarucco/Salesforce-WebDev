"""AI-powered automation features for release notes pipeline.

Provides:
- Release comparison between versions
- Regression detection
- Quality metrics generation
- Changelog generation
- GitHub Issue notifications
- Dynamic badge generation
- Impact prediction and triage
- Content deduplication
- Profile-based notification filtering
- Data export (JSON/CSV)
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from .config import RELEASES_DIR
from .llm_service import LLMService


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


@dataclass
class AISummary:
    """AI-generated summary of release comparison."""

    headline: str
    highlights: list[str]
    risk_areas: list[str]
    overall_trend: str


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


@dataclass
class TriageResult:
    """Automated triage result for a release alert."""

    risk_level: str
    risk_score: int
    categories_at_risk: list[str]
    suggested_actions: list[str]
    priority: str
    summary: str


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


class AIAutomationService:
    """AI-powered automation service for release notes pipeline."""

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

    def __init__(self, llm: Optional[LLMService] = None) -> None:
        self._llm = llm or LLMService()

    @staticmethod
    def load_release_meta(slug: str) -> Optional[dict[str, Any]]:
        """Load .meta.json for a release."""
        meta_path = Path(RELEASES_DIR) / slug / ".meta.json"
        if not meta_path.exists():
            return None
        return json.loads(meta_path.read_text(encoding="utf-8"))  # type: ignore

    async def compare_releases(self, current_slug: str, previous_slug: str) -> ReleaseComparison:
        """Compare two releases and identify differences."""
        current = self.load_release_meta(current_slug)
        previous = self.load_release_meta(previous_slug)

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

    async def detect_regressions(self, current_slug: str, previous_slug: str) -> list[Regression]:
        """Detect features that lost resources between releases."""
        current = self.load_release_meta(current_slug)
        previous = self.load_release_meta(previous_slug)

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

    async def calculate_quality_metrics(self, slug: str) -> Optional[QualityMetrics]:
        """Calculate quality metrics for a release."""
        meta = self.load_release_meta(slug)
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

    async def create_github_issue(
        self, release_name: str, total_features: int, categories: int
    ) -> Optional[str]:
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

        def run_gh() -> Any:
            return subprocess.run(
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

        try:
            result = await asyncio.to_thread(run_gh)
            if result.returncode == 0:
                return cast(str, result.stdout.strip())
        except Exception:
            pass
        return None

    @staticmethod
    def generate_dynamic_badge(release_name: str, total_features: int) -> str:
        """Generate a dynamic badge markdown for the latest release."""
        return f"![Latest Release](https://img.shields.io/badge/Última%20Release-{release_name.replace(' ', '%20')}-blue)"

    async def generate_changelog(self) -> str:
        """Generate an intelligent CHANGELOG.md from release metadata."""
        releases_dir = Path(RELEASES_DIR)
        if not releases_dir.exists():
            return "# Changelog\n\nNo releases found.\n"

        metas = []
        for d in releases_dir.iterdir():
            meta = self.load_release_meta(d.name)
            if meta:
                total = sum(c.get("count", 0) for c in meta.get("categories", []))
                if total > 0:
                    metas.append(meta)

        metas.sort(key=lambda m: m.get("release_id", 0), reverse=True)
        if not metas:
            return "# Changelog\n\nNo releases found.\n"

        system_prompt = (
            "You are an expert Salesforce Release Analyst. Generate a professional and concise "
            "Markdown CHANGELOG based on the provided release metadata. "
            "Focus on high-level trends and the volume of features. "
            "Use Brazilian Portuguese. Format with ## for releases and bullet points for categories."
        )
        user_prompt = f"Release Metadata: {json.dumps(metas)}"

        result = await self._llm.generate_text(user_prompt, system_prompt)
        if result:
            return result

        # Fallback to basic format
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

    async def generate_regression_report(self, current_slug: str, previous_slug: str) -> str:
        """Generate an intelligent regression report between two releases."""
        comparison = await self.compare_releases(current_slug, previous_slug)
        regressions = await self.detect_regressions(current_slug, previous_slug)

        system_prompt = (
            "You are an expert Salesforce Release Analyst. Analyze the release comparison "
            "and detected regressions. Generate a detailed Markdown report in Brazilian Portuguese. "
            "Explain the impact of the regressions and highlight new or removed categories."
        )
        analysis_data = {
            "comparison": vars(comparison),
            "regressions": [vars(r) for r in regressions],
        }
        user_prompt = f"Analysis Data: {json.dumps(analysis_data)}"

        result = await self._llm.generate_text(user_prompt, system_prompt)
        if result:
            return result

        # Fallback to basic format
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

    async def generate_diff_report(self, current_slug: str, previous_slug: str) -> str:
        """Generate an intelligent visual diff report between two releases."""
        comparison = await self.compare_releases(current_slug, previous_slug)
        current = self.load_release_meta(current_slug)
        previous = self.load_release_meta(previous_slug)

        current_cats = (
            {c["name"]: c["count"] for c in current.get("categories", [])} if current else {}
        )
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

        system_prompt = (
            "You are an expert Salesforce Release Analyst. Analyze the provided side-by-side diff "
            "of feature counts between two releases. Generate a Markdown report in Brazilian Portuguese "
            "including a summary table and an intelligent analysis of the most significant changes."
        )
        user_prompt = f"Diff Data: {json.dumps(diff_data)}"

        result = await self._llm.generate_text(user_prompt, system_prompt)
        if result:
            return result

        # Fallback to basic table
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

    async def generate_quality_report(self) -> str:
        """Generate an intelligent quality report for all releases."""
        releases_dir = Path(RELEASES_DIR)
        if not releases_dir.exists():
            return "# Relatório de Qualidade\n\nNenhuma release encontrada.\n"

        all_metrics = []
        for d in sorted(releases_dir.iterdir()):
            if not d.is_dir():
                continue
            meta = self.load_release_meta(d.name)
            if not meta:
                continue
            metrics = await self.calculate_quality_metrics(d.name)
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

        result = await self._llm.generate_text(user_prompt, system_prompt)
        if result:
            return result

        # Fallback to basic format
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

    async def generate_ai_summary(self, current_slug: str, previous_slug: str) -> AISummary:
        """Generate an intelligent natural language summary of release differences."""
        comparison = await self.compare_releases(current_slug, previous_slug)
        regressions = await self.detect_regressions(current_slug, previous_slug)
        current_metrics = await self.calculate_quality_metrics(current_slug)
        previous_metrics = await self.calculate_quality_metrics(previous_slug)

        analysis_data = {
            "comparison": vars(comparison),
            "regressions": [vars(r) for r in regressions],
            "current_metrics": vars(current_metrics) if current_metrics else None,
            "previous_metrics": vars(previous_metrics) if previous_metrics else None,
        }

        system_prompt = (
            "You are an expert Salesforce Release Analyst. Analyze the provided release comparison data "
            "and return a JSON object representing an AISummary with the following fields: "
            "'headline' (concise one-liner), 'highlights' (list of key positive changes), "
            "'risk_areas' (list of concerns), and 'overall_trend' (one of: 'crescimento', 'estável', 'declínio'). "
            "The output must be valid JSON."
        )
        user_prompt = f"Comparison Data: {json.dumps(analysis_data)}"

        result_text = await self._llm.generate_text(user_prompt, system_prompt)
        if not result_text:
            return self._generate_legacy_ai_summary(
                comparison, regressions, current_metrics, previous_metrics
            )

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
        except ValueError, IndexError:
            return self._generate_legacy_ai_summary(
                comparison, regressions, current_metrics, previous_metrics
            )

    def _generate_legacy_ai_summary(
        self,
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

    async def generate_ai_summary_report(self, current_slug: str, previous_slug: str) -> str:
        """Generate a formatted AI summary report in Markdown."""
        summary = await self.generate_ai_summary(current_slug, previous_slug)

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

    async def _load_all_release_metas(self) -> list[dict[str, Any]]:
        """Load all release metadata sorted by release_id."""
        releases_dir = Path(RELEASES_DIR)
        if not releases_dir.exists():
            return []

        metas = []
        for d in releases_dir.iterdir():
            meta = self.load_release_meta(d.name)
            if meta:
                total = sum(c.get("count", 0) for c in meta.get("categories", []))
                if total > 0:
                    metas.append(meta)

        metas.sort(key=lambda m: m.get("release_id", 0))
        return metas

    async def calculate_category_impact_scores(self) -> list[CategoryImpactScore]:
        """Calculate impact scores for all categories based on historical data."""
        metas = await self._load_all_release_metas()
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

    async def predict_next_release_impact(self) -> ImpactPrediction:
        """Predict which categories will have the most impact in the next release."""
        scores = await self.calculate_category_impact_scores()
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

    async def generate_impact_prediction_report(self) -> str:
        """Generate a formatted impact prediction report in Markdown."""
        prediction = await self.predict_next_release_impact()

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

    async def triage_release(self, slug: str) -> TriageResult:
        """Analyze a release and generate automated triage with risk assessment."""
        meta = self.load_release_meta(slug)
        if not meta:
            return TriageResult(
                risk_level="desconhecido",
                risk_score=0,
                categories_at_risk=[],
                suggested_actions=["Verificar se a release existe no repositório"],
                priority="baixa",
                summary="Release não encontrada para análise.",
            )

        metrics = await self.calculate_quality_metrics(slug)
        predictions = await self.predict_next_release_impact()

        risk_score = 0
        categories_at_risk: list[str] = []
        suggested_actions: list[str] = []

        if predictions.high_risk_categories:
            risk_score += len(predictions.high_risk_categories) * 10
            categories_at_risk.extend([c.category for c in predictions.high_risk_categories])
            suggested_actions.append(
                f"Monitorar de perto as {len(predictions.high_risk_categories)} categorias de alto risco"
            )

        all_metas = await self._load_all_release_metas()
        all_slugs_by_id = [m.get("slug", "") for m in all_metas]
        if len(all_slugs_by_id) >= 2:
            prev_slugs = [s for s in all_slugs_by_id if s != slug]
            if prev_slugs:
                prev_slug = prev_slugs[-1]
                regressions = await self.detect_regressions(slug, prev_slug)
                if regressions:
                    risk_score += len(regressions) * 15
                    categories_at_risk.extend([r.category for r in regressions])
                    suggested_actions.append(
                        f"Investigar {len(regressions)} categorias com regressão"
                    )

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
                comparison = await self.compare_releases(slug, prev_slug)
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

    async def generate_triage_report(self, slug: str) -> str:
        """Generate a formatted triage report in Markdown."""
        triage = await self.triage_release(slug)

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

    async def analyze_content_changes(self, release_slug: str) -> DeduplicationResult:
        """Analyze content changes in a release directory."""
        release_dir = Path(RELEASES_DIR) / release_slug
        cache_path = release_dir / ".content_cache.json"

        if not release_dir.exists():
            return DeduplicationResult([], [], [], [], 0, 0.0)

        current_hashes: dict[str, ContentHash] = {}
        for f in release_dir.iterdir():
            if f.is_file() and f.suffix == ".md":
                current_hashes[str(f)] = self._calculate_file_hash(f)

        cached_hashes = self._load_content_cache(cache_path)
        unchanged, changed, new, savings = [], [], [], 0

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

        self._save_content_cache(cache_path, current_hashes)

        return DeduplicationResult(
            unchanged_files=unchanged,
            changed_files=changed,
            new_files=new,
            removed_files=removed,
            total_savings_bytes=savings,
            cache_hit_rate=round(hit_rate, 2),
        )

    def _calculate_file_hash(self, file_path: Path) -> ContentHash:
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

    def _load_content_cache(self, cache_path: Path) -> dict[str, ContentHash]:
        """Load content cache from file."""
        if not cache_path.exists():
            return {}
        try:
            data = json.loads(cache_path.read_text(encoding="utf-8"))
            return {k: ContentHash(**v) for k, v in data.items()}
        except json.JSONDecodeError, TypeError:
            return {}

    def _save_content_cache(self, cache_path: Path, cache: dict[str, ContentHash]) -> None:
        """Save content cache to file."""
        data = {k: vars(v) for k, v in cache.items()}
        cache_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    async def get_content_hash(self, file_path: str) -> Optional[str]:
        """Get the MD5 hash of a file's content."""
        path = Path(file_path)
        if not path.exists():
            return None
        content = path.read_bytes()
        return hashlib.md5(content).hexdigest()

    async def is_content_unchanged(self, file_path: str, expected_hash: str) -> bool:
        """Check if a file's content matches the expected hash."""
        current_hash = await self.get_content_hash(file_path)
        return current_hash == expected_hash if current_hash else False

    async def generate_deduplication_report(self, release_slug: str) -> str:
        """Generate a formatted deduplication report in Markdown."""
        result = await self.analyze_content_changes(release_slug)

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

        lines.extend(["---", "*Relatório gerado automaticamente pelo módulo de AI Automation*"])
        return "\n".join(lines)

    async def filter_features_for_profile(
        self, profile_type: str, categories: list[dict[str, Any]]
    ) -> UserProfile:
        """Filter features based on user profile relevance."""
        profile_config = self.USER_PROFILES.get(profile_type, self.USER_PROFILES["business"])

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
        self, slug: str, profile_type: str
    ) -> FilteredNotification:
        """Generate a filtered notification for a specific user profile."""
        meta = self.load_release_meta(slug)
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
        profile = await self.filter_features_for_profile(profile_type, categories)

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

    async def generate_filtered_notification_report(self, slug: str, profile_type: str) -> str:
        """Generate a formatted filtered notification report in Markdown."""
        notification = await self.generate_filtered_notification(slug, profile_type)

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

    async def export_release_json(self, slug: str) -> str:
        """Export release data as formatted JSON."""
        meta = self.load_release_meta(slug)
        return json.dumps(meta if meta else {}, ensure_ascii=False, indent=2)

    async def export_release_csv(self, slug: str) -> str:
        """Export release feature data as CSV."""
        meta = self.load_release_meta(slug)
        if not meta:
            return ""

        lines = ["category,feature,available_users,available_admins,requires_config,contact_sf"]
        release_dir = Path(RELEASES_DIR) / slug

        for cat_info in meta.get("categories", []):
            cat_name = cat_info["name"]
            slug_name = re.sub(r"[^a-z0-9]+", "_", cat_name.lower()).strip("_")
            md_file = release_dir / f"{slug_name}.md"

            if not md_file.exists():
                continue

            content = md_file.read_text(encoding="utf-8")
            for line in content.split("\n"):
                line = line.strip()
                if not line.startswith("|") or line.startswith("| :") or "Recurso" in line:
                    continue
                cells = [c.strip() for c in line.split("|") if c.strip()]
                if len(cells) >= 5:
                    name = cells[0].replace("**", "").replace(" ⚠️", "")
                    users = "Yes" if "✅" in cells[1] else "No"
                    admins = "Yes" if "✅" in cells[2] else "No"
                    config = "Yes" if "✅" in cells[3] else "No"
                    contact = "Yes" if "✅" in cells[4] else "No"
                    lines.append(
                        f"{cat_name.replace(',', ';')},{name.replace(',', ';')},{users},{admins},{config},{contact}"
                    )

        return "\n".join(lines)

    async def export_all_releases(self, output_dir: str = "exports") -> dict[str, list[str]]:
        """Export all releases as both JSON and CSV files."""
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        results: dict[str, list[str]] = {}
        releases_dir = Path(RELEASES_DIR)

        if not releases_dir.exists():
            return results

        for d in sorted(releases_dir.iterdir()):
            if not d.is_dir() or d.name == "exports":
                continue
            if not (d / ".meta.json").exists():
                continue

            json_content = await self.export_release_json(d.name)
            json_path = out / f"{d.name}.json"
            json_path.write_text(json_content, encoding="utf-8")

            csv_content = await self.export_release_csv(d.name)
            csv_path = out / f"{d.name}.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            results[d.name] = [str(json_path), str(csv_path)]

        return results


# ---------------------------------------------------------------------------
# Backward Compatibility Wrappers
# ---------------------------------------------------------------------------


async def load_release_meta(slug: str) -> Optional[dict[str, Any]]:
    return AIAutomationService().load_release_meta(slug)


async def compare_releases(current_slug: str, previous_slug: str) -> ReleaseComparison:
    return await AIAutomationService().compare_releases(current_slug, previous_slug)


async def detect_regressions(current_slug: str, previous_slug: str) -> list[Regression]:
    return await AIAutomationService().detect_regressions(current_slug, previous_slug)


async def calculate_quality_metrics(slug: str) -> Optional[QualityMetrics]:
    return await AIAutomationService().calculate_quality_metrics(slug)


async def generate_changelog() -> str:
    return await AIAutomationService().generate_changelog()


async def generate_regression_report(current_slug: str, previous_slug: str) -> str:
    return await AIAutomationService().generate_regression_report(current_slug, previous_slug)


async def generate_diff_report(current_slug: str, previous_slug: str) -> str:
    return await AIAutomationService().generate_diff_report(current_slug, previous_slug)


async def generate_quality_report() -> str:
    return await AIAutomationService().generate_quality_report()


async def generate_ai_summary(current_slug: str, previous_slug: str) -> AISummary:
    return await AIAutomationService().generate_ai_summary(current_slug, previous_slug)


async def generate_ai_summary_report(current_slug: str, previous_slug: str) -> str:
    return await AIAutomationService().generate_ai_summary_report(current_slug, previous_slug)


async def calculate_category_impact_scores() -> list[CategoryImpactScore]:
    return await AIAutomationService().calculate_category_impact_scores()


async def predict_next_release_impact() -> ImpactPrediction:
    return await AIAutomationService().predict_next_release_impact()


async def generate_impact_prediction_report() -> str:
    return await AIAutomationService().generate_impact_prediction_report()


async def triage_release(slug: str) -> TriageResult:
    return await AIAutomationService().triage_release(slug)


async def generate_triage_report(slug: str) -> str:
    return await AIAutomationService().generate_triage_report(slug)


async def analyze_content_changes(release_slug: str) -> DeduplicationResult:
    return await AIAutomationService().analyze_content_changes(release_slug)


async def get_content_hash(file_path: str) -> Optional[str]:
    return await AIAutomationService().get_content_hash(file_path)


async def is_content_unchanged(file_path: str, expected_hash: str) -> bool:
    return await AIAutomationService().is_content_unchanged(file_path, expected_hash)


async def create_github_issue(
    release_name: str, total_features: int, categories: int
) -> Optional[str]:
    return await AIAutomationService().create_github_issue(release_name, total_features, categories)


async def create_release_issue(
    release_name: str, total_features: int, categories: int
) -> Optional[str]:
    # Currently create_release_issue is an alias for create_github_issue in the context of this pipeline
    return await AIAutomationService().create_github_issue(release_name, total_features, categories)


async def _load_all_release_metas() -> list[dict[str, Any]]:
    return await AIAutomationService()._load_all_release_metas()


async def _load_content_cache(cache_path: Path) -> dict[str, ContentHash]:
    return AIAutomationService()._load_content_cache(cache_path)


async def generate_deduplication_report(release_slug: str) -> str:
    return await AIAutomationService().generate_deduplication_report(release_slug)


async def filter_features_for_profile(
    profile_type: str, categories: list[dict[str, Any]]
) -> UserProfile:
    return await AIAutomationService().filter_features_for_profile(profile_type, categories)


async def generate_filtered_notification(slug: str, profile_type: str) -> FilteredNotification:
    return await AIAutomationService().generate_filtered_notification(slug, profile_type)


async def generate_filtered_notification_report(slug: str, profile_type: str) -> str:
    return await AIAutomationService().generate_filtered_notification_report(slug, profile_type)


async def export_release_json(slug: str) -> str:
    return await AIAutomationService().export_release_json(slug)


async def export_release_csv(slug: str) -> str:
    return await AIAutomationService().export_release_csv(slug)


async def export_all_releases(output_dir: str = "exports") -> dict[str, list[str]]:
    return await AIAutomationService().export_all_releases(output_dir)


def generate_dynamic_badge(release_name: str, total_features: int) -> str:
    return AIAutomationService().generate_dynamic_badge(release_name, total_features)


def get_latest_release_badge() -> str:
    """Get the latest release name for badge display."""
    # This is a small helper that doesn't need to be async for basic use,
    # but to keep AIAutomationService consistent we can implement it there.
    # Since this was a module level func and didn't use LLM/Network, we can keep it simple.
    releases_dir = Path(RELEASES_DIR)
    if not releases_dir.exists():
        return "N/A"
    latest = None
    latest_id = -1
    for d in releases_dir.iterdir():
        meta = AIAutomationService.load_release_meta(d.name)
        if meta and meta.get("release_id", 0) > latest_id:
            latest_id = meta.get("release_id", 0)
            latest = meta.get("name", d.name)
    return latest or "N/A"
