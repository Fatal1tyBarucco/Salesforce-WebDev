# QWEN.md — Salesforce-WebDev

## Project Overview

**Salesforce Release Intelligence Platform** — Pipeline automatizado para extrair, classificar e versionar Release Notes do Salesforce como artefatos Markdown estruturados (Knowledge-as-Code).

### Principais Tecnologias

| Tecnologia | Propósito |
|---|---|
| Python 3.11+ | Linguagem principal |
| Playwright | Navegador headless para scraping SPA (Salesforce Help requer JS) |
| BeautifulSoup4 + lxml | Parsing HTML e extração de links |
| PyMuPDF (fitz) | Extração de texto de PDFs (`automation/`) |
| requests + tenacity | Cliente HTTP com retry |
| python-slugify | Geração de slugs |
| MkDocs + Material theme | Site de documentação (GitHub Pages) |
| pytest | Executor de testes |
| black + ruff | Formatação e linting |
| mypy (strict) | Verificação estática de tipos |

### Arquitetura

O projeto possui **dois módulos paralelos**:

#### 1. `src/` — Módulo Principal (web scraping, Playwright)

Pipeline que busca Release Notes diretamente do Salesforce Help via Playwright:

```
src/
├── main.py           — Orquestrador: fetch índice → parse links → generate markdown
├── config.py         — Config central: ReleaseInfo, TopicConfig, BASE_URL, releases desde 2025
├── scraper.py        — Playwright headless scraper (SPA, wait domcontentloaded + scroll)
├── parser.py         — Extract article links by topic + build content from link titles
├── generator.py      — Escrita de artefatos Markdown (releases/{slug}/{topic}.md)
├── readme_updater.py — Atualização automática do índice no README.md
├── pdf_parser.py     — Extração de texto de PDF via pdfplumber (legado, não usado no main)
├── logger.py         — Configuração de logging
```

**Fluxo do `src/main.py`:**
1. `SalesforceReleaseScraper.fetch_page(url)` — Busca índice via Playwright
2. `ReleaseNotesParser.extract_article_links(soup)` — Extrai links por tópico
3. `ReleaseNotesParser.build_topic_content_from_links()` — Gera resumos com links
4. `MarkdownGenerator.generate()` — Escreve artefatos .md
5. `_update_readme()` — Atualiza README.md

**Salesforce Help é SPA** — requer Playwright com `wait_until="domcontentloaded"` + scroll + manual wait, não funciona com HTTP simples.

#### 2. `automation/` — Módulo Moderno (strategy-based, extensível)

Pipeline com padrão strategy, classificação ponderada e parsing semântico:

```
automation/
├── core/        — Lógica de negócio (scraper, parser, classifier, etc.)
├── shared/      — Constantes, modelos, utilitários (zero dependência de core/)
├── strategies/  — Strategy pattern (HtmlStrategy, PdfStrategy)
└── tests/       — Testes unitários
```

### Tópicos Monitorados

O pipeline extrai e classifica conteúdo em 5 categorias:

| Tópico | Slug | Keywords / URL Patterns |
|---|---|---|
| Apex | `apex` | rn_apex, trigger, batch, soql |
| Lightning Web Components | `lwc` | rn_lwc, rn_lightning_web, aura, wire |
| Flow & Automação | `flow` | rn_automate_flow, screen flow, process builder |
| Segurança & Perms | `security` | rn_security, rn_identity, shield, oauth |
| Integrações & APIs | `integrations` | rn_api, rn_rest, rn_soap, rn_bulk |

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

### Executar Pipeline Moderno

```bash
python -m automation.core.intelligent_release_pipeline
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
mypy automation/
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

### Salesforce Help Scraping

- **Obrigatório:** Playwright headless (SPA, `wait_until="domcontentloaded"`)
- **Estratégia:** load → wait 5s → scroll → wait 2s → find `div.content`
- **Seletor fallback:** `article`, `#articleViewContent`, `main`, `body`
- **Não funciona:** `requests` / `networkidle` (SPA nunca settle, HTTP simples retorna shell vazio)

### Configuração de Tópicos

**Três registros de keywords** devem ser mantidos em sincronia:

1. `src/config.py` → `MONITORED_TOPICS` (usado pelo `src/` pipeline)
2. `src/parser.py` → `TOPIC_URL_PATTERNS` (URL path matching para categorizar links)
3. `automation/shared/constants.py` → `TOPIC_MAPPING` (usado por `TopicClassifier`)
4. `automation/shared/topic_registry.py` → `TOPIC_REGISTRY` (usado por `WeightedTopicClassifier`)

### Imutabilidade

- Dataclasses de config: `@dataclass(frozen=True)` (ReleaseInfo, TopicConfig)
- Constantes: `Final` annotation
- Keywords: `dict[str, list[str]]` module-level constants

---

## CI/CD (GitHub Actions)

### `release_notes_pipeline.yml`
- Agendamento semanal + workflow_dispatch + PRs
- Jobs: lint (ruff + mypy) → extract (pipeline + auto-commit `[skip ci]`)
- Requer `playwright install chromium` no CI

### `python-quality.yml`
- Ruff → Black check → Mypy (em `automation/`)

---

## Cheatsheet de Arquivos

| Arquivo | Função |
|---|---|
| `src/main.py` | Pipeline principal (web scraping) |
| `src/scraper.py` | Playwright headless scraper |
| `src/parser.py` | Article link extraction + topic grouping |
| `src/config.py` | Releases, tópicos, URLs |
| `src/generator.py` | Markdown artifact writer |
| `automation/core/intelligent_release_pipeline.py` | Pipeline moderno |
| `automation/shared/constants.py` | TOPIC_KEYWORDS + TOPIC_MAPPING |
| `automation/shared/models.py` | ParsedSection, ClassificationResult |
| `pyproject.toml` | black, ruff, mypy, pytest config |
| `requirements.txt` | Runtime deps (incl. playwright) |
| `requirements-dev.txt` | Dev tooling (incl. types-beautifulsoup4) |