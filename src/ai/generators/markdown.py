"""Visual Markdown generator with impact indicators, badges, and ASCII charts.

Produces rich, stakeholder-ready Markdown with emoji indicators,
dynamic tables, and visual trend representations.
"""

from __future__ import annotations

from ..prompts.validation import EnrichmentOutput, ImpactPredictionOutput, ReportOutput

# ---------------------------------------------------------------------------
# Impact emoji mapping
# ---------------------------------------------------------------------------

_IMPACT_EMOJI: dict[str, str] = {
    "alto": "🔴",
    "médio": "🟡",
    "baixo": "🟢",
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}

_PRIORITY_EMOJI: dict[str, str] = {
    "crítica": "🚨",
    "importante": "⚡",
    "opcional": "💡",
    "critica": "🚨",
}

_TYPE_BADGE: dict[str, str] = {
    "security": "🔒 Segurança",
    "performance": "⚡ Performance",
    "bug_fix": "🐛 Bug Fix",
    "new_feature": "✨ Novo Feature",
    "improvement": "📈 Melhoria",
    "deprecation": "⚠️ Depreciação",
    "breaking_change": "💥 Breaking Change",
    "integration": "🔗 Integração",
    "ui_ux": "🎨 UI/UX",
    "other": "📋 Outro",
}


class MarkdownGenerator:
    """Generates visual Markdown content for reports and dashboards."""

    # ------------------------------------------------------------------
    # Impact tables
    # ------------------------------------------------------------------

    @staticmethod
    def impact_table(features: list[dict[str, str]]) -> str:
        """Generate a Markdown table with impact emoji indicators.

        Args:
            features: List of dicts with 'name', 'description', 'impact', 'audience'.

        Returns:
            Formatted Markdown table string.
        """
        if not features:
            return "_Nenhum feature para exibir._\n"

        lines = [
            "| Feature | Descrição | Impacto | Público |",
            "| :--- | :--- | :---: | :--- |",
        ]

        for f in features:
            impact = f.get("impact", "baixo")
            emoji = _IMPACT_EMOJI.get(impact, "⚪")
            name = f.get("name", "?")
            desc = f.get("description", "")
            if len(desc) > 100:
                desc = desc[:97] + "…"
            audience = f.get("audience", "")
            lines.append(f"| **{name}** | {desc} | {emoji} {impact} | {audience} |")

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # Impact distribution
    # ------------------------------------------------------------------

    @staticmethod
    def impact_distribution(high: int, medium: int, low: int) -> str:
        """Generate a visual impact distribution bar.

        Args:
            high: Count of high-impact features.
            medium: Count of medium-impact features.
            low: Count of low-impact features.

        Returns:
            Visual distribution string.
        """
        total = high + medium + low
        if total == 0:
            return "_Sem dados de impacto._\n"

        h_bar = "🔴" * min(high, 20)
        m_bar = "🟡" * min(medium, 20)
        l_bar = "🟢" * min(low, 20)

        lines = [
            "### 📊 Distribuição de Impacto\n",
            f"🔴 Alto: **{high}** ({high * 100 // total}%) {h_bar}",
            f"🟡 Médio: **{medium}** ({medium * 100 // total}%) {m_bar}",
            f"🟢 Baixo: **{low}** ({low * 100 // total}%) {l_bar}",
            f"\n**Total: {total} features**\n",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Inline badges
    # ------------------------------------------------------------------

    @staticmethod
    def type_badge(feature_type: str) -> str:
        """Get an inline badge for a feature type.

        Args:
            feature_type: Feature type string.

        Returns:
            Badge string.
        """
        return _TYPE_BADGE.get(feature_type, f"📋 {feature_type}")

    @staticmethod
    def impact_badge(impact: str) -> str:
        """Get an inline badge for an impact level.

        Args:
            impact: Impact level string.

        Returns:
            Badge string with emoji.
        """
        emoji = _IMPACT_EMOJI.get(impact, "⚪")
        return f"{emoji} {impact}"

    @staticmethod
    def priority_badge(priority: str) -> str:
        """Get an inline badge for an adoption priority.

        Args:
            priority: Priority string.

        Returns:
            Badge string with emoji.
        """
        emoji = _PRIORITY_EMOJI.get(priority, "💡")
        return f"{emoji} {priority}"

    # ------------------------------------------------------------------
    # ASCII charts for trends
    # ------------------------------------------------------------------

    @staticmethod
    def trend_chart(
        data: dict[str, list[int]],
        title: str = "Tendência por Categoria",
    ) -> str:
        """Generate an ASCII bar chart for category trends.

        Args:
            data: Dict mapping category names to lists of counts.
            title: Chart title.

        Returns:
            ASCII chart string.
        """
        if not data:
            return "_Sem dados para gráfico._\n"

        max_val = max(max(vals) for vals in data.values() if vals) or 1
        bar_width = 30

        lines = [f"### {title}\n", "```"]

        for cat, vals in sorted(data.items()):
            if not vals:
                continue
            latest = vals[-1]
            bar_len = int((latest / max_val) * bar_width)
            bar = "█" * bar_len + "░" * (bar_width - bar_len)

            # Trend arrow
            if len(vals) >= 2:
                diff = vals[-1] - vals[-2]
                arrow = "↗" if diff > 0 else ("↘" if diff < 0 else "→")
            else:
                arrow = "→"

            lines.append(f"{cat[:20]:<20} │{bar}│ {latest:>4} {arrow}")

        lines.append("```\n")
        return "\n".join(lines)

    @staticmethod
    def sparkline(values: list[int]) -> str:
        """Generate a simple sparkline from values.

        Args:
            values: List of integer values.

        Returns:
            Sparkline string using Unicode block characters.
        """
        if not values:
            return ""

        blocks = " ▁▂▃▄▅▆▇█"
        max_val = max(values) or 1
        return "".join(blocks[min(int(v * 8 / max_val), 8)] for v in values)

    # ------------------------------------------------------------------
    # Full report sections
    # ------------------------------------------------------------------

    @classmethod
    def enrichment_summary(cls, enrichment: EnrichmentOutput) -> str:
        """Generate a formatted enrichment summary.

        Args:
            enrichment: Validated enrichment output.

        Returns:
            Markdown summary string.
        """
        lines = [f"{enrichment.introduction}\n"]

        features_dict = [
            {
                "name": f.name,
                "description": f.description,
                "impact": f.impact,
                "audience": f.audience,
            }
            for f in enrichment.features
        ]
        lines.append(cls.impact_table(features_dict))

        high = sum(1 for f in enrichment.features if f.impact == "alto")
        medium = sum(1 for f in enrichment.features if f.impact == "médio")
        low = sum(1 for f in enrichment.features if f.impact == "baixo")
        lines.append(cls.impact_distribution(high, medium, low))

        return "\n".join(lines)

    @classmethod
    def report_section(cls, report: ReportOutput) -> str:
        """Generate a formatted report section.

        Args:
            report: Validated report output.

        Returns:
            Markdown report section.
        """
        lines = [
            f"## {report.headline}\n",
            "### 📈 Destaques\n",
        ]
        for h in report.highlights:
            lines.append(f"- ✨ {h}")

        lines.append("\n### ⚠️ Áreas de Risco\n")
        for r in report.risk_areas:
            lines.append(f"- 🔸 {r}")

        lines.append(f"\n### 💡 Recomendação\n{report.recommendation}\n")
        trend_emoji = {"crescimento": "📈", "estável": "➡️", "declínio": "📉"}.get(
            report.trend, "➡️"
        )
        lines.append(f"### 📊 Tendência: {trend_emoji} **{report.trend.upper()}**\n")

        return "\n".join(lines)

    @classmethod
    def prediction_section(cls, prediction: ImpactPredictionOutput) -> str:
        """Generate a formatted impact prediction section.

        Args:
            prediction: Validated prediction output.

        Returns:
            Markdown prediction section.
        """
        risk_emoji = {"alto": "🔴", "moderado": "🟡", "baixo": "🟢"}.get(
            prediction.risk_level, "⚪"
        )
        lines = [
            f"### Nível de Risco: {risk_emoji} **{prediction.risk_level.upper()}**\n",
            "#### 🎯 Categorias com Maior Impacto Previsto\n",
        ]

        for cat, pred in zip(prediction.categories, prediction.predictions):
            lines.append(f"- **{cat}**: {pred}")

        if prediction.preparation_suggestions:
            lines.append("\n#### 🛠️ Sugestões de Preparação\n")
            for suggestion in prediction.preparation_suggestions:
                lines.append(f"- {suggestion}")

        return "\n".join(lines)
