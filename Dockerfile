FROM python:3.13-slim

WORKDIR /app

# Install PostgreSQL client and build tools
RUN apt-get update && \
    apt-get install -y libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Install uv from GHCR
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project code
COPY . .

# Install Python dependencies using uv
RUN uv sync --locked