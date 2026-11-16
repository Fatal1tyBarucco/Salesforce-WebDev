---
name: bump-quality
description: Elevar qualidade do código: mypy strict progressivo, type hints 100%, cobertura >95%, remover `# type: ignore`/`noqa` injustificados, refatorar god modules.
---

# Skill: bump-quality

## Quando Usar
- Migrar módulo para mypy strict (remover overrides temporários)
- Aumentar cobertura de testes em módulo crítico
- Remover `# type: ignore` / `# noqa` sem justificativa escrita
- Refatorar god module (`main.py`, `LLMService`, `SalesforceReleaseScraper`)

## Passos

### 1. Mypy Strict Progressivo (módulo a módulo)
```bash
# Verifique erros atuais no módulo
uv run mypy src/modulo/ --ignore-missing-imports --pretty

# Adicione overrides temporários APENAS em pyproject.toml [tool.mypy.overrides]
# Exemplo:
# [[tool.mypy.overrides]]
# module = "src.legacy_modulo"
# disallow_untyped_defs = false
# ignore_missing_imports = true
# # ADR-XXX: motivo temporário, prazo YYYY-MM-DD
```

### 2. Type Hints 100% em `src/`
- Todas as funções públicas: `def fn(arg: Type) -> ReturnType:`
- Classes: atributos tipados, `__init__` tipado
- Generics: `list[Type]`, `dict[Key, Value]`, `Optional[Type]`
- `from __future__ import annotations` no topo de cada arquivo

### 3. Cobertura >95% (branch coverage)
```bash
# Identifique gaps
uv run pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=95

# Adicione testes em tests/test_modulo.py
# Use factories de tests/factories.py
# Para LLM paths: contract tests com mocks
```

### 4. Remover `# type: ignore` / `# noqa` Injustificados
```bash
# Liste todos
grep -r "# type: ignore" src/ --include="*.py"
grep -r "# noqa" src/ --include="*.py"

# Para cada um: corrija a causa RAIZ ou documente justificativa no código + ADR
# Exemplo justificado:
# x = func()  # type: ignore[assignment] — ADR-012: lib sem stubs, migração pendente
```

### 5. Refatorar God Modules (prioridade: main.py, LLMService, Scraper)
- Extraia responsabilidades para services/adapters
- DI explícita no construtor
- Testes de caracterização (golden) ANTES de refatorar

### 6. Validação Final
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/ --cov=src --cov-fail-under=95
```
