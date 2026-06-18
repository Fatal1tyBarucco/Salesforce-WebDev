![Salesforce Release Intelligence](./assets/banner.png)

# 🚀 Salesforce Release Notes Intelligence

Pipeline automatizado para extração, classificação e versionamento das **Salesforce Release Notes** como artefatos Markdown estruturados (*Knowledge-as-Code*).

### ⚙️ CI/CD Status & Conformidade

[![Python Quality & Validation](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python&logoColor=white) 
![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?logo=playwright&logoColor=white) 
![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg) 
![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg) 
![Black](https://img.shields.io/badge/Formatter-Black-000000.svg)

| Tecnologia / Ferramenta | Descrição | Status no Pipeline |
| :--- | :--- | :---: |
| 🐍 **Python 3.14** | Ambiente de execução principal | `Conforme` |
| 🎭 **Playwright** | Scraper Headless para aplicações SPA do Salesforce Help | `Ativo` |
| 🧪 **Pytest** | Suíte de testes unitários automatizados | `100% Cobertura` |
| 🔍 **Mypy** | Verificação estática de tipos com modo estrito | `Strict` |
| ⚡ **Ruff & Black** | Linter e formatação estrita de código (line-length = 100) | `Conforme` |

---

## 📌 Visão Geral

Este repositório atua como uma **Base de Conhecimento Dinâmica (Knowledge Base)** que captura, estrutura e documenta as funcionalidades, atualizações de segurança e alterações arquiteturais (como Apex, LWC, Flow e Integrações) introduzidas nas releases periódicas da Salesforce.

A estrutura é desenhada para suportar revisões rápidas por Arquitetos e Desenvolvedores, mantendo um log histórico em formato legível (Markdown) nativo do repositório.

## ⚙️ Arquitetura de Atualização Dinâmica

A governança do repositório é mantida por meio de processos automatizados que garantem que as últimas releases sejam extraídas, transformadas e carregadas (ETL) no repositório sem intervenção manual, assegurando a integridade da documentação.

```mermaid
graph TD
    A[Salesforce Release Notes] -->|Web Scraping / API| B(GitHub Actions Workflow)
    B -->|Markdown Generator| C{Processamento de Dados}
    C -->|Parse Categorias| D[Diretórios /releases/]
    C -->|Update Dinâmico| E[README.md Index]
    D --> F((Commit Automático))
    E --> F
    F --> G[Repositório Atualizado]
    
    classDef salesforce fill:#00A1E0,stroke:#fff,stroke-width:2px,color:#fff;
    class A salesforce;

```

---

## 📋 Releases Disponíveis

{% comment %} RELEASE_INDEX_START {% endcomment %}

### ☀️ Summer '26


<details>
<summary><b>📄 Documentação legal (6 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/documentacao_legal.md](./releases/summer_26/documentacao_legal.md)

</details>


<details>
<summary><b>📄 Salesforce geral (31 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/salesforce_geral.md](./releases/summer_26/salesforce_geral.md)

</details>


<details>
<summary><b>📄 Agentforce (19 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/agentforce.md](./releases/summer_26/agentforce.md)

</details>


<details>
<summary><b>📄 Análise de dados (33 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/analise_de_dados.md](./releases/summer_26/analise_de_dados.md)

</details>


<details>
<summary><b>📄 Automação (81 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/automacao.md](./releases/summer_26/automacao.md)

</details>


<details>
<summary><b>📄 Commerce (91 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/commerce.md](./releases/summer_26/commerce.md)

</details>


<details>
<summary><b>📄 Personalização (27 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/personalizacao.md](./releases/summer_26/personalizacao.md)

</details>


<details>
<summary><b>📄 Data 360 (37 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/data_360.md](./releases/summer_26/data_360.md)

</details>


<details>
<summary><b>📄 Desenvolvimento (102 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/desenvolvimento.md](./releases/summer_26/desenvolvimento.md)

</details>


<details>
<summary><b>📄 Experience Cloud (14 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/experience_cloud.md](./releases/summer_26/experience_cloud.md)

</details>


<details>
<summary><b>📄 Field Service (37 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/field_service.md](./releases/summer_26/field_service.md)

</details>


<details>
<summary><b>📄 Hyperforce (3 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/hyperforce.md](./releases/summer_26/hyperforce.md)

</details>


<details>
<summary><b>📄 Setores (327 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/setores.md](./releases/summer_26/setores.md)

</details>


<details>
<summary><b>📄 Marketing (53 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/marketing.md](./releases/summer_26/marketing.md)

</details>


<details>
<summary><b>📄 MuleSoft (6 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/mulesoft.md](./releases/summer_26/mulesoft.md)

</details>


<details>
<summary><b>📄 Aplicativo móvel (14 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/aplicativo_movel.md](./releases/summer_26/aplicativo_movel.md)

</details>


<details>
<summary><b>📄 OmniStudio (10 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/omnistudio.md](./releases/summer_26/omnistudio.md)

</details>


<details>
<summary><b>📄 Gerenciamento de receita (96 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/gerenciamento_de_receita.md](./releases/summer_26/gerenciamento_de_receita.md)

</details>


<details>
<summary><b>📄 Vendas (56 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/vendas.md](./releases/summer_26/vendas.md)

</details>


<details>
<summary><b>📄 Integrações do Salesforce para Slack (2 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/integracoes_do_salesforce_para_slack.md](./releases/summer_26/integracoes_do_salesforce_para_slack.md)

</details>


<details>
<summary><b>📄 Segurança, identidade e privacidade (44 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/seguranca_identidade_e_privacidade.md](./releases/summer_26/seguranca_identidade_e_privacidade.md)

</details>


<details>
<summary><b>📄 Serviço (188 recursos)</b></summary>

> 📄 Detalhes completos: [./releases/summer_26/servico.md](./releases/summer_26/servico.md)

</details>

{% comment %} RELEASE_INDEX_END {% endcomment %}

---

## 🛠️ Stack Tecnológico & Automação

O controle de versão e extração de dados utiliza as seguintes ferramentas:

* **GitHub Actions:** Orquestração de rotinas diárias/semanais (Cron Jobs) para verificar novas atualizações.
* **Markdown:** Estruturação "Enterprise-grade" visando leitura técnica otimizada.
* **Python (Playwright):** Extração defensiva de dados do ecossistema oficial Salesforce com renderização SPA headless.

## 🤝 Como Contribuir

1. Faça o **Fork** do projeto
2. Crie uma nova branch com a sua feature: `git checkout -b feature/minha-feature`
3. Faça o commit de forma detalhada e técnica: `git commit -m 'feat: Implementação de parser para novos limites de governor limits no Apex'`
4. Envie a branch: `git push origin feature/minha-feature`
5. Abra um **Pull Request** detalhando a arquitetura ou correção proposta.

---
