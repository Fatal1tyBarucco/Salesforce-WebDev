---
description: Preparar e validar release via release-please
---

# /release — Release Management

Opera o fluxo de release via `release-please` (Google).

## Uso
```
/release           # Status atual do Release PR
/release validate  # Valida Release PR aberto
/release trigger   # Força trigger manual (workflow_dispatch)
```

## O que faz

### Status (padrão)
```bash
# Verifica se há Release PR aberto
gh pr list --state open --label "release" --json number,title,headRefName

# Mostra versão atual no pyproject.toml
grep '^version' pyproject.toml

# Últimos releases/tags
git tag --sort=-v:refname | head -5
```

### Validate
- Abre Release PR no browser para revisão humana
- Valida: version bump correto, CHANGELOG coerente, breaking changes documentados
- Confirma que apenas `feat:`/`fix:`/`refactor:`/`docs:`/`test:`/`chore:` desde último release

### Trigger
```bash
# Dispara workflow_dispatch manualmente
gh workflow run release-please.yml
```

## Fluxo Normal (Automático)
1. Commits `feat:`/`fix:` em `main` → Release PR auto-atualizado
2. Humano revisa Release PR → merge
3. Merge → tag `vX.Y.Z` + GitHub Release automático
4. Job downstream (futuro): publish PyPI/Docker gated em `release_created`

## Convenções
- Conventional Commits obrigatórios
- Breaking change: `feat(scope)!:` ou footer `BREAKING CHANGE:`
- **Não edite CHANGELOG.md manualmente** — release-please gera
- **Não force push tags** — deixe release-please fazer

## Bloqueadores Conhecidos
- Push em `.github/workflows/*` falha (HTTP 403) — não tente corrigir workflow de release via bot
- Se Release PR não aparece: nenhum `feat:`/`fix:` desde último release
