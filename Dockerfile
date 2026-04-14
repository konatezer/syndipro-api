# ---------- Stage 1: build ----------
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first (cache layer)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Copy application code
COPY . .
RUN uv sync --frozen --no-dev

# ---------- Stage 2: runtime ----------
FROM python:3.13-slim AS runtime

WORKDIR /app

# Copy the virtual-env and app from builder
COPY --from=builder /app /app

# Expose the port
EXPOSE 8000

# Run with uvicorn via the venv
CMD ["/app/.venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
