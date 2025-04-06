# Use a Python image with uv pre-installed
# FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
# Use Python image
FROM python:3.12 AS base

COPY --from=ghcr.io/astral-sh/uv:0.6.12 /uv /uvx /bin/

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_SRC=/src \
    NO_COLOR=true
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Ports for jupyter and tensorboard
EXPOSE 8888
EXPOSE 6006

RUN mkdir -p /app
WORKDIR /app

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Copy bash scripts and set executable flags
RUN mkdir -p /run_scripts
COPY /bash_scripts/* /run_scripts
RUN chmod +x /run_scripts/*

# Run the jupyter server
CMD ["/bin/bash", "/run_scripts/docker_entry"]