# ADR-012 - Absolute Documentation Sync (Contrato Verificável)

A documentação publicada no GitHub Pages passa a ser um espelho fiel do repositório, garantido por um contrato verificável em CI: o manifest `.documentation-manifest.json` é o contrato formal entre código e documentação, e qualquer divergência entre manifest, `mkdocs.yml` (nav), árvore `docs/` e árvore real do repositório é um defeito de build que falha o pipeline — não um aviso.

## Status

**Aceito** — Implementado em `.github/scripts/docs_contract.py`, `.github/scripts/docs_sync_engine.py` (hardening), `mkdocs.yml`, `docs/gen_ref_pages.py`, workflows `documentation-sync.yml` (v2.3), `documentation-build.yml` e `ai-docs.yml`.

## Contexto

A auditoria de sincronia (Fase 1, 2026-11-19) sobre o estado `8397b61` encontrou:

| Estado | Contagem | Exemplos |
|--------|----------|----------|
| ÓRFÃO | 0 | — |
| OMITO | 19 | 7 workflows, 6 scripts de CI, 3 manifestos k8s, 3 scripts utilitários sem cobertura prose |
| OBSOLETO | 1 | tabela de releases do `README.md` divergente de `releases/*.meta.json` |
| DIVERGENTE | 1 | `README.md` sem tabela de releases (paridade pt-BR/English quebrada) |

Causas raiz pelas quais a automação existente permitia o drift:

1. O engine detectava `MISSING_API_DOC` mas não tinha detector nem removedor de evocadores órfãos (módulo apagado, página permanecia).
2. O manifest era regenerado, mas nada validava o contrato de forma dura: o audit retornava 0 independentemente dos findings.
3. Não havia filtro de "artefatos documentáveis": workflows, scripts, k8s e prompts novos não geravam pendência de documentação.
4. A tabela de releases era reconciliada em `docs/index.md` e `README.en.md`, mas não em `README.md` (pt-BR raiz).
5. O build publicava com placeholder de analytics `G-XXXXXXXXXX` e sem versionamento de docs.

## Decisão

### 1. Contrato verificável (`.github/scripts/docs_contract.py`)

Validador tipado, stdlib-only (roda em CI sem venv, como o engine), coberto por `tests/test_docs_contract.py` (15 testes, incluindo simulação de drift). Estados canônicos da Fase 1:

| Estado | Significado | Ação obrigatória |
|--------|-------------|------------------|
| `OK` | existe no repositório e está documentado | nenhuma |
| `ÓRFÃO` | documentado, artefato não existe mais | remover página, nav, links e manifest |
| `OMITO` | existe no repositório, não documentado | criar página e registrar no manifest |
| `OBSOLETO` | documentado, descreve estado desatualizado | atualizar |
| `DIVERGENTE` | pt-BR e English divergem | restaurar paridade |

Subcomandos: `validate` (gate duro, exit 1 em qualquer divergência), `report` (auditoria classificada em JSON), `parity` (paridade pt-BR/English). O gate roda no Documentation Sync (após reconcile + refresh do manifest, com índice stageado) e no Documentation Build (antes do build).

### 2. Reconciliação bidirecional com histórico de remoções

O engine passa a remover, deterministicamente:

- evocadores de API cujo módulo/pacote deixou de existir (evocadores de pacote `__init__.py` são legítimos e preservados);
- entradas de nav cujo alvo não existe nem no índice git nem no filesystem (páginas criadas na própria reconciliação nunca são removidas).

Toda remoção gera registro append-only em `manifest["removals"]` com `path`, `removed_at`, `commit` e `reason` — nada é removido silenciosamente. O histórico sobrevive a regenerações do baseline.

### 3. Filtro de artefatos documentáveis

`documentable_artifacts()` define a obrigação de documentação: módulos `src/`, workflows, scripts (`scripts/` e `.github/scripts/`), manifestos `k8s/`, prompts versionados e ADRs. Superfícies excluídas do índice público: `docs/ai-generated/`, `docs/internal/`, `docs/plans/` (permanecem no repositório; `exclude_docs` no mkdocs.yml) e artefatos locais de runtime.

O índice `docs/reference/repo-index.md` é gerado por código a partir da árvore real (152 artefatos) e o catálogo prose `docs/architecture/automation-catalog.md` cobre workflows, scripts, k8s e prompts. Cobertura é verificada por menção prose real — o índice gerado não conta como cobertura.

### 4. Publicação moderna (GitHub Pages oficial)

- Stack: `mkdocs-material` 9.x mais recente suportada, `mkdocs-gen-files` (página virtual `reference/code-tree.md` derivada de `src/`), `mkdocs-section-index`, `privacy` (sem vazamento de requisições externas), `social` cards habilitadas em CI via `enabled: !ENV [CI, false]` + extra `imaging` (pillow/cairosvg — sem wheel ARM64 em Termux, o build local permanece verde com o plugin desabilitado).
- Features: `navigation.instant`, `navigation.path`, `navigation.indexes`, `content.tooltips`, `search.share`, `toc.follow`, banner `announce` de release (bloco em `custom/main.html`, texto reconciliado pelo engine a partir de `releases/*.meta.json`).
- Versionamento: `mike` sincronizado com as tags de release (24 tags) e com a versão do `pyproject.toml` em main; o branch `gh-pages` é o ledger de versões do mike; o deploy oficial permanece `actions/upload-pages-artifact` + `actions/deploy-pages` (o ledger é materializado em `site/` antes do upload).
- Analytics: placeholder `G-XXXXXXXXXX` removido (defeito de produção; não há propriedade configurada). Reativação documentada via segredo `GA_PROPERTY` + `!ENV`, nunca placeholder commitado.
- Pin de compatibilidade documentado: o extra `docs` mantém `ruff` (formatação de signatures do mkdocstrings após a migração Black → Ruff); `mkdocs-material[imaging]` isolado no extra `imaging` para não quebrar ambientes sem cairo.

### 5. IA com determinismo primeiro

Inventário, drift, links e remoção de nav são tarefas determinísticas de script. A IA escreve prose e traduz; toda saída de IA passa pelos gates antes de commitar: contrato (`docs_contract.py validate`), markdownlint, link checker e `mkdocs build --strict` (step novo no `ai-docs.yml`). O prompt de reconciliação é versionado em `prompts/reconciliation/v1.yaml` (ADR-008) e avaliado no `.promptfoo.yaml` com asserts de fidelidade ao manifest (fonte de verdade, superfície escrevível restrita, JSON estrito, proibição de invenção). Commits do bot de sync preservam a convenção `docs(sync): reconcile documentation — [data]` com marcador skip-ci, autor `github-actions[bot]`.

### 6. Paridade pt-BR/English

A tabela de releases passa a ser reconciliada nas três superfícies (`docs/index.md`, `README.md`, `README.en.md`) a partir de `releases/*.meta.json`. O subcomando `parity` verifica versões declaradas e tabelas entre os READMEs; divergência é estado `DIVERGENTE` e falha o gate.

## Consequências

- Drift estrutural não sobrevive a um ciclo de sync: o gate falha o workflow até a reconciliação (automática para estrutura, prose via IA/humano para conteúdo).
- Novos artefatos documentáveis entram como pendência `OMITO` até existir cobertura prose — o catálogo e o índice tornam a pendência visível.
- O histórico de remoções é auditável no manifest (data, commit, motivo).
- Guards v2.1/v2.2 do Documentation Sync preservados integralmente (anti-loop, skip-ci, concurrency `pages`, push condicional, paridade).
- O build local em Termux/ARM64 continua verde: social cards desabilitadas fora do CI; mkdocs strict sem o extra imaging.
- Trade-off assumido: o nav manual permanece explícito para as superfícies curadas porque o contrato determinístico parseia o nav linha a linha; as superfícies repetitivas (API, ADRs, índice, árvore de código) são derivadas de código pelo engine e pelo mkdocs-gen-files.

## Verificação

- `uv run pytest tests/test_docs_contract.py` — 15 testes, incluindo simulação de drift (remoção → ÓRFÃO → sync remove com histórico; adição → OMITO → sync documenta).
- `python3 .github/scripts/docs_contract.py validate` — exit 0 em sincronia, exit 1 em divergência.
- `uv run mkdocs build --strict` — zero warnings.
- `python3 .github/scripts/docs_contract.py parity` — paridade pt-BR/English.
