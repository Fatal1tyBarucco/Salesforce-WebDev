"""Prompt templates para desambiguação LLM no SFEL.

Usado pelo FeatureLinker quando o passo LLM está ativado e uma pair de
features tem similaridade Jaccard entre LLM_THRESHOLD_LOW e FUZZY_THRESHOLD.
"""

from __future__ import annotations

_PERSONA = (
    "Você é um Arquiteto de Software sênior especialista em Salesforce. "
    "Sua tarefa é determinar se duas features de releases diferentes são "
    "na verdade a mesma funcionalidade (com nome ou categoria levemente "
    "diferente) ou se são recursos distintos."
)

_DISAMBIGUATION_TEMPLATE = (
    "{persona}\n\n"
    "Determine se estas duas features de releases diferentes da Salesforce "
    "são a mesma funcionalidade ou recursos distintos.\n\n"
    "Feature da release anterior ({previous_slug}):\n"
    "  Nome: {prev_name}\n"
    "  Categoria: {prev_category}\n"
    "  Trecho: {prev_snippet}\n\n"
    "Feature da release atual ({current_slug}):\n"
    "  Nome: {curr_name}\n"
    "  Categoria: {curr_category}\n"
    "  Trecho: {curr_snippet}\n\n"
    "Retorne APENAS um JSON válido (sem markdown, sem code fences) com "
    "esta estrutura exata:\n"
    "{{\n"
    '  "same_feature": true|false,\n'
    '  "confidence": 0.0-1.0,\n'
    '  "reasoning": "explicação em 1 frase em Português Brasileiro (pt-BR)"\n'
    "}}\n"
)


def build_disambiguation_prompt(
    prev_name: str,
    prev_category: str,
    prev_snippet: str,
    curr_name: str,
    curr_category: str,
    curr_snippet: str,
    previous_slug: str,
    current_slug: str,
) -> str:
    """Constrói o prompt de desambiguação para o LLM.

    Args:
        prev_name: Nome da feature na release anterior.
        prev_category: Categoria da feature na release anterior.
        prev_snippet: Trecho do markdown da feature anterior.
        curr_name: Nome da feature na release atual.
        curr_category: Categoria da feature na release atual.
        curr_snippet: Trecho do markdown da feature atual.
        previous_slug: Slug da release anterior.
        current_slug: Slug da release atual.

    Returns:
        Prompt pronto para envio ao LLM.
    """
    return _DISAMBIGUATION_TEMPLATE.format(
        persona=_PERSONA,
        previous_slug=previous_slug,
        current_slug=current_slug,
        prev_name=prev_name,
        prev_category=prev_category,
        prev_snippet=prev_snippet[:300],
        curr_name=curr_name,
        curr_category=curr_category,
        curr_snippet=curr_snippet[:300],
    )
