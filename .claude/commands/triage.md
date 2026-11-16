---
description: Triagem de issue/PR: labels, prioridade, duplicatas, info faltante
argument-hint: <issue-number|PR-number>
---

# /triage <issue|PR> — Triagem Automatizada

Triagem inteligente de issues e PRs conforme regras versionadas.

## Uso
```
/triage 123        # Triagem issue #123
/triage PR 456     # Triagem PR #456
```

## O que Faz

### Para Issues
1. **Labels automáticos** baseados em título/corpo:
   - `bug`, `feature`, `docs`, `refactor`, `test`, `chore`, `ci`, `security`
   - `scraper`, `parser`, `llm`, `pipeline`, `docs`, `infra`, `ai`
   - `good first issue`, `help wanted`, `blocked`

2. **Prioridade** (P0-P3) baseada em:
   - Impacto no pipeline (release notes quebrado = P0)
   - Segredos/vulns = P0
   - CI falhando = P1
   - Melhoria/Doc = P2-P3

3. **Duplicatas**: busca issues abertos/fechados com keywords similares

4. **Info faltante**: checklist por tipo
   - Bug: steps to reproduce, expected vs actual, logs, ambiente
   - Feature: user story, acceptance criteria, escopo, dependencies
   - Docs: arquivo alvo, idioma, reconcile needed

5. **GitHub Project**: cria/atualiza item no board (status `Backlog` → `In Progress`)

### Para PRs
1. **Validação gates**: ruff, mypy, pytest, coverage
2. **Labels**: baseados em arquivos alterados (`scraper`, `parser`, `llm`, `docs`, `tests`, `ci`)
3. **Size**: XS/S/M/L/XL (linhas alteradas)
4. **Breaking change check**: `feat!:` ou `BREAKING CHANGE:` no commit
5. **Reviewer suggestion**: baseia-se em `CODEOWNERS` e histórico

## Regras Versionadas (arquivo dedicado)
Crie `.github/triage-rules.yaml` com:
```yaml
labels:
  auto:
    - pattern: "scraper|playwright|chromium"
      label: "scraper"
    - pattern: "llm|openai|gemini|openrouter"
      label: "llm"
priority:
  P0: ["security", "secret", "pipeline broken", "release blocked"]
  P1: ["ci failing", "coverage drop", "regression"]
  P2: ["feature", "enhancement", "refactor"]
  P3: ["docs", "cleanup", "chore"]
duplicate_check:
  enabled: true
  similarity_threshold: 0.7
```

## Entregável
Comentário no issue/PR com:
- Labels aplicados
- Prioridade atribuída
- Duplicatas encontradas (links)
- Info faltante (checklist)
- Próximos passos sugeridos
