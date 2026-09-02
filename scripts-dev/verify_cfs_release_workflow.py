# Copyright 2026 Collector Figures
#
# SPDX-License-Identifier: AGPL-3.0-only

from pathlib import Path
import re


root = Path(__file__).parents[1]
workflow = (root / ".github/workflows/cfs-release.yml").read_text(encoding="utf-8")
ci_workflow = (root / ".github/workflows/cfs-ci.yml").read_text(encoding="utf-8")
dockerfile = (root / "docker/Dockerfile").read_text(encoding="utf-8")
base_lock = (root / "docs/CFS-BASE-IMAGE-LOCK.md").read_text(encoding="utf-8")
permission_plan = (root / "docs/CFS-RELEASE-PERMISSIONS-PLAN.md").read_text(
    encoding="utf-8"
)
promotion_script = (root / "scripts-dev/cfs-promote-oci-tag.sh").read_text(
    encoding="utf-8"
)
integration_script = (
    root / "scripts-dev/cfs-test-local-registry-promotion.sh"
).read_text(encoding="utf-8")
source_gate = workflow.index("Verify release tag is the exact protected main commit")
local_build = workflow.index("Build exact source locally")
scan = workflow.index("Scan local image before publication")
provenance = workflow.index("Create and verify prepublication provenance")
main_recheck = workflow.index("Reverify protected main before any registry mutation")
login = workflow.index("docker/login-action")
candidate = workflow.index("Publish only the run-scoped candidate tag")
sign = workflow.index("Sign, attest and verify the candidate digest")
promotion_main_recheck = workflow.index(
    "Reverify protected main before formal tag promotion"
)
promote = workflow.index("Promote the verified digest without overwriting formal tags")

assert (
    source_gate
    < local_build
    < scan
    < provenance
    < main_recheck
    < login
    < candidate
    < sign
    < promotion_main_recheck
    < promote
)
assert "load: true" in workflow
assert "push: false" in workflow
assert "push: true" not in workflow
assert "format: spdx-json" in workflow
assert "format: cyclonedx" in workflow
assert "refs/remotes/origin/main^{commit}" in workflow
assert 'test "$tag_commit" = "$main_commit"' in workflow
assert (
    "CANDIDATE_TAG: candidate-${{ github.run_id }}-${{ github.run_attempt }}-${{ github.sha }}"
    in workflow
)
assert "cosign sign --yes" in workflow
assert "cosign verify-attestation --type slsaprovenance" in workflow
assert '--certificate-identity "$CERTIFICATE_IDENTITY"' in workflow
assert "certificate-identity-regexp" not in workflow
assert (
    "CERTIFICATE_IDENTITY: https://github.com/${{ github.repository }}/.github/workflows/"
    "cfs-release.yml@refs/tags/${{ github.ref_name }}" in workflow
)
assert "bash scripts-dev/cfs-promote-oci-tag.sh" in workflow
assert "docker buildx imagetools create" not in workflow
assert re.search(
    r"docker buildx imagetools create \\\n\s*--prefer-index=false \\\n\s*--metadata-file",
    promotion_script,
)
assert not re.search(r"imagetools create\s+--tag", promotion_script)
assert "containerimage.descriptor.digest" in promotion_script
assert 'test "$metadata_digest" = "$candidate_digest"' in promotion_script
assert 'test "$raw_manifest_digest" = "$candidate_digest"' in promotion_script
assert "refusing to overwrite" in promotion_script
assert (
    "registry:2@sha256:46faa9a1ae6813194b53921a370f2f4f8c5e1aae228a89bceafef5847a6a3278"
    in integration_script
)
assert "127.0.0.1:5000:5000" in integration_script
assert "different_digest_rejected=true" in integration_script
assert "formal_unchanged=true" in integration_script
assert re.search(r"permissions:\s*\n\s*contents: read", ci_workflow)
assert not re.search(r"packages:\s*write|id-token:\s*write", ci_workflow)
assert "push: false" in ci_workflow
assert "CFS_PUSH_LOCAL_DOCKER_BUILD_PASS" in ci_workflow
assert "cfs-test-local-registry-promotion.sh" in ci_workflow
assert (
    "poetry run black --check sygnal/webpushpushkin.py tests/test_webpush_cfs.py "
    "scripts-dev/verify_cfs_release_workflow.py" in ci_workflow
)
assert (
    "poetry run ruff sygnal/webpushpushkin.py tests/test_webpush_cfs.py "
    "scripts-dev/verify_cfs_release_workflow.py" in ci_workflow
)
assert "poetry run python -m compileall -q sygnal scripts-dev" in ci_workflow
assert 'docker tag "$LOCAL_IMAGE" "$IMAGE:$GITHUB_REF_NAME"' not in workflow[:promote]
assert "PREPUBLISH-SHA256SUMS.txt" in workflow

uv_lock = (
    "ghcr.io/astral-sh/uv:python3.12-bookworm@"
    "sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7"
)
python_lock = (
    "docker.io/library/python:3.12-slim-bookworm@"
    "sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef"
)
assert dockerfile.count(uv_lock) == 2
assert dockerfile.count(python_lock) == 1
assert dockerfile.count("FROM --platform=linux/amd64") == 3
assert "ghcr.io/astral-sh/uv:python3.12-bookworm" in base_lock
assert (
    "sha256:9aa60c50016c0485636ab9a830246a6ef3399aa4a8bab3d17ef4a2358fba2ca7"
    in base_lock
)
assert "docker.io/library/python:3.12-slim-bookworm" in base_lock
assert (
    "sha256:9c47360a2a0355e2da18516d0b1c2126ec22c195d2185e97347c9d98398c5bef"
    in base_lock
)
assert "linux/amd64" in base_lock
assert "Before" in permission_plan
assert "After" in permission_plan
assert "cfs-push-v*" in permission_plan
assert "Job-only release tag creator" in permission_plan
assert "prevent self-review: `false`" in permission_plan
assert "Future Technical Owner" in permission_plan
assert "prevent self-review: `true`" in permission_plan
assert "not applied" in permission_plan.lower()

literal_secret_patterns = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]{20,}"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    re.compile(r"Authorization\s*:\s*Bearer\s+[A-Za-z0-9._~+/-]{12,}", re.I),
]
for source in (
    workflow,
    ci_workflow,
    dockerfile,
    base_lock,
    permission_plan,
    promotion_script,
    integration_script,
):
    assert all(pattern.search(source) is None for pattern in literal_secret_patterns)

print(
    "CFS_PUSH_RELEASE_WORKFLOW_PASS main_gate=true candidate_first=true "
    "exact_identity=true prefer_index_false=true metadata_raw_candidate_equal=true "
    "final_no_overwrite=true base_digests=true static_scope=black,ruff,compileall "
    "actual_credentials=0"
)
