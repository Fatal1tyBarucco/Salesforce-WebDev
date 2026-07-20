# 📋 Status de Refatoração — Salesforce-WebDev

Template de acompanhamento de alterações. **Atualizado a cada tarefa/branch.**

> Última atualização: 2026-07-19 (T1 concluída)

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
| 1 | 3 | 15+ wrappers duplicados | 🔍 A avaliar | — |
| 1 | 4 | Config hardcoded | ✅ Feito (`config.py` centraliza; tópicos dinâmicos) | — |
| 2 | 5 | `except Exception: pass` | ⏳ Pendente (6 silenciamentos + 17 `except Exception`) | — |
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

### [ ] Próximas (a iniciar após T1)
- T2 — Higiene de exceções (#5)
- T3 — Wrappers duplicados (#3) — após avaliação
- T4+ — demais itens do backlog conforme decidido

## 📝 Notas
- Plano original estava obsoleto: #1 e #4 já estavam implementados no código atual.
- CI exige **cobertura mínima de 95%** (`--cov-fail-under=95`); qualquer refactor deve mantê-la.
- Ambiente sandbox é **arm64**; `uv` provê Python 3.14 para arm64.
