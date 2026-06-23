# QWEN.md — Salesforce-WebDev

## Project Overview

**Salesforce Release Intelligence Platform** — Pipeline automatizado para extrair, classificar e versionar Release Notes do Salesforce como artefatos Markdown estruturados (Knowledge-as-Code).

### Principais Tecnologias

| Tecnologia | Propósito |
|---|---|
| Python 3.14 | Linguagem principal |
| Playwright | Navegador headless para scraping SPA (Salesforce Help requer JS) |
| BeautifulSoup4 + lxml | Parsing HTML e extração de links |
| MkDocs + Material theme | Site de documentação (GitHub Pages) |
| pytest | Executor de testes |
| black + ruff | Formatação e linting |
| mypy (strict) | Verificação estática de tipos |

### Arquitetura

O projeto utiliza um pipeline unificado em `src/`:

```
src/
├── main.py              — Orquestrador central
├── config.py            — Config central: ReleaseInfo, TopicNode, URLs
├── scraper.py           — Playwright headless scraper (SPA)
├── parser.py            — FeatureImpactParser + ReleaseNotesParser
├── generator.py         — Markdown artifact writer
├── readme_updater.py    — Auto-update README release section
├── analytics.py         — Static HTML dashboard with SVG charts
├── api.py               — REST API + GraphQL endpoint
├── notifications.py     — Email, Slack, Discord webhooks
├── dashboard.py         — Interactive HTML dashboard with JS
├── workflow.py          — PR-based workflow with triage
├── salesforce.py        — Trailhead linking, org limits, sandbox readiness
├── ai_automation.py     — Release comparison, regressions, quality metrics
├── health.py            — Health check, readiness, Prometheus metrics
├── logger.py            — Structured logging with correlation IDs
```

**Fluxo do `src/main.py`:**
1. `detect_new_release()` — Detecta nova release via comparação de conteúdo
2. `SalesforceReleaseScraper.fetch_page_raw_text()` — Busca Feature Impact via Playwright
3. `FeatureImpactParser.parse_text()` — Extrai categorias e features
4. `_generate_release_files()` — Escreve artefatos .md por categoria
5. `_update_readme_single()` — Salva .meta.json e atualiza history
6. `_update_readme_all()` — Atualiza README.md com details/summary blocks

**Salesforce Help é SPA** — requer Playwright com `wait_until="domcontentloaded"` + scroll + manual wait, não funciona com HTTP simples.

### Releases Configuradas (desde 2025)

| Release | release_id | Slug |
|---|---|---|
| Spring '25 | 254 | spring_25 |
| Summer '25 | 256 | summer_25 |
| Winter '26 | 258 | winter_26 |
| Spring '26 | 260 | spring_26 |
| Summer '26 | 262 | summer_26 |

Padrão de numeração: incrementos de 2 (Summer=x6, Winter=x8, Spring=x0).

---

## Building and Running

### Setup

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
playwright install chromium            # obrigatório para scraping SPA
```

### Executar Pipeline Principal (web scraping)

```bash
python -m src.main
```

### Testes

```bash
pytest
pytest -v
```

### Linting e Type Checking

```bash
ruff check .
black --check .
mypy src/
```

### Site de Documentação

```bash
mkdocs serve
mkdocs build
```

---

## Convenções de Desenvolvimento

### Estilo de Código

- **Formatador:** black com `line-length = 100`
- **Linter:** ruff com `line-length = 100`
- **Tipos:** mypy strict. TODAS as assinaturas DEVEM ter type annotations.
- **Imports:** Biblioteca padrão → terceiros → locais.
- **Docstrings:** Presentes em classes e métodos públicos.
- **Dataclasses:** Todos os data structures usam `@dataclass`, não Pydantic.

### Salesforce Help Scraping

- **Obrigatório:** Playwright headless (SPA, `wait_until="domcontentloaded"`)
- **Estratégia:** load → wait → scroll → extract
- **Não funciona:** `requests` / `networkidle` (SPA nunca settle, HTTP simples retorna shell vazio)

### Configuração de Tópicos

Tópicos são descobertos dinamicamente a partir da árvore de navegação do Salesforce Help (não hardcoded). Use `EXCLUDED_NODE_SLUGS` em `config.py` para filtrar itens não-artigo.

---

## CI/CD (GitHub Actions)

### `release_notes_pipeline.yml`
- Agendamento semanal + workflow_dispatch
- Jobs: lint (ruff + mypy) → extract (pipeline + auto-commit)
- Requer `playwright install chromium` no CI

### `python-quality.yml`
- Ruff → Black check → Mypy (em `src/`)

---

## Cheatsheet de Arquivos

| Arquivo | Função |
|---|---|
| `src/main.py` | Pipeline principal (web scraping) |
| `src/scraper.py` | Playwright headless scraper |
| `src/parser.py` | FeatureImpactParser + ReleaseNotesParser |
| `src/config.py` | Releases, tópicos, URLs |
| `src/generator.py` | Markdown artifact writer |
| `src/analytics.py` | Static HTML dashboard with SVG charts |
| `src/api.py` | REST API + GraphQL endpoint |
| `src/notifications.py` | Email, Slack, Discord webhooks |
| `src/dashboard.py` | Interactive HTML dashboard |
| `src/workflow.py` | PR-based workflow |
| `src/salesforce.py` | Trailhead, org limits, sandbox readiness |
| `src/ai_automation.py` | Release comparison, regressions, quality metrics |
| `src/health.py` | Health check, readiness, Prometheus metrics |
| `src/logger.py` | Structured logging |
| `pyproject.toml` | black, ruff, mypy, pytest config |
| `requirements.txt` | Runtime deps (incl. playwright) |
| `requirements-dev.txt` | Dev tooling (incl. types-beautifulsoup4) |
