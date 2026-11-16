#!/usr/bin/env python3
"""Generate PR body for scheduled pipeline."""

import os
import subprocess


def main():
    release_slug = os.environ.get("RELEASE_SLUG", "")
    release_name = os.environ.get("RELEASE_NAME", "")

    # Get git diff stat
    diff_stat = subprocess.run(
        ["git", "diff", "--stat", "releases/"], capture_output=True, text=True
    ).stdout

    # Get new files
    new_files = subprocess.run(
        ["git", "status", "--short", "releases/"], capture_output=True, text=True
    ).stdout
    new_list = "\n".join(
        [f"- {line[4:]}" for line in new_files.splitlines() if line.startswith("??")]
    )
    mod_list = "\n".join(
        [f"- {line[4:]}" for line in new_files.splitlines() if line.startswith(" M")]
    )

    # Get date
    date_utc = subprocess.run(
        ["date", "-u", "+%Y-%m-%d %H:%M UTC"], capture_output=True, text=True
    ).stdout.strip()

    body = f"""## Release Notes Pipeline — `{release_slug}`

**Release:** {release_name}
**Trigger:** scheduled
**Date:** {date_utc}

### Changes Detected
```
{diff_stat}
```

### New Files
{new_list or "(none)"}

### Modified Files
{mod_list or "(none)"}

### Validation Checklist
- [ ] `.meta.json` valid
- [ ] `.summary_cache.json` valid
- [ ] `.md` files for pt_BR and en_US
- [ ] README.md + README.en.md updated
- [ ] AI reports coherent
- [ ] Gates passing
- [ ] Docs reconcile done
"""

    with open("/tmp/pr_body.md", "w") as f:
        f.write(body)

    print("pr_body_file=/tmp/pr_body.md")


if __name__ == "__main__":
    main()
