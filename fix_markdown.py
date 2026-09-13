#!/usr/bin/env python3
"""Fix markdown lint errors in SOURCE_SCHEMA.md."""
import re

with open('docs/SOURCE_SCHEMA.md') as f:
    content = f.read()

# Fix MD040: bare fences ``` (line 99, 208, 220, 232) → ```text
# Match lines that are exactly ``` (with optional whitespace) followed by newline,
# but NOT followed by a language identifier.
# Pattern: line starts with optional whitespace, then ```, then newline, and next non-empty line is not a language
lines = content.split('\n')
new_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.strip()
    # Check if this is a bare fence (``` alone, no language)
    if stripped == '```' or stripped.startswith('``` ') or re.match(r'^\s*```\w+', stripped):
        # If it's just ``` with no language
        if stripped == '```' or (stripped.startswith('```') and len(stripped) == 3):
            # This is a bare fence; needs language
            # Look ahead to determine language based on content
            # Find closing fence
            j = i + 1
            while j < len(lines) and lines[j].strip() != '```':
                j += 1
            if j < len(lines):
                # Determine language from content between i+1 and j-1
                block_content = '\n'.join(lines[i+1:j])
                lang = 'text'  # default
                if '<' in block_content and '>' in block_content and '</' in block_content:
                    if '<html' in block_content.lower():
                        lang = 'html'
                    elif '<li' in block_content or '<ul' in block_content or '<table' in block_content:
                        lang = 'html'
                    elif '<style' in block_content or '<link' in block_content:
                        lang = 'html'
                elif 'function' in block_content or 'const' in block_content or 'let' in block_content or 'var ' in block_content or '=>' in block_content:
                    lang = 'javascript'
                elif 'import' in block_content or 'def ' in block_content or 'class ' in block_content or 'SECTION_HEADERS' in block_content:
                    lang = 'python'
                elif 'uv run' in block_content or 'pytest' in block_content or '$' in block_content:
                    lang = 'bash'
                elif '{' in block_content and '}' in block_content and ':' in block_content and not 'function' in block_content:
                    lang = 'json'
                elif '|' in block_content and '---' in block_content:
                    lang = 'markdown'
                # Replace opening fence with language
                indent = line[:len(line) - len(line.lstrip())]
                new_lines.append(f'{indent}```{lang}')
                i += 1
                continue
    new_lines.append(line)
    i += 1

content = '\n'.join(new_lines)

# Fix MD012: multiple consecutive blank lines → single blank
lines = content.split('\n')
new_lines = []
prev_blank = False
for line in lines:
    if line.strip() == '':
        if not prev_blank:
            new_lines.append('')
            prev_blank = True
    else:
        new_lines.append(line)
        prev_blank = False
content = '\n'.join(new_lines)

# Fix MD009: trailing spaces at end of lines
lines = [line.rstrip() for line in content.split('\n')]
content = '\n'.join(lines)

# Fix MD029: renumber ordered list items consecutively
lines = content.split('\n')
output = []
i = 0
while i < len(lines):
    line = lines[i]
    m = re.match(r'^(\s*)([0-9]+)\.\s', line)
    if m:
        # Check if next line is also an ordered list item with same indent
        indent = m.group(1)
        if i + 1 < len(lines):
            next_m = re.match(rf'^{re.escape(indent)}[0-9]+\.\s', lines[i+1])
            if next_m:
                # Start of a consecutive ordered list
                items = []
                j = i
                while j < len(lines) and re.match(rf'^{re.escape(indent)}[0-9]+\.\s', lines[j]):
                    items.append(lines[j])
                    j += 1
                # Renumber
                for k, item in enumerate(items, 1):
                    new_item = re.sub(rf'^{re.escape(indent)}[0-9]+\.', f'{indent}{k}.', item)
                    output.append(new_item)
                i = j
                continue
    output.append(line)
    i += 1

content = '\n'.join(output)

# Fix MD031: ensure blank lines before and after fence blocks
lines = content.split('\n')
output = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('```'):
        # Ensure blank before (if previous line is non-blank, non-fence)
        if output and output[-1].strip() != '' and not output[-1].strip().startswith('```'):
            output.append('')
        output.append(line)
        # Look ahead for closing fence
        if i + 1 < len(lines):
            # Find closing fence
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('```'):
                j += 1
            if j < len(lines):
                # Ensure blank after closing fence
                if j + 1 < len(lines) and lines[j+1].strip() != '' and not lines[j+1].strip().startswith('```'):
                    # We'll handle this when we process the closing fence
                    pass
            else:
                # Fence block continues to end of file
                pass
        continue
    output.append(line)

# Second pass: ensure blank after closing fences
output2 = []
for i, line in enumerate(output):
    output2.append(line)
    stripped = line.strip()
    if stripped.startswith('```'):
        # This is a closing fence (previous line is content or opening fence)
        # Check if next line is content (non-blank, non-fence)
        if i + 1 < len(output):
            next_line = output[i+1]
            if next_line.strip() != '' and not next_line.strip().startswith('```'):
                output2.append('')  # Add blank after closing fence
        continue

content = '\n'.join(output2)

with open('docs/SOURCE_SCHEMA.md', 'w') as f:
    f.write(content)

print('Fix applied.')
