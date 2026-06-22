---
description: "Check and fix GitHub AI code scanning findings"
---

Check GitHub AI findings and fix all open issues:

```bash
# List open code scanning alerts
gh api repos/Fatal1tyBarucco/Salesforce-WebDev/code-scanning/alerts --jq '.[] | select(.state == "open") | {number: .number, rule: .rule.description, path: .most_recent_instance.location.path, severity: .rule.severity}'

# List open Dependabot alerts
gh api repos/Fatal1tyBarucco/Salesforce-WebDev/dependabot/alerts --jq '.[] | select(.state == "open") | {number: .number, package: .security_vulnerability.package.name, severity: .security_advisory.severity}'
```

For each finding:
1. Read the file and understand the issue
2. Apply the minimal fix
3. Run quality gate: `black --check . && ruff check . && mypy automation/ src/ && pytest automation/tests/ -q`
4. Commit with descriptive message
5. Push to origin

Report findings fixed and any that couldn't be auto-fixed.
