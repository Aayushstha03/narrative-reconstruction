# --- Stage 1: Build ---
FROM python:3.13-slim AS build

WORKDIR /app

# Install build tools for dependencies
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install uv from GHCR
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project code
COPY . .

# Install Python dependencies
RUN uv sync --locked

# --- Stage 2: Runtime ---
FROM python:3.13-slim

# Copy uv binaries from GHCR
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy installed Python packages from build stage
COPY --from=build /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=build /usr/local/bin /usr/local/bin

# Copy project code
COPY --from=build /app /app

# Set Python path
ENV PYTHONPATH=/app
