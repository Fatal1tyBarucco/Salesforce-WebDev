#!/usr/bin/env bash
# Post-start script for Salesforce-WebDev devcontainer
# Runs every time the container starts

set -euo pipefail

cd /workspaces/Salesforce-WebDev

# Quick sync in case pyproject.toml/uv.lock changed
if [ -f "pyproject.toml" ] && [ -f "uv.lock" ]; then
    uv sync --frozen --extra dev --extra healing --quiet 2>/dev/null || true
fi

# Show git status
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "📍 Git status:"
    git status --short
    echo ""
fi

# Show current branch
BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
echo "🌿 Current branch: $BRANCH"

# Show Python environment
echo "🐍 Python: $(uv run python --version 2>/dev/null)"
echo "📦 Virtual env: $UV_PROJECT_ENVIRONMENT"
echo ""