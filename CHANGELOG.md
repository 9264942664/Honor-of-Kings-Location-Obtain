# Changelog

Append new versions below the existing milestones and preserve prior entries.

## v0.1 · 2026-11-26

- Documented the reference architecture, unresolved protocol questions and
  v1 API design in `LEARNING.md` and `DESIGN.md`.
- Verification scope was documentation review against the supplied APK
  observations. No executable tests were recorded for this milestone.

## v0.2 · 2026-11-26

- Added the Python HTTP skeleton, parser stub, YAML configuration and systemd
  unit under `server/`, with local startup in `README.md` and Ubuntu
  installation in `DEPLOY.md`.
- Python compilation, YAML defaults, environment overrides and in-memory HTTP
  checks passed. Systemd unit verification exited zero with unrelated host
  timer diagnostics. Socket creation was denied and local curl returned 7.

## v0.3 · 2026-11-26

- Documented the Beijing target at `39.96.60.127:18081`, wrapper-based
  installation and health checks. Added this changelog and rollback guidance.
- Re-ran Python compilation, configuration and override checks, systemd
  verification and in-memory HTTP requests. Deployment shell syntax and archive
  contents also passed local checks. The sandbox denied
  local socket creation and local health curl returned 7. Beijing remains
  pending operator verification.

## v0.4 · 2026-11-26

- Added Android capture app `android/` (Kite Capture, com.kite.capture,
  minSdk 26, targetSdk 34): VpnService TUN, UDP-only relay, upload batches
  to /api/client/upload, 2s /snapshot polling, local PCAP export.
- Added GitHub Actions workflow `.github/workflows/build-apk.yml` to build
  the debug APK (kite-capture-debug artifact). Fixed sdkmanager PATH with
  android-actions/setup-android in Muse review before pushing.
- Beijing deployment verified 2026-11-26 ~21:27 after security group TCP
  18081 opened: /health ok, upload accepted 1 / revision 1.
- Known limitation: IPv4 TCP from the selected app is BLOCKED during
  capture, only unfragmented IPv4 UDP is relayed; Honor of Kings login
  (TCP) may fail while capturing. Kotlin compile, Actions build and
  on-device behaviour are untested until the first Actions run.
