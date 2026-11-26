# Phase 1 · Reference architecture

The original brief identifies **662 Radar 1.2.5** and implementation classes
under `com.xiaobu.client`. Phase 1b below records the supplied file’s manifest
identity and supersedes the brief on the reference wire contract.

## Capture, forwarding and display

1. Android's `VpnService` requests user consent and establishes a TUN
   interface. Reads give the service outbound IP packets selected by VPN
   routes. Writes inject inbound IP packets. Forwarding sockets can use
   `protect()` to avoid routing their own traffic back into the TUN.
   [Android VpnService reference](https://developer.android.com/reference/android/net/VpnService)
2. The brief identifies Go `go-tun2socks` and V2Ray core (`v2ray.com/core`).
   Tun2socks connects TUN traffic to userspace transport handlers and can
   forward through a proxy. V2Ray provides configurable proxy routing and
   transport. Those capabilities explain how traffic could keep flowing while
   UDP datagrams are observed. The APK's exact forwarding configuration is
   unknown. [go-tun2socks upstream](https://github.com/eycorsican/go-tun2socks),
   [V2Ray core upstream and project migration](https://github.com/v2ray/v2ray-core)
3. The brief describes `CaptureService` capturing traffic and
   `DatagramUploader` sending UDP datagrams to a remote parser.
   `MirrorGateway`, `DirectUdpGateway` and `PacketQueue` are observed
   classes associated with this part of the app. Their precise call order
   and the mirror point are unknown. `NodeDirectory`, `AppConfigClient`,
   `AppConfigRepository`, `ServerStatus` and `MainActivity` are also
   listed. The brief identifies `/api/client/app-config` and
   `/api/client/nodes` on an HTTP reference server using port 18081.
4. The remote server produces snapshots. `RadarSnapshotClient` fetches
   `/snapshot`, with `X-Kite-Snapshot` observed in the brief.
   `RadarOverlayService`, `RadarScene` and `RadarAdjustPanel` are the
   overlay classes. The brief identifies `assets/radar/atlas.json` and
   `heroes/*.jpg` as resources used to display hero positions.
5. PCAPdroid demonstrates user-space capture without root using a local VPN
   and can export PCAP for offline inspection. IP and UDP headers can identify
   flows and delimit datagrams. Capturing traffic at TUN level does not supply
   application encryption keys or explain game-specific payloads.
   [PCAPdroid upstream](https://github.com/emanuele-f/PCAPdroid)

## Open questions and evidence needed

| Question | Status and evidence |
| --- | --- |
| Honor of Kings UDP message boundaries, versioning, framing, compression and encryption | **Open.** The APK shows the forwarded payload wrapper, but the game payload format requires an authorized capture fixture or protocol specification. [Q, G, U2] |
| Entity identifiers, coordinates, ordering and despawn/reset | **Partially resolved.** The scene uses `entity_key` with `entity_id` fallback, normalized `map_pos.u/v`, stream/frame gating and list replacement. Game-world units/origin, authoritative identity and upstream despawn/reset policy remain open. [S1, S2, M] |
| APK upload destination, transport, framing, metadata, retries and authentication | **Resolved for client behavior.** Room-scoped HTTP POST with bearer token, sequence-numbered JSON batches, hex/flow/direction/timestamp rows, file-backed retries and `accepted_batch`. Server replay and deduplication remain open. [U1–U4, Q, G] |
| Config, nodes and snapshot schemas and `X-Kite-Snapshot` | **Resolved for the traced consumers.** App-config and nodes have separate schemas. Snapshots use the room-scoped endpoint with `X-Kite-Snapshot: radar-v1` and `X-Kite-Viewer-Active: 1` as request properties. Server enforcement and complete room bootstrap remain open. [C, N, S1, H, G] |
| Packet selection and direct versus proxy routing | **Partially resolved.** The Java path wires DirectUdpGateway, with VPN app selection and native configuration routing TCP/DNS direct and other selected UDP to local SOCKS. End-to-end native filtering remains open. [G] |

## Phase 1b · 662 Radar reference deep dive (APK evidence)

The supplied APK's binary manifest declares `com.xiaobu.fengzheng`, version
`1.4.7`, version code 21. The implementation classes use `com.xiaobu.client`.
The evidence applies to this build. See [RADAR_REFERENCE.md](RADAR_REFERENCE.md)
for the offset index, full field tables and asset inventory. [ID]

- The viewer polls `/v1/rooms/{room}/snapshot` and sends
  `X-Kite-Snapshot: radar-v1` and `X-Kite-Viewer-Active: 1`. It can send a
  bearer token extracted from a validated viewer link. Normal cadence targets
  66 ms from poll start. [H, P]
- The scene requires an `entities` array. It checks each row's identity,
  coordinates, stream, frame and type. It interpolates normalized positions
  and replaces its entity list on advancing snapshots. Missing markers drop
  out on replacement. Empty usable lists clear it. The staleness test uses
  8 seconds since local advance. `snapshot_mono_ms` is diagnostic metadata.
  [S1, S2, D, M]
- App-config contains announcement and update metadata. The node directory
  supplies controller identity, node origins, availability mode and optional
  capacity/load readings. [C, N]
- The writer spools numbered JSON batches. It posts to
  `/v1/rooms/{room}/datagrams` and expects a numeric `accepted_batch`.
  Each row carries hex payload, an opaque flow ID, `up`/`down` and a
  wall-clock timestamp in seconds. [U1–U4, Q, G]
- DirectUdpGateway forwards through protected sockets and mirrors eligible
  UDP payloads to the uploader. The separately packaged MirrorGateway has
  its own port filter. [G]
- The map is 702 × 702, the atlas is 2048 × 2048 with 268 entries, and there
  are 138 hero portraits. The view uses normalized coordinates and rotates
  the map and markers together for the selected camp. [A, M, S2]

`DESIGN.md` defines the workspace's separate v1 contract. This inspection
documents the reference build’s contract. Analysis was local only, using
archive inspection, strings and a Python DEX parser after an offline
Androguard install failed. [RADAR_REFERENCE.md](RADAR_REFERENCE.md)
