# Local Development

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Execute Pipeline

```bash
python -m src.main
```

## Execute Tests

```bash
pytest
```

## Validate Quality

```bash
ruff check .
black --check .
mypy src/
```
