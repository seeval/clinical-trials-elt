FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency configuration and source code
COPY pyproject.toml uv.lock ./
COPY . .

# Install dependencies system-wide using pyproject.toml directly
RUN uv pip install --system -r pyproject.toml

EXPOSE 3000
