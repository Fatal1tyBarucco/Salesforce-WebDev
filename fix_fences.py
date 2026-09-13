#!/usr/bin/env python3
"""Fix fences in SOURCE_SCHEMA.md."""
import re

with open('docs/SOURCE_SCHEMA.md') as f:
    content = f.read()

# Replace broken fences with consistent ```bash blocks
content = content.replace(
    '```bash\n\n---\n\n## 8. Validation\n\n### 8.1 Snapshot Tests\n\nThe pipeline includes snapshot tests in `tests/test_snapshot.py` that capture expected parser output. When the DOM changes, these tests will fail and require snapshot regeneration:\n\n```bash\n\nuv run pytest tests/test_snapshot.py           # Run snapshots\nuv run pytest tests/test_snapshot.py --snapshot-update  # Update after intentional changes\n\n```text',
    '```bash\nuv run pytest tests/test_snapshot.py -v\nuv run pytest tests/test_snapshot.py --snapshot-update\n```\n\n## 8. Validation\n\n### 8.1 Snapshot Tests\n\nThe pipeline includes snapshot tests in `tests/test_snapshot.py` that capture expected parser output. When the DOM changes, these tests will fail and require snapshot regeneration:'
)

content = content.replace(
    '```python\n\n# Configuração defensiva — nunca remova sem aprovação\nRATE_LIMIT_RPS = 2\nRATE_LIMIT_MIN_INTERVAL = 1.0 / RATE_LIMIT_RPS  # 0.5 segundos\n\n```bash\n\nSe a taxa de scraping precisar ser ajustada, altere apenas `RATE_LIMIT_MIN_INTERVAL` via `RateLimiter(min_interval=...)`; nunca desative o limitador em produção.',
    '```python\n# Configuração defensiva — nunca remova sem aprovação\nRATE_LIMIT_RPS = 2\nRATE_LIMIT_MIN_INTERVAL = 1.0 / RATE_LIMIT_RPS  # 0.5 segundos\n```\n\nSe a taxa de scraping precisar ser ajustada, altere apenas `RATE_LIMIT_MIN_INTERVAL` via `RateLimiter(min_interval=...)`; nunca desative o limitador em produção.'
)

with open('docs/SOURCE_SCHEMA.md', 'w') as f:
    f.write(content)

print('Fixed fences.')
