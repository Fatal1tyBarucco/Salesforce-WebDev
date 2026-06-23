---
description: "Verify release files exist with correct structure and Trailhead links"
---

Verify release files are correctly generated:

```bash
# 1. Check release directory exists
ls releases/summer_26/*.md | wc -l

# 2. Verify .meta.json exists and has categories
cat releases/summer_26/.meta.json | python -c "import sys,json; d=json.load(sys.stdin); print(f'Categories: {len(d[\"categories\"])}, Features: {d[\"total_features\"]}')"

# 3. Verify Trailhead section in first file
head -10 releases/summer_26/agentforce.md

# 4. Count files with Trailhead links
grep -l "Trailhead" releases/summer_26/*.md | wc -l

# 5. Verify README has release details blocks
grep -c "<details>" README.md
```

Report: file count, meta.json contents, Trailhead presence, README structure.
