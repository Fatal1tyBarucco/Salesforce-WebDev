---
description: "Update Trailhead links in all release files for a given release"
---

Update Trailhead resources in release files:

```python
from src.salesforce import generate_release_resources_section
from pathlib import Path

release_slug = "summer_26"  # Change as needed
release_name = "Summer '26"  # Change as needed
release_dir = Path(f"releases/{release_slug}")

for f in sorted(release_dir.glob("*.md")):
    if f.name.startswith("."):
        continue
    content = f.read_text(encoding="utf-8")
    # Remove old Trailhead section if present
    if "🔗 Trailhead" in content:
        lines = content.split("\n")
        new_lines = []
        skip = False
        for line in lines:
            if "🔗 Trailhead" in line:
                skip = True
                continue
            if skip and line.startswith("## "):
                skip = False
            if not skip:
                new_lines.append(line)
        content = "\n".join(new_lines)
    # Add new section
    section = generate_release_resources_section(release_slug, release_name)
    f.write_text(section + content, encoding="utf-8")
    print(f"  ✓ {f.name}")
```

Then commit and push:
```bash
git add releases/{slug}/*.md && git commit -m "chore: update Trailhead links for {release}" && git push
```
