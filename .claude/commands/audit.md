---
description: Auditoria completa: arquitetura, segurança, performance, dependências
---

# /audit — Auditoria Completa

Executa auditoria multi-dimensional do repositório.

## Uso
```
/audit           # Auditoria completa (padrão)
/audit arch      # Só arquitetura
/audit sec       # Só segurança
/audit perf      # Só performance
/audit deps      # Só dependências
```

## O que Executa

### Arquitetura (`/audit arch`)
- Valida aderência Clean Architecture (`docs/ARQUITETURA.md` vs código real)
- Detecta god modules, imports cruzados, DI ausente
- Verifica duplicação LLM/scraping/parsing/classificação
- Atualiza `docs/DEBITO_TECNICO.md` se divergências

### Segurança (`/audit sec`)
```bash
# SAST básico
grep -r "eval\|exec\|subprocess" src/ --include="*.py" | grep -v test
# Segredos
gitleaks git . --redact
# Dependências
uv export --frozen --no-emit-project | uvx pip-audit -r /dev/stdin
# Actions pinned
grep -r "uses:" .github/workflows/ | grep -v "@[0-9a-f]\{40\}"
```

### Performance (`/audit perf`)
- Scraper: waits fixos, TOC expansion sequencial
- LLM: calls sequenciais, prompt size, concorrência sem limite
- Cache: hit/miss rates, TTL apropriado
- Métricas Prometheus expostas

### Dependências (`/audit deps`)
```bash
uv pip list --outdated
# Agrupamento dependabot
cat .github/dependabot.yml
```

## Entregável
Relatório consolidado com:
- Achados por severidade (🔴 Crítico, 🟠 Alto, 🟡 Médio, 🟢 Baixo)
- Evidência `arquivo:linha` para cada item
- Recomendações priorizadas (impacto × esforço)
- ADR sugerido para decisões irreversíveis

## Gates Obrigatórios Pós-Auditoria
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/ --cov=src --cov-fail-under=95
```
