# ADR-008 - Prompt Versioning & Evaluation

Prompt versionamento, avaliação (promptfoo) e guardrails para LLM prompts.

## Status

**Aceito** — Implementado em `prompts/` (YAML versionado) + `tests/test_prompt_eval.py`.

## Contexto

O pipeline usa LLMs em múltiplos estágios (classificação, enriquecimento, sumarização, geração de relatórios). Prompts eram hardcoded em arquivos Python, dificultando:

- Rastrear mudanças de prompt entre releases
- A/B testing de variantes
- Reprodutibilidade de resultados
- Avaliação sistemática de qualidade (regressão de prompt)
- Rollback quando uma mudança degrada qualidade

Problemas observados:

- Mudança em `system_prompt` quebrou parsing JSON de resposta
- Temperature alta gerava alucinações em classificação
- Sem baseline de qualidade, não dava para saber se "estava melhor"

## Decisão

### 1. Estrutura de Prompts como YAML Versionado

```text
prompts/
├── classification/
│   └── v1.yaml
├── enrichment/
│   └── v1.yaml
├── reporting/
│   └── v1.yaml
└── (futuros: validation, translation, etc.)
```

Cada arquivo YAML contém:

```yaml
---
version: "1.0"              # SemVer do prompt
name: "feature_classification"
description: "Classify Salesforce release features..."
model: "openrouter/free"    # Modelo alvo
temperature: 0.2
max_tokens: 1000
response_format:
  type: "json_object"

system_prompt: |
  Você é um Arquiteto de Soluções Salesforce sênior...

user_prompt_template: |
  Feature: {feature_text}
  Classifique esta feature.

schema:
  type: object
  properties:
    impact: { type: string, enum: ["high", "medium", "low"] }
    ...

test_cases:

  - name: "security_feature"
    vars:
      feature_text: "Nova autenticação MFA obrigatória..."
    expected_contains:

      - "security"
      - "high"
      - "admins"
```

### 2. Semantic Versioning para Prompts

| Tipo de mudança | Exemplo | Version bump |
|-----------------|---------|--------------|
| Patch | Fix typo, ajustar temperature | 1.0 → 1.0.1 |
| Minor | Adicionar campo no schema, novo test_case | 1.0 → 1.1 |
| Major | Mudar schema, remover campo, trocar modelo | 1.0 → 2.0 |

### 3. Avaliação Automatizada com promptfoo

`tests/test_prompt_eval.py` roda `promptfoo evaluate` contra todos os prompts em `prompts/**/v*.yaml`.

```bash
# Rodar avaliação local
uv run promptfoo eval -c prompts/promptfooconfig.yaml
```

Configuração `promptfooconfig.yaml` define:

- Providers (OpenRouter free, Gemini, etc.)
- Prompts a avaliar (descobertos automaticamente)
- Test cases (extraídos do próprio YAML do prompt)
- Assertions: `contains`, `json-schema`, `icontains`, `not-contains`

### 4. Gate no CI

Workflow `prompt-eval.yml` roda em PRs que tocam `prompts/**`:

1. Carrega prompts modificados
2. Executa test cases contra modelo configurado
3. Falha se coverage de assertions < 90% ou regressão detectada
4. Publica relatório no PR summary

### 5. Guardrails em Runtime

`loader.py` (carregador):

- Valida schema Pydantic ao carregar
- Injeta variáveis via `str.format(**vars)`
- Loga versão do prompt usado em cada chamada (observabilidade)
- Cache key inclui `prompt_version` (invalida cache auto em bump)

## Consequences

### Positivas

- **Rastreabilidade total**: `git log prompts/classification/v1.yaml` = histórico completo
- **Reprodutibilidade**: Mesmo input + mesmo prompt versionado = mesmo output (determinístico com temperature=0)
- **Regressão detectada**: CI falha se novo prompt quebra test cases existentes
- **Rollback instantâneo**: `git checkout v1.0 -- prompts/classification/` resolve incidente
- **A/B testing**: Rodar v1.0 e v1.1 lado a lado no mesmo dataset
- **Documentação viva**: `test_cases` no YAML servem como exemplos e contratos

### Negativas / Trade-offs

- **Mais arquivos**: 3-5 arquivos YAML por prompt vs. string inline
- **Curva de promptfoo**: Time precisa aprender assertions syntax (`contains`, `json-schema`, etc.)
- **Custo de eval**: Rodar promptfoo no CI consome tokens LLM (controlado por `PROMPTFOO_MAX_CALLS`)
- **Schema duplication**: Schema no YAML + Pydantic model no código (mitigado: loader valida ambos)

## Testes

```bash
# Avaliação completa
uv run promptfoo eval -c prompts/promptfooconfig.yaml

# Apenas prompts modificados (CI)
uv run promptfoo eval -c prompts/promptfooconfig.yaml --changed

# Cobertura de test cases
uv run pytest tests/test_prompt_eval.py -v
```

## Referências

- [promptfoo Documentation](https://www.promptfoo.dev/)
- ADR-003 (Topic Classification) — classificação via LLM
- ADR-007 (Clean Architecture) — `src/core/classification/service.py` consome prompts versionados
- `prompts/classification/v1.yaml`, `prompts/enrichment/v1.yaml`, `prompts/reporting/v1.yaml`
