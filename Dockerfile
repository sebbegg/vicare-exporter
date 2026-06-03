# An example using multi-stage image builds to create a final image without uv.

# First, build the application in the `/app` directory.
# See `Dockerfile` for details.
FROM ghcr.io/astral-sh/uv:python3.14-alpine3.23 AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads, because we want to use the system interpreter
# across both images. If using a managed Python version, it needs to be
# copied from the build image into the final image; see `standalone.Dockerfile`
# for an example.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project
COPY vicare_exporter /app/vicare_exporter
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked


# Then, use a final image without uv
FROM python:3.14-alpine3.23
# It is important to use the image that matches the builder, as the path to the
# Python executable must be the same, e.g., using `python:3.11-slim-bookworm`
# will fail.

# Setup a non-root user
RUN addgroup -S -g 101 python \
 && adduser -S -g python -u 101 -D python

# Copy the application from the builder
COPY --from=builder --chown=python:python /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the non-root user to run our application
USER python

# Use `/app` as the working directory
WORKDIR /app

ENTRYPOINT ["vicare-exporter"]
