# Runbook - Scraper Failure

## Detection

- Workflow failure
- Empty release artifacts
- Missing markdown generation

## Validation

### Validate Salesforce endpoint

```bash
curl -I https://help.salesforce.com
```

### Execute scraper locally

```bash
python automation/core/orchestrator.py
```

## Recovery

- Validate parser strategy
- Validate release endpoint
- Validate retries
- Rebuild documentation

## Rollback

Revert last pipeline commit if malformed artifacts were generated.
