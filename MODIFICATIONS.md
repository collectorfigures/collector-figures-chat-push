# Collector Figures modifications

Modification date: 2026-08-31

- Add `payload_mode: cfs_minimal` for the CFS WebPush application.
- In minimal mode, forward only `room_id`, `event_id`, `unread`, `cfs_schema`, and an opaque account fingerprint.
- Exclude message content, sender/display name, room name/alias, membership, email, and public Matrix ID from the browser
  Push payload.
- Never log the WebPush `auth` secret, endpoint, or raw `p256dh` push key. Logs use a short one-way push-key identifier.
- Provide `contrib/cfs/sygnal.cfs.yaml` for `com.collectorfigures.chat.web` with an explicit browser endpoint allowlist.
- Run the OCI image as UID/GID 991 with a read-only-root-compatible working directory and a dependency-free healthcheck.

The Safari Web Push endpoint is intentionally not guessed or pre-authorized. It must be learned from the approved
non-Production Safari acceptance environment and added through a separately reviewed allowlist change.
