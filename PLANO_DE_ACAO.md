# 📋 Plano de Ação: newPrompt.md — Feature Gap
**Data:** 02/09/2026 | **Arquivo:** `newPrompt.md` (321 linhas, untracked)

---
## ✅ Passo 1 — Verificar cobertura das features citadas no newPrompt.md

| Feature | Referência no newPrompt | Status no repo |
|---|---|---|
| Token Bucket (rate limit 2 req/s) | §Resiliência | `token_bucket.py` existe — verificar se conectado |
| Cache com TTL 24h | §Resiliência | `cache_manager.py` — verificar TTL |
| Backoff exponencial + jitter | §Resiliência | `scraper_retry` — verificar |
| Circuit Breaker (3 falhas → 60s) | §Resiliência | `circuit_breaker.py` existe |
| Playwright Async (concorrência) | §Concorrência | `scraper.py` — verificar `asyncio.gather` |
| Snapshot testing (scraper + parser) | §Testes | `tests/test_snapshot.py` + `snapshots/` — 9 snapshots |
| FastAPI REST API | §Arquitetura | `src/api.py` existe |
| Slack/Discord notifications | §Arquitetura | `notifications.py` + `smart_notifications.py` |
| MkDocs docs completos | §Arquitetura | `docs/`, `mkdocs.yml` — i18n [en, pt] |

---
## 🔴 Passo 2 — Executar verificação real
1. Ler `newPrompt.md` completo (321 linhas)
2. Comparar linha a linha com `src/` e `tests/`
3. Identificar gaps não cobertos pelo novo plano
4. Atualizar `PLANO_DE_ACAO.md` com gaps novos
5. Executar correções passo a passo

---
## ✅ Resultado do Mapeamento (Passo 3 concluído)

| Feature `newPrompt.md` | Status | Observação |
|---|---|---|
| Scraper (Playwright Async) | ✅ | `asyncio.gather`, `async_playwright` |
| Parser / Generator | ✅ | `parser.py`, `generator.py`, MkDocs |
| API REST (FastAPI) | ✅ | `api.py` com endpoints |
| Cache TTL 24h | ✅ | `CacheManager(ttl=86400)` |
| Circuit Breaker | ✅ | `threshold=3`, `cooldown=60.0` |
| Token Bucket 2 req/s | ✅ | `RateLimiter(RATE_LIMIT_RPS=2)` integrado (`scraper.py:76-89`, `108`) | Nenhum |
| Snapshot scraper/parser | ⚠️ | `test_snapshot.py` (9 snapshots) — não cobre `scraper.py` diretamente |
| Notifications / Analytics | ✅ | `notifications.py`, `smart_notifications.py`, `analytics.py` |

---
## 🔴 Gaps Reais Confirmados (Passo 3.5 — executar)

### Gap A: Token Bucket não integrado
Arquivo `token_bucket.py` existe (`ls src/` não mostrou, mas `search_files` pode localizar). Se não estiver ligado ao scraper (linha 581), o rate limit de 2 req/s do `newPrompt.md` não é respeitado.

### Gap B: Snapshot de `scraper.py`
`tests/test_snapshot.py` captura snapshots, mas `test_scraper_snapshot` mencionado no newPrompt.md (§Testes) não existe como arquivo específico para scraper.

---
## 📦 Passo 4 — Executar correções (a partir deste ponto)

