# Salesforce Release Intelligence Platform — GEMINI.md

Este documento define as diretrizes de arquitetura, convenções de código e fluxos de trabalho para o projeto. Todas as intervenções do agente devem seguir estas regras.

## 🎯 Visão Geral
Plataforma de automação para extração, classificação e versionamento de **Salesforce Release Notes** como artefatos Markdown estruturados (Knowledge-as-Code).

---

## 🏗️ Arquitetura do Sistema

O projeto utiliza um pipeline unificado em `src/`:

### Pipeline Principal (`src/`)
Orquestra a busca direta no portal Salesforce Help via Playwright.
- **main.py**: Orquestrador central.
- **scraper.py**: Implementação do scraper Playwright headless. **Crítico:** O portal é um SPA, requer espera e scroll.
- **parser.py**: Extração de links e agrupamento por tópicos.
- **config.py**: Definições de releases (ids e nomes) e tópicos monitorados.
- **analytics.py**: Dashboard HTML com gráficos SVG.
- **api.py**: REST API e GraphQL endpoint.
- **notifications.py**: Email, Slack, Discord webhooks.
- **dashboard.py**: Dashboard interativo com JS.
- **workflow.py**: PR-based workflow com triage.
- **salesforce.py**: Trailhead linking, org limits, sandbox readiness.
- **ai_automation.py**: Comparação, regressões, quality metrics.
- **health.py**: Health check, readiness, Prometheus metrics.
- **logger.py**: Logging estruturado com correlation IDs.

---

## 🛠️ Padrões de Código e Qualidade

### Formatação e Linting
- **Black**: Formatador obrigatório (`line-length = 100`).
- **Ruff**: Linter principal (`line-length = 100`).
- **Mypy**: Verificação de tipos estática em modo `strict`. **Toda assinatura deve ter type annotations.**

### Testes
- **Pytest**: Executor de testes.
- **Cobertura**: Alvo de 100% de cobertura. Testes de ponto de entrada devem usar `compile()` e mocks para evitar efeitos colaterais.

---

## 🕷️ Estratégia de Scraping (Salesforce Help)

O portal Salesforce Help é uma Single Page Application (SPA) complexa.
1. **Ferramenta**: Usar **Playwright** (`chromium`). `requests` ou `networkidle` não funcionam.
2. **Ciclo de Carregamento**:
   - `wait_until="domcontentloaded"`
   - Espera manual (ex: 5s) + Scroll para disparar carregamento dinâmico.
   - Seletores fallback: `div.content`, `article`, `#articleViewContent`.

---

## 📋 Gerenciamento de Tópicos e Releases

### Sincronização de Keywords
Ao adicionar ou modificar tópicos, o seguinte arquivo deve ser mantido:
1. `src/config.py` (`EXCLUDED_NODE_SLUGS`)

### Numeração de Releases
As releases seguem incrementos de 2 no `release_id`:
- **Spring**: Final 0 ou 4 (ex: 254, 260)
- **Summer**: Final 6 (ex: 256, 262)
- **Winter**: Final 8 (ex: 258, 268)

---

## 🚀 Workflows e CI/CD
- **Qualidade**: Executar `ruff check .`, `black .` e `mypy` antes de qualquer commit.
- **Pipelines**: O workflow `python-quality.yml` valida PRs e pushes na `main`.
