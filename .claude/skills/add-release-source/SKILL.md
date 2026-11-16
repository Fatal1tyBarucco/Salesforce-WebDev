---
name: add-release-source
description: Adicionar nova fonte de release notes (novo portal, nova versão Salesforce, novo idioma). Inclui: seletores CSS, parser, validação, testes de caracterização, docs.
---

# Skill: add-release-source

## Quando Usar
- Salesforce lança novo portal de release notes (ex.: novo ano, novo formato)
- Precisa suportar novo idioma além de pt_BR/en_US
- Nova fonte de dados (PDF, API, RSS) para enriquecer pipeline

## Passos

### 1. Mapear Seletores (docs/SOURCE_SCHEMA.md)
```markdown
## Nova Fonte: {nome}
- Base URL: https://help.salesforce.com/...
- TOC container: `seletor CSS`
- Article content: `seletor CSS`
- Feature impact table: `seletor CSS`
- ARIA attributes: `role`, `aria-level`, `data-is-link`
```

### 2. Estender Parser (`src/parser.py` ou `src/infrastructure/parsing.py`)
- Adicione seletores em `TOC_SELECTORS` / `CONTENT_SELECTORS`
- Implemente `extract_topic_tree` para nova estrutura HTML
- Valide com HTML fixture real (salve em `tests/fixtures/html/`)

### 3. Testes de Caracterização
```bash
# Gere golden files
CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_parser.py -q
# Valide
uv run pytest tests/test_characterization_parser.py -q
```

### 4. Atualizar Scraper se Necessário (`src/scraper.py` ou `src/infrastructure/scraping.py`)
- Novos waits/timeouts se SPA diferente
- Nova expansão de TOC se estrutura diferente
- Circuit breaker threshold ajustado

### 5. Docs e Reconcile
- Atualize `docs/SOURCE_SCHEMA.md`
- `python3 .github/scripts/docs_sync_engine.py reconcile`
- Commit + push

## Validação Final
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/test_characterization_parser.py -q
```
