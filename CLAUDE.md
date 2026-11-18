# CLAUDE.md — Salesforce-WebDev

Pipeline ETL "Knowledge-as-Code": extrai, classifica e versiona as Salesforce Release Notes.
Este arquivo traz só o que o Claude Code não deduz sozinho. Convenções gerais e histórico
estão em `AGENTS.md` (leia sob demanda; **não** use `@AGENTS.md`, ele é grande e carregaria
tudo em toda sessão).

## Stack

Python `>=3.14,<3.15` · uv · Playwright + BeautifulSoup/lxml · LLM multi-provider
(OpenAI-compatível e Google GenAI) · Pydantic · FastAPI (extra `healing`) · MCP `mcp==1.30.0`.

## Mapa do código

- `src/core/` (classification, enrichment, pipeline, summarization), `src/domain/`,
  `src/infrastructure/` (scraping, parsing, llm, llm_adapters, mcp, storage, github, ...) e
  `src/ai/`: **arquitetura nova (Clean Architecture)**. Código novo vai aqui.
- Módulos soltos em `src/*.py` (`scraper.py`, `parser.py`, `llm_service.py`, `main.py`...):
  **legado em migração**. Corrija bugs, mas não expanda; migre quando tocar.
- `releases/{spring_26,summer_26,winter_26,winter_27}/` + `releases/ARCHIVE.md`: dados
  versionados. `releases/*/.meta.json` é a fonte de verdade da sincronização de docs.
- `tests/` (factories em `tests/factories.py`, goldens em `tests/golden/`, snapshots syrupy),
  `stubs/` (stubs do mypy), `docs/` (MkDocs), `k8s/`, `scripts/`, `prompts/`.

## Comandos

```bash
uv sync --extra dev                       # dependências
uv run playwright install chromium        # browsers do scraper
uv run ruff check . && uv run black --check .
uv run mypy src/ --ignore-missing-imports
uv run pytest tests/ -q                   # rápido
uv run pytest tests/ --cov=src --cov-fail-under=95   # gate completo
uv run python -m src.main [--release SLUG] [--dry-run]
python3 .github/scripts/docs_sync_engine.py reconcile   # após mexer em docs
```

## Definição de pronto (espelha o CI `python-quality.yml`)

**Ruff** (lint + format), mypy (`src/`) e pytest com cobertura ≥95% precisam passar.
Antes de commitar, rode `uv run ruff format .`. `uv lock --check` também é gate:
`uv.lock` e `pyproject.toml` devem ter a mesma `version` (corrija com `uv lock`, nunca à mão).

## Regras de código

- DI explícita, sem estado global, Pydantic nas fronteiras. 100% de type hints em `src/`
  (mypy `strict = true`).
- Null-safe e bulk-safe; sem exceção por referência nula.
- **Nunca** `except (A, B):` sem `as`: o Black 26.10 remove os parênteses e gera código
  inválido no py314. Use `except (A, B) as e:` ou `except Exception:`.
- `datetime.now()`, não `datetime.utcnow()` (deprecado).
- HTML externo e respostas de LLM são **entrada não confiável**: valide com schemas Pydantic e
  trate como risco de prompt injection.
- Commits no padrão Conventional Commits: `feat|fix|refactor|test|docs|chore(scope): ...`.

## Testes

- Determinísticos: use `tests/factories.py`. Nada de rede real; `tests/conftest.py` já
  stuba `openai` e `google`.
- Testes **não escrevem na raiz do repo**. `generate_ai_reports_async` grava `CHANGELOG.md`,
  `QUALITY_REPORT.md`, `DIFF_REPORT.md` etc. no cwd: use `tmp_path`/`isolated_cwd`. Nunca
  commite `NOTIFICATION_DIGEST.md`.
- Goldens (`tests/golden/**`) são byte-exatos: regenere só com
  `CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_*.py`. Snapshots:
  `pytest tests/test_snapshot.py --snapshot-update`. Nunca edite à mão.
- `_build_release_block` é congelado pelos goldens do summarizer (`lines = [""]` e linhas em
  branco após `</details>` são intencionais).
- `tests/infrastructure/mcp/test_knowledge_server.py` usa a API **FastMCP**
  (`server.mcp.call_tool`, `server.mcp.list_tools`), não a API low-level do `Server`.
- syrupy: **não** adicione ao `pyproject.toml` (rebaixa o pytest para 8.4.2). O CI instala com
  `uv pip install "syrupy>=4.9.0,<5"`; localmente use `uv run --no-sync` ou `python -m pytest`.

## Documentação

- Qualquer mudança em docs exige: `reconcile` → validar (lint + links) → commit + push.
  `docs/.documentation-manifest.json` é gerado pelo `reconcile`; não edite.
- `.github/scripts/docs_sync_engine.py` deve continuar **stdlib-only** em `python3`. Depois de
  editá-lo: `python3 -m py_compile` e `... audit` (0 findings).
- `docs/`, `releases/`, `tests/golden/`, `.claude/`, `.github/` não são reescritos pelo
  reconcile. Seletores do scraper: `docs/SOURCE_SCHEMA.md`.

## CI e GitHub

- Nenhum token disponível edita `.github/workflows/*` (HTTP 403). Se uma correção exigir isso,
  entregue o diff e avise um humano. **Nunca diga que fez push que não aconteceu.**
- `settings.json` nega `Read(.github/workflows/*)`; peça o conteúdo ao humano se precisar.
- Ações de terceiros ficam fixadas por SHA; não volte para tags mutáveis (`@v5`).
- `actions/upload-artifact` ≥ v4.4 ignora arquivos ocultos: use `include-hidden-files: true`.
- Ao trabalhar numa issue, mantenha o GitHub Project #5 em dia (In Progress → In Review →
  Done). IDs e mutations GraphQL estão em `AGENTS.md`, seção "GitHub Project Integration".

## Ambiente (Termux / ARM64)

`mkdocs` best-effort falha (Playwright sem wheel ARM64) e `ruff` pode não estar linkado: isso
não bloqueia o CI. Reporte o bloqueio como ele é, sem inventar resultado.

## Fluxos de IA do repo

- Comandos (`.claude/commands/`): `/diag`, `/refactor <módulo>`, `/release`, `/audit`,
  `/triage <issue>`, `/prompt-eval`.
- Subagentes (`.claude/agents/`): `architect`, `python-engineer`, `test-engineer`,
  `code-reviewer`, `docs-writer`, `release-manager`, `security-auditor`.
- Skills (`.claude/skills/`): `add-release-source`, `new-llm-provider`, `debug-ci`,
  `bump-quality`, `prompt-eval`, `knowledge-as-code-update`.
- MCP (`.mcp.json`): `github` (remoto, usa `GITHUB_TOKEN`), `playwright` (debug do scraper) e
  `salesforce-knowledge` (serve `releases/` via FastMCP; exige `uv sync --extra dev` antes).
- Hooks (`.claude/hooks/`, entrada por JSON no stdin; não existe `$FILE`): após Edit/Write em
  `.py` roda `ruff check --fix` + `ruff format`; antes de `git commit` roda ruff check,
  `ruff format --check`, mypy e `uv lock --check`; antes de `git push` roda `pytest -x`
  (timeout 300s — **timeout = não verificado, não falha**; veja hook). Falha bloqueia (exit 2).

## Variáveis de ambiente

Pelo menos um provider LLM: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY` ou
`GEMINI_API_KEY`. Automação GitHub: `GITHUB_TOKEN`, `RELEASE_TOKEN`; opcionais:
`OPENCODE_API_KEY`, `COMMENT_TOKEN`. Não existe `.env.example`; nunca leia nem commite `.env*`.

## Referências

`docs/ARQUITETURA.md` · `docs/DEBITO_TECNICO.md` · `docs/MODERNIZACAO.md` ·
`docs/architecture/decisions/` (ADRs) · `docs/SOURCE_SCHEMA.md` · `PLANO_DE_MODERNIZACAO.md`
