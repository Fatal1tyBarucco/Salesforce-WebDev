# Local Development

## Setup

Install dependencies:

```bash
uv sync --extra dev
```text

Para instalar apenas o ambiente de execução (sem ferramentas de desenvolvimento):

```bash
uv sync
```text

## Execute Pipeline

```bash
uv run python src/main.py
```text

## Execute Tests

```bash
uv run pytest
```text

## Validate Quality

```bash
uv run ruff check .
uv run black --check .
uv run mypy src/
```
