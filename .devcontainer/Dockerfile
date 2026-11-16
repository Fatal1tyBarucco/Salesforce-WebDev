# DevContainer for Salesforce-WebDev
# Python 3.14, uv, Playwright, MCP, structlog

FROM mcr.microsoft.com/devcontainers/python:1.4.0-3.14-bookworm

# Install system dependencies for Playwright and building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    gnupg \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatspi2.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /usr/local/bin/uv

# Set up non-root user (vscode user already exists in base image)
USER vscode

# Set working directory
WORKDIR /workspaces/Salesforce-WebDev

# Configure uv to use the project's virtual environment
ENV UV_PROJECT_ENVIRONMENT=/workspaces/Salesforce-WebDev/.venv
ENV UV_SYNC_ARGS="--extra dev --extra healing"

# Pre-install Python dependencies (will be overridden by postCreateCommand)
# This layer caches dependencies for faster rebuilds
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra dev --extra healing 2>/dev/null || true

# Install Playwright Chromium (will be run again in postCreateCommand for updates)
RUN uv run playwright install chromium --with-deps 2>/dev/null || true

# Set up shell aliases and environment
RUN echo 'alias pytest="uv run pytest"' >> ~/.bashrc \
    && echo 'alias ruff="uv run ruff"' >> ~/.bashrc \
    && echo 'alias mypy="uv run mypy"' >> ~/.bashrc \
    && echo 'alias mutmut="uv run mutmut"' >> ~/.bashrc \
    && echo 'export PYTHONPATH=/workspaces/Salesforce-WebDev' >> ~/.bashrc

# Default command
CMD ["sleep", "infinity"]