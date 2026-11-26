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
