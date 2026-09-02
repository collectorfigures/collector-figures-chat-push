# CFS Push base image lock

Status: source preflight only. No OCI image was built or published by this record.

| Stage | Image and tag | Exact linux/amd64 manifest digest | Platform |
|---|---|---|---|
| requirements | `ghcr.io/astral-sh/uv:python3.12-bookworm` | `sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7` | `linux/amd64` |
| builder | `ghcr.io/astral-sh/uv:python3.12-bookworm` | `sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7` | `linux/amd64` |
| runtime | `docker.io/library/python:3.12-slim-bookworm` | `sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef` | `linux/amd64` |

Registry indexes observed during the 2026-09-02 preflight were `sha256:85d4cb1afa769a7338e095b927bee941cf5ec92266c7424b3f6c0f2748567248` for the uv tag and `sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254` for the Python tag. Dockerfile execution is bound to the platform-specific manifests above, not the moving tag or index alone.
