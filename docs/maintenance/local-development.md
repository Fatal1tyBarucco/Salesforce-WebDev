# Local Development

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Execute Pipeline

```bash
python automation/core/orchestrator.py
```

## Execute Tests

```bash
pytest
```

## Validate Quality

```bash
ruff check .
black --check .
mypy automation/
```
