# ADR-001 - Parser Strategy Pattern

## Status

Accepted

## Context

Salesforce Release Notes may evolve across HTML and PDF formats.

## Decision

Use Strategy Pattern for parsing abstraction.

## Consequences

### Benefits

- Extensible parser architecture
- Isolated parsing logic
- Easier testing
- Future format support

### Trade-Offs

- Slightly increased abstraction complexity
