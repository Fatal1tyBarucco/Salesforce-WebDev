"""Salesforce Feature Evolution Ledger (SFEL) — feature-level cross-release linkage.

Rastreia a vida de features individuais através de múltiplos ciclos de release
da Salesforce, produzindo um ledger estruturado de nascimentos, renomeações,
mudanças de categoria e remoções entre releases consecutivas.
"""

from __future__ import annotations

from . import linker, models, prompts, service

__all__ = ["linker", "models", "prompts", "service"]
