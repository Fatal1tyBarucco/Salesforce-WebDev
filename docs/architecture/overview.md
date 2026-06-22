# Architecture Overview

## Vision

Salesforce Release Intelligence Platform built around Knowledge-as-Code principles.

## Objectives

- Automated Salesforce Release extraction
- Semantic technical classification
- GitOps-driven documentation lifecycle
- Centralized architectural knowledge
- Automated technical portal generation

## Core Components

| Component | Responsibility |
|---|---|
| GitHub Actions | Pipeline orchestration |
| Playwright Scraper | Retrieve Salesforce Release Notes (SPA rendering) |
| Feature Impact Parser | Parse feature impact tables (availability flags) |
| DOM Topic Parser | Extract topic hierarchy from navigation tree |
| Markdown Generator | Generate per-category documentation artifacts |
| Readme Updater | Auto-update README with release details |
| AI Automation | Changelog, quality metrics, regression detection |
| MkDocs | Publish technical portal |

## Architectural Principles

- Modular architecture
- Strong typing
- Retry resilience
- Stateless processing
- CI/CD first
- Documentation as product

## High-Level Flow

```text
GitHub Actions
    ↓
Release Discovery
    ↓
HTML Scraping
    ↓
Semantic Parsing
    ↓
Topic Classification
    ↓
Markdown Generation
    ↓
Knowledge Base
```
