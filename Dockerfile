# Container image for the Salesforce Release Notes pipeline.
FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

# Install uv (the project's package manager) from the official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv
ENV PATH="/uv:$PATH"

WORKDIR /app

# Install dependencies first for better layer caching.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra dev || uv sync --extra dev

# Install Playwright browser binaries required for headless scraping.
RUN uv run playwright install --with-deps chromium

# Copy application source.
COPY . .

# Default entrypoint: run the release-notes extraction pipeline.
CMD ["uv", "run", "python", "src/main.py"]
