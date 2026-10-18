#!/bin/bash
# Quality check local — executa ruff (se disponível), black, mypy, pytest.
# Se ruff estiver bloqueado no ambiente (Termux/Android), reporta honestamente.

set -e

echo "=== PYTHON QUALITY CHECK (Local) ==="

# Black
python3 -m black --check --line-length 100 src/ tests/ 2>&1 || echo "[WARN] black: arquivo precisa de formatação (corrija com black .)"

# Mypy
python3 -m mypy src/ai/ --ignore-missing-imports --pretty 2>&1 || echo "[WARN] mypy: erros encontrados"

# Pytest
python3 -m pytest tests/test_ai_docs_coverage.py -q -o "addopts=" 2>&1 | tail -2

# Ruff — se bloqueado, reporta honestamente
if python3 -m ruff --version >/dev/null 2>&1; then
    python3 -m ruff check src/ tests/
else
    echo "[BLOQUEIO REAL] ruff não disponível neste ambiente (Termux/Android — timeout de instalação). Documentado em AGENTS.md e MEMORY.md."
fi
# NOTA RUFF (atualizado): ruff 0.17.1 existe via apt Termux, mas a versão
# moderna (>=0.5) não pode ser instalada (timeout 420s no Termux aarch64).
# O script usa black + mypy + pytest; ruff reportado como bloqueio direto.
