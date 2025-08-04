FROM python:3.12-slim

# Install uv
RUN pip install uv

# Install Postgres client libs
RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY pyproject.toml .

COPY uv.lock .

# Install all dependencies
RUN uv sync --locked

COPY . .
