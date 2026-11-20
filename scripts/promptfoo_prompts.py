"""promptfoo prompt loaders (ADR-012, requisito 4.2).

Thin wrappers exposing the production prompt builders to promptfoo's
``file://`` python loader.  Imports are lazy (inside each function) with a
sys.path bootstrap, because the production modules use relative imports and
pydantic — run eval with ``PROMPTFOO_PYTHON=.venv/bin/python``.

Usage:
    PROMPTFOO_PYTHON=.venv/bin/python npx --yes promptfoo eval \
        -c .promptfoo.yaml --filter-providers deterministic-echo
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _bootstrap() -> None:
    for path in (str(ROOT), str(ROOT / ".github" / "scripts")):
        if path not in sys.path:
            sys.path.insert(0, path)


def prompt_classification(context: dict | None = None) -> str:
    """System prompt de classificação de features."""
    _bootstrap()
    from src.ai.prompts.classification import build_classification_system_prompt

    return build_classification_system_prompt()


def prompt_enrichment(context: dict | None = None) -> str:
    """System prompt de enriquecimento de features."""
    _bootstrap()
    from src.ai.prompts.enrichment import build_enrichment_system_prompt

    return build_enrichment_system_prompt()


def prompt_reporting(context: dict | None = None) -> str:
    """System prompt de relatórios."""
    _bootstrap()
    from src.ai.prompts.reporting import build_reporting_system_prompt

    return build_reporting_system_prompt()


def prompt_reconciliation(context: dict | None = None) -> str:
    """System prompt de reconciliação de documentação (braço LLM do sync)."""
    _bootstrap()
    from documentation_reconcile import build_reconciliation_system_prompt

    return build_reconciliation_system_prompt()
