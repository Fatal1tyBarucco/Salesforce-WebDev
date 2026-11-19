---
name: doc-conventions
description: Convenções de documentação para Salesforce-WebDev
paths:
  - "docs/**/*.md"
  - "README*.md"
  - "releases/**/*.md"
---

# Convenções de Documentação

## Reconcile Obrigatório
**Qualquer alteração em docs exige:**
```bash
python3 .github/scripts/docs_sync_engine.py reconcile
# validar (lint + links + mkdocs best-effort)
git add docs/
git commit -m "docs(sync): reconcile documentation"
git push
```

## Estrutura Bilíngue
- `mkdocs.yml` em português (nav principal)
- Inglês em `releases/*/en/` + `README.en.md`
- `docs_sync_engine.py` sincroniza ambos (source of truth = `releases/*/.meta.json`)
- `docs/.documentation-manifest.json` gerado pelo `reconcile` — **não edite**

## MkDocs Material
- Tema: Material, idioma `pt`
- `mkdocs build --strict` é best-effort (continue-on-error no CI — ARM64/Playwright)
- `markdownlint-cli2 docs/` e `markdown-link-check docs/` no CI

## Diagramas Mermaid
- Sintaxe válida (labels com aspas se pontuação: `node["label, com vírgula"]`)
- Atualize em `docs/ARQUITETURA.md` quando arquitetura mudar

## ADRs
- Template: título, status, contexto, decisão, consequências, alternativas
- Local: `docs/architecture/decisions/adr-NNN-titulo.md`
- Numerados sequencialmente

## Seletores do Scraper
- Documentados em `docs/SOURCE_SCHEMA.md`
- CSS selectors, ARIA attributes, feature impact format

## O que NÃO É Reescrito pelo Reconcile
- `docs/`, `releases/`, `tests/golden/`, `.claude/`, `.github/` — são conteúdo, não reescritos
- Desenrolar link de golden corrompe byte-exact fixtures → falha characterization tests

## Validação Local
```bash
python3 .github/scripts/docs_sync_engine.py audit    # deve dar 0 findings
python3 -m py_compile .github/scripts/docs_sync_engine.py
mkdocs build --strict  # best-effort
markdownlint-cli2 docs/
markdown-link-check docs/
```
