# CFS Push base image lock

Local candidate 02, 2026-09-07. These are base platform manifests, not published CFS image identities.

| Stage | Image and tag | Exact linux/amd64 manifest digest | Platform |
|---|---|---|---|
| requirements | `ghcr.io/astral-sh/uv:python3.12-alpine` | `sha256:35da51582abbc137cc0860033b2b65fb86c22e0d4c7cb2715758cbd8cd29f08f` | `linux/amd64` |
| builder | `ghcr.io/astral-sh/uv:python3.12-alpine` | `sha256:35da51582abbc137cc0860033b2b65fb86c22e0d4c7cb2715758cbd8cd29f08f` | `linux/amd64` |
| runtime | `docker.io/library/python:3.12-alpine3.23` | `sha256:f0b72408d0c2ee5cf1df64adce9b92ab4f2d3c8cfbb879ac5ab1d0ec07208555` | `linux/amd64` |

The pinned uv image read-back is Python 3.12.14, uv 0.12.10 and Alpine 3.23.5. Runtime uses the same Python/musl distribution. No cross-distribution packages are copied. Native compilation stays in the builder; build-base 0.5-r3 and libffi-dev 3.5.2-r0 are exact Alpine 3.23 pins. Runtime libuuid 2.41.6-r1 applies available util-linux security fixes without removing the package.

The Python tag index observed on 2026-09-07 was `sha256:167bc85084c9df34480efc26b4528fb68feaa8a79183b5658952137025b6f061`; execution is bound to the platform manifest above, not the moving tag or index alone. Resulting CFS source/config/manifest/scan/SBOM bindings are separate LOCAL_NONPUBLISHED evidence. Adoption requires runtime, TLS, upstream and security validation; no VEX or scanner exemption is granted by this document.
