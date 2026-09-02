# Dockerfile to build the matrixdotorg/sygnal docker images.
#
# To build the image, run `docker build` command from the root of the
# sygnal repository:
#
#    docker build -f docker/Dockerfile .
#

ARG POETRY_VERSION=1.8.3

###
### Stage 0: generate requirements.txt
###
### The CFS release candidate is intentionally restricted to linux/amd64.
###
# linux/amd64 manifest lock for ghcr.io/astral-sh/uv:python3.12-bookworm
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm@sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7 AS requirements

WORKDIR /sygnal

# Copy just what we need to run `poetry export`...
COPY pyproject.toml poetry.lock /sygnal/

# If specified, we won't verify the hashes of dependencies.
# This is only needed if the hashes of dependencies cannot be checked for some
# reason, such as when a git repository is used directly as a dependency.
ARG TEST_ONLY_SKIP_DEP_HASH_VERIFICATION

# If specified, we won't use the Poetry lockfile.
# Instead, we'll just install what a regular `pip install` would from PyPI.
ARG TEST_ONLY_IGNORE_POETRY_LOCKFILE

# This silences a warning as uv isn't able to do hardlinks between its cache
# (mounted as --mount=type=cache) and the target directory.
ENV UV_LINK_MODE=copy

# Export the dependencies, but only if we're actually going to use the Poetry lockfile.
# Otherwise, just create an empty requirements file so that the Dockerfile can
# proceed.
ARG POETRY_VERSION
RUN --mount=type=cache,target=/root/.cache/uv \
  if [ -z "$TEST_ONLY_IGNORE_POETRY_LOCKFILE" ]; then \
    uvx --with poetry-plugin-export==1.8.0 \
        poetry@${POETRY_VERSION} export -o /sygnal/requirements.txt ${TEST_ONLY_SKIP_DEP_HASH_VERIFICATION:+--without-hashes}; \
  else \
    touch /sygnal/requirements.txt; \
  fi

###
### Stage 1: builder
###
# linux/amd64 manifest lock for ghcr.io/astral-sh/uv:python3.12-bookworm
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm@sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7 AS builder

# This silences a warning as uv isn't able to do hardlinks between its cache
# (mounted as --mount=type=cache) and the target directory.
ENV UV_LINK_MODE=copy

# To speed up rebuilds, install all of the dependencies before we copy over
# the whole sygnal project, so that this layer in the Docker cache can be
# used while you develop on the source.
#
# This is aiming at installing the `[tool.poetry.depdendencies]` from pyproject.toml.
COPY --from=requirements /sygnal/requirements.txt /sygnal/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv pip install --prefix="/install" --no-deps -r /sygnal/requirements.txt

# Copy over the rest of the sygnal source code.
COPY sygnal /sygnal/sygnal/
# ... and what we need to `pip install`.
COPY pyproject.toml README.md /sygnal/

# Repeat of earlier build argument declaration, as this is a new build stage.
ARG TEST_ONLY_IGNORE_POETRY_LOCKFILE

# Install the sygnal package itself.
# If we have populated requirements.txt, we don't install any dependencies
# as we should already have those from the previous `pip install` step.
RUN \
  --mount=type=cache,target=/root/.cache/uv \
  --mount=type=cache,target=/sygnal/target,sharing=locked \
  --mount=type=cache,target=${CARGO_HOME}/registry,sharing=locked \
  if [ -z "$TEST_ONLY_IGNORE_POETRY_LOCKFILE" ]; then \
    uv pip install --prefix="/install" --no-deps /sygnal; \
  else \
    uv pip install --prefix="/install" /sygnal; \
  fi

###
### Stage 2: runtime
###

# linux/amd64 manifest lock for docker.io/library/python:3.12-slim-bookworm
FROM --platform=linux/amd64 docker.io/library/python:3.12-slim-bookworm@sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef

ARG CFS_SOURCE_COMMIT=unknown
LABEL org.opencontainers.image.title="Collector Figures Chat Push Gateway" \
      org.opencontainers.image.source="https://github.com/collectorfigures/collector-figures-chat-push" \
      org.opencontainers.image.licenses="AGPL-3.0-only" \
      org.opencontainers.image.revision="${CFS_SOURCE_COMMIT}"

COPY --from=builder /install /usr/local

RUN groupadd --gid 991 sygnal \
  && useradd --uid 991 --gid 991 --home-dir /nonexistent --shell /usr/sbin/nologin sygnal \
  && install -d -o 991 -g 991 -m 0750 /data

WORKDIR /data
USER 991:991

EXPOSE 5000/tcp

ENTRYPOINT ["python", "-m", "sygnal.sygnal"]

HEALTHCHECK --start-period=25s --interval=15s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=4).read()" || exit 1
