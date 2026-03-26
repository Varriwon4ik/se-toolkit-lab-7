# LMS Telegram Bot Dockerfile
# Uses uv for dependency management (follows backend pattern)

# ---
# Stage 1: Build the application
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}astral/uv:python3.14-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Sync dependencies from project root
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=bot/pyproject.toml,target=bot/pyproject.toml \
    uv sync --frozen --no-install-project

# Copy bot directory
COPY bot /app/bot
COPY pyproject.toml uv.lock /app/

# Sync with the bot package
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# ---
# Stage 2: Final image
# ---

ARG REGISTRY_PREFIX=harbor.pg.innopolis.university/docker-hub-cache/
FROM ${REGISTRY_PREFIX}python:3.14.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot

# Copy the application from the builder
COPY --from=builder --chown=nonroot:nonroot /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user
USER nonroot

WORKDIR /app/bot

# Set environment variables for Docker networking
ENV LMS_API_BASE_URL=http://backend:8000
ENV LLM_API_BASE_URL=http://host.docker.internal:8080

CMD ["python", "bot.py"]
