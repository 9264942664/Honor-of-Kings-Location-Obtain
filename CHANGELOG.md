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

## v0.7 · 2026-11-26

- Added `tools/analyze_pcap.py` (Python 3.10+ standard library only, no
  tshark/scapy): top remote IPs/ports by packets and bytes, UDP vs TCP
  split, per-flow packet sizes and timing/pps, likely game-server flows,
  per-second summaries, with `--json` / `--top` / `--local-ip` options.
- Added `tools/gen_test_pcap.py` to generate a synthetic PCAP with known
  ground truth for testing the analyzer.
- Verified on synthetic PCAPs: output matches the known input exactly
  (231 packets / 35,188 bytes, top flow 200 packets / 50.25 pps, only the
  high-rate UDP flow flagged as likely game server); empty, truncated
  and garbage files do not crash.
- Known limits: classic PCAP only, not pcapng; the game-server heuristic
  (>= 50 packets, >= 10 pps, >= 2 s UDP) is unvalidated on real Honor of
  Kings traffic until a real game capture is analyzed.

## v0.8 · 2026-11-26

- Added `RADAR_REFERENCE.md`: deep analysis of the reference APK
  (snapshot schema, X-Kite-Snapshot semantics, app-config and nodes
  schemas, coordinate/map mapping, entity lifecycle, upload wire format,
  server requirements), with APK evidence per claim and UNKNOWNs marked.
- Updated `LEARNING.md` with the Phase 1b deep-dive findings.
- Correction: the supplied APK is not 662 Radar 1.2.5 / com.xiaobu.client
  as first assumed; its manifest declares com.xiaobu.fengzheng 1.4.7
  (versionCode 21), SHA-256
  0ddd6b94ba5baca44dd4e797ceb8afba706588cc91a45a4b047fc619baf547a2.
  Findings apply to this build; 1.2.5 behavior is UNKNOWN.
- Key finding: the reference contract differs from our v1 contract —
  room-scoped `GET /v1/rooms/{room}/snapshot` and
  `POST /v1/rooms/{room}/datagrams` with hex payloads and
  `accepted_batch`, `X-Kite-Snapshot: radar-v1` as a request header,
  versus our `/snapshot` + `/api/client/upload` with base64. Whether to
  adapt our server to the reference contract is an open design decision.


## v0.9 · 2026-11-26

- Added `PCAP_ANALYSIS.md` and a reproducible stdlib probe for the real
  Honor of Kings capture. Reproduced the 92,545-packet baseline and
  measured 32,574 datagrams on the leading gameplay candidate.
- Verified two incrementing counters, three 1,400-byte inbound payloads
  with actual zero fill, and plaintext HTTP game resource range downloads.
- Added the offline parser hypothesis and four passing unit tests. A
  full-capture self-check matched 32,574 signatures and produced zero
  entities. Python compilation and an in-memory v1 HTTP smoke check passed.
- Recorded the findings in Phase 1c of `LEARNING.md` and kept the v1
  HTTP contract. The capture covers phone-to-game-server traffic.

## v0.9.1 · 2026-11-26

- Renamed the phone app's display name from "Kite Capture" to "Kite"
  (`android:label` in AndroidManifest.xml, VPN session name and
  notification title in CaptureService.kt, android/README.md title).
- Package/application id `com.kite.capture` is unchanged, so an installed
  app updates in place. Artifact name `kite-capture-debug`, server and
  API contract are unchanged.
- Note: the first Actions runs for this rename (#8, #9) failed at
  "Assemble debug APK" because the first push accidentally wrote the
  files as base64 text instead of their real contents (wrong
  `push_files` content encoding). The files were restored to their
  correct text in 4c4faa9 and run #10 passed. Lesson: use the
  `push-files` CLI, which snapshots local files directly, not
  hand-built base64 in `--arguments-json`.
