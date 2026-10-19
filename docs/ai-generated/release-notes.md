<!-- gerado por IA em 2026-10-19T03:48:57+00:00 — revisar antes de publicar -->

# Notas de Release

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

## 📊 Distribuição de Impacto

🔴 Alto: **3** (42%) 🔴🔴🔴
🟡 Médio: **3** (42%) 🟡🟡🟡
🟢 Baixo: **1** (14%) 🟢

Total: **7 features**

## Mudanças por tipo nesta execução

```text
📋 bugfix             │██████████████████████████████│    3 →
📋 documentation      │██████████░░░░░░░░░░░░░░░░░░░░│    1 →
📋 feature            │██████████████████████████████│    3 →
```

Sparkline da distribuição alto/médio/baixo: ██▂

## Revisão Necessária

- **Revisão de alterações no change_collector.py** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Validação de novos prompts de IA** — Baixa confiança ou sinalizada pelo classificador. (0.65)
- **Verificação de schemas de documentos gerados** — Baixa confiança ou sinalizada pelo classificador. (0.70)
- **Auditoria de logs AI Docs** — Baixa confiança ou sinalizada pelo classificador. (0.60)
