# Workflow Operations

## Execute Pipeline Locally

```bash
python -m src.main
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
mypy src/
```

## Build Documentation

```bash
mkdocs build
```

## Operational Recommendations

- Always validate quality gates locally before push
- Validate generated markdown artifacts
- Review GitHub Actions logs after execution
