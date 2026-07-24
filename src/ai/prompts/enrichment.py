"""Prompt templates for feature enrichment.

Uses a professional persona with business context to generate
rich, validated descriptions for Salesforce release features.
"""

from __future__ import annotations

from typing import Any

from .validation import EnrichmentOutput

# ---------------------------------------------------------------------------
# Persona & system prompt
# ---------------------------------------------------------------------------

_PERSONA = (
    "Você é um Arquiteto CTA (Certified Technical Architect) da Salesforce "
    "com 10 anos de experiência em implementações enterprise. "
    "Sua expertise abrange Sales Cloud, Service Cloud, Marketing Cloud, "
    "Platform, Einstein AI, Flow, Apex, LWC, e integrações com MuleSoft."
)

_SYSTEM_TEMPLATE = (
    "{persona}\n\n"
    "Sua tarefa é enriquecer as release notes do Salesforce com descrições "
    "profissionais, análises de impacto e contexto de negócio.\n\n"
    "Você DEVE responder com um JSON válido (sem markdown, sem code fences) "
    "com esta estrutura exata:\n"
    "{{\n"
    '  "introduction": "visão geral de 2-3 frases sobre o tema da categoria e as mudanças mais importantes",\n'
    '  "features": [\n'
    "    {{\n"
    '      "name": "nome exato do feature como fornecido",\n'
    '      "description": "descrição profissional de 1-2 frases explicando o que o feature faz e por que importa",\n'
    '      "impact": "alto|médio|baixo",\n'
    '      "audience": "usuários|admins|ambos",\n'
    '      "use_cases": ["caso de uso 1", "caso de uso 2"],\n'
    '      "risks": ["risco ou consideração 1"],\n'
    '      "code_example": "exemplo opcional de configuração ou código"\n'
    "    }}\n"
    "  ]\n"
    "}}\n\n"
    "Diretrizes:\n"
    "- 'alto' = features que mudam fluxos de trabalho, habilitam novas capacidades, "
    "ou têm impacto em compliance/segurança\n"
    "- 'médio' = melhorias úteis que aprimoram funcionalidades existentes\n"
    "- 'baixo' = ajustes menores, mudanças de UI, ou features de nicho\n"
    "- 'usuários' = features voltados a usuários finais\n"
    "- 'admins' = features voltados a administradores/developadores\n"
    "- 'ambos' = relevante para ambos os públicos\n"
    "- Descrições devem explicar o valor de negócio, não apenas repetir o nome\n"
    "- Escreva em Português Brasileiro (pt-BR)\n"
    "- Seja conciso mas informativo\n"
    "- use_cases: 2-3 exemplos práticos de como usar o feature\n"
    "- risks: riscos potenciais, dependências, ou considerações de migração\n"
    "- code_example: quando aplicável, forneça exemplo de Apex, SOQL, ou configuração\n"
    "- TODO feature na entrada DEVE aparecer na saída, na mesma ordem"
)


def build_enrichment_system_prompt() -> str:
    """Build the system prompt for enrichment with the CTA persona.

    Returns:
        Complete system prompt string.
    """
    return _SYSTEM_TEMPLATE.format(persona=_PERSONA)


def build_enrichment_user_prompt(
    release_name: str,
    category_name: str,
    features_text: str,
    release_context: str = "",
) -> str:
    """Build the user prompt for enriching a category.

    Args:
        release_name: Release name (e.g. "Summer '26").
        category_name: Category name (e.g. "Agentforce").
        features_text: Pre-formatted feature list.
        release_context: Additional release context.

    Returns:
        Complete user prompt string.
    """
    parts = [f"Release: {release_name}", f"Categoria: {category_name}"]
    if release_context:
        parts.append(f"Contexto: {release_context}")
    parts.append(f"\nFeatures para enriquecer:\n{features_text}")
    return "\n".join(parts)


def build_release_context(
    release_name: str,
    total_features: int,
    categories: list[dict[str, Any]],
) -> str:
    """Build a context string from release metadata.

    Args:
        release_name: Human-readable release name.
        total_features: Total number of features.
        categories: List of category dicts with 'name' key.

    Returns:
        Context string for the prompt.
    """
    cat_names = ", ".join(c.get("name", "") for c in categories[:10])
    return (
        f"Release {release_name} com {total_features} recursos "
        f"em {len(categories)} categorias. Categorias: {cat_names}"
    )


def parse_enrichment_response(response: str) -> EnrichmentOutput | None:
    """Parse and validate an LLM enrichment response.

    Args:
        response: Raw LLM response string.

    Returns:
        Validated EnrichmentOutput or None if parsing fails.
    """
    import json
    import re

    try:
        clean = response.strip()
        if clean.startswith("```"):
            clean = re.sub(r"^```(?:json)?\s*", "", clean)
            clean = re.sub(r"\s*```$", "", clean)

        data = json.loads(clean)
        return EnrichmentOutput.model_validate(data)
    except Exception:
        return None
