---
description: "Clean leftover release files and restore README from last commit"
---

Clean up leftover files that keep appearing in the working directory:

```bash
# Remove leftover release files (legacy 5-topic files from old classifier)
rm -f releases/summer_26/{apex,flow,integrations,lwc,security}.md

# Remove any other untracked release files
find releases/ -name "*.md" -not -name ".meta.json" -newer .git/HEAD 2>/dev/null | xargs rm -f

# Restore README if it was overwritten by pipeline
git checkout HEAD -- README.md

# Verify clean state
git status --short
```

Report what was cleaned and the final git status.
