# Phase 1 · Reference architecture

The supplied APK analysis identifies **662 Radar 1.2.5** (Android package
`com.xiaobu.client`). The class names, endpoint paths and flow below come
from that brief. The numeric reference hosts are omitted.

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

| TODO | Evidence needed |
| --- | --- |
| Honor of Kings UDP message boundaries, versioning, framing, compression and whether or how contents are encrypted | A protocol specification or authorized, versioned capture fixtures with known plaintext where available, expected decoded fields, and controlled session events. |
| Entity identifiers, coordinate units and origin, update ordering, and despawn or reset semantics | Authorized fixtures paired with known entity positions and lifecycle events. |
| APK upload wire format, including destination, transport, framing, metadata, retries and any authentication | Authorized inspection of the uploader and an upload exchange or protocol specification. The fact that it uploads game UDP datagrams does not establish the upload transport. |
| Config, nodes and snapshot response schemas, and the direction, value and semantics of `X-Kite-Snapshot` | Authorized client call-site inspection and representative request and response fixtures. |
| Packet selection and proxy versus direct routing | Authorized call-graph inspection and controlled flow traces identifying both traffic paths. |
