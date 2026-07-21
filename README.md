![Salesforce Release Intelligence](./assets/banner.png)

<div align="center">

# 🚀 Salesforce Release Notes Intelligence

### *Knowledge-as-Code para o ecossistema Salesforce*

[![Python Quality](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml)
[![Pipeline](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/release_notes_pipeline.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/release_notes_pipeline.yml)
[![Docs](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/documentation-build.yml/badge.svg)](https://fatal1tybarucco.github.io/Salesforce-WebDev/)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Headless-2EAD33?logo=playwright&logoColor=white)
![Coverage](https://img.shields.io/badge/Cobertura-95%25-2ECC71)
![License](https://img.shields.io/badge/License-Educacional-blue)

**Pipeline automatizado** que transforma as Release Notes da Salesforce em artefatos Markdown estruturados, com análise AI, classificação de impacto e distribuição multi-canal.

[📚 Documentação](https://fatal1tybarucco.github.io/Salesforce-WebDev/) · [🐛 Reportar Bug](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues) · [💡 Solicitar Feature](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues)

</div>

---

## 🌟 O Que Este Projeto Faz

A cada trimestre, a Salesforce lança centenas de novas funcionalidades espalhadas por dezenas de categorias. **Acompanhar manualmente é inviável.**

Este repositório automatiza todo o ciclo:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   🌐 Salesforce Help ──▶ 🤖 Scraper ──▶ 🧠 AI ──▶ 📦 Markdown     │
│        (SPA)              (Playwright)   (LLM)    (Estruturado)     │
│                                                                     │
│                           ──▶ 📧 Email ──▶ 💬 Slack ──▶ 🐙 GitHub  │
│                              (Digest)     (Webhook)    (Issues)     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ✨ Capacidades

| Capacidade | Descrição |
|:-----------|:----------|
| 🔍 **Detecção Automática** | Detecta novas releases comparando conteúdo com a versão anterior |
| 🎭 **Scraping SPA** | Playwright renderiza JavaScript completo do portal Salesforce Help |
| 🧠 **Classificação AI** | Classifica features por impacto (Alto/Médio/Baixo) e tipo via LLM |
| 📊 **Relatórios Inteligentes** | Changelog, regressões, diff, qualidade — tudo gerado por AI |
| 🔄 **Deduplicação** | Content-hash evita reprocessar conteúdo inalterado |
| 📧 **Notificações** | Email, Slack e Discord com filtros por perfil de interesse |
| 🐙 **GitHub Integration** | Issues automáticas, PRs com triage, badges dinâmicos |
| 🌐 **REST + GraphQL API** | Acesso programático a todos os dados via HTTP |
| 📈 **Dashboard Interativo** | HTML com busca, comparação, heatmap e exportação CSV/JSON |
| 🏥 **Health Monitoring** | Endpoints `/health`, `/ready`, `/metrics` (Prometheus) |

---

## 📦 Releases Catalogadas

<!-- RELEASE_BADGE -->
![Latest Release](https://img.shields.io/badge/Última%20Release-Summer%20'26-00A1E0?style=for-the-badge&logo=salesforce&logoColor=white)

<table>
<tr>
<td align="center" width="33%">
<img src="https://img.shields.io/badge/☀️-Summer_'26-FF6B35?style=for-the-badge" /><br/>
<strong>1.373 recursos</strong><br/>
22 categorias<br/>
<a href="./releases/summer_26/">📄 Explorar</a>
</td>
<td align="center" width="33%">
<img src="https://img.shields.io/badge/🌸-Spring_'26-FF69B4?style=for-the-badge" /><br/>
<strong>1.438 recursos</strong><br/>
21 categorias<br/>
<a href="./releases/spring_26/">📄 Explorar</a>
</td>
<td align="center" width="33%">
<img src="https://img.shields.io/badge/❄️-Winter_'26-00BFFF?style=for-the-badge" /><br/>
<strong>1.348 recursos</strong><br/>
19 categorias<br/>
<a href="./releases/winter_26/">📄 Explorar</a>
</td>
</tr>
</table>

> **📊 Total: 4.159 recursos** catalogados em **3 releases** sazonais do Salesforce.

<details>
<summary><b>☀️ Summer '26 — Detalhes por Categoria</b></summary>

<br/>

| Categoria | Recursos | Documentação |
|:----------|:--------:|:-------------|
| 🏭 Setores | 309 | [pt_BR](./releases/summer_26/pt_BR/setores.md) |
| 🛠️ Serviço | 198 | [pt_BR](./releases/summer_26/pt_BR/servico.md) |
| 💻 Desenvolvimento | 127 | [pt_BR](./releases/summer_26/pt_BR/desenvolvimento.md) |
| ⚙️ Automação | 118 | [pt_BR](./releases/summer_26/pt_BR/automacao.md) |
| 💰 Gerenciamento de Receita | 97 | [pt_BR](./releases/summer_26/pt_BR/gerenciamento_de_receita.md) |
| 📊 Data 360 | 72 | [pt_BR](./releases/summer_26/pt_BR/data_360.md) |
| 📈 Marketing | 64 | [pt_BR](./releases/summer_26/pt_BR/marketing.md) |
| 🔬 Análise de Dados | 58 | [pt_BR](./releases/summer_26/pt_BR/analise_de_dados.md) |
| 🔒 Segurança e Privacidade | 58 | [pt_BR](./releases/summer_26/pt_BR/seguranca_identidade_e_privacidade.md) |
| 💼 Vendas | 58 | [pt_BR](./releases/summer_26/pt_BR/vendas.md) |
| 🔧 Field Service | 48 | [pt_BR](./releases/summer_26/pt_BR/field_service.md) |
| 🤖 Agentforce | 37 | [pt_BR](./releases/summer_26/pt_BR/agentforce.md) |
| 📄 Salesforce Geral | 36 | [pt_BR](./releases/summer_26/pt_BR/salesforce_geral.md) |
| 🎨 Personalização | 33 | [pt_BR](./releases/summer_26/pt_BR/personalizacao.md) |
| 📱 Aplicativo Móvel | 17 | [pt_BR](./releases/summer_26/pt_BR/aplicativo_movel.md) |
| 🌐 Experience Cloud | 14 | [pt_BR](./releases/summer_26/pt_BR/experience_cloud.md) |
| 🏗️ OmniStudio | 9 | [pt_BR](./releases/summer_26/pt_BR/omnistudio.md) |
| 🔗 MuleSoft | 8 | [pt_BR](./releases/summer_26/pt_BR/mulesoft.md) |
| 📜 Documentação Legal | 6 | [pt_BR](./releases/summer_26/pt_BR/documentacao_legal.md) |
| ⚡ Hyperforce | 3 | [pt_BR](./releases/summer_26/pt_BR/hyperforce.md) |
| 💬 Slack Integration | 2 | [pt_BR](./releases/summer_26/pt_BR/integracoes_do_salesforce_para_slack.md) |
| 🤝 Partner Cloud | 1 | [pt_BR](./releases/summer_26/pt_BR/partner_cloud.md) |

</details>

<details>
<summary><b>🌸 Spring '26 — Detalhes por Categoria</b></summary>

<br/>

| Categoria | Recursos | Documentação |
|:----------|:--------:|:-------------|
| 🏭 Setores | 194 | [pt_BR](./releases/spring_26/pt_BR/setores.md) |
| 📱 Aplicativo Móvel | 187 | [pt_BR](./releases/spring_26/pt_BR/aplicativo_movel.md) |
| 🛠️ Serviço | 167 | [pt_BR](./releases/spring_26/pt_BR/servico.md) |
| ⚙️ Automação | 151 | [pt_BR](./releases/spring_26/pt_BR/automacao.md) |
| 💰 Gerenciamento de Receita | 131 | [pt_BR](./releases/spring_26/pt_BR/gerenciamento_de_receita.md) |
| 💻 Desenvolvimento | 97 | [pt_BR](./releases/spring_26/pt_BR/desenvolvimento.md) |
| 📈 Marketing | 72 | [pt_BR](./releases/spring_26/pt_BR/marketing.md) |
| 🔒 Segurança e Privacidade | 61 | [pt_BR](./releases/spring_26/pt_BR/seguranca_identidade_e_privacidade.md) |
| 🔬 Análise de Dados | 54 | [pt_BR](./releases/spring_26/pt_BR/analise_de_dados.md) |
| 📊 Data 360 | 53 | [pt_BR](./releases/spring_26/pt_BR/data_360.md) |
| 💼 Vendas | 85 | [pt_BR](./releases/spring_26/pt_BR/vendas.md) |
| 🔧 Field Service | 41 | [pt_BR](./releases/spring_26/pt_BR/field_service.md) |
| 🤖 Agentforce | 35 | [pt_BR](./releases/spring_26/pt_BR/agentforce.md) |
| 📄 Salesforce Geral | 38 | [pt_BR](./releases/spring_26/pt_BR/salesforce_geral.md) |
| 🌐 Experience Cloud | 21 | [pt_BR](./releases/spring_26/pt_BR/experience_cloud.md) |
| 🎨 Personalização | 18 | [pt_BR](./releases/spring_26/pt_BR/personalizacao.md) |
| 🏗️ OmniStudio | 10 | [pt_BR](./releases/spring_26/pt_BR/omnistudio.md) |
| 🔗 MuleSoft | 8 | [pt_BR](./releases/spring_26/pt_BR/mulesoft.md) |
| 📜 Documentação Legal | 6 | [pt_BR](./releases/spring_26/pt_BR/documentacao_legal.md) |
| ⚡ Hyperforce | 5 | [pt_BR](./releases/spring_26/pt_BR/hyperforce.md) |
| 🤝 Partner Cloud | 4 | [pt_BR](./releases/spring_26/pt_BR/partner_cloud.md) |

</details>

<details>
<summary><b>❄️ Winter '26 — Detalhes por Categoria</b></summary>

<br/>

| Categoria | Recursos | Documentação |
|:----------|:--------:|:-------------|
| 🏭 Setores | 459 | [pt_BR](./releases/winter_26/pt_BR/setores.md) |
| 💻 Desenvolvimento | 101 | [pt_BR](./releases/winter_26/pt_BR/desenvolvimento.md) |
| 📈 Marketing | 87 | [pt_BR](./releases/winter_26/pt_BR/marketing.md) |
| 🔬 Análise de Dados | 91 | [pt_BR](./releases/winter_26/pt_BR/analise_de_dados.md) |
| 🎨 Personalização | 65 | [pt_BR](./releases/winter_26/pt_BR/personalizacao.md) |
| 🔒 Segurança e Privacidade | 55 | [pt_BR](./releases/winter_26/pt_BR/seguranca_identidade_e_privacidade.md) |
| 💼 Vendas | 154 | [pt_BR](./releases/winter_26/pt_BR/vendas.md) |
| 🤝 Partner Cloud | 156 | [pt_BR](./releases/winter_26/pt_BR/partner_cloud.md) |
| 🛠️ Serviço | 41 | [pt_BR](./releases/winter_26/pt_BR/servico.md) |
| 🤖 Agentforce | 39 | [pt_BR](./releases/winter_26/pt_BR/agentforce.md) |
| 📄 Salesforce Geral | 32 | [pt_BR](./releases/winter_26/pt_BR/salesforce_geral.md) |
| 🔧 Field Service | 24 | [pt_BR](./releases/winter_26/pt_BR/field_service.md) |
| 🏗️ OmniStudio | 8 | [pt_BR](./releases/winter_26/pt_BR/omnistudio.md) |
| 🌐 Experience Cloud | 8 | [pt_BR](./releases/winter_26/pt_BR/experience_cloud.md) |
| 📱 Aplicativo Móvel | 7 | [pt_BR](./releases/winter_26/pt_BR/aplicativo_movel.md) |
| 📜 Documentação Legal | 11 | [pt_BR](./releases/winter_26/pt_BR/documentacao_legal.md) |
| ⚡ Hyperforce | 5 | [pt_BR](./releases/winter_26/pt_BR/hyperforce.md) |
| 🔗 MuleSoft | 4 | [pt_BR](./releases/winter_26/pt_BR/mulesoft.md) |
| 💬 Slack Integration | 1 | [pt_BR](./releases/winter_26/pt_BR/integracoes_do_salesforce_para_slack.md) |

</details>

---

## 🏗️ Como Funciona

### Fluxo do Pipeline

```mermaid
flowchart TB
    subgraph DETECT["🔍 1. DETECÇÃO"]
        A[Salesforce Help] -->|Comparar conteúdo| B{Nova release?}
        B -->|Não| C[Atualizar README]
        B -->|Sim| D[Identificar release]
    end

    subgraph SCRAPE["🎭 2. SCRAPING"]
        D --> E[Playwright Chromium]
        E -->|SPA JavaScript| F[Feature Impact HTML]
        E -->|Download| G[PDF Release-in-a-Box]
        F --> H[Rate Limiter + Circuit Breaker]
        H --> I[Cache content-hash]
    end

    subgraph PARSE["📋 3. PARSING"]
        I --> J[FeatureImpactParser]
        J -->|Extrair tabelas| K[Categorias + Features]
        J -->|Hierarquia| L[Árvore de tópicos]
    end

    subgraph GENERATE["📦 4. GERAÇÃO"]
        K --> M[MarkdownGenerator]
        L --> M
        M -->|pt_BR| N[releases/slug/pt_BR/*.md]
        M -->|en_US| O[releases/slug/en_US/*.md]
        M --> P[.meta.json]
        M --> Q[README.md]
    end

    subgraph AI["🧠 5. ANÁLISE AI"]
        P --> R[LLM Service]
        R -->|OpenAI / Gemini| S[Classificação de impacto]
        R --> T[Changelog inteligente]
        R --> U[Relatório de regressões]
        R --> V[Diff entre releases]
        R --> W[Resumo executivo]
    end

    subgraph NOTIFY["📤 6. DISTRIBUIÇÃO"]
        S --> X[GitHub Issues]
        T --> Y[Email Digest]
        U --> Z[Slack / Discord]
        V --> AA[CHANGELOG.md]
        W --> AB[QUALITY_REPORT.md]
    end

    style DETECT fill:#E8F5E9,stroke:#4CAF50,color:#000
    style SCRAPE fill:#E3F2FD,stroke:#2196F3,color:#000
    style PARSE fill:#FFF3E0,stroke:#FF9800,color:#000
    style GENERATE fill:#F3E5F5,stroke:#9C27B0,color:#000
    style AI fill:#FCE4EC,stroke:#E91E63,color:#000
    style NOTIFY fill:#E0F7FA,stroke:#00BCD4,color:#000
```

### Arquitetura em Camadas

```mermaid
flowchart LR
    subgraph ENTRADA["🌐 Entrada"]
        SF[Salesforce Help<br/>SPA JavaScript]
        TH[Trailhead<br/>Módulos]
    end

    subgraph PIPELINE["⚙️ Pipeline"]
        SCRAPER[🎭 Scraper<br/>Playwright]
        PARSER[📋 Parser<br/>HTML/MD]
        LLM[🧠 LLM<br/>OpenAI/Gemini]
        GEN[📦 Generator<br/>Markdown]
    end

    subgraph RESILIENCIA["🛡️ Resiliência"]
        CB[⚡ Circuit Breaker]
        RL[🚦 Rate Limiter]
        CACHE[💾 Cache Manager]
        RETRY[🔄 Retry + Backoff]
    end

    subgraph SAIDA["📤 Saída"]
        MD[📄 Markdown]
        API[🌐 REST/GraphQL]
        NOTIF[📧 Email/Slack]
        GH[🐙 GitHub]
        DASH[📊 Dashboard]
    end

    SF --> SCRAPER
    TH --> GEN
    SCRAPER --> PARSER
    PARSER --> LLM
    LLM --> GEN

    SCRAPER --- CB
    SCRAPER --- RL
    SCRAPER --- CACHE
    SCRAPER --- RETRY

    GEN --> MD
    GEN --> API
    GEN --> NOTIF
    GEN --> GH
    GEN --> DASH

    style ENTRADA fill:#E8F5E9,stroke:#4CAF50,color:#000
    style PIPELINE fill:#E3F2FD,stroke:#2196F3,color:#000
    style RESILIENCIA fill:#FFF3E0,stroke:#FF9800,color:#000
    style SAIDA fill:#F3E5F5,stroke:#9C27B0,color:#000
```

---

## ⚡ Quick Start

### Pré-requisitos

| Requisito | Versão | Instalação |
|:----------|:-------|:-----------|
| Python | 3.14+ | [python.org](https://www.python.org/) |
| uv | Latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Playwright | Chromium | `uv run playwright install chromium` |

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/Fatal1tyBarucco/Salesforce-WebDev.git
cd Salesforce-WebDev

# 2. Instale dependências
uv sync --extra dev

# 3. Instale o navegador Playwright
uv run playwright install chromium

# 4. Configure as chaves LLM (pelo menos uma)
export OPENAI_API_KEY="sk-..."    # ou
export GOOGLE_API_KEY="AIza..."   # ou
export OPENCODE_API_KEY="..."     # ou
export MIMOCODE_API_KEY="..."
```

### Execução

```bash
# Pipeline completo
uv run python src/main.py

# Release específica
uv run python src/main.py --release summer_26

# Dry run (sem escrever arquivos)
uv run python src/main.py --dry-run

# Iniciar API server
uv run python -c "from src.api import start_api_server; start_api_server()"

# Iniciar health server
uv run python -c "from src.health import start_health_server; start_health_server()"
```

---

## 🛡️ Resiliência

O pipeline foi projetado para operar de forma autônoma e resiliente:

```mermaid
stateDiagram-v2
    [*] --> Fechado: Início

    Fechado --> Fechado: ✅ Sucesso
    Fechado --> Aberto: ❌ 3 falhas consecutivas

    Aberto --> Aberto: 🚫 Rejeita requests
    Aberto --> MeioAberto: ⏱️ Cooldown 60s

    MeioAberto --> Fechado: ✅ Probe sucesso
    MeioAberto --> Aberto: ❌ Probe falha

    state Fechado {
        [*] --> Normal
        Normal --> Normal: Operação normal
    }

    state Aberto {
        [*] --> Cooldown
        Cooldown --> Cooldown: Aguardando
    }
```

| Componente | Configuração | Comportamento |
|:-----------|:-------------|:--------------|
| ⚡ **Circuit Breaker** | 3 falhas → 60s cooldown | Para após falhas consecutivas, retoma automaticamente |
| 🚦 **Rate Limiter** | Token-bucket, 2 req/s | Respeita limites do Salesforce |
| 🔄 **Retry** | 5 tentativas, backoff exponencial | `2^n` segundos + jitter aleatório |
| 💾 **Cache TTL** | 24h (metadata), 30d (content-hash) | Evita refetch de conteúdo inalterado |
| ⏱️ **Timeout** | 30s (HTTP), 60s (LLM) | Nunca fica preso indefinidamente |

---

## 🧪 Qualidade de Código

```bash
# Quality gate completa (mesma do CI)
uv run ruff check src/          # Linter
uv run black --check src/       # Formatter
uv run mypy src/                # Type checker (strict)
uv run pytest tests/ --cov=src --cov-fail-under=95  # Tests + coverage
```

| Ferramenta | Configuração | Status |
|:-----------|:-------------|:------:|
| 🐍 **Python** | 3.14, type hints completos | ✅ |
| 🔍 **Mypy** | `strict = true` | ✅ |
| ⚡ **Ruff** | `line-length = 100` | ✅ |
| 🖤 **Black** | `target-version = py313` | ✅ |
| 🧪 **Pytest** | 95.71% cobertura | ✅ |
| 📦 **uv** | Lock file determinístico | ✅ |

---

## 🌐 API

O projeto expõe uma API REST + GraphQL standalone (zero dependências externas):

### REST

```bash
# Listar todas as releases
curl http://localhost:8081/releases

# Detalhes de uma release
curl http://localhost:8081/releases/summer_26

# Features de uma categoria
curl http://localhost:8081/releases/summer_26/categories/agentforce

# Comparar duas releases
curl http://localhost:8081/diff/summer_26/spring_26
```

### GraphQL

```bash
# Query flexível
curl -X POST http://localhost:8081/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ releases { name totalFeatures categories { name count } } }"}'
```

### Health & Metrics

```bash
# Health check
curl http://localhost:8080/health

# Readiness probe
curl http://localhost:8080/ready

# Prometheus metrics
curl http://localhost:8080/metrics
```

---

## 📁 Estrutura do Projeto

```
Salesforce-WebDev/
│
├── 📂 src/                          # Código fonte
│   ├── main.py                      # 🎯 Orquestrador principal + DI
│   ├── scraper.py                   # 🎭 Playwright + Circuit Breaker
│   ├── parser.py                    # 📋 Parser HTML/Markdown
│   ├── llm_service.py               # 🧠 Multi-provider LLM
│   ├── generator.py                 # 📦 Geração Markdown
│   ├── config.py                    # ⚙️ Configuração central
│   ├── exceptions.py                # ⚠️ Hierarquia de exceções
│   ├── circuit_breaker.py           # ⚡ Circuit Breaker unificado
│   ├── cache_manager.py             # 💾 Cache TTL + content-hash
│   ├── health.py                    # 🏥 Health checks + métricas
│   ├── api.py                       # 🌐 REST + GraphQL + OpenAPI
│   ├── notifications.py             # 📧 Email/Slack/Discord
│   ├── salesforce.py                # 🔗 Trailhead integration
│   ├── feature_classifier.py        # 🏷️ Classificação via LLM
│   ├── impact_analyzer.py           # 📊 Análise de impacto
│   ├── issue_triage.py              # 🐙 Triage automático
│   ├── logger.py                    # 📝 Logging JSON estruturado
│   ├── translator.py                # 🌍 Tradução via LLM
│   ├── dashboard.py                 # 📈 Dashboard HTML interativo
│   └── automation/                  # 🤖 Pacote de automação AI
│       ├── service.py               #    Facade principal
│       ├── reporting.py             #    Relatórios AI
│       ├── comparison.py            #    Comparação entre releases
│       ├── impact.py                #    Scores de impacto
│       ├── content.py               #    Deduplicação
│       ├── export.py                #    Exportação JSON/CSV
│       ├── github_ops.py            #    GitHub Issues
│       ├── notifications.py         #    Notificações filtradas
│       ├── models.py                #    Dataclasses
│       └── badge.py                 #    Badges dinâmicos
│
├── 📂 releases/                     # 📄 Artefatos Markdown
│   ├── summer_26/
│   ├── spring_26/
│   └── winter_26/
│
├── 📂 tests/                        # 🧪 Testes pytest
├── 📂 docs/                         # 📚 Documentação MkDocs
├── 📂 .github/workflows/            # 🔄 CI/CD GitHub Actions
│
├── mkdocs.yml                       # 📖 Config MkDocs
├── pyproject.toml                   # 📦 Config do projeto
└── uv.lock                          # 🔒 Lock file
```

---

## 🤝 Contribuição

```mermaid
flowchart LR
    A[Fork] --> B[Branch]
    B --> C[Code]
    C --> D[Quality Gate]
    D --> E[PR]
    E --> F[Review]
    F --> G[Merge]

    style A fill:#E8F5E9,stroke:#4CAF50,color:#000
    style B fill:#E3F2FD,stroke:#2196F3,color:#000
    style C fill:#FFF3E0,stroke:#FF9800,color:#000
    style D fill:#FCE4EC,stroke:#E91E63,color:#000
    style E fill:#F3E5F5,stroke:#9C27B0,color:#000
    style F fill:#E0F7FA,stroke:#00BCD4,color:#000
    style G fill:#E8F5E9,stroke:#4CAF50,color:#000
```

1. **Fork** o repositório
2. Crie uma branch: `git checkout -b feature/minha-feature`
3. Instale dependências: `uv sync --extra dev`
4. Execute a quality gate completa:
   ```bash
   uv run ruff check src/ && uv run black --check src/ && uv run mypy src/ && uv run pytest --cov=src --cov-fail-under=95
   ```
5. Commit: `git commit -m 'feat: descrição da alteração'`
6. Push: `git push origin feature/minha-feature`
7. Abra um **Pull Request**

---

## 📄 Licença

Este projeto é mantido para fins educacionais e de referência técnica.

---

<div align="center">

**Feito com ☕ e código Python**

[⬆ Voltar ao topo](#-salesforce-release-notes-intelligence)

</div>
