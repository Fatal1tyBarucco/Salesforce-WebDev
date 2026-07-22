#!/usr/bin/env bash
# pre-push hook: run pytest fast
# Skips gracefully if project dependencies are not installed.
set -e

if ! python3 -c "import openai" 2>/dev/null; then
    echo "⚠️  Project dependencies not installed (run 'uv sync' first). Skipping pytest."
    exit 0
fi

echo "🧪 Running pytest (fast)..."
python3 -m pytest tests/ -x -q --tb=short --no-header
