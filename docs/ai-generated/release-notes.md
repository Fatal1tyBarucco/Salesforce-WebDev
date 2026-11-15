<!-- gerado por IA em 2026-11-15T12:47:38+00:00 — revisar antes de publicar -->

# Notas de Release

## Nova atualização

Esta release implementa uma refatoração para Clean Architecture em src/core e src/infrastructure, com módulos de core, infrastructure e models organizados em camadas desacopladas. Refatoração estrutural de alto impacto pode exigir atualização de imports e deve ser validada quanto a compatibilidade com consumidores existentes. A correção no fallback do LLMService visa preservar a disponibilidade do serviço em falhas de provedores. Ajustes no schema GraphQL com tipos Strawberry e ChangeType podem alterar contratos de API para consumidores externos. A ampliação da cobertura de testes, correções de quality gates, atualizações de dependências e reconciliação documental também foram incluídas. Riscos principais: possíveis imports desatualizados após a refatoração, necessidade de revisão de compatibilidade do schema GraphQL e fallback do LLM.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Implementação da Clean Architecture em src/core e src/infrastructure — 📋 refactor** | Adição de módulos core (classification, enrichment, pipeline, summarization) e infrastructure (ap… | 🔴 high | src/core, src/infrastructure, src/models, src/orchestrator.py, src/main.py · Prioridade: 💡 P1 |
| **Adição de cobertura de teste abrangente (95% meta) — 📋 feature** | Criação de 14 novos arquivos de teste cobrindo core (classification, enrichment, pipeline, summar… | 🟡 medium | tests/test_core_classification_service.py, tests/test_core_enrichment_service.py, tests/test_core_pipeline_orchestrator.py, tests/test_core_summarization_service.py, tests/test_infrastructure_generation.py, tests/test_infrastructure_github.py, tests/test_infrastructure_llm.py, tests/test_infrastructure_llm_coverage.py, tests/test_infrastructure_messaging.py, tests/test_infrastructure_notification_step.py, tests/test_infrastructure_parsing.py, tests/test_infrastructure_routes.py, tests/test_infrastructure_scraping.py, tests/test_infrastructure_storage.py, tests/test_infrastructure_translation.py, tests/test_main_coverage_additional.py, tests/test_models_coverage.py, tests/test_orchestrator_coverage.py · Prioridade: 💡 P2 |
| **Correção de quality gates (ruff, black, mypy, mkdocs) — 📋 bugfix** | Correção de múltiplos problemas de linting e formatação: ISC004 (concatenação implícita de string… | 🟢 low | .github/scripts/build_failure_issue.py, .github/scripts/documentation_reconcile.py, .github/scripts/documentation_sync.py, .github/scripts/fix_markdown.py, .github/scripts/update_changelog_auto.py, src/ai/llm/client.py, src/api.py, src/release_discovery.py, tests/test_ai_docs.py, tests/test_llm_service.py, stubs/openai, stubs/prometheus_client, stubs/syrupy · Prioridade: 💡 P3 |
| **Correção do schema GraphQL com Strawberry types — 📋 bugfix** | Substituição de dict[str, Any] por ChangeType (Strawberry type) no schema GraphQL em src/infrastr… | 🟡 medium | src/infrastructure/api/graphql.py, src/infrastructure/api/__init__.py, pyproject.toml · Prioridade: 💡 P2 |
| **Adição da dependência strawberry-graphql — 📋 bugfix** | Adição do pacote strawberry-graphql às dependências core em pyproject.toml e atualização do uv.lo… | 🟡 medium | pyproject.toml, uv.lock, src/infrastructure/api/graphql.py · Prioridade: 💡 P1 |
| **Fix do chain de fallback do LLMService — 📋 bugfix** | Correção de bug no chain de fallback do LLMService (linhas 147, 158-163 do src/infrastructure/llm… | 🔴 high | src/infrastructure/llm.py, tests/test_infrastructure_llm_coverage.py · Prioridade: 💡 P0 |
| **Atualização de dependência soupsieve (2.9 para 4.0) — ⚡ Performance** | Upgrade da dependência indireta soupsieve de versão 2.9 para 4.0 no grupo uv, aplicado em 1 diret… | 🟢 low | uv.lock, pyproject.toml · Prioridade: 💡 P3 |
| **Atualização de testes para novos limites de retry e tokens — 📋 bugfix** | Ajuste das expectativas de teste em test_ai_docs.py e test_ai_docs_coverage.py para coincidir com… | 🟢 low | tests/test_ai_docs.py, tests/test_ai_docs_coverage.py · Prioridade: 💡 P3 |
| **Reconciliação de documentação e atualização do manifest — 📋 documentation** | Atualização do docs/.documentation-manifest.json com novos mapeamentos entre código e documentaçã… | 🟢 low | docs/.documentation-manifest.json, mkdocs.yml, docs/api/core-classification-service.md, docs/api/core-enrichment-service.md, docs/api/core-pipeline-orchestrator.md, docs/api/core-pipeline-steps.md, docs/api/core-summarization-service.md, docs/architecture/decisions/adr-007-clean-architecture.md · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto

🔴 Alto: **2** (22%) 🔴🔴
🟡 Médio: **3** (33%) 🟡🟡🟡
🟢 Baixo: **4** (44%) 🟢🟢🟢🟢

Total: **9 features**

## Mudanças por tipo nesta execução

```text
⚡ Performance        │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 bugfix             │██████████████████████████████│    5 →
📋 documentation      │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 refactor           │██████░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▄▆█


## Revisão Necessária

- **Verificação de backwards compatibility da arquitetura** — Executar análise estática de dependências para identificar todos os imports que precisam ser atualizados (0.80)
- **Revisão do schema GraphQL para consumers externos** — Verificar versão do schema GraphQL e comunicar mudanças para consumidores externos se necessário (0.75)
- **Revisão da lógica de fallback do LLMService** — Revisar todos os caminhos de fallback e testes de integração com providers reais (0.85)
- **Validação dos novos documentos de API** — Comparar documentação com código-fonte para verificar consistência (0.70)

---

## Nova atualização

Esta release introduz o design system no dashboard com suporte a dark mode e recursos de acessibilidade, além de corrigir o rastreamento de estado de fences no fix_markdown.py e atualizar diversas dependências de ferramentas e bibliotecas para as versões mais recentes.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Aplicar design system ao dashboard com suporte a dark mode e acessibilidade — 📋 feature** | Extração de tokens e componentes reutilizáveis em src/design-system/, migração do dashboard_templ… | 🔴 high | src/dashboard_template.html, src/design-system/ · Prioridade: 💡 P0 |
| **Corrigir rastreamento de estado de fences em fix_markdown.py — 📋 bugfix** | Script passa a rastrear in_fence para distinguir abertura e fechamento de blocos markdown, evitan… | 🟢 low | .github/scripts/fix_markdown.py · Prioridade: 💡 P2 |
| **Atualizar actions/setup-python para v7.1.0 — ⚡ Performance** | Bump da ação actions/setup-python de 7.0.0 para 7.1.0 em workflows de CI. | 🟢 low | .github/workflows/ai-docs.yml, .github/workflows/dependabot-lock-refresh.yml · Prioridade: 💡 P3 |
| **Atualizar astral-sh/setup-uv para v10.3.3 — ⚡ Performance** | Bump da ação astral-sh/setup-uv para versão 10.3.3 em múltiplos workflows. | 🟢 low | .github/workflows/copilot-setup-steps.yml, .github/workflows/dependabot-lock-refresh.yml · Prioridade: 💡 P3 |
| **Atualizar pyasn1 para 0.6.5 — ⚡ Performance** | Bump da dependência indireta pyasn1 de 0.6.4 para 0.6.5 no grupo uv. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar grupo uv com certifi, filelock, langgraph-sdk e virtualenv — ⚡ Performance** | Bump de quatro dependências indiretas do grupo uv para versões mais recentes. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar aiohttp para 3.14.4 — ⚡ Performance** | Bump da dependência direta aiohttp de 3.14.3 para 3.14.4. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |
| **Atualizar black para 26.10.1 — ⚡ Performance** | Bump da dependência de desenvolvimento black de 26.10.0 para 26.10.1. | 🟢 low | pyproject.toml · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto

🔴 Alto: **1** (12%) 🔴
🟡 Médio: **0** (0%)
🟢 Baixo: **7** (87%) 🟢🟢🟢🟢🟢🟢🟢

Total: **8 features**

## Mudanças por tipo nesta execução

```text
⚡ Performance        │██████████████████████████████│    6 →
📋 bugfix             │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │█████░░░░░░░░░░░░░░░░░░░░░░░░░│    1 →
```

Sparkline da distribuição alto/médio/baixo: ▁ █

---

## Nova atualização 1

Esta release corrige a falha de deploy no GitHub Pages que impedia a publicação de artefatos de release e afetava a entrega contínua do Intelligence Hub. Ajusta cabeçalhos Markdown para conformidade com lint MD001/MD036 e melhora o upload de artefatos de logs de IA no workflow ai-docs. Introduz gestão de orçamento de tokens de saída no cliente LLM, com variáveis de ambiente e escalonamento exponencial em retentativas para reduzir completions vazias ou truncadas. Adiciona novos testes de cobertura para módulos de IA e documentação. Simplifica o tratamento de exceções no docs_sync_engine, substituindo blocos específicos por captura genérica de Exception, o que pode mascarar erros específicos e requer atenção. Atualiza o manifesto de documentação com novos artefatos gerados por IA. Um import não utilizado em orchestrator.py está sob revisão.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Simplificação de tratamento de exceções no docs_sync_engine — 📋 refactor** | Substituição de múltiplos blocos `except OSError, ValueError:` por `except Exception:` em funções… | 🟢 low | .github/scripts/docs_sync_engine.py · Prioridade: 💡 P3 |
| **Correção do deploy no GitHub Pages com etapa de upload — 📋 bugfix** | Adição de job de build do site (index.html com links aos artefatos), upload do artefato via actio… | 🔴 high | .github/workflows/salesforce_release_intelligence_hub.yml · Prioridade: 💡 P0 |
| **Ajuste de cabeçalhos Markdown para conformidade MD001/MD036 — 📋 bugfix** | Alteração de cabeçalhos `###` para `##` no gerador de relatórios de impacto e adição de spec `tex… | 🟢 low | src/ai/generators/markdown.py · Prioridade: 💡 P3 |
| **Gestão de orçamento de tokens de saída no cliente LLM — 📋 feature** | Introdução de variáveis de ambiente AI_DOCS_MAX_OUTPUT_TOKENS e AI_DOCS_MAX_OUTPUT_TOKENS_LIMIT, … | 🟡 medium | src/ai/llm/client.py · Prioridade: 💡 P1 |
| **Atualização do manifesto de documentação com novos artefatos IA — 📋 documentation** | Adição de referências a docs/ai-generated/release-notes.md, leadership.md, roadmap.md em múltipla… | 🟢 low | docs/.documentation-manifest.json · Prioridade: 💡 P3 |
| **Novos testes de cobertura para módulos IA e docs — 📋 feature** | Adição de test_ai_docs.py, test_ai_docs_coverage.py, test_ai_coverage.py e atualização de test_ma… | 🟡 medium | tests/test_ai_docs.py, tests/test_ai_docs_coverage.py, tests/test_ai_coverage.py, tests/test_main_coverage.py · Prioridade: 💡 P2 |
| **Ajuste no workflow ai-docs para upload de artefatos ocultos — 📋 bugfix** | Mudança de if-no-files-found: ignore para warn e adição de include-hidden-files: true no upload d… | 🟢 low | .github/workflows/ai-docs.yml · Prioridade: 💡 P3 |

## 📊 Distribuição de Impacto 1

🔴 Alto: **1** (14%) 🔴
🟡 Médio: **2** (28%) 🟡🟡
🟢 Baixo: **4** (57%) 🟢🟢🟢🟢

Total: **7 features**

## Mudanças por tipo nesta execução 1

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │████████████████████░░░░░░░░░░│    2 →
📋 refactor           │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
```yaml

Sparkline da distribuição alto/médio/baixo: ▂▄█

## Revisão Necessária

- **Importação de re no orchestrator.py sem uso aparente** — Baixa confiança ou sinalizada pelo classificador. (0.40)

---

Correções críticas no pipeline de geração de documentação via IA. Corrige falha em completions LLM vazias que impactava a funcionalidade principal. Implementa novo pipeline OpenRouter gratuito com suporte a rate-limiting. Expansão significativa do change_collector.py para coleta de mudanças Git/GitHub. Prevenção de headings duplicados no changelog automático. Correção de caminhos no sync de documentação para ambientes CI. Atualização do manifesto de documentação com novos arquivos.

| Feature | Descrição | Impacto | Público |
| :--- | :--- | :---: | :--- |
| **Correção de falha em completions LLM vazios — 📋 bugfix** | Corrige problema onde respostas do LLM retornavam vazias, impactando a geração automática de docu… | 🔴 high | src/ai/llm/client.py, src/ai/orchestrator.py · Prioridade: 💡 P0 |
| **Adição de pipeline OpenRouter gratuito para documentação — 📋 feature** | Implementa novo pipeline de documentação usando OpenRouter free tier, com suporte a rate-limiting… | 🔴 high | .github/workflows/ai-docs.yml, src/ai/orchestrator.py, src/ai/llm/client.py, src/ai/config/models.py · Prioridade: 💡 P1 |
| **Prevenção de headings duplicados no changelog automático — 📋 bugfix** | Modifica a lógica de atualização automática do changelog para evitar criação de múltiplas seções … | 🟡 medium | .github/scripts/update_changelog_auto.py · Prioridade: 💡 P2 |
| **Correção de caminhos no pipeline de sync de documentação — 📋 bugfix** | Altera uso de /tmp para caminhos relativos ao workspace, garantindo consistência em ambientes CI. | 🟡 medium | .github/workflows/documentation-sync.yml, .github/scripts/docs_sync_engine.py · Prioridade: 💡 P2 |
| **Atualização de manifesto de documentação com novos arquivos — 📋 documentation** | Adiciona novos arquivos ao manifesto de documentação incluindo README.en.md, ai-config-models.md … | 🟢 low | docs/.documentation-manifest.json, mkdocs.yml · Prioridade: 💡 P3 |
| **Expansão significativa do change collector — 📋 feature** | Reescrita completa do change_collector.py com novas funcionalidades de coleta de mudanças Git/Git… | 🔴 high | src/ai/collectors/change_collector.py, src/ai/schemas/change.py, tests/test_ai_docs.py, tests/test_ai_docs_coverage.py · Prioridade: 💡 P1 |
| **Exposição de diagnóstico de falha com testes validados — 📋 feature** | Implementa exposição de diagnóstico de falhas com cobertura de testes validada. | 🟡 medium | src/ai/orchestrator.py, tests/test_ledger/test_service.py · Prioridade: 💡 P2 |

## 📊 Distribuição de Impacto 1 1

🔴 Alto: **3** (42%) 🔴🔴🔴
🟡 Médio: **3** (42%) 🟡🟡🟡
🟢 Baixo: **1** (14%) 🟢

Total: **7 features**

## Mudanças por tipo nesta execução 1 1

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████████████████████████████│    3 →
```

Sparkline da distribuição alto/médio/baixo: ██▂

## Revisão Necessária 1

- **Revisão de alterações no change_collector.py** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Validação de novos prompts de IA** — Baixa confiança ou sinalizada pelo classificador. (0.65)
- **Verificação de schemas de documentos gerados** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Auditoria de logs AI Docs** — Baixa confiança ou sinalizada pelo classificador. (0.60)
