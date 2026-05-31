# ADR-003 - Topic Classification Strategy

## Status

Accepted

## Context

Salesforce Release Notes contain heterogeneous technical domains.

## Decision

Use modular topic classification with extensible keyword mapping.

## Initial Domains

- Apex
- LWC
- Flow
- Security
- Integrations

## Architectural Goals

- Extensibility
- Low coupling
- Simple onboarding of new domains
- Independent topic evolution

## Future Evolution

- Weighted scoring
- Semantic classification
- NLP-assisted grouping
- Confidence ranking
