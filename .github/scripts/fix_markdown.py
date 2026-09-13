#!/usr/bin/env python3
"""Fix deterministic markdown lint errors (MD022, MD024, MD031, MD032, MD040, MD047, MD012, MD009, MD029)."""
import re
import sys
from pathlib import Path

DOCS_DIR = Path("docs")


def detect_language(block_lines):
    """Heuristically detect code block language from content."""
    if not block_lines:
        return "text"
    text = "\n".join(block_lines).strip()
    if not text:
        return "text"
    lower = text.lower()
    # HTML patterns
    if re.search(r"<\s*html|<\s*li|<\s*table|<\s*style|<\s*link|<\s*head|<\s*body", text):
        return "html"
    if re.search(r"<\s*\w+[\s>]", text) and "</" in text:
        return "html"
    # JavaScript patterns
    if re.search(r"\bfunction\b|\bconst\b|\blet\b|\bvar\b|\bimport\b|\bexport\b|=>\s*\{", text):
        return "javascript"
    # Python patterns
    if re.search(r"\bdef \w+|\bclass \w+|\bimport \w+|\bprint\(|\bif __name__|SECTION_HEADERS|RATE_LIMIT", text):
        return "python"
    # Bash patterns
    if re.search(r"\b(uv|pytest|npm|node|yarn|pip|python|bash|sh)\b", text) or "$ " in text or "&&" in text or re.search(r"^\s*[a-z_]+\s*&&", text, re.MULTILINE):
        return "bash"
    if re.search(r"^\s*[a-z_]+\s*\|\s*[a-z_]+", text, re.MULTILINE):
        return "bash"
    # JSON patterns
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return "json"
    if stripped.startswith("[") and stripped.endswith("]"):
        return "json"
    # YAML patterns (key: value)
    if re.search(r"^\w+:\s*\S", text, re.MULTILINE) and ":" in text and "-" in text:
        return "yaml"
    # Markdown tables
    if "|" in text and re.search(r"^\|[-:\s|]+\|$", text, re.MULTILINE):
        return "markdown"
    return "text"


def fix_md022_headings(lines):
    """Ensure blank line before headings if missing."""
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and stripped.startswith("#") and len(stripped) > 1 and stripped[1] == "#":
            if i > 0 and lines[i - 1].strip() != "":
                out.append("")
            out.append(line)
            continue
        out.append(line)
    return out


def fix_md024_duplicate_headings(lines):
    """Rename duplicate headings with incrementing suffix."""
    seen = {}
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped and stripped.startswith("#") and len(stripped) > 1 and stripped[1] == "#":
            match = re.match(r"^(#{2,6})\s+(.+)", line)
            if match:
                level = match.group(1)
                text = match.group(2).strip()
                if text in seen:
                    seen[text] += 1
                    out.append(f"{level} {text} {seen[text]}")
                else:
                    seen[text] = 0
                    out.append(line)
                continue
        out.append(line)
    return out


def fix_md031_fences(lines):
    """Ensure blank lines before opening fence and after closing fence."""
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("```"):
            # Check if this is opening or closing fence
            # Opening fence: line starts with ``` followed by optional language
            # Closing fence: line is just ``` (possibly with whitespace)
            # If indented, it's not a fence
            if stripped == "```" or re.match(r"```\w+$", stripped):
                # This is a fence line
                # Ensure blank before (if previous non-blank non-fence)
                if out and out[-1].strip() != "" and not out[-1].strip().startswith("```"):
                    out.append("")
                out.append(line)
                # Find matching closing fence
                j = i + 1
                fence_indent = len(line) - len(line.lstrip())
                while j < len(lines):
                    next_stripped = lines[j].strip()
                    if next_stripped == "```" or (next_stripped.startswith("```") and len(next_stripped) <= 10):
                        # Check if this is closing fence (same or less indented than opening)
                        if len(lines[j]) - len(lines[j].lstrip()) <= fence_indent + 1:
                            break
                    j += 1
                if j < len(lines):
                    # Copy content lines (i+1 to j-1)
                    for k in range(i + 1, j):
                        out.append(lines[k])
                    out.append(lines[j])  # closing fence
                    # Ensure blank after if next line is non-blank non-fence
                    if j + 1 < len(lines) and lines[j + 1].strip() != "" and not lines[j + 1].strip().startswith("```"):
                        out.append("")
                    i = j + 1
                else:
                    # No closing fence found; just copy
                    i += 1
            else:
                out.append(line)
                i += 1
        else:
            out.append(line)
            i += 1
    return out


def fix_md032_lists(lines):
    """Ensure blank line before list items if previous is non-blank non-list."""
    out = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("- ") or stripped.startswith("* ") or re.match(r"^\d+\.\s", stripped):
            if i > 0 and lines[i - 1].strip() != "" and not re.match(r"^[\s]*[-*+]|^[\s]*\d+\.", lines[i - 1].strip()):
                out.append("")
            out.append(line)
        else:
            out.append(line)
    return out


def fix_md040_fence_language(lines):
    """Add language identifier to opening fences that lack one."""
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        # Opening fence: starts with ``` followed by optional language/token
        if stripped.startswith("```"):
            indent = line[: len(line) - len(line.lstrip())]
            # Check if it has a language (```text,```python,etc.)
            m = re.match(r"^(\s*)`{3}(\w+)?(\s*)$", line)
            if m:
                lang = m.group(2) or ""
                if not lang:
                    # Find closing fence
                    j = i + 1
                    while j < len(lines) and not lines[j].strip().startswith("```"):
                        j += 1
                    if j < len(lines):
                        # Extract content lines (excluding fences)
                        content_lines = lines[i + 1 : j]
                        lang = detect_language(content_lines)
                        out.append(f"{indent}```{lang}")
                        # Copy content lines
                        for k in range(i + 1, j):
                            out.append(lines[k])
                        out.append(lines[j])  # closing fence (unchanged)
                        i = j + 1
                    else:
                        out.append(line)
                        i += 1
                else:
                    out.append(line)
                    i += 1
            else:
                out.append(line)
                i += 1
        else:
            out.append(line)
            i += 1
    return out


def fix_md047_trailing_newline(lines):
    """Ensure file ends with exactly one newline."""
    text = "\n".join(lines)
    text = text.rstrip("\n") + "\n"
    return text.split("\n")


def fix_md012_multi_blank(lines):
    """Collapse multiple consecutive blank lines into one."""
    out = []
    prev_blank = False
    for line in lines:
        if line.strip() == "":
            if not prev_blank:
                out.append("")
                prev_blank = True
        else:
            out.append(line)
            prev_blank = False
    return out


def fix_md009_trailing_spaces(lines):
    """Remove trailing spaces from each line."""
    return [line.rstrip() for line in lines]


def fix_md029_ordered_lists(lines):
    """Renumber ordered list items consecutively within each group."""
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)(\d+)\.\s", line)
        if m:
            indent = m.group(1)
            # Check if this is start of consecutive ordered list
            j = i
            while j < len(lines) and re.match(rf"^{re.escape(indent)}\d+\.\s", lines[j]):
                j += 1
            if j > i + 1:  # More than one item
                for k in range(i, j):
                    item = lines[k]
                    new_item = re.sub(rf"^{re.escape(indent)}\d+\.", f"{indent}{k - i + 1}.", item)
                    out.append(new_item)
                i = j
            else:
                out.append(line)
                i += 1
        else:
            out.append(line)
            i += 1
    return out


def fix_markdown_file(filepath):
    """Apply all fixes to a single markdown file. Returns True if any changes made."""
    original = filepath.read_text(encoding="utf-8")
    lines = original.split("\n")

    # Apply fixes in order
    lines = fix_md022_headings(lines)
    lines = fix_md024_duplicate_headings(lines)
    lines = fix_md031_fences(lines)
    lines = fix_md032_lists(lines)
    lines = fix_md040_fence_language(lines)
    lines = fix_md047_trailing_newline(lines)
    lines = fix_md012_multi_blank(lines)
    lines = fix_md009_trailing_spaces(lines)
    lines = fix_md029_ordered_lists(lines)

    fixed = "\n".join(lines)
    if fixed != original:
        filepath.write_text(fixed, encoding="utf-8")
        return True
    return False


def main():
    changed_files = []
    for md_file in DOCS_DIR.rglob("*.md"):
        try:
            if fix_markdown_file(md_file):
                changed_files.append(str(md_file))
        except Exception as e:
            print(f"Error processing {md_file}: {e}", file=sys.stderr)

    if changed_files:
        print("Fixed files:", file=sys.stderr)
        for f in changed_files:
            print(f"  {f}", file=sys.stderr)
        return 1  # Signal changes made (for CI detection)
    print("No markdown fixes needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
