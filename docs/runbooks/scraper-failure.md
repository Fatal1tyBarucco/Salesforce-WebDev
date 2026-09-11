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
uv run python src/main.py
# ou, para execução em modo dry-run:
uv run python src/main.py --dry-run
```

### Validar ambiente Playwright

```bash
uv run playwright install chromium
uv run python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Recovery

- Validate parser strategy
- Validate release endpoint
- Validate retries
- Rebuild documentation

## Rollback

Revert last pipeline commit if malformed artifacts were generated.
