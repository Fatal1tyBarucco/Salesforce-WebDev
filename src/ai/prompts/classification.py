"""Prompt templates for feature classification.

Uses a security and architecture analyst persona to classify
Salesforce release features with business context and justification.
"""

from __future__ import annotations

import json
import re

from .validation import ClassificationOutput

# ---------------------------------------------------------------------------
# Persona & system prompt
# ---------------------------------------------------------------------------

_PERSONA = (
    "Você é um Analista de Segurança e Arquitetura Salesforce sênior "
    "com 8 anos de experiência em reviews de segurança, análise de impacto "
    "arquitetural e governança de plataformas CRM enterprise."
)

_SYSTEM_TEMPLATE = (
    "{persona}\n\n"
    "Sua tarefa é classificar features do Salesforce Release Notes "
    "fornecendo análise técnica e de negócio detalhada.\n\n"
    "Você DEVE responder com um JSON válido (sem markdown, sem code fences) "
    "com esta estrutura exata:\n"
    "{{\n"
    '  "type": "security|performance|bug_fix|new_feature|improvement|'
    'deprecation|breaking_change|integration|ui_ux|other",\n'
    '  "impact": "alto|médio|baixo",\n'
    '  "audience": "usuários|admins|ambos",\n'
    '  "priority": "crítica|importante|opcional",\n'
    '  "justification": "justificativa em 1 frase para a classificação"\n'
    "}}\n\n"
    "Diretrizes de classificação:\n\n"
    "**Tipo:**\n"
    "- security: vulnerabilidades, patches, MFA, cript auditoria, compliance\n"
    "- performance: otimização de queries, cache, latência, throughput\n"
    "- bug_fix: correção de bugs conhecidos, hotfixes\n"
    "- new_feature: funcionalidades novas, GA de features em beta\n"
    "- improvement: melhorias em funcionalidades existentes\n"
    "- deprecation: features sendo descontinuados\n"
    "- breaking_change: mudanças que quebram backward compatibility\n"
    "- integration: APIs, conectores, MuleSoft, integrações externas\n"
    "- ui_ux: mudanças de interface, design, acessibilidade\n"
    "- other: não se encaixa em nenhuma categoria acima\n\n"
    "**Impacto:**\n"
    "- alto: muda fluxos de trabalho críticos, compliance, segurança\n"
    "- médio: melhoria significativa mas não quebra nada\n"
    "- baixo: ajuste menor, visual, ou nicho\n\n"
    "**Prioridade de adoção:**\n"
    "- crítica: deve ser adotada imediatamente (segurança, breaking changes)\n"
    "- importante: adotar no próximo ciclo de desenvolvimento\n"
    "- opcional: adotar quando conveniente\n\n"
    "**Justificativa:**\n"
    "- Máximo 1 frase explicando o raciocínio da classificação\n"
    "- Deve referenciar o impacto técnico ou de negócio\n\n"
    "- Escreva em Português Brasileiro (pt-BR)"
)


def build_classification_system_prompt() -> str:
    """Build the system prompt for classification with the analyst persona.

    Returns:
        Complete system prompt string.
    """
    return _SYSTEM_TEMPLATE.format(persona=_PERSONA)


def build_classification_user_prompt(
    feature_name: str,
    feature_description: str = "",
    release_name: str = "",
    category_name: str = "",
) -> str:
    """Build the user prompt for classifying a feature.

    Args:
        feature_name: Feature name.
        feature_description: Optional feature description.
        release_name: Optional release name for context.
        category_name: Optional category name for context.

    Returns:
        Complete user prompt string.
    """
    parts = [f"Feature: {feature_name}"]
    if feature_description:
        parts.append(f"Descrição: {feature_description}")
    if release_name:
        parts.append(f"Release: {release_name}")
    if category_name:
        parts.append(f"Categoria: {category_name}")
    return "\n".join(parts)


def parse_classification_response(response: str) -> ClassificationOutput | None:
    """Parse and validate an LLM classification response.

    Args:
        response: Raw LLM response string.

    Returns:
        Validated ClassificationOutput or None if parsing fails.
    """
    try:
        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)

        data = json.loads(clean)
        return ClassificationOutput.model_validate(data)
    except Exception:
        return None
