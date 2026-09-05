# Local security dependency candidate — 2026-09-05

Compatibility follow-up: the first targeted upstream run was 60/61 because
service_identity 24.1.0 calls removed pyOpenSSL X509.get_extension. The verified
24.2.0 wheel switches that path to to_cryptography and is the minimal compatible
stable release; 26.1.0 is not required. The failed run is retained.

The current official Python 3.12-slim-bookworm amd64 manifest is still the frozen
9c47360a... manifest. Debian's signed repository offered one additional installed
package update: libpcre2-8-0 10.42-1+deb12u1, explicitly pinned in the Dockerfile.
The local candidate does not change Debian major versions or accept unresolved
OS scanner findings. Those remain visible for exact-asset review.

This is an unpublished candidate, not a release or vulnerability exception.
The original scan contained 90 High/Critical package records across Web/Push;
these were not 90 independently exploitable defects.

Runtime package updates are limited to the affected existing dependency graph:
Twisted 26.4.0 (stable, not 26.4.0rc2), aiohttp 3.14.3, cryptography 49.0.0,
PyJWT 2.13.0, pyasn1 0.6.4, thrift 0.24.0, tornado 6.5.8, urllib3 2.7.0,
and setuptools 78.1.1. These versions correspond to the recorded advisory fix
floors. The separate remote Dependabot PR is not merged or modified.

pyOpenSSL 26.3.0 is the first 26.x stable release whose declared dependency range
accepts cryptography 49.0.0: 26.0/26.1/26.2 cap it below 47/48/49 respectively.
26.4.0 exists but is not needed for that compatibility constraint.
The package Python floor moves to 3.10 because urllib3 2.7.0 requires it; the
actual CFS image remains Python 3.12/linux-amd64. No Python 3.8 support is claimed.

Evidence source: exact-version official PyPI JSON at
`https://pypi.org/pypi/<package>/<version>/json`, obtained on 2026-09-05;
raw metadata and full lock diff are in the local candidate review package.
The final image must be rescanned. No ignore-unfixed, lowered threshold, blanket
development-dependency exception or historical VEX inheritance is authorized.
