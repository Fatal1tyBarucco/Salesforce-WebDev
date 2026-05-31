# Runbook - GitHub Actions Failure

## Symptoms

- workflow failure
- timeout execution
- dependency installation failure
- markdown generation interruption

## Validation Steps

- inspect GitHub Actions logs
- validate Python version
- validate requirements files
- validate repository permissions

## Recovery Actions

1. Re-run failed workflow
2. Validate parser execution locally
3. Validate Salesforce endpoint availability
4. Validate generated artifacts

## Rollback Strategy

- revert malformed commits
- restore previous generated artifacts
- rebuild documentation
