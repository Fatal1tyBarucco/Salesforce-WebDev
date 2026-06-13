# Salesforce Release Intelligence Platform — GEMINI.md

Este documento define as diretrizes de arquitetura, convenções de código e fluxos de trabalho para o projeto. Todas as intervenções do agente devem seguir estas regras.

## 🎯 Visão Geral
Plataforma de automação para extração, classificação e versionamento de **Salesforce Release Notes** como artefatos Markdown estruturados (Knowledge-as-Code).

---

## 🏗️ Arquitetura do Sistema

O projeto é dividido em dois módulos distintos que operam em paralelo:

### 1. Módulo `src/` (Pipeline Principal de Web Scraping)
Orquestra a busca direta no portal Salesforce Help via Playwright.
- **main.py**: Orquestrador central.
- **scraper.py**: Implementação do scraper Playwright headless. **Crítico:** O portal é um SPA, requer espera e scroll.
- **parser.py**: Extração de links e agrupamento por tópicos.
- **config.py**: Definições de releases (ids e nomes) e tópicos monitorados.

### 2. Módulo `automation/` (Pipeline Moderno Baseado em Estratégias)
Design extensível utilizando o padrão Strategy e classificação ponderada.
- **core/**: Lógica de negócio e orquestração moderna.
- **shared/**: Modelos e constantes (não deve depender de `core/`).
- **strategies/**: Implementação de `HtmlStrategy`.

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
Ao adicionar ou modificar tópicos, os seguintes arquivos devem ser mantidos em sincronia:
1. `src/config.py` (`MONITORED_TOPICS`)
2. `src/parser.py` (`TOPIC_URL_PATTERNS`)
3. `automation/shared/constants.py` (`TOPIC_MAPPING`)
4. `automation/shared/topic_registry.py` (`TOPIC_REGISTRY`)

### Numeração de Releases
As releases seguem incrementos de 2 no `release_id`:
- **Spring**: Final 0 ou 4 (ex: 254, 260)
- **Summer**: Final 6 (ex: 256, 262)
- **Winter**: Final 8 (ex: 258, 268)

---

## 🚀 Workflows e CI/CD
- **Qualidade**: Executar `ruff check .`, `black .` e `mypy` antes de qualquer commit.
- **Pipelines**: O workflow `python-quality.yml` valida PRs e pushes na `main`.
