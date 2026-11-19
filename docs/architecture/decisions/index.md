# Decisões de Arquitetura (ADRs)

Decisões de design documentadas do projeto Salesforce Release Intelligence.

## ADRs Publicadas

- **[ADR-001 Parser Strategy](adr-001-parser-strategy.md)** — Estratégia de parsing: árvore de navegação e tabelas de feature impact
- **[ADR-002 GitHub Actions](adr-002-github-actions.md)** — Pipeline de CI/CD e automação via GitHub Actions
- **[ADR-003 Topic Classification](adr-003-topic-classification.md)** — Classificação de tópicos via LLM
- **[ADR-004 Auto-Healing](adr-004-auto-healing.md)** — Auto-healing do scraper e resiliência do pipeline
- **[ADR-005 Documentation Reconciliation](adr-005-documentation-reconciliation.md)** — Reconciliação contínua da documentação
- **[ADR-006 Feature Evolution Ledger](adr-006-feature-evolution-ledger.md)** — Rastreamento cross-release de features individuais
- **[ADR-007 Clean Architecture Migration](adr-007-clean-architecture.md)** — Migração para clean architecture
- **[ADR-008 Prompt Versioning](adr-008-prompt-versioning.md)** — Versionamento de prompts em YAML
- **[ADR-009 Scraper Resilience](adr-009-scraper-resilience.md)** — Resiliência do scraper (retry, circuit breaker)
- **[ADR-010 LLM Cache Strategy](adr-010-llm-cache-strategy.md)** — Estratégia de cache LLM
- **[ADR-011 Cache Layer Hardening](adr-011-cache-layer-hardening.md)** — Cache atômico, com lock, integridade SHA-256, fingerprint de releases e runtime não versionado
- **[ADR-012 Absolute Documentation Sync](adr-012-absolute-documentation-sync.md)** — Contrato verificável manifest × nav × docs × repositório, reconciliação bidirecional com histórico de remoções e publicação moderna (mike, gen-files, privacy, social)
