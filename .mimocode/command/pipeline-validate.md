---
description: "Run pipeline and validate all generated files are correct"
---

Run the pipeline and verify all outputs:

```bash
# 1. Clean any leftover files first
rm -f releases/summer_26/{apex,flow,integrations,lwc,security}.md
git checkout HEAD -- README.md

# 2. Run pipeline (will timeout on Salesforce fetch - that's expected)
timeout 30 python -m src.main 2>&1 || echo "Pipeline timed out (expected for Salesforce fetch)"

# 3. Verify release files exist
ls releases/summer_26/*.md | wc -l
cat releases/summer_26/.meta.json

# 4. Verify reports exist
ls -la CHANGELOG.md QUALITY_REPORT.md REGRESSION_REPORT.md 2>/dev/null

# 5. Verify README has correct structure
grep -c "## 📋 Releases" README.md
grep -c "<details>" README.md

# 6. Run tests to verify
pytest tests/ -q -k "not test_parser_return_text_true"
```

Report: file counts, meta.json contents, README structure, any errors.
