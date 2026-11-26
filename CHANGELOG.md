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

## v0.5 · 2026-11-26

- Persisted accepted uploads as daily UTC JSONL captures under
  `/var/lib/hok-radar`, provisioned by the systemd unit's `StateDirectory`.
- Added configurable 100 MiB per-file rotation and 500 MiB total retention,
  with numeric suffixes and oldest-file deletion.
- Added `GET /api/captures` to list files and `GET /api/captures/<name>`
  to download them as NDJSON.
- Verified live on Beijing 39.96.60.127:18081: upload accepted 1 /
  revision 1, capture file on disk, survives service restart.

## v0.6 · 2026-11-26

- Added an IPv4 TCP relay for the selected app. An app SYN opens a
  protected socket to the original destination with a 10-second connect
  timeout. A successful connect sends SYN-ACK with MSS 1460 and a
  65,535-byte receive window. The app ACK establishes the flow. App and
  remote FINs half-close their respective directions, and resets or
  socket errors tear down the flow.
- Limited the relay to 32 concurrent connections with one worker per
  connection and a 60-second idle timeout in either direction. Excess
  connects and queue overflow reset the flow. The relay drops and re-ACKs
  duplicate or out-of-order app data and caps each app queue at 64
  MTU-sized segments. Remote data fits MTU 1500, the peer MSS, and the
  peer window. The TUN leg repeats SYN-ACK on duplicate SYN and omits
  data and FIN retransmission and zero-window probes.
- Added active TCP connections to the app status and included full
  IPv4 TCP packets in both directions in the local raw-IP PCAP and
  captured counter. Only UDP datagrams go to `/api/client/upload` for
  the Honor of Kings location parser. TCP login and matchmaking packets
  stay in the PCAP. IPv6 still bypasses capture and IPv4 fragments are
  still dropped.
- Kotlin compile and on-device test not yet done - must be verified by GitHub Actions build.
  An Android device is needed to verify live relay behavior after the build.
