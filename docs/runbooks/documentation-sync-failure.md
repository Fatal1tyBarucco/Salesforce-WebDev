# Runbook — Falha no Document Sync

## Sintomas

- Workflow `documentation-sync.yml` falha no step de reconciliação determinística
- `mkdocs build --strict` reporta erro; esse step é best-effort e não bloqueia o sync
- Link checker ou markdown lint bloqueiam o commit
- O workflow detecta drift mas não consegue reconciliar
- Commit do bot é skipado pelo anti-loop sem motivo aparente

## Diagnóstico e causas comuns

### 1. Inspecionar drift sem escrita

O modo `audit` foi removido. Todo push/PR executa `reconcile` obrigatoriamente: instala dependências, reconcilia, valida e faz push.

**Validação:**

```bash
# Executar a engine de detecção de drift localmente (leitura)
DRIFT_REPORT=/tmp/drift_report.json python3 .github/scripts/docs_sync_engine.py audit
```text

**Ação:**

- No GitHub Actions, o modo é obrigatório (`reconcile`); `audit` foi removido para garantir que qualquer alteração reflita na documentação.
- Inspecionar `/tmp/drift_report.json` no ambiente local para ver os findings

### 2. mkdocs build --strict falhou

O build falha por:

- Nav inválida (arquivo referenciado não existe)
- Snippet faltando (`--8<--` apontando para arquivo inexistente)
- Diretiva mkdocstrings com módulo inexistente

**Validação local:**

```bash
uv run mkdocs build --strict
```text

**Ação:**

- Corrigir a causa do erro (criar arquivo faltante, remover snippet inválido, ajustar nav)
- Commit da correção manualmente

### 3. Link checker encontrou link quebrado

`markdown-link-check` falhou porque um link Markdown está quebrado (HTTP 404, DNS falha, etc.).

**Validação:**

```bash
npx --yes markdown-link-check --quiet --config .github/link-check-config.json docs/
```text

**Ação:**

- Corrigir o link quebrado
- Se o link for intencionalmente externo e não-controlável, adicionar ao `ignorePatterns` do `.github/link-check-config.json`

### 4. Markdown lint falhou

`markdownlint-cli2` encontrou violações de estilo.

**Validação:**

```bash
npx --yes markdownlint-cli2 "docs/**/*.md" --config-file .markdownlint.json --ignore node_modules
```text

**Ação:**

- Corrigir as violações reportadas (títulos, listas, espaçamento, etc.)
- Se uma regra é muito restritiva para o contexto, ajustar no `.markdownlint.json`

### 5. Anti-loop skipou sem motivo

O guard anti-loop skipou porque o último commit tem autor `github-actions[bot]` e mensagem começando com `docs(sync):`.

**Ação:**

- Verificar se há commits duplicados ou bootstraps incorretos
- Se for esperado (ex: sync acaba de rodar), é comportamento normal

### 6. Conflito de concorrência no push

O push sem force pode ser rejeitado se outro processo atualizar o branch durante a execução.

**Ação:**

- O workflow tenta buscar, rebasear e fazer push até três vezes, com espera progressiva
- Conflito de conteúdo interrompe o workflow para evitar sobrescrever alterações; resolva-o e execute novamente

## Verificação Pós-Falha

```bash
# 1. Verificar estado do branch
git status

# 2. Verificar diff pendente
git diff --stat

# 3. Validar build
uv run mkdocs build --strict

# 4. Validar links
npx --yes markdown-link-check --quiet --config .github/link-check-config.json docs/

# 5. Verificar lint
npx --yes markdownlint-cli2 "docs/**/*.md" --config-file .markdownlint.json --ignore node_modules
```
