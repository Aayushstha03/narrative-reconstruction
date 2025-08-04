FROM python:3.13-slim

WORKDIR /app

# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .

RUN uv sync --locked

CMD ["uv", "run", "fastapi", "dev", "src/api/main.py", "--host", "0.0.0.0", "--port", "8000"]
