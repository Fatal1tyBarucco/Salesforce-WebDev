"""GitHub Issue creation."""

from __future__ import annotations

import asyncio
import subprocess
from typing import Any, Optional, cast


async def create_github_issue(
    release_name: str, total_features: int, categories: int
) -> Optional[str]:
    """Create a GitHub Issue for a new release detection."""
    body = f"""## Nova Release Detectada: {release_name}

### Resumo
- **Total de recursos:** {total_features}
- **Categorias:** {categories}

### Detalhes
A automação detectou uma nova release do Salesforce e processou os dados automaticamente.

### Arquivos Gerados
- `releases/{release_name.lower().replace(' ', '_').replace("'", "")}/` — Diretório da release
- `CHANGELOG.md` — Changelog atualizado
- `QUALITY_REPORT.md` — Relatório de qualidade

---
*Gerado automaticamente pelo pipeline de Release Notes Intelligence*
"""

    def run_gh() -> Any:
        return subprocess.run(
            [
                "gh",
                "issue",
                "create",
                "--title",
                f"Release: {release_name}",
                "--body",
                body,
                "--label",
                "release",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

    try:
        result = await asyncio.to_thread(run_gh)
        if result.returncode == 0:
            return cast(str, result.stdout.strip())
    except Exception:
        pass
    return None
