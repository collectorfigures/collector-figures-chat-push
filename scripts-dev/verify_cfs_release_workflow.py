# Copyright 2026 Collector Figures
#
# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path


workflow = (Path(__file__).parents[1] / ".github/workflows/cfs-release.yml").read_text(
    encoding="utf-8"
)
local_build = workflow.index("Build exact source locally")
scan = workflow.index("Scan local image before publication")
provenance = workflow.index("Create and verify prepublication provenance")
login = workflow.index("docker/login-action")
publish = workflow.index("Publish the already-scanned local image")

assert local_build < scan < provenance < login < publish
assert "load: true" in workflow
assert "push: false" in workflow
assert "push: true" not in workflow
assert "format: spdx-json" in workflow
assert "format: cyclonedx" in workflow
assert 'test "$tag_digest" = "$sha_digest"' in workflow
assert "cosign sign --yes" in workflow
assert "cosign verify-attestation --type slsaprovenance" in workflow
assert "PREPUBLISH-SHA256SUMS.txt" in workflow

print("CFS_PUSH_RELEASE_WORKFLOW_PASS scan_before_publish=true")
