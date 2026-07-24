"""Prompt templates for report generation with storytelling.

Uses a CTO persona to create engaging, stakeholder-ready reports
with headlines, highlights, risks, and actionable recommendations.
"""

from __future__ import annotations

import json
import re
from typing import Any

from .validation import ReportOutput

# ---------------------------------------------------------------------------
# Persona & system prompt
# ---------------------------------------------------------------------------

_PERSONA = (
    "Você é um Diretor de Tecnologia (CTO) apresentando para stakeholders "
    "de negócios. Sua comunicação é clara, inspiradora e orientada a dados. "
    "Você transforma dados técnicos em narrativas que executivos entendem "
    "e valorizam."
)

_SYSTEM_TEMPLATE = (
    "{persona}\n\n"
    "Sua tarefa é criar relatórios de release do Salesforce com storytelling "
    "profissional que engaje stakeholders e direcione a tomada de decisão.\n\n"
    "Você DEVE responder com um JSON válido (sem markdown, sem code fences) "
    "com esta estrutura exata:\n"
    "{{\n"
    '  "headline": "headline chamativa e inspiradora (máx 200 chars)",\n'
    '  "highlights": ["destaque 1", "destaque 2", "destaque 3"],\n'
    '  "risk_areas": ["risco 1", "risco 2"],\n'
    '  "recommendation": "1 recomendação acionável e específica",\n'
    '  "trend": "crescimento|estável|declínio"\n'
    "}}\n\n"
    "Diretrizes de storytelling:\n"
    "- Headline: frase impactante que resume o momento (use emojis quando apropriado)\n"
    "- Highlights: 3 destaques que mostram progresso e oportunidades\n"
    "- Risk Areas: 2 riscos que merecem atenção da liderança\n"
    "- Recommendation: 1 ação concreta que o time deve tomar\n"
    "- Trend: direção geral baseada nos dados\n"
    "- Use linguagem inspiradora mas profissional\n"
    "- Emojis são bem-vindos para tornar o relatório visual\n"
    "- Escreva em Português Brasileiro (pt-BR)\n"
    "- Foque em valor de negócio, não em detalhes técnicos"
)


def build_reporting_system_prompt() -> str:
    """Build the system prompt for report generation with the CTO persona.

    Returns:
        Complete system prompt string.
    """
    return _SYSTEM_TEMPLATE.format(persona=_PERSONA)


def build_changelog_prompt(release_metas: list[dict[str, str | int | list[dict[str, str | int]]]]) -> str:
    """Build prompt for CHANGELOG generation.

    Args:
        release_metas: List of release metadata dicts.

    Returns:
        Complete user prompt string.
    """
    return (
        "Gere um CHANGELOG.md profissional baseado nos metadados das releases abaixo.\n"
        "Use ## para releases e bullet points para categorias.\n"
        "Foque em tendências de alto nível e volume de features.\n\n"
        f"Metadados: {json.dumps(release_metas)}"
    )


def build_regression_report_prompt(
    comparison_data: dict[str, Any],
    regressions_data: list[dict[str, Any]],
) -> str:
    """Build prompt for regression report generation.

    Args:
        comparison_data: Comparison dict.
        regressions_data: List of regression dicts.

    Returns:
        Complete user prompt string.
    """
    return (
        "Analise a comparação de releases e as regressões detectadas. "
        "Gere um relatório detalhado em Markdown explicando o impacto "
        "das regressões e destacando categorias novas ou removidas.\n\n"
        f"Comparação: {json.dumps(comparison_data)}\n"
        f"Regressões: {json.dumps(regressions_data)}"
    )


def build_diff_report_prompt(diff_data: list[dict[str, int | str]]) -> str:
    """Build prompt for diff report generation.

    Args:
        diff_data: List of category diff dicts.

    Returns:
        Complete user prompt string.
    """
    return (
        "Analise o diff lado a lado de contagem de features entre duas releases. "
        "Gere um relatório Markdown com tabela de resumo e análise inteligente "
        "das mudanças mais significativas.\n\n"
        f"Dados do Diff: {json.dumps(diff_data)}"
    )


def build_ai_summary_prompt(analysis_data: dict[str, Any]) -> str:
    """Build prompt for AI summary generation.

    Args:
        analysis_data: Combined analysis data dict.

    Returns:
        Complete user prompt string.
    """
    return (
        "Analise os dados de comparação de releases abaixo e gere um resumo "
        "executivo com headline, destaques, áreas de risco e tendência geral.\n\n"
        f"Dados: {json.dumps(analysis_data)}"
    )


def build_impact_prediction_prompt(
    scores_data: list[dict[str, Any]],
    historical_summary: str,
) -> str:
    """Build prompt for impact prediction with context.

    Args:
        scores_data: Category impact scores.
        historical_summary: Summary of historical trends.

    Returns:
        Complete user prompt string.
    """
    return (
        "Com base nos scores de impacto por categoria e no histórico, "
        "preveja quais categorias terão maior impacto na próxima release. "
        "Inclua sugestões de preparação para os times.\n\n"
        f"Scores de Impacto: {json.dumps(scores_data)}\n"
        f"Histórico: {historical_summary}"
    )


def parse_report_response(response: str) -> ReportOutput | None:
    """Parse and validate an LLM report response.

    Args:
        response: Raw LLM response string.

    Returns:
        Validated ReportOutput or None if parsing fails.
    """
    try:
        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)

        data = json.loads(clean)
        return ReportOutput.model_validate(data)
    except Exception:
        return None
