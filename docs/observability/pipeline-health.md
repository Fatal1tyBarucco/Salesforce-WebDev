# Pipeline Health

## Monitoring Objectives

- Detect execution failures
- Validate workflow stability
- Validate artifact generation
- Track release processing health

## Health Indicators

| Indicator | Description |
|---|---|
| Workflow Success | GitHub Actions execution success |
| Artifact Generation | Markdown creation validation |
| Parser Execution | Semantic extraction validation |
| Retry Frequency | External instability indicator |

## Failure Signals

- workflow interruption
- empty markdown artifacts
- parsing failures
- excessive retries

## Recovery Actions

- rerun workflows
- validate parser strategy
- validate Salesforce endpoint
- inspect logs
