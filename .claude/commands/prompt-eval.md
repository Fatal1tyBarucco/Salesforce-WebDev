---
description: Avaliação de prompts versionados (promptfoo): criar casos, rodar eval, gate CI
---

# /prompt-eval — Avaliação de Prompts

Gerencia ciclo de vida de prompts versionados com promptfoo.

## Uso
```
/prompt-eval           # Roda eval completo (todos prompts)
/prompt-eval classification   # Só prompt de classificação
/prompt-eval enrichment       # Só prompt de enriquecimento
/prompt-eval create <nome>    # Cria scaffold para novo prompt
```

## Estrutura
```
src/ai/prompts/
├── classification.py    # build_classification_system_prompt, parse_classification_response
├── enrichment.py        # build_enrichment_prompt
├── reporting.py         # build_reporting_prompt
├── validation.py        # build_validation_prompt
└── __init__.py

.promptfoo.yaml          # Config promptfoo (providers, prompts, tests)
tests/prompts/           # Casos de teste YAML
docs/prompt-eval/        # Resultados versionados
```

## Fluxo

### 1. Criar Novo Prompt (`/prompt-eval create classification_v2`)
- Scaffold em `classification_v2.py`
- Schema em `classification_v2.py`
- Casos de teste em `tests/prompts/test_classification_v2.yaml`
- Entry em `.promptfoo.yaml`

### 2. Rodar Eval
```bash
# Local
uvx promptfoo eval -c .promptfoo.yaml

# Com provider específico
uvx promptfoo eval -c .promptfoo.yaml -p openrouter:openrouter/free
```

### 3. Gate no CI
Workflow `prompt-eval.yml`:
```yaml
on: [push, pull_request]
jobs:
  prompt-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: promptfoo/action@v1
        with:
          config: .promptfoo.yaml
          threshold: 0.85
```

### 4. Versionar Resultados
```bash
# Salva resultado com timestamp
uvx promptfoo eval -c .promptfoo.yaml -o docs/prompt-eval/classification-$(date +%Y%m%d-%H%M).json
```

### 5. Comparar com Baseline
```bash
# Diff simples
diff docs/prompt-eval/classification-baseline.json docs/prompt-eval/classification-latest.json
```

## Providers Configurados
- `openrouter:openrouter/free` (gratuito, fallback chain)
- `opencode:gemini-3.6-flash` (via OpenCode)
- `google:gemini-3.6-flash` (direto, ~20 req/dia free)

## Métricas de Gate
- **Schema compliance**: 100% (Pydantic validation)
- **Semantic similarity**: ≥ 0.85 vs baseline (embedding cosine)
- **Latency**: ≤ 30s p95
- **Cost**: ≤ $0.01 por 1k tokens (quando aplicável)

## Não Faça
- Não commite API keys em `.promptfoo.yaml` (use env vars)
- Não rode eval em produção sem gate
- Não altere prompt sem versionar (git commit + tag)
