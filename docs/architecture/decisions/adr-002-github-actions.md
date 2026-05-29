# ADR-002 - GitHub Actions Orchestration

## Status

Accepted

## Context

The platform requires autonomous execution, scheduling, validation and repository-centric automation.

## Decision

Use GitHub Actions as the primary orchestration engine.

## Rationale

- Native GitHub integration
- Native cron scheduling
- Built-in CI/CD support
- Repository as single source of truth
- Simplified operational model

## Consequences

### Benefits

- Reduced operational overhead
- Integrated workflow visibility
- Easier governance
- Native artifact lifecycle

### Trade-Offs

- GitHub-hosted runtime dependency
- Workflow runtime limitations
- Dependency on GitHub availability
