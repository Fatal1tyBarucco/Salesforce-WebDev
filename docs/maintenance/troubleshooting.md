# Troubleshooting

## Scraper Failure

### Symptoms

- HTTP timeout
- empty payload
- Salesforce response changes

### Actions

- validate Salesforce endpoint
- inspect HTML structure
- rerun GitHub workflow
- validate retry logs

---

## Parser Failure

### Symptoms

- missing markdown content
- malformed sections

### Actions

- inspect semantic parser
- validate HTML strategy
- review topic extraction

---

## Workflow Failure

### Actions

- inspect GitHub Actions logs
- validate dependencies
- validate Python version
- rerun workflow
