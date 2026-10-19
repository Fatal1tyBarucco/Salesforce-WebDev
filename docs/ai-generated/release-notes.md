<!-- gerado por IA em 2026-10-19T14:57:56+00:00 — revisar antes de publicar -->

# Notas de Release

## Nova atualização

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

## 📊 Distribuição de Impacto

🔴 Alto: **1** (14%) 🔴
🟡 Médio: **2** (28%) 🟡🟡
🟢 Baixo: **4** (57%) 🟢🟢🟢🟢

Total: **7 features**

## Mudanças por tipo nesta execução

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

## 📊 Distribuição de Impacto 1

🔴 Alto: **3** (42%) 🔴🔴🔴
🟡 Médio: **3** (42%) 🟡🟡🟡
🟢 Baixo: **1** (14%) 🟢

Total: **7 features**

## Mudanças por tipo nesta execução 1

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
