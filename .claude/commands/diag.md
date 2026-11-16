---
description: Diagnóstico rápido do repositório (gates, arquitetura, débito técnico)
---

# /diag — Diagnóstico Rápido

Executa verificação completa do estado do repositório.

## O que faz
1. **Gates**: roda ruff, ruff format, mypy, pytest (rápido)
2. **Arquitetura**: mostra diagrama de componentes (resumo de `docs/ARQUITETURA.md`)
3. **Débito técnico**: top 5 itens críticos de `docs/DEBITO_TECNICO.md`
4. **Git status**: branch, arquivos modificados, commits recentes
5. **CI status**: últimos runs dos workflows principais

## Uso
```
/diag
```

## Saída Esperada
```
=== GATES ===
ruff check:        ✅ OK
ruff format:       ✅ OK
mypy src/:         ✅ OK
pytest (fast):     ✅ 2059 passed (180s)

=== ARQUITETURA (resumo) ===
Componentes: 4 camadas (EXTERNAL, INFRA, CORE, AI, LEGACY)
Fluxo ETL: 6 estágios (Detect → Scrape → Parse → Enrich → Generate → AI Reports)
Workflows: 10 ativos (Quality, Pipeline, Doc Sync, Doc Build, AI Docs, Intel, Deps, Copilot, Release)

=== DÉBITO TÉCNICO (top 5) ===
🔴 LLM: 3 implementações duplicadas (llm_service, infra/llm, ai/llm/client)
🔴 main.py: God module (30+ imports, orquestra tudo inline)
🟠 Scraper: waits fixos 15-30s/página, DI ausente
🟠 FeatureEnricher: LLM calls sequenciais (5-15 min)
🟠 Cobertura: ~10-15% real (llm_service 23%, release_summarizer 0% LLM path)

=== GIT ===
Branch: feat/fase-2-ai-native
Modified: 6 files (configs + whitespace)
Untracked: docs/, tests/golden/, tests/fixtures/, test_characterization*
Commits recentes: 5 (Fase 1 + Fase 0)

=== CI (últimos runs) ===
python-quality:     ✅ success (2min atrás)
release-please:     ⏳ never run (novo)
documentation-sync: ✅ success (4 falhas anteriores resolvidas)
```
