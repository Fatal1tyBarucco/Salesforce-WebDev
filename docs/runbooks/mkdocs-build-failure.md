# Runbook — Falha no MkDocs Build

## Sintomas

- `mkdocs build` ou `mkdocs build --strict` retorna erro
- GitHub Actions workflow `documentation-build.yml` falha no step de build
- O site publicado no GitHub Pages não reflete as mudanças esperadas
- Erro de "file not found" ou "directive não reconhecida" nos logs

## Causas Comuns e Ações

### 1. Nav inválida — arquivo referenciado não existe

O mkdocs.yml referencia um arquivo que não existe no disco.

**Erro típico:**

```
mkdocs.exceptions.ConfigError: Documentation file not found: docs/arquivo-inexistente.md
```

**Ação:**

```bash
# Verificar qual arquivo está faltando
uv run mkdocs build --strict 2>&1 | grep "Documentation file not found"

# Verificar se o arquivo existe
ls -la docs/caminho/para/arquivo.md

# Se faltar, criar o arquivo ou remover a entrada do nav
```

### 2. Snippet Markdown faltando

`docs/changelog.md` usa `--8<-- "CHANGELOG.md"` (pymdownx.snippets). Se `CHANGELOG.md` não existir na raiz, o snippet falha.

**Ação:**

```bash
# Verificar se CHANGELOG.md existe na raiz
ls -la CHANGELOG.md 2>/dev/null || echo "CHANGELOG.md não existe"

# Se não existir, criar:
cat > CHANGELOG.md << 'EOF'
# Changelog

## Versão Atual

Documentação em construção.
EOF
```

Ou remover o snippet de `docs/changelog.md` e manter o changelog apenas no MkDocs.

### 3. Diretiva mkdocstrings com módulo inexistente

Um arquivo em `docs/api/*.md` referencia `::: src.modulo` e o módulo não existe em `src/`.

**Ação:**

```bash
# Verificar se o módulo existe
ls -la src/modulo_que_deve_existir.py

# Se não existir, remover ou corrigir a diretiva no arquivo docs/api/*.md
```

### 4. Extensão de Markdown não carregada

Uma extensão usada no documento não está listada em `mkdocs.yml` em `markdown_extensions`.

**Ação:**

- Verificar se a extensão está em `mkdocs.yml` em `markdown_extensions`
- Se for uma extensão customizada (ex: `pymdownx.*`), garantir que está nas dependências

### 5. Plugin mkdocstrings com configuração inválida

O handler Python do mkdocstrings não consegue encontrar os módulos.

**Ação:**

```bash
# Verificar se os módulos estão acessíveis
PYTHONPATH=. uv run python -c "import src.main; print('OK')"

# Se falhar, verificar se src/ tem __init__.py ou se o path está correto
ls src/__init__.py
```

### 6. Erro de template ou tema

O Material for MkDocs não consegue carregar um template customizado.

**Ação:**

- Verificar se `custom_dir` no mkdocs.yml aponta para um diretório existente
- Se usar template customizado, confirmar que os arquivos necessários existem

## Verificação Pós-Correction

```bash
# Build completo com validação estrita
uv run mkdocs build --strict

# Verificar se o site foi gerado
ls -la site/

# Verificar navegação
grep -r "href=" site/sitemap.xml | head -20
```
