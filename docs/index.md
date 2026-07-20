# Salesforce Release Intelligence

Automated pipeline for extracting, classifying, and version-controlling Salesforce Release Notes as structured Markdown artifacts.

## Overview

This platform uses **Playwright** to scrape the Salesforce Help portal (a JavaScript SPA), parses feature impact tables and topic hierarchies, and generates a structured knowledge base under `releases/`.

## Quick Start

```bash
# Install dependencies (uv + Python 3.14)
uv sync --extra dev

# Install Playwright browser
uv run playwright install chromium

# Run pipeline
uv run python src/main.py

# Run tests
uv run pytest
```

## Refatoração

A iniciativa contínua de refatoração do código Python (regras de tolerância zero, auditoria de integrações) está documentada em [Refatoração — Status & Auditoria](refatoracao.md).

## Documentation

Navigate the sidebar to explore architecture decisions, maintenance guides, runbooks, and the project roadmap.
