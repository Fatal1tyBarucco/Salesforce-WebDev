# Local Development

## Setup

Install dependencies:

```bash
uv sync --extra dev
```

Para instalar apenas o ambiente de execução (sem ferramentas de desenvolvimento):

```bash
uv sync
```

## Execute Pipeline

```bash
uv run python src/main.py
```

## Execute Tests

```bash
uv run pytest
```

## Validate Quality

```bash
uv run ruff check .
uv run black --check .
uv run mypy src/
```
