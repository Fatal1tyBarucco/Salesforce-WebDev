# Runbook — Falha no Document Sync

## Sintomas

- Workflow `documentation-sync.yml` falha no step de reconciliação LLM
- `mkdocs build --strict` falha após mudanças documentais
- Link checker ou markdown lint bloqueiam o commit
- O workflow detecta drift mas não consegue reconciliar
- Commit do bot é skipado pelo anti-loop sem motivo aparente

## Causa Raiz Comum

### 1. Provider LLM indisponível

Se `GOOGLE_API_KEY`, `OPENCODE_API_KEY` e `OPENROUTER_API_KEY` estiverem ausentes ou inválidos, o step de reconciliação falha.

**Validação:**

```bash
# Verificar secrets configurados (secreto, apenas indicador de presença)
gh secret list | grep -E "GOOGLE_API_KEY|OPENCODE_API_KEY|OPENROUTER_API_KEY"
```

**Ação:**

- Confirmar que pelo menos uma chave LLM está configurada nos secrets do repositório
- Se nenhuma chave disponível, o sync deve ser executado em modo `audit` (sem escrita)

### 2. mkdocs build --strict falhou

O build falha por:

- Nav inválida (arquivo referenciado não existe)
- Snippet faltando (`--8<--` apontando para arquivo inexistente)
- Diretiva mkdocstrings com módulo inexistente

**Validação local:**

```bash
uv run mkdocs build --strict
```

**Ação:**

- Corrigir a causa do erro (criar arquivo faltante, remover snippet inválido, ajustar nav)
- Commit da correção manualmente

### 3. Link checker encontrou link quebrado

`markdown-link-check` falhou porque um link Markdown está quebrado (HTTP 404, DNS falha, etc.).

**Validação:**

```bash
uv run markdown-link-check --config .github/link-check-config.json docs/
```

**Ação:**

- Corrigir o link quebrado
- Se o link for intencionalmente externo e não-controlável, adicionar ao `ignorePatterns` do `.github/link-check-config.json`

### 4. Markdown lint falhou

`markdownlint-cli2` encontrou violações de estilo.

**Validação:**

```bash
uv run markdownlint-cli2 "docs/**/*.md" --config-file .markdownlint.yml
```

**Ação:**

- Corrigir as violações reportadas (títulos, listas, espaçamento, etc.)
- Se uma regra é muito restritiva para o contexto, ajustar no `.markdownlint.yml`

### 5. Anti-loop skipou sem motivo

O guard anti-loop skipou porque o último commit tem autor `github-actions[bot]` e mensagem começando com `docs(sync):`.

**Ação:**

- Verificar se há commits duplicados ou bootstraps incorretos
- Se for esperado (ex: sync acaba de rodar), é comportamento normal

### 6. Conflito de concorrência no push

O `git push --force-with-lease` falhou porque outro processo escreveu no branch entre o checkout e o push.

**Ação:**

- O `git pull --rebase` antes do push deve resolver a maioria dos casos
- Se persistir, re-executar o workflow manualmente

## Verificação Pós-Falha

```bash
# 1. Verificar estado do branch
git status

# 2. Verificar diff pendente
git diff --stat

# 3. Validar build
uv run mkdocs build --strict

# 4. Validar links
uv run markdown-link-check --config .github/link-check-config.json docs/

# 5. Verificar lint
uv run markdownlint-cli2 "docs/**/*.md" --config-file .markdownlint.yml
```
