#!/usr/bin/env bash
# Post-create script for Salesforce-WebDev devcontainer
# Runs once after container creation

set -euo pipefail

echo "🚀 Running post-create setup..."

# Ensure we're in the workspace
cd /workspaces/Salesforce-WebDev

# Sync dependencies with uv (uses cached layer from Dockerfile if unchanged)
echo "📦 Syncing Python dependencies..."
uv sync --frozen --extra dev --extra healing

# Install Playwright Chromium with system dependencies
echo "🌐 Installing Playwright Chromium..."
uv run playwright install chromium --with-deps

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
uv run pre-commit install
uv run pre-commit install --hook-type pre-push

# Verify key tools
echo "✅ Verifying tooling..."
uv run python --version
uv run pytest --version
uv run ruff --version
uv run mypy --version
uv run mutmut version

# Run a quick test to verify everything works
echo "🧪 Running quick smoke test..."
uv run pytest tests/ -x -q --tb=short --timeout=30 -k "not integration and not slow" --maxfail=3 || true

echo "✨ Post-create setup complete!"
echo ""
echo "Available commands:"
echo "  pytest          - Run tests (uv run pytest)"
echo "  ruff check .    - Lint code"
echo "  ruff format .   - Format code"
echo "  mypy src/       - Type check"
echo "  mutmut run      - Mutation testing"
echo ""
echo "Happy coding! 🎉"
