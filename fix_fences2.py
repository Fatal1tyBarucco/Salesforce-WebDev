#!/usr/bin/env python3
"""Fix fence issues: convert erroneous second fences to closing fences, remove empty blocks."""

import re

def detect_language(content_lines):
    """Heuristically detect code block language."""
    if not content_lines:
        return "text"
    text = "\n".join(content_lines).strip()
    if not text:
        return "text"
    lower = text.lower()
    if re.search(r"<\s*html|<\s*li|<\s*table|<\s*style|<\s*link|<\s*head|<\s*body|</\w+>", text):
        return "html"
    if re.search(r"\bfunction\b|\bconst\b|\blet\b|\bvar\b|\bimport\b|\bexport\b|=>\s*\{", text):
        return "javascript"
    if re.search(r"\bdef \w+|\bclass \w+|\bimport \w+|\bprint\(|\bif __name__|SECTION_HEADERS|RATE_LIMIT", text):
        return "python"
    if re.search(r"\b(uv|pytest|npm|node|yarn|pip|python|bash|sh)\b", text) or "$ " in text or re.search(r"^\s*[a-z_]+\s*&&", text, re.MULTILINE):
        return "bash"
    if re.search(r"^\w+:\s*\S", text, re.MULTILINE) and ":" in text:
        return "yaml"
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return "json"
    if "|" in text and re.search(r"^\|[-:\s|]+\|$", text, re.MULTILINE):
        return "markdown"
    return "text"

with open('docs/SOURCE_SCHEMA.md') as f:
    lines = f.read().split('\n')

output = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    
    if stripped.startswith('```'):
        # Find next fence
        next_fence_idx = None
        for j in range(i + 1, len(lines)):
            if lines[j].strip().startswith('```'):
                next_fence_idx = j
                break
        
        if next_fence_idx is None:
            # No closing fence found; keep as-is
            output.append(line)
            i += 1
            continue
        
        # Get content between fences
        content_lines = lines[i + 1 : next_fence_idx]
        content = '\n'.join(content_lines).strip()
        
        if content == '':
            # Empty code block - remove both fences
            print(f"Removing empty block: lines {i + 1}-{next_fence_idx + 1}")
            i = next_fence_idx + 1
            continue
        
        # Opening fence
        indent = line[: len(line) - len(line.lstrip())]
        has_lang = bool(re.match(r'```\w+', stripped))
        
        if has_lang:
            output.append(line)
        else:
            lang = detect_language(content_lines)
            output.append(f'{indent}```{lang}')
        
        # Content lines
        for cl in content_lines:
            output.append(cl)
        
        # Closing fence - just ```
        closing_indent = lines[next_fence_idx][: len(lines[next_fence_idx]) - len(lines[next_fence_idx].lstrip())]
        output.append(f'{closing_indent}```')
        
        i = next_fence_idx + 1
    else:
        output.append(line)
        i += 1

with open('docs/SOURCE_SCHEMA.md', 'w') as f:
    f.write('\n'.join(output))

print(f"Fixed. Lines: {len(lines)} → {len(output)}")
