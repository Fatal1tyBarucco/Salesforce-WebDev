---
name: prompt-eval
description: Avaliar prompts versionados (promptfoo): criar casos de teste, rodar eval, gate no CI, versionar prompts em prompts/.
---

# Skill: prompt-eval

## Quando Usar
- Novo prompt para LLM (classificação, enriquecimento, sumarização, tradução)
- Mudança em prompt existente (regressão)
- Comparar provedores/modelos para mesmo prompt
- Gate de qualidade no CI para prompts

## Estrutura de Prompts (`src/ai/prompts/`)
```
src/ai/prompts/
├── classification.py    # build_classification_system_prompt, parse_classification_response
├── enrichment.py        # build_enrichment_prompt
├── reporting.py         # build_reporting_prompt
├── validation.py        # build_validation_prompt
└── __init__.py
```

## Promptfoo Config (`.promptfoo.yaml`)
```yaml
prompts:
  - file://src/ai/prompts/classification.py:build_classification_system_prompt
  - file://src/ai/prompts/enrichment.py:build_enrichment_prompt
providers:
  - openrouter:openrouter/free
  - opencode:gemini-3.6-flash
  - google:gemini-3.6-flash
tests:
  - vars:
      feature_text: "Nova funcionalidade de IA para automação de vendas"
    assert:
      - type: json-schema
        schema: src/ai/schemas/classification.py:ClassificationResult
```

## Passos

### 1. Criar/Atualizar Prompt
- Arquivo em `src/ai/prompts/{categoria}.py`
- Função `build_{categoria}_prompt(vars) -> str`
- Função `parse_{categoria}_response(response) -> PydanticModel`
- Schema em `src/ai/schemas/{categoria}.py`

### 2. Casos de Teste (YAML ou Python)
- `tests/prompts/test_{categoria}.yaml` ou `.py`
- Variáveis de entrada + asserções (schema, contains, not-contains, regex)
- Casos edge: vazio, malformado, longo, multilíngue

### 3. Rodar Eval
```bash
# Local
uvx promptfoo eval -c .promptfoo.yaml

# CI (gate)
# .github/workflows/prompt-eval.yml:
#   - uses: promptfoo/action@v1
#     with: { config: .promptfoo.yaml }
```

### 4. Versionar Resultados
- `docs/prompt-eval/{categoria}-{timestamp}.json`
- Compare com baseline anterior
- Gate: score ≥ threshold (ex.: 0.85)

### 5. Validação Final
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uvx promptfoo eval -c .promptfoo.yaml
```
