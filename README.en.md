<div align="center">

<img src="./assets/banner1.png" alt="Salesforce Release Intelligence" width="800" />

</div>

# 🚀 Salesforce Release Notes Intelligence

Automated pipeline for extraction, classificação e versionamento das **Salesforce Release Notes** como artefatos Markdown estruturados (*Knowledge-as-Code*).

### ⚙️ CI/CD Status & Conformidade

<!-- RELEASE_BADGE -->
![Release](https://img.shields.io/badge/Release-Winter%20%2727-2196F3?style=flat)
[![Python Quality & Validation](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/python-quality.yml)
[![Release Notes Pipeline](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/release_notes_pipeline.yml/badge.svg)](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/actions/workflows/release_notes_pipeline.yml)
![Python](https://img.shields.io/badge/Python-3.14-blue.svg?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Headless_SPA-green.svg?logo=playwright&logoColor=white)
![Mypy](https://img.shields.io/badge/Mypy-Strict_Mode-blue.svg)
![Ruff](https://img.shields.io/badge/Ruff-Linter-black.svg)
![uv](https://img.shields.io/badge/uv-Package_Manager-blue.svg)

| Technology / Tool | Description | Pipeline Status |
| :--- | :--- | :---: |
| 🐍 **Python 3.14** | Ambiente de execução principal | `Conforme` |
| 🎭 **Playwright** | Scraper Headless para aplicações SPA do Salesforce Help | `Ativo` |
| 🧪 **Pytest** | Suíte de testes unitários automatizados | `450+ testes` |
| 🔍 **Mypy** | Verificação estática de tipos com modo estrito | `Strict` |
| ⚡ **Ruff & Black** | Linter e formatação estrita de código (line-length = 100) | `Conforme` |
| 📦 **uv** | Gerenciamento de dependências com lock file determinístico | `Ativo` |

---

## 📖 Overview

Este repositório contém um pipeline ETL assíncrono para scraping das *Salesforce Release Notes*, processamento local para classificação e sumarização, e geração de documentação estática via **MkDocs**.

## 🏗️ System Architecture

```mermaid
flowchart LR
    A[Salesforce Help] -->|Playwright SPA| B[scraper.py]
    B -->|DOM Parsing| C[parser.py]
    C -->|Feature Impact| D[generator.py]
    D -->|Markdown| E[releases/]
    D -->|Update| F[README.md]
    E -->|Jekyll| G[GitHub Pages]
    F -->|Jekyll| G

    B -->|Retry + Circuit Breaker| H{Resilience Layer}
    H -->|Cache Hit| I[cache/]
    H -->|Cache Miss| A
```

**Princípios de Design:**
* **Separação de Conceitos (SoC):** Camadas isoladas para rede (`scraper.py`), parsing (`parser.py`), geração (`generator.py`)
* **I/O Não Bloqueante:** `asyncio` + Playwright async para processamento paralelo
* **Resiliência:** Circuit Breaker + Token-bucket rate limiter + Exponential backoff com jitter

## ⚙️ Pré-requisitos e Instalação

Este projeto utiliza `uv` para gerenciamento determinístico de dependências.

```bash
# Instale o uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone e instale
git clone https://github.com/Fatal1tyBarucco/Salesforce-WebDev.git
cd Salesforce-WebDev
uv sync

# Instale browsers do Playwright
uv run playwright install chromium
```

## 🚀 Uso e Execução

```bash
# Executar pipeline completo
uv run python -m src.main

# Executar release específica
uv run python -m src.main --release summer_26

# Dry run (sem escrever arquivos)
uv run python -m src.main --dry-run
```

## 🛡️ Governança e Resiliência

| Componente | Configuração | Description |
| :--- | :--- | :--- |
| **Rate Limiter** | 2 req/s, token-bucket | Evita throttling do Salesforce |
| **Circuit Breaker** | 3 falhas → cooldown 60s | Para requisições após falhas consecutivas |
| **Cache TTL** | 24 horas | Previne refetch de conteúdo não alterado |
| **Exponential Backoff** | Base 2s + jitter | Retry inteligente com anti-thundering-herd |

## 🧪 Testes e Qualidade

```bash
# Executar testes
uv run pytest tests/

# Com cobertura
uv run pytest tests/ --cov=src --cov-report=term-missing

# Quality gate (ordem CI)
uv run ruff check src/
uv run black --check src/
uv run mypy src/
```

**Meta:** Cobertura >99%, zero erros de tipo, zero warnings de lint.

---



















































## 📋 Releases Disponíveis

<div style="padding:12px;margin-bottom:20px;border:1px solid #d0d7de;border-radius:6px;background:#f6f8fa;text-align:center;"><strong>🌐 Language / Idioma:</strong> <strong>🇺🇸 English</strong> | <a href="./README.md">🇧🇷 Português</a></div>

### ❄️ Winter '27

> 📊 **Executive Summary:** A release Winter '27 apresenta um conjunto robusto de 1.123 novos recursos e aprimoramentos distribuídos por 19 categorias, representando a evolução contínua da plataforma Salesforce com foco em Agentforce, Experience Cloud e soluções setoriais. O destaque central é a consolidação do Agentforce como pilar estratégico da plataforma, com 129 recursos dedicados à criação, configuração e otimização de agentes de IA autônomos para diferentes cenários de negócio. A categoria Setores lidera em volume com 286 recursos, oferecendo soluções especializadas para indústrias específicas, desde manufatura até serviços financeiros e saúde. O Experience Cloud emerge como segunda maior categoria com 143 recursos, focando em experiências digitais modernas baseadas em LWR (Lightning Web Runtime) com novos templates, componentes e capacidades de engajamento. O Serviço (140 recursos) transforma a central de atendimento com Agentforce, introduzindo roteamento inteligente, assistentes de IA para agentes e métricas de qualidade de atendimento. O Gerenciamento de Receita (123 recursos) aprimora processos de cotação, precificação e faturamento com automação avançada. O Partner Cloud (38 recursos) expande as capacidades de ecossistema, enquanto o Field Service (37 recursos) melhora a gestão de operações de campo. A plataforma também avança em Segurança (25 recursos), Automação (72 recursos) e Data 360 (7 recursos), garantindo que as organizações possam operar com maior eficiência, segurança e inteligência artificial integrada em todos os processos.


> 📌 **Key Themes:** Agentforce para Todos • Experiências Digitais Modernas • Soluções Setoriais Profundas • Atendimento Autônomo • Ecosistema de Parceiros


> 🎯 **Strategic Impact:** A Winter '27 representa uma release focada em experiência digital e agentes autônomos, com impacto direto na capacidade das organizações de oferecer atendimento ao cliente de alta qualidade via Agentforce e criar portais web modernos via Experience Cloud. As 286 inovações em Setores permitem que empresas de qualquer indústria implementem soluções Salesforce com mendalamas funcionalidades específicas do seu setor, reduzindo time-to-value em implementações verticais.


> ⚠️ **Migration Notes:** A Winter '27 mantém a compatibilidade com versões anteriores, mas recomenda-se que organizações usando Experience Cloud com templates Force.com avaliem a migração para LWR. Usuários do Agentforce devem revisar as novas políticas de uso de dados e configurações de privacidade dos agentes.


<details>
<summary><b>📄 Salesforce General (28 features)</b></summary>


> A categoria Salesforce Geral reúne 28 recursos que abrangem mudanças transversais na plataforma. Incluem-se atualizações de interface Lightning Experience, melhorias de performance em carregamento de páginas, correções de bugs e aprimoramentos gerais que beneficiam todas as implementações Salesforce.

> 📄 Full details: [./releases/winter_27/en_US/salesforce_geral.md](./releases/winter_27/en_US/salesforce_geral.md)

</details>


<details>
<summary><b>📄 Data Analysis (26 features)</b></summary>


> A Análise de Dados apresenta 26 recursos focados em capacidades analíticas da plataforma. Os recursos incluem novos conectores para fontes de dados externas, melhorias em visualizações de dashboards e funcionalidades de business intelligence que permitem às organizações extrair insights mais profundos. A integração com Salesforce Einstein Analytics oferece capacidades de análise preditiva acessíveis a usuários de negócio sem necessidade de código.

> 📄 Full details: [./releases/winter_27/en_US/analise_de_dados.md](./releases/winter_27/en_US/analise_de_dados.md)

</details>


<details>
<summary><b>📄 Automation (72 features)</b></summary>


> A Automação oferece 72 recursos que expandem as capacidades do Flow Builder e processos de negócio automatizados. Destaques incluem novos gatilhos de fluxo para eventos do Agentforce, ações de automação baseadas em decisões de IA e melhorias na experiência de criação de fluxos com interface simplificada. A categoria também introduz recursos de orchestration para coordenar múltiplos fluxos e agentes em processos de negócio complexos.

> 📄 Full details: [./releases/winter_27/en_US/automacao.md](./releases/winter_27/en_US/automacao.md)

</details>


<details>
<summary><b>📄 Data 360 (7 features)</b></summary>


> O Data 360 apresenta 7 recursos focados em conectividade e qualidade de dados. Os recursos incluem novos conectores para plataformas de dados externas, ferramentas de profilamento de dados e capacidades de governança que permitem às organizações manter dados confiáveis para análises e decisões de negócio.

> 📄 Full details: [./releases/winter_27/en_US/data_360.md](./releases/winter_27/en_US/data_360.md)

</details>


<details>
<summary><b>📄 Experience Cloud (143 features)</b></summary>


> O Experience Cloud lidera em volume de conteúdo com 143 recursos, focando na modernização de experiências digitais. A transição para Lightning Web Runtime (LWR) como tecnologia base traz novos templates de sites, componentes otimizados para performance e capacidades de personalização avançadas. Novos recursos incluem publicação de artigos com IA generativa, portal de autoatendimento remodelado e integrações profundas com Slack para colaboração em comunidades. A plataforma também introduz melhorias em SEO, analytics de comportamento de visitantes e ferramentas de A/B testing para otimização deConversion.

> 📄 Full details: [./releases/winter_27/en_US/experience_cloud.md](./releases/winter_27/en_US/experience_cloud.md)

</details>


<details>
<summary><b>📄 Field Service (37 features)</b></summary>


> O Field Service apresenta 37 recursos que aprimoram a gestão de serviços de campo. Destaques incluem melhorias no algoritmo de agendamento inteligente, novas capacidades mobile para técnicos de campo e integração aprimorada com IoT para manutenção preditiva. A categoria também introduz recursos de realidade aumentada para辅助 técnicos em diagnósticos remotos.

> 📄 Full details: [./releases/winter_27/en_US/field_service.md](./releases/winter_27/en_US/field_service.md)

</details>


<details>
<summary><b>📄 Hyperforce (5 features)</b></summary>


> A Hyperforce apresenta 5 recursos focados na infraestrutura de nuvem de próxima geração. Os recursos incluem expansão para novas regiões de nuvem pública, aprimoramentos de segurança de infraestrutura e ferramentas de monitoring para garantir alta disponibilidade e performance.

> 📄 Full details: [./releases/winter_27/en_US/hyperforce.md](./releases/winter_27/en_US/hyperforce.md)

</details>


<details>
<summary><b>📄 Industries (286 features)</b></summary>


> A categoria Setores lidera em volume com 286 recursos, oferecendo soluções especializadas para indústrias específicas. Abrange Automotivo (com Agentforce para Automotive e gestão de concessionárias), Saúde (com Epic Integration e Patient 360), Serviços Financeiros (com Wealth Management Cloud e Banking), Manufatura (com Manufacturing Cloud e gestão de cadeia de suprimentos), Varejo (com Commerce Cloud e Retail), Educação (com Education Cloud e gestão de alunos) e Utilities (com utilities cloud para setor elétrico). O destaque é a profundidade das soluções setoriais que permitem implementações turnkey para cada indústria.

> 📄 Full details: [./releases/winter_27/en_US/setores.md](./releases/winter_27/en_US/setores.md)

</details>


<details>
<summary><b>📄 Marketing (1 features)</b></summary>


> A categoria Marketing apresenta 1 recurso focado em automação de campanhas. Este recurso introduz novas capacidades de segmentação que permitem marketers criar públicos-alvo mais precisos para campanhas de marketing direcionado.

> 📄 Full details: [./releases/winter_27/en_US/marketing.md](./releases/winter_27/en_US/marketing.md)

</details>


<details>
<summary><b>📄 MuleSoft (1 features)</b></summary>


> O MuleSoft apresenta 1 recurso focado em conectividade e APIs. O recurso representa a continuação do compromisso da Salesforce com integração via MuleSoft como camada de integração central para arquiteturas enterprise.

> 📄 Full details: [./releases/winter_27/en_US/mulesoft.md](./releases/winter_27/en_US/mulesoft.md)

</details>


<details>
<summary><b>📄 Partner Cloud (38 features)</b></summary>


> A Partner Cloud apresenta 38 recursos focados em ecossistemas de parceiros. Destaques incluem melhorias no portal de parceiros, ferramentas de registro e qualificação de leads compartilhados, e capacidades de comunicação entre organizações dentro do ecossistema Salesforce. A categoria também introduz recursos de co-selling e incentive management.

> 📄 Full details: [./releases/winter_27/en_US/partner_cloud.md](./releases/winter_27/en_US/partner_cloud.md)

</details>


<details>
<summary><b>📄 Revenue Management (123 features)</b></summary>


> O Gerenciamento de Receita conta com 123 recursos para otimização de processos de CPQ (Configure, Price, Quote) e gestão de faturamento. Os recursos incluem configuração de produtos com IA, precificação dinâmica baseada em múltiplos fatores, geração de cotações automatizada e ferramentas de aprovação de pedidos. A categoria também aprimora capacidades de reconhecimento de receita e gestão de assinaturas.

> 📄 Full details: [./releases/winter_27/en_US/gerenciamento_de_receita.md](./releases/winter_27/en_US/gerenciamento_de_receita.md)

</details>


<details>
<summary><b>📄 Sales (44 features)</b></summary>

> 📄 Full details: [./releases/winter_27/en_US/vendas.md](./releases/winter_27/en_US/vendas.md)

</details>


<details>
<summary><b>📄 Salesforce Slack Integrations (7 features)</b></summary>


> A categoria de Integrações Slack apresenta 7 recursos que aprofundam a colaboração entre Salesforce e Slack. Novos recursos incluem sync bidirecional de registros, notificações contextuais em canais e ferramentas de search que permitem buscar dados do Salesforce diretamente do Slack.

> 📄 Full details: [./releases/winter_27/en_US/integracoes_do_salesforce_para_slack.md](./releases/winter_27/en_US/integracoes_do_salesforce_para_slack.md)

</details>


<details>
<summary><b>📄 Security, Identity & Privacy (25 features)</b></summary>


> A Segurança, Identidade e Privacidade reúne 25 recursos críticos para proteção de dados e gestão de acessos. Destaques incluem novas políticas de uso de dados para Agentforce, controles de acesso granulares baseados em contexto, ferramentas de auditoria de atividades de IA e aprimoramentos em políticas de senha e autenticação multifator.

> 📄 Full details: [./releases/winter_27/en_US/seguranca_identidade_e_privacidade.md](./releases/winter_27/en_US/seguranca_identidade_e_privacidade.md)

</details>


<details>
<summary><b>📄 Service (140 features)</b></summary>


> A categoria Serviço apresenta 140 recursos, transformando o Service Cloud em Agentforce Service. Destaques incluem a central de contato Agentforce com roteamento inteligente baseado em IA, assistentes de resposta para agentes com conhecimento da base de artigos, métricas de qualidade em tempo real e análise de sentimento de conversas. A categoria também introduz recursos de autoatendimento com IA generativa, portal de casos remodelado e integrações com WhatsApp Business e outras plataformas de messaging.

> 📄 Full details: [./releases/winter_27/en_US/servico.md](./releases/winter_27/en_US/servico.md)

</details>


<details>
<summary><b>📄 Legal Documentation (8 features)</b></summary>


> A categoria Documentação Legal reúne 8 recursos dedicados a atualizações de termos, políticas e conformidade legal da plataforma. Inclui atualizações sobre navegadores compatíveis, políticas de uso de dados e documentação de conformidade com regulamentações de privacidade. É essencial que administradores e equipes jurídicas revisem estes recursos para manter conformidade organizacional.

> 📄 Full details: [./releases/winter_27/en_US/documentacao_legal.md](./releases/winter_27/en_US/documentacao_legal.md)

</details>


<details>
<summary><b>📄 OmniStudio (3 features)</b></summary>


> O OmniStudio conta com 3 recursos que aprimoram as capacidades de configuração de processos digitais. Os recursos incluem melhorias em flexcards para experiências mais responsivas, updates em OmniScripts para fluxos de navegação e ferramentas de debugging para desenvolvedores.

> 📄 Full details: [./releases/winter_27/en_US/omnistudio.md](./releases/winter_27/en_US/omnistudio.md)

</details>


<details>
<summary><b>📄 Agentforce (129 features)</b></summary>


> O Agentforce consolida-se como o centro da estratégia de IA da Salesforce com 129 recursos na Winter '27. A plataforma expande o Agentforce Builder com novos templates de agentes para casos de uso específicos como vendas, serviço e operações. O Agentforce for Service introduz roteamento inteligente de casos baseado em IA, assistentes de resposta com conhecimento da base de artigos e métricas de qualidade de atendimento em tempo real. Novos recursos incluem análise de sentimento de conversas, resumo automático de casos e suggestions de artigos relevantes durante interações. Para desenvolvedores, o Agentforce SDK permite criação de agentes customizados com integração a sistemas externos via APIs REST e GraphQL.

> 📄 Full details: [./releases/winter_27/en_US/agentforce.md](./releases/winter_27/en_US/agentforce.md)

</details>



<details>
<summary><h3>☀️ Summer '26</h3></summary>

> 📊 **Executive Summary:** A release Summer '26 representa uma atualização significativa do ecossistema Salesforce, com 1373 novos recursos distribuídos em 22 categorias.


<details>
<summary><b>📄 Legal Documentation (6 features)</b></summary>


> A categoria Documentação legal reúne 6 recursos referentes a documentação legal. Esta categoria abrange melhorias e novas funcionalidades para documentação legal.

> 📄 Full details: [./releases/summer_26/en_US/documentacao_legal.md](./releases/summer_26/en_US/documentacao_legal.md)

</details>



<details>

<summary><h3>🌸 Spring '26</h3></summary>

> 📊 **Executive Summary:** A release Salesforce Spring '26 apresenta um impressionante conjunto de 1.438 novos recursos e aprimoramentos distribuídos por 21 categorias, consolidando a plataforma como referência em inovação para CRM e automação de negócios. O destaque central desta release é a evolução do Agentforce, que agora conta com o Agentforce Builder disponível ao público em geral, permitindo a criação de agentes de IA mais complexos e sofisticados. A categoria Serviço lidera em volume com 167 recursos, transformando o Service Cloud no Serviço Agentforce, com novas capacidades de central de contato, voz, messaging e gerenciamento de serviço de TI. O Aplicativo Móvel acompanha com 187 recursos, garantindo que as equipes possam operar com plena funcionalidade em dispositivos móveis. A Automação oferece 151 recursos incluindo avanços significativos no Flow Builder, com geração de fluxos por IA agora disponível ao público em geral, orquestração de fluxos aprimorada e novas capacidades de processamento em lote de prompts. Os Setores trazem o maior volume de inovações setoriais com 194 recursos, abrangendo desde automotivo e finanças até saúde e serviços públicos. O Gerenciamento de Receita apresenta 131 recursos para otimização de CPQ e billing. Em Vendas, com 85 recursos, o Sales Cloud se transforma em Agentforce Sales, introduzindo geração de leads autônoma, qualificação por IA e nutrição de leads automatizada. A plataforma também avança em Segurança, Identidade e Privacidade com 61 recursos, incluindo novas políticas de aplicativos conectados, login sem senha com chaves de acesso e aprimoramentos no Salesforce Shield. A Análise de Dados com 54 recursos e o Data 360 com 53 recursos expandem as capacidades de insights e gestão de dados. O Desenvolvimento com 97 recursos oferece novas ferramentas para desenvolvedores, incluindo tipos personalizados do Lightning para Agentforce. Com 72 recursos, o Marketing aprimora campanhas e engajamento. Experience Cloud (21 recursos), Personalização (18 recursos), Field Service (41 recursos), MuleSoft (8 recursos), OmniStudio (10 recursos), Hyperforce (5 recursos), Partner Cloud (4 recursos) e Documentação Legal (6 recursos) completam o panorama desta release abrangente. A Spring '26 representa um marco na estratégia da Salesforce de integrar IA generativa e agentes autônomos em todas as camadas da plataforma, capacitando organizações de todos os tamanhos a automatizar processos, aumentar a produtividade e oferecer experiências personalizadas em escala.


<details>
<summary><b>📄 Legal Documentation (6 features)</b></summary>


> A categoria Documentação Legal da release Spring '26 contém 6 recursos dedicados a atualizações de termos, políticas e conformidade legal da plataforma Salesforce. Estes recursos garantem que as organizações estejam alinhadas com as mais recentes exigências regulatórias e mudanças contratuais, incluindo atualizações de termos de serviço, políticas de privacidade e documentação de conformidade. É essencial que administradores e equipes jurídicas revisem esses recursos para manter a conformidade organizacional.

> 📄 Full details: [./releases/spring_26/en_US/documentacao_legal.md](./releases/spring_26/en_US/documentacao_legal.md)

</details>


<details>
<summary><b>📄 Salesforce General (38 features)</b></summary>


> A categoria Salesforce Geral reúne 38 recursos que abrangem mudanças transversais na plataforma Salesforce. Incluem-se aprimoramentos gerais na experiência do usuário, atualizações de infraestrutura e melhorias que afetam múltiplos produtos e nuvens. Recursos como mudanças na interface do Lightning Experience, atualizações de API e aprimoramentos de desempenho estão incluídos, proporcionando uma base mais sólida para todas as implementações Salesforce.

> 📄 Full details: [./releases/spring_26/en_US/salesforce_geral.md](./releases/spring_26/en_US/salesforce_geral.md)

</details>


<details>
<summary><b>📄 Agentforce (35 features)</b></summary>


> O Agentforce recebe 35 recursos na Spring '26, com destaque para a disponibilidade geral do Agentforce Builder. Principais novidades incluem: ação de conversão de áudio em texto, melhoria de pesquisa web com domínios permitidos, visualização de tela aprimorada (beta) para criação mais rápida de agentes complexos, conexão com Chat v2 aprimorado, criação de agentes de funcionários, métricas RAG para avaliação de desempenho de IA, encaminhamento de chamadas de voz via SIP, otimização de agentes com reprodução de sessão de Voice, e suporte a modelos como NVIDIA Nemotron 3 Nano 30B (beta). A categoria também inclui a evolução do Prompt Builder com processamento em lote aprimorado e suporte a modelos antropicados.

> 📄 Full details: [./releases/spring_26/en_US/agentforce.md](./releases/spring_26/en_US/agentforce.md)

</details>


<details>
<summary><b>📄 Data Analysis (54 features)</b></summary>


> A Análise de Dados conta com 54 recursos na Spring '26, expandindo significativamente as capacidades de business intelligence e insights da plataforma. Os recursos abrangem aprimoramentos em relatórios, dashboards e ferramentas analíticas que permitem às organizações extrair insights mais profundos de seus dados. Incluem-se melhorias em visualização de dados, integração com fontes externas e capacidades de análise preditiva, capacitando equipes a tomar decisões baseadas em dados com maior agilidade e precisão.

> 📄 Full details: [./releases/spring_26/en_US/analise_de_dados.md](./releases/spring_26/en_US/analise_de_dados.md)

</details>


<details>
<summary><b>📄 Automation (151 features)</b></summary>


> A Automação é uma das categorias mais robustas com 151 recursos. O Flow Builder recebeu aprimoramentos significativos, incluindo geração de fluxos por IA agora disponível ao público em geral, evolução iterativa de fluxos com Agentforce e interface simplificada com elementos de ramificação recolhíveis. Destaques incluem: tabelas de dados com classificação e edição inline, painéis Kanban em fluxos de tela (beta), visualização nativa de arquivos, integração com Marketing Cloud para automação de emails, fluxos acionados por segmento com agendamento aprimorado, experiências de caminho com análise comparativa, processos de aprovação de fluxo com novas capacidades de depuração e orquestração de fluxos no aplicativo Automação Lightning.

> 📄 Full details: [./releases/spring_26/en_US/automacao.md](./releases/spring_26/en_US/automacao.md)

</details>


<details>
<summary><b>📄 Customization (18 features)</b></summary>


> A categoria Personalização oferece 18 recursos focados em adaptar a plataforma Salesforce às necessidades específicas de cada organização. Os recursos permitem maior flexibilidade na configuração de layouts, campos, processos e experiências do usuário, garantindo que cada implementação possa ser moldada para atender aos requisitos de negócio únicos. Incluem-se aprimoramentos em flexipages, páginas de registro e componentes personalizáveis do Lightning.

> 📄 Full details: [./releases/spring_26/en_US/personalizacao.md](./releases/spring_26/en_US/personalizacao.md)

</details>


<details>
<summary><b>📄 Data 360 (53 features)</b></summary>


> O Data 360 apresenta 53 recursos que expandem as capacidades de gestão e integração de dados da plataforma. Os recursos incluem aprimoramentos na conectividade entre fontes de dados, qualidade de dados, governança e capacidades de processamento em tempo real. Destaques incluem fluxos do Data 360 com suporte a licenças específicas e limites de taxa maiores, fluxos de transmissão assíncronos para notificações em massa e rastreamento aprimorado de dados em tempo real com gráficos personalizados.

> 📄 Full details: [./releases/spring_26/en_US/data_360.md](./releases/spring_26/en_US/data_360.md)

</details>


<details>
<summary><b>📄 Development (97 features)</b></summary>


> A categoria Desenvolvimento reúne 97 recursos para desenvolvedores Salesforce. Destaca-se a nova ferramenta Lightning Types MCP (Visualização do desenvolvedor) para acelerar a criação de tipos personalizados do Lightning para Agentforce. Os recursos abrangem aprimoramentos no Apex, APIs, ferramentas de depuração, testes e implantação, além de novas capacidades de extensão e integração. Desenvolvedores podem esperar melhorias significativas na produtividade e nas capacidades de personalização programática da plataforma.

> 📄 Full details: [./releases/spring_26/en_US/desenvolvimento.md](./releases/spring_26/en_US/desenvolvimento.md)

</details>


<details>
<summary><b>📄 Experience Cloud (21 features)</b></summary>


> O Experience Cloud conta com 21 recursos na Spring '26, focados em aprimorar a criação e gestão de portais, sites e comunidades digitais. Os recursos incluem melhorias na experiência do usuário, personalização de temas e templates, aprimoramentos de desempenho e novas capacidades de engajamento, permitindo às organizações criar experiências digitais mais ricas e interativas para clientes, parceiros e funcionários.

> 📄 Full details: [./releases/spring_26/en_US/experience_cloud.md](./releases/spring_26/en_US/experience_cloud.md)

</details>


<details>
<summary><b>📄 Field Service (41 features)</b></summary>


> O Field Service recebe 41 recursos que aprimoram a gestão de serviços de campo. Os recursos incluem melhorias no agendamento e otimização de despacho, capacidades mobile aprimoradas para técnicos de campo, integração com IoT para manutenção preditiva e aprimoramentos na gestão de inventário de peças. A categoria também inclui novas capacidades de assistência por IA para diagnóstico e resolução de problemas em campo.

> 📄 Full details: [./releases/spring_26/en_US/field_service.md](./releases/spring_26/en_US/field_service.md)

</details>


<details>
<summary><b>📄 Hyperforce (5 features)</b></summary>


> A Hyperforce apresenta 5 recursos focados na infraestrutura de nuvem de próxima geração da Salesforce. Os recursos incluem aprimoramentos na escalabilidade, desempenho e disponibilidade da plataforma, permitindo que as organizações executem workloads Salesforce em infraestrutura de nuvem pública com maior flexibilidade e eficiência operacional.

> 📄 Full details: [./releases/spring_26/en_US/hyperforce.md](./releases/spring_26/en_US/hyperforce.md)

</details>


<details>
<summary><b>📄 Industries (194 features)</b></summary>


> A categoria Setores lidera em volume com 194 recursos, oferecendo soluções especializadas para indústrias específicas. Abrange setores como Automotivo (com Agentforce para Automotive, finanças automotivas e gerenciamento de frotas), Saúde, Serviços Financeiros, Manufatura, Varejo e Serviços Públicos. Destaques incluem Agentforce para setores específicos, gerenciamento de inventário aprimorado, planilhas de horas com otimização de custos, e soluções de venda adicional e cruzada com IA. A categoria garante que organizações de qualquer indústria possam aproveitar capacidades personalizadas e relevantes.

> 📄 Full details: [./releases/spring_26/en_US/setores.md](./releases/spring_26/en_US/setores.md)

</details>


<details>
<summary><b>📄 Mobile App (187 features)</b></summary>


> O Aplicativo Móvel é uma das maiores categorias com 187 recursos, garantindo que as equipes possam operar com plena funcionalidade em dispositivos móveis. Os recursos incluem aprimoramentos na experiência do usuário mobile, novas capacidades offline, integração aprimorada com funcionalidades de IA e melhorias de desempenho. A categoria assegura que vendedores, agentes de serviço e gestores possam acessar todas as funcionalidades críticas diretamente de seus dispositivos móveis.

> 📄 Full details: [./releases/spring_26/en_US/aplicativo_movel.md](./releases/spring_26/en_US/aplicativo_movel.md)

</details>


<details>
<summary><b>📄 Marketing (72 features)</b></summary>


> O Marketing conta com 72 recursos que aprimoram campanhas, engajamento e automação de marketing. Os recursos incluem integração aprimorada com o Flow Builder para automação de emails, capacidades de segmentação mais sofisticadas, aprimoramentos em jornadas do cliente e novas ferramentas de análise de campanha. A categoria também inclui melhorias na integração entre Marketing Cloud e outras nuvens Salesforce para uma visão unificada do cliente.

> 📄 Full details: [./releases/spring_26/en_US/marketing.md](./releases/spring_26/en_US/marketing.md)

</details>


<details>
<summary><b>📄 MuleSoft (8 features)</b></summary>


> O MuleSoft apresenta 8 recursos focados em integração e conectividade. Os recursos aprimoram as capacidades de integração de APIs, automação de fluxos de trabalho entre sistemas e conectividade com aplicações externas, permitindo que as organizações integrem o ecossistema Salesforce com outras plataformas de forma mais eficiente e escalável.

> 📄 Full details: [./releases/spring_26/en_US/mulesoft.md](./releases/spring_26/en_US/mulesoft.md)

</details>


<details>
<summary><b>📄 OmniStudio (10 features)</b></summary>


> O OmniStudio conta com 10 recursos que aprimoram as capacidades de configuração e automação de processos digitais. Os recursos incluem melhorias em flexcards, OmniScripts e DataRaptors, permitindo a criação de experiências digitais mais ricas e processos de negócio mais eficientes sem necessidade de código customizado.

> 📄 Full details: [./releases/spring_26/en_US/omnistudio.md](./releases/spring_26/en_US/omnistudio.md)

</details>


<details>
<summary><b>📄 Partner Cloud (4 features)</b></summary>


> A Partner Cloud apresenta 4 recursos focados em ecossistemas de parceiros. Os recursos aprimoram as capacidades de gestão de parceiros, compartilhamento de dados e colaboração no ecossistema, facilitando a criação e manutenção de redes de parceiros mais eficientes e integradas.

> 📄 Full details: [./releases/spring_26/en_US/partner_cloud.md](./releases/spring_26/en_US/partner_cloud.md)

</details>


<details>
<summary><b>📄 Revenue Management (131 features)</b></summary>


> O Gerenciamento de Receita oferece 131 recursos para otimização de processos de CPQ (Configure, Price, Quote) e billing. Os recursos incluem aprimoramentos na configuração de produtos, precificação dinâmica, geração de cotações e gestão de faturamento. A categoria também inclui melhorias em reconhecimento de receita, gestão de assinaturas e automação de processos financeiros, capacitando equipes de vendas e financeiras a operar com maior eficiência e precisão.

> 📄 Full details: [./releases/spring_26/en_US/gerenciamento_de_receita.md](./releases/spring_26/en_US/gerenciamento_de_receita.md)

</details>


<details>
<summary><b>📄 Sales (85 features)</b></summary>


> A categoria Vendas conta com 85 recursos, com o Sales Cloud se transformando em Agentforce Sales. Destaques incluem: geração de leads de entrada do Agentforce com captura e agendamento autônomo de reuniões, qualificação automatizada por IA, nutrição de leads com configuração guiada e gerenciamento automático de limites. O Agentforce Sales Management promove negócios com sugestões pós-reunião e gestão de pipeline aprimorada. A categoria também inclui Insights de Conversas do Einstein com resumos de chamada generativos, transcrições de fornecedor e suporte a Gong, além do aplicativo Agentforce Sales no ChatGPT (beta).

> 📄 Full details: [./releases/spring_26/en_US/vendas.md](./releases/spring_26/en_US/vendas.md)

</details>


<details>
<summary><b>📄 Security, Identity & Privacy (61 features)</b></summary>


> A Segurança, Identidade e Privacidade reúne 61 recursos críticos para proteção de dados e acesso. Destaques incluem: descontinuação de redirecionamentos para nomes de host legados, criação de aplicativos conectados desabilitada por padrão, Backup e Recuperação como aplicativo nativo, configuração de login sem senha com chaves de acesso (beta), alertas de segurança para fluxos OAuth, ativação de dispositivo obrigatória para SSO, e Solicitações de Privacidade com Direito de ser esquecido. A categoria também aprimora o Salesforce Shield com assistentes de configuração e o monitoramento de eventos.

> 📄 Full details: [./releases/spring_26/en_US/seguranca_identidade_e_privacidade.md](./releases/spring_26/en_US/seguranca_identidade_e_privacidade.md)

</details>


<details>
<summary><b>📄 Service (167 features)</b></summary>


> A categoria Serviço contém 167 recursos, com o Service Cloud se transformando em Serviço Agentforce. Destaques incluem: Salesforce Voice com gerenciamento de números e canais, chamadas de voz do WhatsApp, resposta de voz interativa e gravação de transcrições. A Central de Contato do Agentforce pode ser configurada no Salesforce Go. O messaging recebeu aprimoramentos significativos com créditos de mensagens, verificação de licenças e suporte aprimorado ao WhatsApp unificado com recibos de leitura e indicadores de digitação. O Gerenciamento de Serviço inclui modelos prontos para uso, priorização de problemas e validações de campo. Para TI, destacam-se o portal de autoatendimento remodelado, assistência proativa baseada em prioridade, diagnóstico de causa raiz e integração com Microsoft Teams.

> 📄 Full details: [./releases/spring_26/en_US/servico.md](./releases/spring_26/en_US/servico.md)

</details>

</details>





<details>

<summary><h3>❄️ Winter '26</h3></summary>

> 📊 **Executive Summary:** A release Salesforce Winter '26 representa um marco significativo na evolução da plataforma, com impressionantes 1.348 recursos distribuídos em 19 categorias. O volume massivo de novidades reflete a aceleração estratégica da Salesforce em três pilares fundamentais: inteligência artificial generativa e agentes autônomos, unificação de dados em tempo real e modernização da experiência do desenvolvedor.

O destaque absoluto é o ecossistema Agentforce, que consolida a visão de agentes de IA autônomos com 39 recursos dedicados. A plataforma expande o suporte a modelos de IA — incluindo Claude Sonnet 4.5, OpenAI o3/o4-mini e Amazon Nova na Plataforma Einstein — além de introduzir Agentforce Voice para conversas por voz, Rastreamento de sessão para visibilidade do comportamento do agente e Otimização do Agentforce (beta) para análise de eficácia. A migração do Agentforce (padrão) para agentes de funcionários com fluxo simplificado sinaliza a maturidade do produto para uso empresarial em larga escala.

A categoria Setores domina com 459 recursos, demonstrando o compromisso da Salesforce com soluções verticais. Destacam-se: Life Sciences Cloud para Engajamento do Cliente (GA), Agentforce para Healthcare com correspondência inteligente de provedores, Insurance Cloud com automação de declarações, Education Cloud com metas de carreira do aluno via Agentforce, e Manufacturing Cloud com reabastecimento inteligente de inventário. O Partner Cloud, com 156 recursos, inaugura o gerenciamento completo do ciclo de vida de parceiros com Revenue Cloud, Precificação do Salesforce e Gerenciamento de uso avançado.

Vendas (154 recursos) e Desenvolvimento (101 recursos) completam o topo da escala. Em Vendas, o Agentforce SDR evolui para Nutrição de leads com suporte a Microsoft Exchange, enquanto o Flow Builder recebe automação de decisões com IA generativa e fluxos de transmissão para públicos dinâmicos. Em Desenvolvimento, o SLDS 2 chega como GA com modo escuro (beta), o LWC recebe API v65.0 com Gerenciamento de estado (beta) e Lightning Out 2.0 para experiências externas, além de ferramentas de MCP do LWC para acelerar o desenvolvimento com IA.

Análise de dados (91 recursos) impulsiona a era do Tableau Next com semânticas aprimoradas, Otimização de modelo semântico (beta) e integração profunda com Slack via Agentforce para Analytics. Marketing (87 recursos) avança com Marketing Cloud Next, gerenciamento de fidelidade expandido e promoções globais. Segurança (55 recursos) introduz Detecção de dados expandida, rastreamento de atividade do agente em tempo real e Criptografia de banco de dados GA.

A infraestrutura Hyperforce expande para mais regiões com suporte a AWS Direct Connect e Continuidade avançada entre regiões. O Data Cloud é renomeado para Data 360, consolidando a visão de dados unificados. Field Service (24 recursos) adiciona escala dinâmica e VRA de múltiplos participantes. Personalização (65 recursos) moderniza a experiência administrativa com classificação por várias colunas em listas e segmentação expandida do Data 360. A estratégia de descontinuação é clara: Chat legado, Salesforce para Outlook (dez/2027), Lightning Sync para EWS e Salesforce Functions estão sendo aposentados.

Em suma, a Winter '26 posiciona o Salesforce como uma plataforma de agentes de IA empresariais, com dados unificados via Data 360, soluções verticais profundas e uma experiência de desenvolvimento modernizada. A direção estratégica é inequívoca: cada interação de negócio será mediada por agentes inteligentes, cada decisão será informada por dados unificados e cada setor terá soluções nativas específicas.


<details>
<summary><b>📄 Legal Documentation (11 features)</b></summary>


> Com 11 recursos, esta categoria foca em informações estruturais da release. Inclui atualizações sobre navegadores compatíveis para Lightning Experience, Salesforce Classic e CRM Analytics. Documenta como e quando os recursos ficam disponíveis, com impacto imediato para alguns e ação de administrador para outros. As mudanças na documentação visam facilitar a localização de informações sobre compatibilidade e disponibilidade de recursos.

> 📄 Full details: [./releases/winter_26/en_US/documentacao_legal.md](./releases/winter_26/en_US/documentacao_legal.md)

</details>


## 🛠️ Stack Tecnológico

| Ferramenta | Uso no Projeto |
| :--- | :--- |
| **GitHub Actions** | CI/CD: lint, typecheck, extração, deploy automático |
| **uv** | Gerenciamento de dependências com lock file determinístico |
| **Playwright** | Scraper headless para páginas SPA do Salesforce Help |
| **Python 3.14** | Linguagem principal com type hints completos |
| **BeautifulSoup** | Parser HTML para extração de dados estruturados |
| **Markdown** | Formato de saída para documentação técnica |
| **MkDocs** | Portal técnico publicado no GitHub Pages |
| **stdlib HTTP** | REST API e health check server (zero dependências externas) |
| **gh CLI** | PR workflow e GitHub integration |

### Módulos do Pipeline

| Módulo | Responsabilidade |
| :--- | :--- |
| `src/main.py` | Orquestrador: detectar releases, extrair, parse, gerar, atualizar README |
| `src/scraper.py` | Playwright headless, circuit breaker, rate limiter, cache, download PDF |
| `src/parser.py` | Extração de hierarquia ToC + tabela Feature Impact |
| `src/generator.py` | Gera arquivos `.md` por categoria |
| `src/ai_automation.py` | Comparação entre releases, detecção de regressões, quality metrics |
| `src/analytics.py` | Dashboard HTML com gráficos SVG |
| `src/api.py` | REST API para acesso programático |
| `src/notifications.py` | Email digest, Slack/Discord webhooks |
| `src/dashboard.py` | Dashboard interativo com JS |
| `src/workflow.py` | PR-based workflow com triage |
| `src/salesforce.py` | Trailhead linking, org limits, sandbox readiness |
| `src/health.py` | Health check (`/health`, `/ready`), Prometheus metrics (`/metrics`) |
| `src/logger.py` | Logging estruturado com correlation IDs |

---

## 🤝 Como Contribuir

1. Faça o **Fork** do projeto
2. Crie uma nova branch: `git checkout -b feature/minha-feature`
3. Instale dependências: `uv sync --extra dev`
4. Execute a quality gate:
   ```bash
   uv run ruff check src/
   uv run black --check src/
   uv run mypy src/
   uv run pytest tests/ --cov=src --cov-fail-under=99
   ```
5. Faça o commit: `git commit -m 'feat: descrição da alteração'`
6. Envie: `git push origin feature/minha-feature`
7. Abra um **Pull Request**

---

## 📄 Licença

Este projeto é mantido para fins educacionais e de referência técnica.

---

![Salesforce Release Intelligence - Banner 2](./assets/banner2.png)

---

<div align="center">

Made with ☕ and Python code

</div>
