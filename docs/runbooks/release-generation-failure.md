# Runbook — Falha na Geração de Release

## Sintomas

- O pipeline de releases (`release_notes_pipeline.yml`) falha
- Arquivos Markdown de release não são gerados em `releases/`
- `.meta.json` não é atualizado
- README não reflete a release mais recente
- Release Notes publicadas no GitHub Pages estão desatualizadas

## Causas Comuns e Ações

### 1. Falha no Scraper (Salesforce Help inacessível)

O scraper não consegue acessar a Salesforce Help (timeout, DNS, mudança de DOM).

**Ação:**

- Verificar conectividade: `curl -I https://help.salesforce.com`
- Executar scraper localmente para diagnóstico:
  ```bash
  uv run python src/main.py --dry-run
  ```
- Verificar se os selectors do DOM ainda são válidos (ver `docs/SOURCE_SCHEMA.md`)
- Se o DOM mudou, atualizar selectors e snapshots

### 2. Falha no Parser (estrutura de HTML alterada)

O parser não consegue extrair a árvore de tópicos ou as tabelas de feature impact.

**Ação:**

```bash
# Rodar snapshot tests para detectar regressão
uv run pytest tests/test_snapshot.py -v

# Se falhar, verificar diff e atualizar snapshots se a mudança foi intencional
uv run pytest tests/test_snapshot.py --snapshot-update
```

### 3. Falha no LLM (provider indisponível)

A classificação de release ou a geração de resumos falha porque nenhum provider LLM está disponível.

**Ação:**

- Verificar se pelo menos uma chave LLM está configurada nos secrets
- Verificar se o provider tem quota disponível
- Executar em modo dry-run para validar sem chamar LLM:
  ```bash
  uv run python src/main.py --dry-run
  ```

### 4. Falha na Geração de Markdown (permissão, caminho inválido)

O generator não consegue escrever os arquivos Markdown.

**Ação:**

- Verificar permissões do diretório `releases/`:
  ```bash
  ls -la releases/
  ```
- Verificar se o caminho do release é válido e criável

### 5. Falha na Atualização do README

O README bilingue não é atualizado após a geração.

**Ação:**

- Verificar se o script de geração do README executou sem erro
- Se o README foi modificado manualmente, pode haver conflito com a geração automática
- Reverter mudanças manuais no README antes de rodar o pipeline novamente

### 6. Falha no Commit e Push

O pipeline não consegue commitar e pushar as mudanças.

**Ação:**

- Verificar permissões do token de autenticação (GITHUB_TOKEN ou RELEASE_TOKEN)
- Verificar se o branch está protegido por branch protection rules
- Se usar RELEASE_TOKEN, confirmar que ele tem escopo `repo`

## Verificação Pós-Correction

```bash
# 1. Executar pipeline em dry-run para validar sem efeitos colaterais
uv run python src/main.py --dry-run

# 2. Verificar se releases foram geradas
ls -la releases/

# 3. Verificar meta.json
cat releases/*.meta.json 2>/dev/null | head -50

# 4. Verificar se README foi atualizado
git diff README.md

# 5. Rodar testes
uv run pytest tests/ -v

# 6. Validar documentação
uv run mkdocs build --strict
```
