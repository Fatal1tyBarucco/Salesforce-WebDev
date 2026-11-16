"""Helpers de comparação com golden files para a suíte de caracterização.

A suíte `tests/test_characterization_*.py` congela o comportamento ATUAL do
pipeline em arquivos versionados em `tests/golden/`. Cada teste serializa a
saída real do código (texto Markdown ou JSON canônico) e compara byte a byte
com o golden correspondente.

Regenerar goldens após mudança intencional de comportamento:

    CHAR_GOLDEN_UPDATE=1 uv run pytest tests/test_characterization_*.py

Sem a variável, o teste falha se o golden não existir ou divergir.

Este módulo não contém testes; existe apenas como helper compartilhado.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

GOLDEN_DIR: Path = Path(__file__).resolve().parent / "golden"

#: Variável de ambiente que habilita a regeneração dos goldens.
UPDATE_VAR: str = "CHAR_GOLDEN_UPDATE"

#: Instante congelado (freezegun) usado por todos os testes que leem relógio.
FROZEN_TIMESTAMP: str = "2026-06-01 09:00:00"


def golden_update_enabled() -> bool:
    """True quando a regeneração de goldens foi solicitada via ambiente."""
    return os.environ.get(UPDATE_VAR) == "1"


def assert_matches_golden(actual: str, name: str) -> None:
    """Compara `actual` com o golden `name` (caminho relativo a tests/golden/).

    Em modo update, grava `actual` como novo golden e retorna.
    """
    path = GOLDEN_DIR / name
    if golden_update_enabled():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual, encoding="utf-8")
        return
    assert path.is_file(), (
        f"Golden file ausente: {path}. "
        f"Gere com: {UPDATE_VAR}=1 uv run pytest tests/test_characterization_*.py"
    )
    expected = path.read_text(encoding="utf-8")
    assert actual == expected, _mismatch_report(name, expected, actual)


def assert_matches_golden_json(payload: Any, name: str) -> None:
    """Serializa `payload` como JSON (indentado, UTF-8) e compara com o golden."""
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    assert_matches_golden(text, name)


def _mismatch_report(name: str, expected: str, actual: str) -> str:
    """Monta um relatório apontando a primeira linha divergente."""
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    for idx, (exp, act) in enumerate(zip(expected_lines, actual_lines), start=1):
        if exp != act:
            return (
                f"Golden '{name}' divergiu na linha {idx}.\n"
                f"  esperado: {exp!r}\n"
                f"  obtido:   {act!r}\n"
                f"(esperado={len(expected_lines)} linhas, obtido={len(actual_lines)} linhas)"
            )
    return (
        f"Golden '{name}' divergiu no tamanho: "
        f"esperado={len(expected_lines)} linhas, obtido={len(actual_lines)} linhas"
    )
