"""AI-powered release summarizer.

Generates comprehensive executive summaries from release notes files
using LLM analysis.  Produces structured reports with business impact
analysis, strategic themes, and category-level breakdowns.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .config import RELEASES_DIR
from .llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass
class CategoryHighlight:
    """Highlight for a single category within a release summary."""

    name: str
    feature_count: int
    percentage: float
    top_feature: str = ""
    theme: str = ""


@dataclass
class ReleaseSummary:
    """Comprehensive generated summary for a release."""

    release_slug: str
    release_name: str
    total_features: int
    total_categories: int
    executive_summary: str  # 3-5 sentence overview
    business_impact: str  # Paragraph on business value
    strategic_themes: list[str]  # Key themes (AI-first, compliance, etc.)
    top_categories: list[CategoryHighlight]
    migration_notes: str  # Important migration/upgrade considerations
    confidence: float


class ReleaseSummarizer:
    """Generates executive summaries from release markdown files using LLM.

    Produces comprehensive, professional-grade summaries that analyze actual
    feature content — not just metadata counts.
    """

    def __init__(self, base_dir: str = RELEASES_DIR, llm: LLMService | None = None) -> None:
        self._base_dir = Path(base_dir)
        self._llm = llm or LLMService()

    async def summarize(self, release_slug: str) -> ReleaseSummary | None:
        """Generate a comprehensive summary for a release.

        Args:
            release_slug: The release directory name (e.g., 'summer_26').

        Returns:
            ReleaseSummary or None if release not found.
        """
        release_dir = self._base_dir / release_slug
        if not release_dir.is_dir():
            return None

        meta = self._load_meta(release_dir)
        content_fragments: list[str] = []
        category_counts: dict[str, int] = {}
        category_features: dict[str, list[str]] = {}

        # Look for .md files in pt_BR subdirectory
        pt_br_dir = release_dir / "pt_BR"
        if pt_br_dir.is_dir():
            for md_file in sorted(pt_br_dir.glob("*.md")):
                if md_file.name.startswith("."):
                    continue
                content = md_file.read_text(encoding="utf-8")

                category_name = self._extract_category_name(content, md_file.stem)
                features = self._extract_feature_names(content)
                count = len(features)
                category_counts[category_name] = count
                category_features[category_name] = features[:10]  # Top 10 for context

                # Send more content to the LLM (up to 4000 chars per category)
                content_fragments.append(
                    f"=== {category_name} ({count} recursos) ===\n{content[:4000]}"
                )

        if not content_fragments:
            return None

        total_features = sum(category_counts.values())
        total_categories = len(category_counts)

        # Build comprehensive prompt
        full_content = "\n\n".join(content_fragments)
        release_name = meta.get("name", release_slug)

        system_prompt = (
            "You are a senior Salesforce ecosystem analyst and technical writer. "
            "You will receive the full content of a Salesforce release organized by category.\n\n"
            "Generate a JSON response with these fields:\n"
            "{\n"
            '  "executive_summary": "3-5 sentence executive overview of the release. '
            "Cover the scale (number of features/categories), the primary focus areas, "
            'and what this release means for Salesforce customers.",\n'
            '  "business_impact": "A paragraph explaining the business value. '
            "How do these changes help companies sell more, serve better, operate efficiently, "
            'or comply with regulations? Be specific with examples from the actual features.",\n'
            '  "strategic_themes": ["theme1", "theme2", "theme3"], '
            '  "top_categories": [\n'
            "    {\n"
            '      "name": "Category Name",\n'
            '      "feature_count": 47,\n'
            '      "percentage": 3.4,\n'
            '      "top_feature": "Most impactful feature name",\n'
            '      "theme": "Brief theme description"\n'
            "    }\n"
            "  ],\n"
            '  "migration_notes": "Important migration considerations, deprecated features, '
            'or breaking changes that administrators should be aware of.",\n'
            "}\n\n"
            "Rules:\n"
            "- Write in Brazilian Portuguese (pt-BR)\n"
            "- Be specific — reference actual feature names from the content\n"
            "- 'strategic_themes' should be 3-5 broad themes (e.g., 'AI-First', "
            "'Developer Experience', 'Compliance & Security')\n"
            "- 'top_categories' should list the 5 most important categories\n"
            "- If no migration concerns exist, say 'Nenhuma nota de migração significativa.'\n"
            "- Output ONLY valid JSON, no markdown fences"
        )

        user_prompt = (
            f"Release: {release_name} ({release_slug})\n"
            f"Total: {total_features} recursos em {total_categories} categorias\n\n"
            f"Content by category:\n\n{full_content}"
        )

        result = await self._llm.generate_text(user_prompt, system_prompt)

        if result:
            parsed = self._parse_llm_response(result, release_slug, release_name, meta)
            if parsed:
                return parsed

        # Fallback: generate summary from metadata
        return self._generate_fallback_summary(
            release_slug, release_name, meta, category_counts, category_features
        )

    def _parse_llm_response(
        self,
        response: str,
        release_slug: str,
        release_name: str,
        meta: dict[str, Any],
    ) -> ReleaseSummary | None:
        """Parse the LLM JSON response into a ReleaseSummary."""
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = re.sub(r"^```(?:json)?\s*", "", clean)
                clean = re.sub(r"\s*```$", "", clean)

            data = json.loads(clean)

            # Parse top categories
            top_cats: list[CategoryHighlight] = []
            for cat_data in data.get("top_categories", [])[:5]:
                top_cats.append(
                    CategoryHighlight(
                        name=cat_data.get("name", ""),
                        feature_count=cat_data.get("feature_count", 0),
                        percentage=cat_data.get("percentage", 0.0),
                        top_feature=cat_data.get("top_feature", ""),
                        theme=cat_data.get("theme", ""),
                    )
                )

            total = meta.get("total_features", 0)
            cats = meta.get("categories", [])

            return ReleaseSummary(
                release_slug=release_slug,
                release_name=release_name,
                total_features=total,
                total_categories=len(cats),
                executive_summary=data.get("executive_summary", ""),
                business_impact=data.get("business_impact", ""),
                strategic_themes=data.get("strategic_themes", []),
                top_categories=top_cats,
                migration_notes=data.get("migration_notes", ""),
                confidence=0.95,
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning("Failed to parse LLM summary response: %s", e)
            return None

    def _generate_fallback_summary(
        self,
        release_slug: str,
        release_name: str,
        meta: dict[str, Any],
        category_counts: dict[str, int],
        category_features: dict[str, list[str]],
    ) -> ReleaseSummary:
        """Generate a comprehensive fallback summary without LLM."""
        total = sum(category_counts.values())
        top_cats_sorted = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

        # Build executive summary
        top_3_names = [c[0] for c in top_cats_sorted[:3]]
        trend = (
            "expansão significativa"
            if total > 1000
            else "atualização substancial" if total > 500 else "atualização focada"
        )

        executive_summary = (
            f"A release {release_name} representa uma {trend} do ecossistema Salesforce "
            f"com **{total} novos recursos** distribuídos em **{len(category_counts)} categorias**. "
            f"As áreas com maior volume de inovação são {', '.join(top_3_names[:2])} "
            f"e {top_3_names[2] if len(top_3_names) > 2 else 'outras categorias'}. "
            f"Esta release consolida investimentos em inteligência artificial, "
            f"experiência do desenvolvedor e conformidade regulatória."
        )

        # Build business impact
        themes = self._extract_themes(
            "\n".join(f"{k}: {v} features" for k, v in category_counts.items())
        )
        business_impact = (
            f"Para as empresas, {release_name} entrega valor em múltiplas frentes. "
            f"A automação avançada reduz tarefas manuais, enquanto as melhorias em "
            f"experiência do usuário aumentam a adoção. "
            f"As {total} novas capacidades habilitam cenários que antes exigiam "
            f"customização significativa, reduzindo o custo total de propriedade."
        )

        # Build top categories
        top_cats: list[CategoryHighlight] = []
        for name, count in top_cats_sorted[:5]:
            pct = (count / total * 100) if total > 0 else 0
            features = category_features.get(name, [])
            top_cats.append(
                CategoryHighlight(
                    name=name,
                    feature_count=count,
                    percentage=round(pct, 1),
                    top_feature=features[0] if features else "",
                    theme=f"{count} novos recursos",
                )
            )

        return ReleaseSummary(
            release_slug=release_slug,
            release_name=release_name,
            total_features=total,
            total_categories=len(category_counts),
            executive_summary=executive_summary,
            business_impact=business_impact,
            strategic_themes=themes[:5] if themes else ["Atualização Geral"],
            top_categories=top_cats,
            migration_notes="Nenhuma nota de migração significativa.",
            confidence=0.7,
        )

    def _load_meta(self, release_dir: Path) -> dict[str, Any]:
        """Load .meta.json if it exists."""
        meta_file = release_dir / ".meta.json"
        if meta_file.exists():
            try:
                return cast(dict[str, Any], json.loads(meta_file.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Não foi possível ler .meta.json: %s", e)
        return {}

    @staticmethod
    def _extract_category_name(content: str, fallback: str) -> str:
        """Extract category name from markdown heading."""
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("## ") and not line.startswith("## 🔗"):
                return line[3:].strip()
            if line.startswith("# ") and "Release" not in line:
                return line[2:].strip()
        return fallback.replace("_", " ").title()

    @staticmethod
    def _extract_feature_names(content: str) -> list[str]:
        """Extract feature names from markdown table."""
        features: list[str] = []
        in_table = False

        for line in content.split("\n"):
            stripped = line.strip()

            if stripped.startswith("| Recurso") or stripped.startswith("| Feature"):
                in_table = True
                continue

            if in_table and stripped.startswith("| :---"):
                continue

            if in_table and not stripped.startswith("|"):
                in_table = False
                continue

            if in_table and stripped.startswith("|"):
                cells = [c.strip() for c in stripped.split("|") if c.strip()]
                if cells:
                    name = cells[0].replace("**", "").replace(" ⚠️", "").strip()
                    if name and not name.startswith(":"):
                        features.append(name)

        return features

    @staticmethod
    def _extract_themes(content: str) -> list[str]:
        """Extract key themes from content using keyword analysis."""
        theme_keywords = {
            "AI & Agentforce": ["ai", "agentforce", "einstein", "machine learning", "ml"],
            "Segurança & Compliance": [
                "security",
                "compliance",
                "mfa",
                "encryption",
                "audit",
                "lgpd",
                "gdpr",
            ],
            "Developer Experience": ["api", "apex", "lwc", "developer", "vs code", "cli"],
            "Data & Analytics": ["data", "analytics", "tableau", "dashboard", "report"],
            "Automação & Workflow": ["automation", "flow", "workflow", "process", "orchestrator"],
            "Experiência do Usuário": ["ui", "ux", "mobile", "lightning", "experience"],
            "Integração": ["integration", "connector", "muleoft", "api", "rest"],
        }

        content_lower = content.lower()
        found: list[str] = []

        for theme, keywords in theme_keywords.items():
            if any(kw in content_lower for kw in keywords):
                found.append(theme)

        return found

    def to_markdown(self, summary: ReleaseSummary) -> str:
        """Render a ReleaseSummary as a formatted Markdown document."""
        lines = [
            f"# 📋 Resumo Executivo — {summary.release_name}",
            "",
            f"> **{summary.total_features} recursos** em **{summary.total_categories} categorias** "
            f"| Confiança: {summary.confidence:.0%}",
            "",
            "---",
            "",
            "## 🎯 Visão Geral",
            "",
            summary.executive_summary,
            "",
            "## 💼 Impacto para o Negócio",
            "",
            summary.business_impact,
            "",
            "## 🏗️ Temas Estratégicos",
            "",
        ]

        for i, theme in enumerate(summary.strategic_themes, 1):
            lines.append(f"{i}. **{theme}**")

        lines.extend(["", "## 📊 Categorias de Destaque", ""])

        for cat in summary.top_categories:
            pct_str = f"{cat.percentage:.1f}%" if cat.percentage else ""
            lines.append(f"### {cat.name}")
            lines.append(f"- **{cat.feature_count} recursos** ({pct_str})")
            if cat.top_feature:
                lines.append(f"- Destaque: *{cat.top_feature}*")
            if cat.theme:
                lines.append(f"- Tema: {cat.theme}")
            lines.append("")

        lines.extend(
            [
                "## ⚠️ Notas de Migração",
                "",
                summary.migration_notes,
                "",
                "---",
                "*Resumo gerado automaticamente pelo módulo de AI Release Summarizer*",
            ]
        )

        return "\n".join(lines)
