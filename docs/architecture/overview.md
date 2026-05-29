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
| Release Scraper | Retrieve Salesforce Release Notes |
| Semantic Parser | Extract technical sections |
| Topic Classifier | Categorize architectural topics |
| Markdown Generator | Generate documentation artifacts |
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
