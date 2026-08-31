# Local verification record

Date: 2026-08-31

```text
Upstream source commit: 53c25a82f85739eb58f2c95b9483f61ac8deedc4
CFS minimal-payload tests: 3/3 PASS
Python compile: PASS
CFS config/static contract: PASS
Actual credentials found: 0
Docker build: NOT RUN — local Docker daemon unavailable
Deployment performed: NO
Production mutation: 0
```

The full upstream suite on Windows reported `44 passed / 20 failed`. The 20 failures are limited to upstream GCM and HTTP
proxy tests that require Twisted listener behavior and temporary credential files not functioning in this Windows runner.
They are retained as failures, not converted to PASS. The public Linux workflow runs the complete upstream suite and is the
required platform result before release.
