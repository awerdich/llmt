FROM python:3.12 AS base

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_SRC=/src \
    NO_COLOR=true \
    UV_COMPILE_BYTECODE=1 \
    UV_SYSTEM_PYTHON=true \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON_PREFERENCE=only-system \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local
    
# Ports for jupyter and tensorboard
EXPOSE 8888

RUN mkdir -p /app
WORKDIR /app

# Copy the project files to create the environment
COPY README.md .
COPY src/llmt/__init__.py src/llmt/__init__.py

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=.git,target=.git \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
     uv sync --frozen

# Copy bash scripts and set executable flags
RUN mkdir -p /run_scripts
COPY /bash_scripts/* /run_scripts
RUN chmod +x /run_scripts/*

# Run the jupyter server
CMD ["/bin/bash", "/run_scripts/docker_entry"]