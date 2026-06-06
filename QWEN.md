# QWEN.md — Salesforce-WebDev

## Project Overview

**Salesforce Release Intelligence Platform** — Pipeline automatizado para extrair, classificar e versionar Release Notes do Salesforce como artefatos Markdown estruturados (Knowledge-as-Code).

### Principais Tecnologias

| Tecnologia | Propósito |
|---|---|
| Python 3.11+ | Linguagem principal |
| BeautifulSoup4 + lxml | Parsing HTML (páginas de release notes) |
| pdfplumber | Extração de texto de PDFs (legado `src/`) |
| PyMuPDF (fitz) | Extração de texto de PDFs (`automation/`) |
| Playwright | Navegador headless para páginas JS |
| requests | Cliente HTTP (com retry via tenacity) |
| python-slugify | Geração de slugs para diretórios/arquivos |
| MkDocs + Material theme | Site de documentação (GitHub Pages) |
| pytest | Executor de testes |
| black + ruff | Formatação e linting |
| mypy (strict) | Verificação estática de tipos |

### Arquitetura

O projeto possui **dois módulos paralelos** que evoluíram ao longo do tempo:

#### 1. `src/` — Módulo Legado (estável, PDF-first)

Pipeline síncrono simples orquestrado por `src/main.py`:

```
src/
├── main.py           — Entry point: orquestra extração de PDFs
├── config.py         — Config central: dataclasses ReleaseInfo, TopicConfig
├── pdf_parser.py     — Extração de texto de PDF via pdfplumber
├── parser.py         — Segmentação de seções HTML (usado pelo scraper)
├── scraper.py        — Web scraper via Playwright (assíncrono)
├── generator.py      — Escrita de artefatos Markdown (releases/{slug}/{topic}.md)
├── readme_updater.py — Atualização automática do índice no README.md
├── logger.py         — Configuração de logging (stdout, nível INFO)
```

**Fluxo:** `main()` → `PDFReleaseParser.parse()` → `MarkdownGenerator.generate()` → `_update_readme()`

#### 2. `automation/` — Módulo Moderno (strategy-based, extensível)

Pipeline sofisticado com padrão strategy, classificação ponderada e parsing semântico:

```
automation/
├── core/
│   ├── intelligent_release_pipeline.py  — Pipeline de integração de alto nível
│   ├── orchestrator.py                  — ReleasePipelineOrchestrator
│   ├── scraper.py                       — ReleaseNotesScraper
│   ├── parser.py                        — ReleaseNotesParser (delega para strategy)
│   ├── semantic_parser.py               — SemanticParser (HTML → ParsedSection[])
│   ├── classifier.py                    — TopicClassifier (baseado em keywords)
│   ├── weighted_classifier.py           — WeightedTopicClassifier (score de confiança)
│   ├── pdf_extraction_engine.py         — PdfExtractionEngine (PyMuPDF)
│   ├── generator.py                     — MarkdownArtifactGenerator
│   └── readme_updater.py                — ReadmeUpdater
├── shared/
│   ├── config.py                        — ApplicationConfig dataclass
│   ├── constants.py                     — TOPIC_MAPPING (registro de keywords)
│   ├── models.py                        — ReleaseTopicContent, ParsedSection, ClassificationResult
│   ├── topic_registry.py                — TOPIC_REGISTRY (listas estendidas de keywords)
│   ├── file_utils.py                    — Utilitários de diretório/arquivo
│   ├── http_client.py                   — Cliente HTTP com retry
│   └── logger.py                        — Logging estruturado
├── strategies/
│   ├── parser_strategy.py               — Base abstrata: ParserStrategy
│   ├── html_strategy.py                 — Implementação HtmlStrategy
│   └── pdf_strategy.py                  — Implementação PdfStrategy
└── tests/
    ├── test_parser.py                   — Testes unitários do parser
    └── test_classifier.py               — Testes unitários do classificador
```

**Fluxo do módulo `automation/core/intelligent_release_pipeline.py`:**
`PdfExtractionEngine.extract_text()` → `SemanticParser.parse_sections()` → `WeightedTopicClassifier.classify()`

#### Configuração e Dados de Release

```
├── releases/
│   ├── winter_26/       — Artefatos gerados (apex.md, flow.md, etc.)
│   ├── summer_26/
│   ├── spring_26/
│   └── summer_25/
├── cache/
│   └── processed_releases.json    — Controla releases já processadas
├── pdfs/                          — PDFs locais (não versionados, ver .gitignore)
└── docs/                          — Site de documentação MkDocs
    ├── architecture/
    ├── contribution/
    ├── maintenance/
    ├── observability/
    ├── roadmap/
    ├── runbooks/
    └── index.md
```

### Tópicos Monitorados

O pipeline extrai e classifica conteúdo em 5 categorias:

| Tópico | Slug | Exemplo de Keywords |
|---|---|---|
| Apex | `apex` | trigger, batch, queueable, soql, sosl |
| Lightning Web Components | `lwc` | lwc, aura, wire, lms |
| Flow & Automação | `flow` | screen flow, process builder, workflow |
| Segurança & Permissões | `security` | shield, encryption, profile, oauth |
| Integrações & APIs | `integrations` | rest, soap, bulk, platform event |

Novos tópicos podem ser adicionados inserindo um `TopicConfig` / entrada no `TOPIC_REGISTRY` — sem necessidade de alterar o motor principal.

### Fontes de Processamento

1. **PDFs** — Arquivos locais no diretório `pdfs/` (nomeados pelo slug da release, ex: `summer_26.pdf`)
2. **Web scraping** — Portal de ajuda Salesforce (Playwright headless, assíncrono)
3. **Parsing semântico** — Conteúdo HTML via BeautifulSoup em seções estruturadas
4. **Classificação ponderada** — Correspondência multi-keyword com score de confiança

---

## Building and Running

### Setup

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt   # dependências de desenvolvimento
playwright install chromium            # para o scraper Playwright
```

### Executar Pipeline Legado (extração de PDF)

```bash
python -m src.main
```

### Executar Pipeline Moderno

```bash
python -m automation.core.intelligent_release_pipeline
```

### Executar Orquestrador (pipeline via web scraping)

```bash
python -m automation.core.orchestrator
```

### Dry Run / Release Específica

```bash
python -m src.main --dry-run
python -m src.main --release summer_26   # release única
```

### Testes

```bash
pytest
pytest automation/tests/                 # apenas testes do módulo automation
pytest -v                                 # modo verboso
```

### Linting e Type Checking

```bash
ruff check .                              # lint
black --check .                           # verificação de formatação
black .                                   # formatação automática
mypy src/                                 # type check módulo legado
mypy automation/                          # type check módulo automation
```

### Site de Documentação

```bash
mkdocs serve                              # preview local em http://127.0.0.1:8000
mkdocs build                              # build do site estático em site/
```

---

## Convenções de Desenvolvimento

### Estilo de Código

- **Formatador:** black com `line-length = 100`
- **Linter:** ruff com `line-length = 100`
- **Tipos:** mypy em modo strict. TODAS as assinaturas de função DEVEM ter anotações de tipo. Usar `from __future__ import annotations` nos módulos de automation.
- **Imports:** Biblioteca padrão → terceiros → locais, separados por linhas em branco.
- **Docstrings:** Presentes em todas as classes e métodos públicos. Usar `"""Aspas duplas"""`.

### Convenções de Estrutura

- `automation/shared/` — Constantes, modelos, utilitários compartilhados (zero dependência de `core/`)
- `automation/core/` — Componentes de lógica de negócio
- `automation/strategies/` — Implementações do padrão Strategy
- `src/` — Módulo legado, usar como referência mas preferir `automation/` para novas funcionalidades

### Modelos de Dados

Dataclasses principais utilizadas no projeto:

| Classe | Módulo | Campos |
|---|---|---|
| `ReleaseInfo` | `src/config.py` | `name`, `release_id`, `slug` |
| `TopicConfig` | `src/config.py` | `slug`, `display_name`, `keywords` |
| `ParsedSection` | `automation/shared/models.py` | `title`, `content` |
| `ClassificationResult` | `automation/shared/models.py` | `topic_name`, `content`, `confidence_score` |
| `ReleaseTopicContent` | `automation/shared/models.py` | `topic_name`, `content` |
| `ApplicationConfig` | `automation/shared/config.py` | Várias constantes de configuração |

### Configuração de Tópicos

**Existem dois registros de keywords** que devem ser mantidos em sincronia:

1. `automation/shared/constants.py` → `TOPIC_MAPPING` (usado por `TopicClassifier`)
2. `automation/shared/topic_registry.py` → `TOPIC_REGISTRY` (usado por `WeightedTopicClassifier`)
3. `src/config.py` → `MONITORED_TOPICS` (legado, usado pelos módulos `src/`)

### Práticas de Teste

- Testes vivem em `automation/tests/`
- Usam assert statements simples (não unittest.TestCase)
- Testes unitários focados em lógica de parsing/classificação
- Nenhum framework de mocking observado até o momento

### Imutabilidade

- Dataclasses de configuração usam `@dataclass(frozen=True)` (ReleaseInfo, TopicConfig, ApplicationConfig)
- Constantes usam a anotação `Final`
- Registros de keywords são constantes `dict[str, list[str]]` em nível de módulo

### Padrão de Numeração de Release IDs

IDs de release do Salesforce incrementam em 2: Summer=x6, Winter=x8, Spring=x0:

- Summer '25 → 256
- Winter '26 → 258
- Spring '26 → 260
- Summer '26 → 262

### Índice Automático do README

O índice do README.md usa marcadores para atualização automática:

```
<!-- RELEASE_INDEX_START -->
(conteúdo gerado automaticamente)
<!-- RELEASE_INDEX_END -->
```

---

## CI/CD (GitHub Actions)

### `release_notes_pipeline.yml`

- **Trigger:** Agendamento semanal (Seg 08:00 UTC), workflow_dispatch, ou PRs alterando `src/`
- **Jobs:**
  1. `lint` — Verificações Ruff + mypy
  2. `extract` — Executa pipeline de extração, commita artefatos gerados
- **Funcionalidades:** Modo dry-run, filtro por release, auto-commit com `[skip ci]`

### `python-quality.yml`

- **Trigger:** Todos os PRs + workflow_dispatch
- **Steps:** Ruff → Black check → Mypy (em `automation/`)

### `documentation-build.yml` / `jekyll-gh-pages.yml`

- Build e deploy do site MkDocs para GitHub Pages

---

## Cheatsheet de Arquivos Relevantes

| Arquivo | Função |
|---|---|
| `src/main.py` | Entry point legado |
| `src/config.py` | Definições de tópicos e releases |
| `automation/core/intelligent_release_pipeline.py` | Pipeline moderno de alto nível |
| `automation/core/orchestrator.py` | Orquestrador completo do pipeline |
| `automation/shared/constants.py` | Mapeamentos de keywords |
| `automation/shared/topic_registry.py` | Keywords estendidas de tópicos |
| `automation/shared/models.py` | Tipos de dados centrais |
| `automation/strategies/parser_strategy.py` | Strategy abstrata de parser |
| `pyproject.toml` | Configuração de ferramentas (black, ruff, mypy, pytest) |
| `mkdocs.yml` | Configuração do site de documentação |
| `requirements.txt` | Dependências de runtime |
| `requirements-dev.txt` | Ferramentas de desenvolvimento |