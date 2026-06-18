---
description: "Trigger the release notes CI workflow and monitor until completion"
---

Trigger the release notes pipeline and watch until it completes:

```bash
gh workflow run "🚀 Salesforce Release Notes Pipeline" 2>&1
```

Then extract the run ID from the output URL and monitor:

```bash
gh run watch <RUN_ID> --exit-status 2>&1
```

Report the final status (success/failure) and any errors.
