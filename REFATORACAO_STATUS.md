# 📋 Status de Refatoração — Salesforce-WebDev

Template de acompanhamento de alterações. **Atualizado a cada tarefa/branch.**

> Última atualização: 2026-07-20 (T1, T2 e T3 concluídas)

## 🔧 Workflow adotado
- **1 branch por tarefa**: `refactor/<escopo>` (criada a partir de `main`).
- **Commits incrementais** + push (com aprovação do usuário).
- **Ao concluir**: merge em `main` + **exclusão da branch** (remoto + local).
- **Validação**: `uv run ruff` + `black --check` + `mypy src/` + `pytest` (cobertura ≥ 95% via CI e local).
- **Ambiente**: `uv` + Python 3.14; deps via `uv sync --extra dev`.

## 📊 Backlog reconciliado (plano original × código real)
| Fase | # | Item do plano | Estado real | Ação |
|---|---|---|---|---|
| 1 | 1 | `ai_automation.py` 1428→5 módulos | ✅ Feito (`src/automation/`, 20 arquivos; `ai_automation.py` virou shim de 201 ln) | — |
| 1 | 2 | `main.py` funções 100-157 ln | ⏳ Pendente (god-module 960 ln: pipeline + geração de docs + formatação) | `refactor/phase1-decompose-main` |
| 1 | 3 | 15+ wrappers duplicados | ✅ Resolvido (obsoleto, sem duplicação real) | — |
| 1 | 4 | Config hardcoded | ✅ Feito (`config.py` centraliza; tópicos dinâmicos) | — |
| 2 | 5 | `except Exception: pass` | ✅ Feito (T2: 6 silenciamentos → logging) | — |
| 2 | 6 | Type stubs faltando | 🔍 A avaliar | — |
| 2 | 7 | Cache sem invalidação | 🔍 A avaliar | — |
| 2-3 | 8 | Dependency Injection | 🔍 A avaliar | — |
| 2-3 | 9 | Event System | 🔍 A avaliar | — |
| 2-3 | 10 | Async Context Managers | 🔍 A avaliar | — |
| 2 | 11 | Testes de integração reais | 🔍 A avaliar | — |
| 2 | 12 | Property-based testing | 🔍 A avaliar | — |
| 2 | 13 | Snapshot testing | 🔍 A avaliar | — |
| 3 | 14 | Parallel scraping | 🔍 A avaliar | — |
| 3 | 15 | Incremental updates | 🔍 A avaliar | — |
| 3 | 16 | Streaming | 🔍 A avaliar | — |
| 4-5 | 17 | CLI (click/typer) | 🔍 A avaliar | — |
| 4-5 | 18 | Logging estruturado (structlog) | 🔍 A avaliar | — |
| 4-5 | 19 | Prometheus metrics | 🔍 A avaliar | — |
| 4-5 | 20 | Docker support | 🔍 A avaliar | — |
| 4-5 | 21 | Pre-commit hooks | 🔍 A avaliar | — |
| 4-5 | 22 | Semantic release | 🔍 A avaliar | — |
| 4-5 | 23 | GH Actions matrix | 🔍 A avaliar | — |
| 4-5 | 24 | MkDocs documentation | ⚠️ Existe (`docs/`, `mkdocs.yml`, workflow `documentation-build.yml`) — melhorias possíveis | — |
| 4-5 | 25 | Performance benchmarks | 🔍 A avaliar | — |

## 🚧 Tarefas (detalhe)
### [x] T1 — Decompor `main.py` (Fase 1, #2) ✅ CONCLUÍDA
- **Branch**: `refactor/phase1-decompose-main`
- **Status**: ✅ Concluída (aguardando aprovação p/ push → merge em `main` → exclusão da branch)
- **Objetivo**: separar responsabilidade de orquestração (pipeline/CLI) de renderização de documentos (formatação + geração de README/markdown).
- **Arquivos**:
  - `src/release_docs.py` (NOVO, ~323 linhas): constantes de release + helpers puros (`_build_release_name`, `_slugify_category`, `_get_release_emoji`, formatadores) + geração de arquivos/README (`_generate_release_files`, `_update_readme_*`, `_build_release_block`, `_update_badge`).
  - `src/main.py` (~960 → ~145 linhas de orquestração): `detect_new_release`, `_process_*`, `_generate_ai_reports_async`, `run_pipeline`, `main` + re-export das funções movidas (padrão shim já usado no projeto).
  - Testes ajustados: `tests/test_src_main.py`, `tests/test_main_extra.py`, `tests/test_main_coverage.py`, `tests/test_i18n.py` — patches de `RELEASES_DIR` agora incidem também em `src.release_docs.RELEASES_DIR`; `generate_toggle_html` re-exportado em `main` p/ compatibilidade.
- **Commits**: 1 (refactor + ajustes de testes + status)
- **Validação (uv)**: ruff ✅ | black ✅ | mypy (strict) ✅ | pytest ✅
- **Cobertura**: 95% (195 linhas não cobertas — igual/levemente melhor que baseline 196).
- **Resultado pytest**: 683 passaram / 685; as 2 falhas (`test_load_meta_os_error`, `test_load_cache_os_error`) são **pré-existentes e ambientais** (rodamos como `root` no sandbox; passam no runner GitHub). Nenhuma falha nova introduzida.
- **Merge/Exclusão**: ✅ (merge em `main` + branch `refactor/phase1-decompose-main` excluída)

### [x] T2 — Higiene de exceções (#5) ✅ CONCLUÍDA
- **Branch**: `refactor/phase2-exception-hygiene`
- **Status**: ✅ Concluída (merge em `main` local; push em lote pendente de aprovação)
- **Objetivo**: eliminar os 6 `except ...: pass` silenciosos; `logger.debug` (best-effort: github CLI, ToC, diff/PR) e `logger.warning` (`.meta.json` corrompido).
- **Arquivos**: `src/automation/github_ops.py` (_logger+_), `src/release_summarizer.py` (_logger+_), `src/health.py`, `src/scraper.py`, `src/workflow.py`.
- **Validação**: ruff ✅ | black ✅ | mypy ✅ | pytest ✅ (95% cov; 2 falhas pré-existentes ambientais).
- **Notas**: 17 `except Exception` restantes já logam; narrowing fica como T2b opcional.

### [x] T3 — Wrappers duplicados (#3) ✅ CONCLUÍDA
- **Branch**: `refactor/t3-resolve-wrappers`
- **Objetivo**: confirmar se há duplicação real de wrappers e fechar o item.
- **Achado**: `src/automation/github_ops.py::run_gh()` (função nested, exclusiva p/ `gh issue create`) e `src/workflow.py::_run_gh(args, check)` (wrapper genérico usado em PR/merge em `workflow.py:193,208`) têm responsabilidades e call sites distintos — **não é duplicação redundante**. Não foi removido nenhum código.
- **Resultado**: item #3 marcado como resolvido (obsoleto). Sem alteração em `.py`.

### [ ] Próximas (a partir de T4)

- T4 (#6) — Type stubs (`stubs/` dir) · T5 (#7) — Cache com invalidação inteligente (content-hash) · T6 (#8) — Dependency Injection · T7 (#9) — Event System · T8 (#10) — Async Context Managers.
- Testes (#11-13): integração real, property-based, snapshot.
- Performance (#14-16): scraping paralelo, updates incrementais, streaming.
- DX/Infra (#17-25): CLI (click/typer), logging estruturado, Prometheus, Docker, pre-commit, semantic release, GH Actions matrix, MkDocs, benchmarks.

## 📝 Notas
- Plano original estava obsoleto: #1 e #4 já estavam implementados no código atual.
- CI exige **cobertura mínima de 95%** (`--cov-fail-under=95`); qualquer refactor deve mantê-la.
- Ambiente sandbox é **arm64**; `uv` provê Python 3.14 para arm64.
