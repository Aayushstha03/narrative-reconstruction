FROM python:3.13-slim

WORKDIR /app

# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .

RUN uv sync --locked

# wait 5seconds for db to start beofore testing connection:)
CMD ["sh", "-c", "for i in 1 2 3; do uv run src/test_postgres.py && break || (echo 'Retrying in 5s...' && sleep 5); done"]
