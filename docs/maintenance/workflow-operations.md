# Workflow Operations

## Execute Pipeline Locally

```bash
python automation/core/orchestrator.py
```

## Execute Tests

```bash
pytest
```

## Execute Lint Validation

```bash
ruff check .
```

## Execute Formatting Validation

```bash
black --check .
```

## Execute Type Validation

```bash
mypy automation/
```

## Build Documentation

```bash
mkdocs build
```

## Operational Recommendations

- Always validate quality gates locally before push
- Validate generated markdown artifacts
- Review GitHub Actions logs after execution
