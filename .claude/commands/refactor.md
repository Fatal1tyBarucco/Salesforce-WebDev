---
description: Refatoração segura de módulo com testes de caracterização
argument-hint: <módulo>
---

# /refactor <módulo> — Refatoração Segura

Refatora um módulo seguindo Clean Architecture, com testes de caracterização (golden files) protegendo comportamento.

## Uso
```
/refactor src/scraper.py
/refactor src/llm_service.py
/refactor src/main.py
```

## Fluxo Obrigatório

### 1. Verificar Testes de Caracterização Existentes
```bash
# Se não existirem, CRIE primeiro (test-engineer)
uv run pytest tests/test_characterization_*.py -q
```

### 2. Rodar Gates Antes
```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/ -x -q
```

### 3. Planejar Refatoração (com architect se complexo)
- Identificar responsabilidades a extrair
- Definir ports/adapters (Clean Architecture)
- DI explícita no construtor
- Pydantic nas fronteiras

### 4. Implementar (python-engineer)
- Novo código em `src/services/`, `src/infrastructure/`, `src/domain/`
- Testes unitários novos (test-engineer)
- Manter comportamento idêntico (golden files passam)

### 5. Validar
```bash
# Golden files devem passar SEM alteração
uv run pytest tests/test_characterization_*.py -q

# Gates completos
uv run ruff check . && uv run ruff format --check . && uv run mypy src/ --ignore-missing-imports && uv run pytest tests/ --cov=src --cov-fail-under=95
```

### 6. Atualizar Docs se Arquitetura Mudou
- `docs/ARQUITETURA.md` (diagramas Mermaid)
- ADR em `docs/architecture/decisions/adr-NNN-titulo.md`

## Regras de Ouro
- **Nunca refatore sem golden files** — crie antes se não existirem
- **Um módulo por PR** — mudanças pequenas, revisáveis
- **DI explícita** — não instancie `CacheManager`, `RateLimiter`, `CircuitBreaker` internamente
- **Null-safe** — `except (A, B) as e:`, nunca `except (A, B):`
