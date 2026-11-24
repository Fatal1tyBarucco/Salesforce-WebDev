# Cache Layer Diagnostic Report — Salesforce-WebDev

**Date:** 2026-11-24  
**Author:** Senior Software Engineer (Cache Optimization Task)  
**Scope:** `src/cache_manager.py`, `src/cache_io.py`, `src/processed_releases.py`, consumers, CI, docs

---

## 1. Current State Summary

The cache layer has been substantially implemented per **ADR-011** (Cache Layer Hardening). All major requirements R1–R10 are addressed in code:

| Requisito | Status | Evidência |
|-----------|--------|-----------|
| R1: Escrita atômica | ✅ Implementado | `cache_io.atomic_write_json` (temp + fsync + os.replace) |
| R2: Concorrência segura | ✅ Implementado | `FileLock` (fcntl/msvcrt), single-flight em `ProcessedReleasesStore.run_once` |
| R3: Integridade e recuperação | ✅ Implementado | Envelope v2 (schema_version + SHA-256 checksum), quarentena rotacionada |
| R4: Hashing SHA-256 | ✅ Implementado | `compute_file_hash` usa SHA-256; `load_content_cache` migra MD5 tolerante |
| R5: Eviction controlada | ✅ Implementado | Budgets LRU por namespace (1000 entries / 50 MiB), `clear_expired` preguiçoso |
| R6: Observabilidade | ✅ Implementado | `CacheStats` com `by_namespace` + `eviction_reasons`; `persist_stats()` → `cache/stats.json` |
| R7: Fingerprinting de release | ✅ Implementado | `compute_release_fingerprint` (meta normalizado + hashes MD + PARSER_VERSION) |
| R8: CI e versionamento | ✅ Resolvido | ADR-011: `cache/` não versionado; artefato `pipeline-cache` nos workflows; `actions/cache` com chave `uv.lock` |
| R9: Configuração centralizada | ✅ Implementado | `src/config.py` seção "Cache Layer (ADR-011)" com todos TTLs, budgets, timeouts |
| R10: Testes de robustez | ✅ 149 testes | `test_cache_manager.py` (96), `test_cache_io.py` (25), `test_processed_releases.py` (28) |

**Quality Gates (current):**
- `ruff check .` → ✅ Passes
- `ruff format --check .` → ✅ Passes (694 files already formatted)
- `mypy src/ --ignore-missing-imports` → ❌ 4 errors in `src/automation/ledger/service.py` (outside cache scope)
- `pytest` cache tests → ✅ 149 passed
- **Coverage cache modules:** 91% (target ≥95%)

---

## 2. Diagnostic Table — Gaps to Close

| Problema | Evidência (arquivo:linha) | Impacto | Risco | Severidade |
|----------|---------------------------|---------|-------|------------|
| Cobertura < 95% nos módulos de cache | `cache_io.py`: 91%, `cache_manager.py`: 90%, `processed_releases.py`: 93% | Falha no gate CI `pytest --cov-fail-under=95` | Pipeline bloqueia merge | **Crítica** |
| Linhas de erro não cobertas em `cache_io.py` | 101-102 (cleanup temp), 189-191 (quarantine scan), 195-196 (quarantine unlink), 250 (early return `__exit__`), 272-274 (no fcntl/msvcrt), 283-284 (fcntl unlock), 289-290 (msvcrt unlock) | Exceções de I/O não testadas; degradação silenciosa não verificada | Médio | **Alta** |
| Linhas de erro não cobertas em `cache_manager.py` | 354, 357 (early returns `invalidate`), 363-364 (lock/error), 376, 379 (early returns `invalidate_namespace`), 388-389 (unlink error), 391-393 (rmdir error), 394-396 (lock timeout), 429-427 (full_scan branch), 435-346 (lock timeout sweep), 453-454 (quarantine scan), 480-482 (persist_stats error), 561-563 (lock timeout load_content), 580 (non-string warning), 586-587 (save_content error), 659-661 (v2 missing data), 684-685 (evict expired error), 702-703 (last_access refresh error), 717-719 (budget scan error), 724-725 (stat error), 734-738 (read_json_safe budget), 740-747 (LRU eviction error), 758-760 (sweep scan error), 766-767 (quarantine sweep), 771-772 (quarantine sweep), 776-778 (sweep eviction error), 817-818 (migration write error) | Caminhos de erro e branches não exercitados | Médio | **Alta** |
| Linhas de erro não cobertas em `processed_releases.py` | 106-118 (categories processing), 124-126 (OSError rglob), 131-132 (OSError compute_file_hash), 216-217 (lock timeout mark_processed), 228-233 (lock timeout invalidate), 371-373 (lock timeout _load_state), 404-413 (release attribute handling) | Error paths e attribute guards não testados | Médio | **Alta** |
| mypy falha em `src/automation/ledger/service.py` | Linhas 45, 451, 457, 463 | Bloqueia gate CI mypy (embora fora do escopo do cache) | Baixo | **Alta** (fora de escopo) |

---

## 3. Cache Consumers — Verified Mapping

| Consumer | Module | Cache Usage |
|----------|--------|-------------|
| Scraper | `src/scraper.py:94` | `CacheManager(cache_dir=CACHE_DIR)` — TTL content cache |
| Orchestrator | `src/orchestrator.py:23,123` | `ProcessedReleasesStore` + `CacheManager.persist_stats()` |
| Impact Engine | `src/impact_propagation/engine.py` | `CacheManager` for propagation graph TTL |
| LLM Adapters | `src/infrastructure/llm_adapters/cache.py` | Exact-match + semantic cache via `CacheManager` |
| Scraper Adapter | `src/infrastructure/scraping/cache_adapter.py` | Adapter wrapping `CacheManager` |
| Playwright Adapter | `src/infrastructure/scraping/playwright_adapter.py` | `ScraperCacheAdapter(CacheManager(...))` |
| Main Entry | `src/main.py` | Instantiates `CacheManager`, passes to orchestrator |

All consumers use the public API correctly. No direct file I/O on cache files outside the cache layer.

---

## 4. CI/CD Cache Strategy — Verified

| Pipeline | Cache Restore | Cache Upload | Finalizer |
|----------|---------------|--------------|-----------|
| `release_notes_pipeline.yml` | `actions/cache` key `runner.os-pipeline-cache-${run_id}` | `upload-artifact` name `pipeline-cache` (30d) | `scripts/cache_maintenance.py --cache-dir cache` |
| `scheduled-pipeline.yml` | Same as above | Same as above | Same as above |
| `python-quality.yml` | `setup-uv enable-cache` + `uv.lock` glob | None (no runtime cache needed) | N/A |

**Contradição doc/.gitignore:** Resolvida via ADR-011 — `cache/` permanece em `.gitignore`; histórico auditável vive em artefatos de workflow e `releases/`.

---

## 5. Action Plan — Phases 2–6

### Fase 2: Arquitetura (já consolidada no ADR-011)
- Design válido; nenhum componente novo necessário.
- Estratégia por instância de cache já definida na tabela ADR-011 (seção 9).

### Fase 3: Implementação — Fechar gaps de cobertura
Adicionar testes determinísticos (sem `time.sleep`, clock injetado) para:
1. **cache_io.py**: Falhas de cleanup temp, rotação quarentena, lock degraded paths, unlock errors
2. **cache_manager.py**: Early returns, lock timeouts, OSError em unlink/rmdir/stat, budget scan errors, LRU eviction errors, sweep errors, content-cache migration errors
3. **processed_releases.py**: Categories branch, rglob/compute_file_hash OSError, lock timeouts em mark/invalidate/load_state, release attribute guards

### Fase 4: Testes
- Executar suíte expandida e confirmar ≥95% coverage nos 3 módulos.
- Executar `mutmut` dedicado ao cache (score baseline vs pós-mudanças).

### Fase 5: Revisão e Otimização
- Checklist R1–R10 com evidência.
- Análise performance: I/O calls/run, lock contention, LRU overhead.
- Validação docs: `docs/maintenance/cache-management.md` reconciliado.

### Fase 6: Entrega Final
- Sumário executivo, arquivos alterados, comandos de validação, commit message.

---

## 6. Decisions Recorded

| Item | Decisão | Justificativa |
|------|---------|---------------|
| Storage backend | Manter filesystem (JSON) | ADR-011: suficiente para pipeline semanal; Redis/DB adicionam complexidade operacional sem benefício claro |
| Lock fallback | Degrada a no-op com warning quando sem fcntl/msvcrt | Documentado em ADR-011; correção single-processo depende de atomic writes |
| Quarantine rotation | 3 cópias por arquivo (config `CACHE_QUARANTINE_KEEP`) | Balance entre debugabilidade e espaço em disco |
| `ttl=0` semantics | Preservado para compatibilidade com adapters scraper/LLM | Congelado por testes existentes (`test_infrastructure_*`) |
| `PARSER_VERSION` | Bump manual em `config.py` | Força reprocessamento quando parser altera saída; documentado |
| Coverage target | 95% branch coverage nos módulos de cache | Gate obrigatório do repositório |

---

## 7. Next Steps

1. **Immediate**: Add test coverage for uncovered error paths (Phase 3)
2. **Then**: Run full quality gates (ruff, format, mypy, pytest --cov=95)
3. **Then**: Validate docs reconciliation
4. **Final**: Commit with Conventional Commits message