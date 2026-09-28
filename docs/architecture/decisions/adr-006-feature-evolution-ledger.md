# ADR-006 Feature Evolution Ledger

Rastreamento cross-release de features individuais e detecção de mudanças de ciclo de vida.

## Status

**Proposta** — Implementada em `src/automation/ledger/`.

## Contexto

O pipeline de Release Notes processa cada release de forma isolada: scraper → parse → enrichment LLM → geração de Markdown. O pipeline não conecta uma release com a anterior em nível de **feature individual**.

Módulos existentes que operam em nível de release ou de categoria:

- `automation/comparison.py` — comparação entre releases a nível de **categoria** (ex: "Plataforma teve +5 features"). Não rastreia features individuais.
- `automation/impact.py` — análise de impacto de uma release isolada (scores por categoria). Não cruza informações entre releases.
- `nl_search.py` — busca estática de features em um release. Não tem noção de histórico ou evolução.
- `automation/reporting.py` — gera diff entre releases via LLM, mas o diff é a nível de release (resumo executivo, changelog), não a nível de feature.

**Problema:** sem um módulo dedicado, é impossível responder perguntas como:

- "A feature `Flow Builder` mudou de nome entre spring_26 e summer_26?"
- "Quais features foram removidas na release mais recente?"
- "Qual é o histórico completo de `Campanhas de Marketing` através de todas as releases?"
- "A feature `Apex Debug` mudou de categoria?"

## Decisão

Criar um subpacote `src/automation/ledger/` com dois componentes principais:

1. **`FeatureLinker`** (`linker.py`) — algoritmo de linkage entre features de duas releases consecutivas, com 5 níveis de match em ordem de confiança:
   - **EXACT** — nome normalizado idêntico + mesma categoria → `ALIVE` ou `CATEGORY_CHANGED`
   - **FUZZY** — Jaccard ≥ 0.5 + mesma categoria → `RENAMED` ou `ALIVE`
   - **HEURISTIC** — mesma categoria + melhor par mútuo com Jaccard ≥ 0.2 → `RENAMED`
   - **LLM** — similaridade 0.2–0.5, desambiguação opcional via LLM → `RENAMED` ou `ALIVE`
   - First-match-wins: uma vez associado, o pair é removido do pool.

2. **`FeatureEvolutionLedgerService`** (`service.py`) — orquestra:
   - Extração de features brutas de um release (.md files, categoria, snippet)
   - Geração de `LedgerDiff` + `LedgerStats` entre dois releases
   - Cache com TTL (1h) + content-hash no `CacheManager` existente (namespace `sfel`)
   - Consulta de histórico de uma feature (`get_feature_history`)
   - Emissão de evento `ledger.generated` no `EventBus`

**Por que 5 níveis e não apenas LLM?** O LLM é lento, caro e opcional. Os 4 primeiros níveis (EXACT, CATEGORY_CHANGE, FUZZY, HEURISTIC) cobrem a grande maioria dos casos de forma determinística e instantânea. O LLM só entra como desambiguação para os casos ambíguos (similaridade 0.2–0.5) onde o algoritmo heurístico não tem confiança.

**Por que não integrar com `comparison.py`?** O `comparison.py` compara categorias (volumes, métricas agregadas). O linker opera em nível de feature individual (nome + categoria). São problemas diferentes com outputs diferentes: `comparison.py` produz um diff agregado de categorias; o linker produz `FeatureLink` individualizados. A sortida do linker (count por status) pode ser consumida pelo `comparison.py` se necessário, mas os módulos permanecem separados por responsabilidade.

## Consequências

### Positivas

- Possibilidade de consultar a trajetória de qualquer feature através de todas as releases
- Detecção automática de renomeações, mudanças de categoria, criações e remoções de features
- Cache com invalidação automática (content-hash via CacheManager existente)
- Fallback determinístico: o linker funciona sem LLM (4 primeiros níveis); o LLM é opcional
- Evento `ledger.generated` na EventBus existente para dashboard e notificações

### Negativas / Trade-offs

- **Histórico é recomputado a cada chamada**: `get_feature_history` varre todos os `.meta.json` e re-extrai features de cada release. Para uma história de feature com many releases, isso é O(n Releases × tamanho do release). Um banco de dados seria mais eficiente, mas introduziria dependência externa.
- **LLMs são opcionais mas melhoram precisão**: sem LLM, features com similaridade muito baixa (< 0.2) ficam sem match e aparecem como `BORN` (se na release atual) ou `REMOVED` (se na anterior). Isso pode gerar falsos positivos de remoção/criação para renomeações radicais.
- **Nenhuma integração com Org do cliente**: o ledger rastreia apenas as features presentes nas release notes públicas. Para cruzar com metadata de uma Org específica, seria necessário um módulo separado ("Org Impact Engine").
- **Arquitetura do README e 문서의 atualização pendente**: a feature deve ser documentada em ADR, README e docs/index.md para que o Documentation Sync Engine (que atualiza apenas estrutura, não conteúdo) não deixe documentação desatualizada.

## Testes

```text
tests/test_ledger/
├── conftest.py                  # Fixtures: releases_dir_fake (3 releases), cache_dir, mock_llm_service
├── test_linker.py               # 17 testes: _jaccard, _tokenize_name, EXACT, CATEGORY_CHANGE, FUZZY, HEURISTIC
├── test_linker_coverage.py      # 7 testes de branches do linker (used_current, used_previous, HEURISTIC append, etc.)
├── test_service.py              # 17 testes: extração, cache, histórico, events, edge cases
├── test_service_coverage.py     # 10 testes: LLM step (true/false/attr_err/exception), OSError, cache falha, invalidação
├── test_service_branch_coverage.py  # 6 testes: DEPRECATED, REMOVED, BORN via mock linker, cache/stats validation error, short names
├── test_models_pydantic.py      # 11 testes: validação Pydantic, enums, constraints
└── test_prompts.py              # 3 testes: prompt builder (campos, truncamento)
```

> **Cobertura**: pytest com `--cov=src.automation.ledger` + `--cov-fail-under=95`

## Integração com o Pipeline

O módulo é **autonomous**: não é chamado pelo orchestrator nem pelo pipeline principal. Para usar na prática:

```python
from src.automation.ledger.service import FeatureEvolutionLedgerService

svc = FeatureEvolutionLedgerService()
diff = await svc.generate_ledger("summer_26", "spring_26")
history = await svc.get_feature_history("Flow Builder")
```

A integração no pipeline principal (chamada automática após cada `process_single_release`) é trabalho futuro, não parte deste ADR.
