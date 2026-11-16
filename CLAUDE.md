# CLAUDE.md — Salesforce-WebDev (Claude Code Context)

> **Versão**: 2.0 (2026-11-15)  
> **Fonte de verdade para agentes**: @AGENTS.md (este arquivo só acrescenta o específico do Claude Code)

---

## Contexto Essencial

**Projeto**: Pipeline ETL "Knowledge-as-Code" para Salesforce Release Notes  
**Stack**: Python 3.14 + uv + Playwright + LLM multi-provider (OpenAI/Google GenAI) + Pydantic + FastAPI  
**Arquitetura**: Clean Architecture em migração (`src/core/`, `src/infrastructure/`, `src/ai/`) + módulos legados em `src/` raiz  
**Dados versionados**: `releases/{spring_26,summer_26,winter_26,winter_27}/` + `releases/ARCHIVE.md`

---

## Comandos Essenciais

| Ação | Comando |
|------|---------|
| Instalar deps | `uv sync --extra dev` |
| Instalar Playwright | `uv run playwright install chromium` |
| Lint + Format | `uv run ruff check . && uv run ruff format --check .` |
| Typecheck | `uv run mypy src/ --ignore-missing-imports` |
| Testes (rápido) | `uv run pytest tests/ -q` |
| Testes + Coverage | `uv run pytest tests/ --cov=src --cov-fail-under=95` |
| Docs sync (local) | `python3 .github/scripts/docs_sync_engine.py reconcile` |
| Pipeline manual | `uv run python -m src.main [--release SLUG] [--dry-run]` |

---

## Convenções Obrigatórias (além do AGENTS.md)

1. **Clean Architecture**: novo código em `domain/`, `services/`, `infrastructure/`, `entrypoints/` — DI explícita, sem estado global, Pydantic nas fronteiras
2. **SOLID + Null-safe + Bulk-safe**: sem exceções por referência nula; `except (A, B) as e:` (nunca `except (A, B):` — Black 26.10 quebra)
3. **Ruff only**: `ruff check` + `ruff format` (Black removido na Fase 1)
4. **Mypy strict progressivo**: overrides temporários rastreados em ADR; 100% type hints em `src/`
5. **Testes determinísticos**: factories em `tests/factories.py`; golden files em `tests/golden/`; syrupy para snapshots LLM
6. **Fronteiras não confiáveis**: HTML externo + respostas LLM → validar com Pydantic schemas; tratar como risco de prompt injection
7. **Conventional Commits**: `feat(scope):`, `fix(scope):`, `refactor(scope):`, `test(scope):`, `docs(scope):`, `chore(scope):`

---

## Definição de Pronto (DoD)

- [ ] `uv run ruff check .` passa
- [ ] `uv run ruff format --check .` passa
- [ ] `uv run mypy src/ --ignore-missing-imports` passa
- [ ] `uv run pytest tests/ --cov=src --cov-fail-under=95` passa (≥95%)
- [ ] Docs alteradas → `reconcile` + validação + commit+push
- [ ] GitHub Project board atualizado (In Progress → In Review → Done)
- [ ] ADR criado para decisões arquiteturais irreversíveis

---

## Armadilhas Conhecidas (do AGENTS.md + Fase 1)

- **Black 26.10 + py314**: remove parênteses de `except (A, B):` → SyntaxError. **Use Ruff format.**
- **pytest-syrupy**: força downgrade pytest 9.x → 8.4.2 local. Use `uv run --no-sync` ou `python -m pytest`.
- **`actions/upload-artifact` v4.4+**: exclui hidden files por default. Use `include-hidden-files: true`.
- **Testes não escrevem na raiz**: `generate_ai_reports_async` escreve `CHANGELOG.md` etc. relativo ao cwd — use `tmp_path` fixture.
- **`docs_sync_engine.py`**: deve rodar com `python3` stdlib-only. Após editar, `python3 -m py_compile` + `audit`.
- **Push em `.github/workflows/*`**: **falha sempre** (HTTP 403 GitHub App / GITHUB_TOKEN). Reporte a humano — nunca diga que pushou.
- **`fix_markdown.py`**: deve rastrear estado de fence open/close (corrigido 2026-11-04). Valide com `python3 .github/scripts/fix_markdown.py` → `git status` limpo.
- **mkdocs ARM64 (Termux)**: `playwright` sem wheel → best-effort falha. `continue-on-error: true` já configurado.
- **Ruff 0.17.1 não linkado / python3.13 indisponível no Termux**: não bloqueia CI GitHub (ubuntu-latest). Documente honestamente.

---

## Workflows de IA (Claude Code)

| Comando | Descrição |
|---------|-----------|
| `/diag` | Diagnóstico rápido do repo (gates, arquitetura, débito) |
| `/refactor <módulo>` | Refatoração segura com testes de caracterização |
| `/release` | Dispara release-please (ou prepara Release PR manual) |
| `/audit` | Auditoria completa: arquitetura, segurança, performance, deps |
| `/triage <issue>` | Triagem de issue/PR: labels, prioridade, duplicatas, info faltante |
| `/prompt-eval` | Avaliação de prompts versionados (promptfoo) |

**Subagentes disponíveis** (`.claude/agents/`): `architect`, `python-engineer`, `test-engineer`, `code-reviewer`, `docs-writer`, `release-manager`, `security-auditor`

**Skills disponíveis** (`.claude/skills/`): `add-release-source`, `new-llm-provider`, `debug-ci`, `bump-quality`, `prompt-eval`, `knowledge-as-code-update`

---

## Variáveis de Ambiente (`.env.example`)

```bash
# LLM Providers (pelo menos um)
OPENROUTER_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
GEMINI_API_KEY=

# GitHub (para automação)
GITHUB_TOKEN=
RELEASE_TOKEN=

# Opcional
OPENCODE_API_KEY=
COMMENT_TOKEN=
```

---

## Referências Rápidas

- Arquitetura: `docs/ARQUITETURA.md` (diagramas Mermaid)
- Débito técnico: `docs/DEBITO_TECNICO.md` (evidência arquivo:linha)
- Plano modernização: `docs/MODERNIZACAO.md` (status por fase)
- ADRs: `docs/architecture/decisions/`
- Selectors Salesforce: `docs/SOURCE_SCHEMA.md`
