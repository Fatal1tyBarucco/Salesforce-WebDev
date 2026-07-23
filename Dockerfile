# ── Stage 1: Builder ─────────────────────────────────────────────
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv
ENV PATH="/uv:$PATH"

WORKDIR /app

# Install dependencies (cached layer — only rebuilds when lock changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --extra dev || uv sync --extra dev

# Install Playwright browser binaries
RUN uv run playwright install --with-deps chromium

# ── Stage 2: Runtime ────────────────────────────────────────────
FROM python:3.13-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv
ENV PATH="/uv:$PATH"

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /app/.venv .venv
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application source
COPY src/ src/
COPY releases/ releases/
COPY pyproject.toml ./

# Health check — verifies the Python process is alive
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD ["python", "-c", "import sys; sys.exit(0)"]

# Default entrypoint: run the release-notes extraction pipeline
CMD ["uv", "run", "python", "src/main.py"]
