# Radar reference · local APK evidence

The supplied file `_____root___0_miaf.apk` declares application ID **`com.xiaobu.fengzheng`**, version name **`1.4.7`**, and version code **21**. Its DEX implementation classes use **`com.xiaobu.client`**. The earlier brief identifies 662 Radar 1.2.5. Findings below apply to the supplied file. SHA-256 is `0ddd6b94ba5baca44dd4e797ceb8afba706588cc91a45a4b047fc619baf547a2`. [ID]

“Observed” means a literal, asset, or behavior traced through the packaged bytecode. “Inferred” identifies a conclusion drawn from those observations. “UNKNOWN” identifies a gap. Hex offsets are byte offsets in the original `classes.dex`.

## Snapshot schema

Observed consumer is Android `org.json.JSONObject` / `JSONArray`. Field types describe the accessor and the canonical JSON representation. Android `opt*` accessors can coerce some values. The overlay path was traced through `RadarSnapshotClient.fetchMeasured`, `RadarOverlayService`, `RadarView.update`, and `RadarScene.apply`. [S1, S2, H, P]

| Path | JSON representation and handling | Evidence |
| --- | --- | --- |
| `entities` | Required array, 0–4,096 entries. Individual entries are inspected as objects. | [S1] |
| `entities[].removed` | Optional boolean, defaults false. True skips the row. | [S1] |
| `entities[].coordinate_kind` | String, must equal `actor_position` for a row to participate. | [S1] |
| `entities[].map_pos.u`, `entities[].map_pos.v` | Required for a participating row. `map_pos` is an object with two finite numbers in inclusive range 0–1. | [S1] |
| `entities[].entity_key`, `entities[].entity_id` | String key with `entity_id` as the `optString` fallback. Effective key must be nonempty. | [S1] |
| `entities[].stream_id` | Required nonempty string for a participating row. | [S1] |
| `entities[].frame_number` | Required nonnegative long for a participating row, defaults −1. | [S1] |
| `entities[].entity_type` | String allowlist `hero`, `monster`, `monster_spawn`, `tower`, `base`, `building`, `minion`, `unit`, `trap`, `vision`. | [S1] |
| `entities[].camp`, `entities[].hero_id` | Optional integers, default 0. Camp participates in affiliation and orientation. Hero ID is the portrait lookup key. | [S1, S2, M] |
| `entities[].is_self`, `entities[].map_hidden` | Optional booleans, default false. Self participates in camp and orientation selection. Hidden participates in rendering. | [S1, S2, M] |
| `entities[].map_icon`, `entities[].map_icon_scale` | Optional string default empty and number default 1. Scale is clamped to 0.1–4, with fallback 1 if the result is nonfinite. | [S1, M] |
| `entities[].health.current`, `entities[].health.max` | Optional numbers in an optional object. Defaults −1 and 0. Derived alive flag is false at exactly zero current health. | [S1] |
| `entities[].remaining_ms` | Optional number, default 0. Used in monster-spawn rendering. | [S1, M] |
| `decoder`, `decoder.ended`, `decoder.native` | Optional objects at `decoder` and `decoder.native`. Optional boolean `ended` defaults false and drives end-state display and polling. `native` is passed to the status formatter when applicable. | [S2, P] |
| `decoder.native.stage`, `preparation_ready`, `preparation_for_next_match`, `output_frame` | Optional nested status keys under `decoder.native`. Stage string defaults empty, booleans default false, output frame is a long with default −1. Stage literals tested include `error`, `complete`, `warming`, `ready_for_match`, `waiting_initialization`, `waiting_capacity`. | [ST] |
| `decoder.performance` | Optional diagnostics object. The overlay passes it to diagnostics configuration. `enabled` is checked against boolean true, `capture_id` and `telemetry_token` are read as strings. | [D, P] |
| `decoder.performance.epoch` | Optional diagnostic context string. Context comparison also reads `capture_id`. | [D] |
| `decoder.performance.correlation` | Optional diagnostics object. Version gate reads integer `version` and compares to 1. Copies `clock_id` if present and numeric `snapshot_mono_ms`, `frame_received_mono_ms`, `frame_output_mono_ms`, `output_frame`, `output_batch`. Reads output batch and frame as longs for trace correlation. | [D] |

The scene derives coordinates from `map_pos.u/v`, identity from `entity_key/entity_id`, affiliation from `camp`, and alive state from `health.current`. The entity accessor list above contains no flat `id`, `heroId`, `x`, `y`, `team`, `hp`, `alive` or `timestamp` reads. The top-level scene accessor list contains no revision requirement. [S1, S2]

## X-Kite-Snapshot semantics

| Item | Observed client behavior | Evidence |
| --- | --- | --- |
| URL | GET `{origin}/v1/rooms/{room}/snapshot`. Uses `HttpURLConnection` with no output body or method override. Redirect following and caches are disabled. | [H] |
| `X-Kite-Snapshot` | **Request** property, fixed literal **`radar-v1`**. The response path reads `Server-Timing`. It has no read of an `X-Kite-Snapshot` response header. | [H] |
| `X-Kite-Viewer-Active` | **Request** property, fixed literal **`1`** on a fetch. | [H] |
| `Access` | Holds origin, room, token. Viewer URI must match the current session origin's scheme and authority, have no query, have path `/r/[0-9]{6}`, and have either no fragment or a fragment matching `v=[A-Za-z0-9_-]{43}`. The fragment token, when present, becomes `Authorization: Bearer …`. Invalid access resolves to null. | [H] |
| `FetchResult` | Holds parsed `snapshot`, local monotonic timing fields and parsed server timing. `fetch` returns the snapshot member. `record` emits `view_response` diagnostics with request/response timings. The active connection can be cancelled and the validity predicate is checked during fetch. | [H] |
| `matchesSnapshotContext` | A **LatencyDiagnostics** method. It checks enabled/open diagnostics and matches `decoder.performance.capture_id` and `epoch` against local diagnostics state. Used by tracing, including `ViewTraceState`. Scene admission uses separate checks. | [D, S1, S2] |
| `emptySnapshot` | A **TransferStats** factory. Returns zero counters/rates with packet and acknowledgment ages of −1. The DEX method index locates it on TransferStats. | [U4] |

**Inferred:** `radar-v1` selects a representation/protocol variant and `1` signals an active viewer. **UNKNOWN:** server handling or enforcement of these headers, including whether the viewer signal changes resource use. Client literals are fixed across polls. [H]

## App-config schema

Observed `GET /api/client/app-config` with `Accept: application/json`, HTTP 200 required, 5 s connect/read timeouts, then strict boolean `ok: true` and object `config`. All nine keys below are fetched with `get`, so all must be present on a successful decode. Defaults refer to the separate local `AppConfig.empty()` state. Text must be a string within its length limit, without NUL, and is trimmed. Integers must be JSON integers represented by Java Integer/Long. [C]

| Key under `config` | Type, constraints, and local empty value | Role |
| --- | --- | --- |
| `revision` | long 0–Long.MAX_VALUE, empty 0 | Config revision metadata |
| `updatedAt` | long 0–Long.MAX_VALUE, empty 0 | Config update metadata. Time unit UNKNOWN. |
| `announcementEnabled` | boolean, empty false | Announcement gate |
| `announcement` | string ≤8,192 characters, empty string | Announcement text |
| `versionCode` | int 0–Integer.MAX_VALUE, empty 0 | Compared with installed build |
| `versionName` | string ≤64 characters, empty string | Display version |
| `releaseNotes` | string ≤8,192 characters, empty string | Update notes |
| `downloadUrl` | string ≤2,048 characters, empty string | HTTP(S) update link when version code is positive |
| `forceUpdate` | boolean, empty false | Mandatory-update flag for newer version |

Version code 0 requires empty version name and URL and false force-update. A positive code requires nonempty version name and a valid download URL. Repository methods load a cached config for the origin and support startup and manual refresh. Endpoint paths, batching, polling, and node choice have independent call sites and no keys in this decoder. [C, N, U2, P]

## Nodes schema

Observed `GET /api/client/nodes` via `RoomClient.request` with null body and token. The top-level object directly supplies `controllerId` and `nodes`. Controller ID and node IDs match `[A-Za-z0-9_-]{1,128}`. The required node array has at most 1,000 entries. [N, U1]

| Node key | Type and handling |
| --- | --- |
| `mode` | Optional string, defaults `active`. Both `active` and `offline` are included. Other modes are skipped. Only `active` sets the node's reachable flag. |
| `id` | Required string accessor and unique within included entries. |
| `name` | Required string accessor, nonempty, at most 128 characters. |
| `origin` | Required string accessor, passed through `RoomClient.validOrigin` for an HTTP(S) origin. |
| `maxClients` | Optional integral number 1–10,000. Missing or invalid yields −1. |
| `onlineClients`, `connectedClients` | Optional nonnegative integral numbers up to Integer.MAX_VALUE. Missing or invalid yields −1. |
| `cpuPercent` | Optional finite number 0–100, otherwise −1. |
| `memoryBytes`, `memoryLimitBytes` | Optional longs, default −1. |

Node methods compute remaining capacity and compare availability. Selectability checks reachable state and known capacity (valid maximum and online counts). `require` validates controller identity, node identity and origin and checks selectability. `url`, `region`, `priority` and `health` do not appear as reads in the node parser. [N]

## Upload wire format

Observed **POST `{origin}/v1/rooms/{room}/datagrams`**, fixed-length UTF-8 JSON, `Content-Type: application/json; charset=utf-8`. Room setup provides `origin`, `room` and `upload_token`. The upload token is passed to `RoomClient` for the bearer request header. [U1, U2]

Illustrative body assembled from the observed serializer and packet constructor, with example subject values [U2, Q, G].

```json
{"batch":1,"datagrams":[{"payload_hex":"000102","flow":"f1","direction":"up","timestamp":1700000000.125}]}
```

- `batch` is the uploader's long sequence. Rows contain lowercase hex `payload_hex`, opaque string `flow`, string `direction` (`up` or `down`), and a double `timestamp` from device wall-clock milliseconds divided by 1,000. The socket tuple stays in the gateway. DirectUdpGateway assigns an incrementing flow ID for a target in a SOCKS association and emits it as `f` plus the integer. The row has no source/destination address or port fields. `capturedNanos` is internal telemetry state. [U2, Q, G]
- The writer gathers up to 64 rows, checks a running 450,000-character row budget, and seals against an adaptive collection window. The character check is a loop threshold. It persists UTF-8 bodies as `%010d.json` with `counter.txt` and restores pending files. Writer-side backlog limit is 128 MiB as indicated by the guard and UI string. [U2]
- `UploadBatchTiming` has `MIN_MILLIS`, `MAX_MILLIS`, `blockedUntil`, `requestMillis`, `requestStarted` and `sending`. It adjusts collection delay using measured request time, pending batch count, in-flight request age and retry backoff, bounded to 66–1,000 ms. [U3]
- Sender reads `accepted_batch` as a long and accepts an acknowledgment at least as large as the submitted file's number. A smaller value triggers `Unacknowledged batch`. Confirmed batches are removed from disk. Retry backoff computes `min(10000, 500 × (1 << min(5, attempt)))` ms. The sender has terminal rejection branches for 401, 403, 404, 409, 410 and 413, preserving pending records. `finish` has a separate room-scoped `/finish` POST with an empty object. Server deduplication or idempotency is UNKNOWN. [U2]
- `TransferStats` counts captured and acknowledged packets/bytes by direction and derives pending totals, rates, and last-packet/ack ages. Restored and confirmed counters read `payload_hex` and `direction` from local serialized rows. [U4]

## Coordinate and map mapping

- `assets/radar/map.png` is **702 × 702**. `assets/radar/atlas.png` is **2048 × 2048**. `assets/radar/atlas.json` contains **268** named entries with `rect`, `size` and `offset` arrays. `assets/radar/heroes/` contains **138** numeric `.jpg` files. The loader parses the numeric stem, and the draw path retrieves the corresponding integer `hero_id` portrait. [A, M]
- `RadarView.onDraw` centers a square of side `min(viewWidth, viewHeight)`, multiplied by 0.98 in embedded mode. Marker centers use `x = left + side × u` and `y = top + side × v`. The renderer also computes a sprite scale of `side / 702`. The display origin for unrotated markers is at the map's top-left. For rotated scenes it uses `1-u`, `1-v`, and rotates the background bitmap 180° about the view center. `RadarScene.apply` sets rotation for a self hero in camp 2, with camps 1 and 2 recognized in this self branch. The 702-pixel dimension is an asset resolution. Game-world bounds, origin, units and upstream world-to-`u/v` transformation are UNKNOWN. [M, S2, A]
- Atlas names include health bars and rings (`bl_*`, `Battle_HP_Blue_Ring`, `Battle_HP_Red_Ring`, `Img_Map_*Loop_Hp`), team markers (`friend`, `enemy`, loop variants), the `Hero_Dead` sprite, map bases, towers, objectives, signals and minimap markers. The exact keys are enumerated below. [A]

## Entity lifecycle

- Rows removed or unusable are skipped. A valid array with no usable rows clears the entity list and ID map and resets frame/advance and orientation state. An advancing snapshot builds a new ID map and render list for the chosen stream. Missing entities drop out on replacement. Old per-ID state supplies motion history, and a stream change affects that history. This is full-list consumption with local interpolation, with no per-row patch applied to the previous entity list. [S1, S2]
- The scene tracks the maximum accepted row frame, prefers a hero stream when choosing a stream, and uses stream and frame checks before replacement. Same-stream lower or repeated maxima do not advance the render state. Point time is derived as `frame_number × 66` for interpolation. Upload timestamp and snapshot correlation clocks are separate. [S1, S2, D, Q]
- Exactly zero current HP yields dead. The renderer skips dead rows in its general path with explicit exceptions for types such as towers/buildings and `monster_spawn`. Spawn rendering tests the supplied countdown and looks up icon variants with `_dead`, `_Ready`, or `_Dead`. The atlas contains `Hero_Dead`. A literal `Hero_Dead` selection was not found in the draw path. Dynamic selection through an icon key is possible where the renderer uses that key. [S1, M, A]
- `RadarScene.stale` compares elapsed local time since last advance against **8,000 ms**. Draw uses the stale result for the waiting state. The room/link change or expiry clears the scene. `snapshot_mono_ms` is optional trace correlation data. TransferStats ages report local capture/ack activity. An independent per-entity timeout and the server's despawn policy are UNKNOWN. [S2, D, M, P, U4]

## Capture path

| Component | Observed role |
| --- | --- |
| `CaptureService` / `VpnRouting` | Android VpnService subclass establishes a TUN with IPv4 default route, address `10.111.0.2/32`, MTU 1,500, and nonblocking mode. Per-app mode selects `com.tencent.tmgp.sgame`; global mode excludes the radar app package. It hands the TUN descriptor to `Tun2socks.startV2Ray` and sets up socket protection. It creates the room uploader and passes its sink to DirectUdpGateway. [G] |
| `NativeTunnelConfig` / `libgojni.so` | Generated V2Ray config declares a `freedom` direct outbound, TCP direct, DNS rules targeting direct, and a UDP rule targeting local SOCKS. Arm64 native strings identify `github.com/eycorsican/go-tun2socks` and `v2ray.com/core`. The config and JNI call establish the Java-side handoff. Internal native filtering and runtime routing were not traced. [G] |
| `DirectUdpGateway` | The path wired by CaptureService. Local login and UDP association handling, protected UDP channels per target within an association, outbound forwarding and inbound replies. Successful forwarding has a payload copy path to the sink in both directions. No game-port or game-IP allowlist appears in the traced Java direct-gateway payload path. [G] |
| `MirrorGateway` | Separate SOCKS implementation with TCP forwarding, UDP association sockets and a mirroring sink interface. Its `shouldMirror` excludes destination ports 53 and 853. CaptureService instantiates DirectUdpGateway. The 53/853 filter belongs to MirrorGateway and cannot be attributed to the direct gateway. [G] |
| `PacketQueue` | Bounded queue, 4,096 records and 8 MiB aggregate payloads. Clones payloads with metadata for the writer thread. Queue saturation can stop recording with pending data retained. [Q, U2] |
| `NodeDirectory` / `ServerStatus` | Directory loads and validates controller node metadata. Status translates decoder/preparation stages for the UI. Its room-monitor preparation helper additionally reads `preparation_ready_workers`, capped to 0–3 for display. That helper is distinct from the snapshot status formatter. [N, ST] |

**Inferred:** the principal capture scope is app routing plus the native rules that select which UDP reaches the local gateway. The Java copy path supports both directions for eligible forwarded flows. The effective selection across all native and Android branches is UNKNOWN. [G]

## Server requirements checklist

These are client-side compatibility observations. No server was run or contacted.

- Provide a room-scoped snapshot endpoint on the current session origin. A valid viewer link and any required bearer authorization must already be established. Reply HTTP **200**, UTF-8 JSON object, ≤**4 MiB**. The client sets 6 s connect/read timeouts. The smallest scene input observed is `{"entities":[]}`, which can render a waiting/empty state. [H, S1, S2]
- To supply a drawable entity, send an eligible row as in the example below and advance the frame for later full snapshots. Assets, display settings, stream choice and overlay lifecycle also affect whether a marker is visible. [S1, S2, M, P]

```json
{"entities":[{"coordinate_kind":"actor_position","map_pos":{"u":0.5,"v":0.5},"entity_id":"example","stream_id":"stream","frame_number":1,"entity_type":"hero","hero_id":105}]}
```

- Snapshot fetches are single-flight while screen and overlay are active. Normal scheduling targets **66 ms from poll start**, ended scenes use **1,500 ms**, and fetch failures use **2,000 ms**. There are additional 500/700/1,000 ms scheduling branches for lifecycle and readiness. 401/404/410 expire the link and clear the scene. A missing/non-array or oversized `entities` triggers `JSONException("Invalid snapshot entities")`; the overlay marks invalid data and schedules again. Non-object or invalid individual rows take skip branches. [P, S1, H]
- Minimal successful app-config example, with all nine required keys. [C]

```json
{"ok":true,"config":{"revision":0,"updatedAt":0,"announcementEnabled":false,"announcement":"","versionCode":0,"versionName":"","releaseNotes":"","downloadUrl":"","forceUpdate":false}}
```

- Minimal parseable node directory example below. An empty directory supplies no selectable origin. For actual selection supply an eligible active node with controller and node identity, name and valid origin, plus valid `maxClients` and `onlineClients` values. For example, `{"id":"node","name":"Node","origin":"https://node.example","maxClients":10,"onlineClients":0}` is a constructed active node row with available capacity. [N]

```json
{"controllerId":"controller","nodes":[]}
```

- If the APK also handles capture, room creation and monitoring must supply session state. CaptureService obtains `viewer_url` and constructs the uploader from the room response. Accept upload bodies and acknowledge with `accepted_batch`. The minimal endpoints and JSON examples above were derived for their individual client consumers. A complete room authorization/lease/bootstrap contract is UNKNOWN. [G, H, U1, U2]

## UNKNOWN list

- Behavior of the 1.2.5 build identified in the earlier brief. [ID]
- Game UDP framing, compression, encryption, plaintext, authoritative game-entity IDs, world coordinates and upstream normalization. [Q, G, S1]
- Server rules for stream identity and switching, authoritative reset/despawn policy, full server response schema beyond client reads, and any server-specific header enforcement. [S2, D, H]
- Exact end-to-end native packet selection under all modes, complete server room/authorization contract, and server upload replay/deduplication behavior. [G, U2]
- Runtime interoperability and timing under network conditions. Examples are constructed from call sites and were never sent. [H, C, N, U1]

## Evidence index

| Tag | APK evidence |
| --- | --- |
| ID | Binary `AndroidManifest.xml` root attributes `package`, `versionName`, `versionCode`; DEX class descriptors `Lcom/xiaobu/client/...`. |
| H | `RadarSnapshotClient.access` 0x249b8, path regex at 0x24a36, fragment regex 0x24a54. `fetchMeasured` 0x24adc, URL literals 0x24b74/0x24b8c, bearer 0x24bf8–0x24c26, header setters 0x24c2c–0x24c42, status/timing/body 0x24c54–0x24d12. `Access` 0x247f8, `FetchResult.record` 0x2483c, `cancel` 0x24ed8. |
| S1 | `RadarScene.apply` 0x23cc4, container test 0x23cdc–0x23cf8, allowlist 0x23d0e–0x23d36, required row and coordinate checks 0x23d7a–0x23eee, optional fields 0x23f20–0x24032, error literal 0x245a4. |
| S2 | `RadarScene.apply` stream/frame selection 0x23eee–0x23f1e, frame-to-time 0x23d68/0x24048, ended/status and clear/ordering 0x240b2–0x2418c, buffer and advance 0x2418e–0x24380, stream filtering, ID matching, camp and replacement 0x24384–0x24596. `stale` 0x245b0, `tick` 0x24610, `clear` 0x2477c. |
| D | `LatencyDiagnostics.matchesSnapshotContext` 0x13374, configure reads 0x135ba–0x13610, epoch 0x138ea, correlation object 0x13a4e–0x13a78, correlation version and numbers 0x14bea–0x14d22. `ViewTraceState.matches` 0x28568 and `replace` 0x28630. |
| P | `RadarOverlayService.poll` 0x215a0 and `schedule` 0x21698. Callback generation/current-link and delays 0x21148–0x21204, HTTP expiry and invalid-data branch 0x2128a–0x212dc, elapsed-time scheduling 0x212de–0x2130c. |
| C | `AppConfigClient.fetch` 0xd3d8, envelope 0xd4fe–0xd522, `decode` 0xd2cc, keys and limits 0xd2ea–0xd3d6, boolean/string/integer helpers 0xd1e0/0xd614/0xd66c, URL validation 0xd220. `AppConfig.empty` 0xdde4, announcement/update predicates 0xdd48/0xdd80/0xddb8. `AppConfigRepository` cache constructor 0xd920 and refresh/start 0xdc34/0xdcfc. |
| N | `NodeDirectory.load` 0x1d9e4, `parse` 0x1da18, node JSON reads 0x1da2c–0x1dbe4, `count` 0x1de0c, `require` 0x1dca0, `compareAvailability` 0x1dd0c, `Node.selectable` 0x1d8a4. `RoomClient.validOrigin` 0x26998. |
| U1 | `RoomClient.request` 0x26ae0, header/method 0x26ba2–0x26c0c, success response handling 0x26d00–0x26d9c, UTF-8 encoding helper `bytes` 0x26880. `DatagramUploader.transport` 0x10890 and constructor 0x10a14. |
| U2 | `DatagramUploader.row` 0x10910, wire keys 0x10996–0x109ca. `persist` 0x10dcc, row/length thresholds 0x10ea6–0x10ec0, wrapper 0x11010–0x11036, persistence 0x111fc–0x11240, backlog message 0x11350. `send` 0x1142c, finish 0x11490–0x114d2, datagrams path/token 0x1179a–0x117ca, ack 0x118b2–0x119e0, rejection codes 0x11cc4–0x11d1e. `backoff` 0x10c28. |
| U3 | `UploadBatchTiming.delayMillis` 0x28368, `backingOff` 0x28458, `completed` 0x2849c, `started` 0x28524, class field table. |
| U4 | `TransferStats.emptySnapshot` 0x27f34, `snapshot` 0x27f80, `captured` 0x28228, `confirmed` 0x2826c, `restored` 0x282f0 and `TransferStats$Snapshot` field table and age/pending/rate methods. |
| Q | `PacketQueue.offer` 0x1e748 (byte cap at 0x1e772), constructor 0x1e888 (capacity at 0x1e8a2), `PacketQueue$Packet` constructor 0x1e6d8 (timestamp 0x1e706–0x1e71c). |
| M | `RadarView.loadAssets` 0x25490, assets at 0x254a4–0x254d4 and portrait filename check 0x2565a. `onDraw` 0x2570c, stale and layer/rectangle/bitmap setup, layout 0x257a0–0x257fe, rotation 0x25840–0x25896, coordinates 0x259e8–0x25a44, dead/spawn 0x259c0–0x259e4 and 0x25b4a–0x25bee, portraits 0x25cd0/0x25d86. Camp orientation 0x243d4–0x24418 in `RadarScene.apply`. |
| A | `assets/radar/atlas.json` keys and records, PNG IHDR dimensions and archive entries under `assets/radar/heroes/`. |
| G | `CaptureService.run` 0xf1c8, game package 0xf2f8, viewer/uploader setup 0xf908–0xf940, direct gateway 0xf9da–0xf9f2, VPN builder/TUN 0xfa4e–0xfa56, JNI startup 0xfb28. `VpnRouting.create` 0x286a8, `NativeTunnelConfig.create` 0x1d444, `DirectUdpGateway.copy` 0x123bc, `handshake` 0x12420, `inbound` 0x12718, `outbound` 0x1281c. `MirrorGateway.shouldMirror` 0x1cab0, `session` 0x1d0a4, `tcp` 0x1d300. `lib/arm64-v8a/libgojni.so` native package path strings. |
| ST | `ServerStatus.describe` 0x27660 and `preparation` 0x2777c. Worker count read at 0x2785c; `CaptureService.monitorRoom` 0xe95c. |

### Complete atlas key inventory

- **Battle_ (9)**. `Battle_BaoJun`, `Battle_Bg_BloodBg`, `Battle_Bg_MapBaiXian`, `Battle_Bg_MapHuiCheng`, `Battle_Bg_MapRedXian`, `Battle_Bg_YuanBlueGlow`, `Battle_HP_Blue_Ring`, `Battle_HP_Red_Ring`, `Battle_Map_Ding`.
- **Other (14)**. `BianQue_Position`, `enemy`, `enemy_Strengthen`, `FlamingMountains_Circle`, `friend`, `friend_Strengthen`, `Img_light_bar5`, `Juexing_DeathIcon1`, `Juexing_DeathIcon2`, `pvp10_Mask`, `pvp_9_small_door`, `Signal_Normal`, `Wangwei_MiniMap1`, `Wangwei_MiniMap2`.
- **bl_ (9)**. `bl_bgblueHp1`, `bl_bgblueHp2`, `bl_bgredHp1`, `bl_bgredHp2`, `bl_blueHp1`, `bl_blueHp2`, `bl_Hp2`, `bl_redHp1`, `bl_redHp2`.
- **Commander_ (3)**. `Commander_SignalMain_Chetui`, `Commander_SignalMain_Jihe`, `Commander_SignalMain_Jingong`.
- **CountDown (4)**. `CountDown_Baojun`, `CountDown_Zhuzai`, `CountDownBg_Baojun`, `CountDownBg_Zhuzai`.
- **Hero_ (7)**. `Hero_Buff_miaozhun`, `Hero_Buff_Yadianna_Blue`, `Hero_Buff_Yadianna_Green`, `Hero_Buff_Yadianna_Red`, `Hero_Buff_Yao_Blue`, `Hero_Buff_Yao_Red`, `Hero_Dead`.
- **Icon_ (46)**. `Icon_AnYingXianFeng000`, `Icon_BaoXiang_1`, `Icon_Caomuzhiling2`, `Icon_Caomuzhiling`, `Icon_ChuanSongDian1`, `Icon_ChuanSongDian2`, `Icon_ChuanSongKou`, `Icon_CJSH_Trap_2`, `Icon_Dalong2`, `Icon_Dalong2_Dead`, `Icon_Dalong`, `Icon_Dalong_dead`, `Icon_FengBaoXianFeng000`, `Icon_FuHuoGuai`, `Icon_FuHuoGuai_dead`, `Icon_heianbaojun`, `Icon_heianbaojun_Dead`, `Icon_HN2`, `Icon_HN`, `Icon_JiaSuDian`, `Icon_KongTou`, `Icon_liushan_lingjian`, `Icon_MiniMap_SupportCoin`, `Icon_nianshou`, `Icon_ShenShi_1`, `Icon_ShenShi_1_Bg`, `Icon_shiyedaoju`, `Icon_shiyedaoju_Enemy`, `Icon_shiyeguai`, `Icon_shiyeguai_Enemy`, `Icon_SuperXiaolong`, `Icon_SuperXiaolong_Dead`, `Icon_TaoShaBattleNtf`, `Icon_TsBoss`, `Icon_XiaoGuai_1`, `Icon_XiaoGuai_1_2`, `Icon_XiaoGuai_1_Ready`, `Icon_XiaoGuai_2`, `Icon_XiaoGuai_2_Ready`, `Icon_Xiaolong`, `Icon_Xiaolong_Dead`, `Icon_xiaozhuzai`, `Icon_xiaozhuzai_Dead`, `Icon_yuangubaojun`, `Icon_yuangubaojun_Dead`, `Icon_ZhuZaiXianFeng000`.
- **Img_Map_ (58)**. `Img_Map_Anyingxianfeng`, `Img_Map_Base_Green`, `Img_Map_Base_Green_Dying`, `Img_Map_Base_Green_outline`, `Img_Map_Base_Red`, `Img_Map_Base_Red_Dying`, `Img_Map_Base_Red_outline`, `Img_Map_BlueEye`, `Img_Map_BlueLoop`, `Img_Map_BlueLoop_Hp`, `Img_Map_Caomuzhiling_blue`, `Img_Map_Caomuzhiling_red`, `Img_Map_ChaoJiBing_blue`, `Img_Map_ChaoJiBing_red`, `Img_Map_ChaoJiBing_Strengthen_blue`, `Img_Map_ChaoJiBing_Strengthen_red`, `Img_Map_CyanLoop`, `Img_Map_GreenLoop`, `Img_Map_GreenLoop_Hp`, `Img_Map_HaiyueBlue`, `Img_Map_HaiyueRed`, `Img_Map_HuBaoTieQi_blue`, `Img_Map_HuBaoTieQi_red`, `Img_Map_JiGuanZaoWu_Red`, `Img_Map_JiGuanZaoWub_Blue`, `Img_Map_LingBaoZhaoHuan_Blue`, `Img_Map_LingBaoZhaoHuan_Red`, `Img_Map_MaChe_Blue`, `Img_Map_MaChe_Red`, `Img_Map_MuNiuLiuMa_blue`, `Img_Map_MuNiuLiuMa_red`, `Img_Map_PaoChe_blue`, `Img_Map_PaoChe_red`, `Img_Map_PaoChe_Strengthen_blue`, `Img_Map_PaoChe_Strengthen_red`, `Img_Map_PinkLoop`, `Img_Map_RedEye`, `Img_Map_RedLoop`, `Img_Map_RedLoop_Hp`, `Img_Map_RedLoop_OB`, `Img_Map_Strengthen_Blue`, `Img_Map_Strengthen_Red`, `Img_Map_TaoShaLoop02`, `Img_Map_TaoShaLoop03`, `Img_Map_Tower_Supply`, `Img_Map_WhiteLoop`, `Img_Map_WuJun_DuiYou`, `Img_Map_WuJunLoop01`, `Img_Map_WuJunLoop01_2`, `Img_Map_WuJunLoop02`, `Img_Map_WuJunLoop02_2`, `Img_Map_WuJunLoop03`, `Img_Map_WuJunLoop03_2`, `Img_Map_WuJunLoop04`, `Img_Map_WuJunLoop04_2`, `Img_Map_WuJunLoop05`, `Img_Map_WuJunLoop05_2`, `Img_Map_YellowLoop`.
- **img_map_ (2)**. `img_map_bluedie`, `img_map_reddie`.
- **Map (31)**. `Map5467_Img_FaultFragmentBig`, `Map5467_Img_FaultFragmentSmall`, `Map_boom_shenmengxi_blue`, `Map_boom_shenmengxi_red`, `Map_End`, `Map_Machine_Marker_01`, `Map_Machine_Marker_02`, `Map_Machine_Marker_03`, `Map_Machine_Marker_04`, `Map_Marked01`, `Map_Marked02`, `Map_Marked03`, `Map_Marked04`, `Map_Marked05`, `Map_NerYearActivebuff`, `Map_Point_1`, `Map_Point_2`, `Map_ShiYeDaoJu_lamp`, `Map_Skill_Indicator_Normal`, `Map_Skill_Indicator_Red`, `Map_Start`, `Map_Track_chengjisihan_blue`, `Map_Track_chengjisihan_red`, `Map_Track_GongSunLi_blue`, `Map_Track_GongSunLi_red`, `Map_Track_Houyi_blue`, `Map_Track_Houyi_red`, `Map_Track_JuJi_blue`, `Map_Track_Luban_blue`, `Map_Track_Luban_red`, `Map_Track_Mengya_blue`.
- **Mini (43)**. `Mini_Map_CommanderAI_Done`, `Mini_Map_CommanderAI_Reject`, `Mini_Map_DaYuDaDing_Bule`, `Mini_Map_DaYuDaDing_Red`, `Mini_Map_DaYuXiaoDing_Bule`, `Mini_Map_DaYuXiaoDing_Gray_Bule`, `Mini_Map_DaYuXiaoDing_Gray_Red`, `Mini_Map_DaYuXiaoDing_GrayFull_Bule`, `Mini_Map_DaYuXiaoDing_GrayFull_Red`, `Mini_Map_DaYuXiaoDing_Red`, `Mini_Map_DaYuXiaoDingFull_Bule`, `Mini_Map_DaYuXiaoDingFull_Red`, `Minimap9_circle2`, `Minimap9_circle`, `Minimap9Small_circle1`, `Minimap9Small_circle2`, `MiniMap_DaQiao_Portal2`, `MiniMap_DaQiao_Portal`, `MiniMap_FootBall`, `MiniMap_GearBall_Blue`, `MiniMap_GearBall_OutLine`, `MiniMap_GearBall_Red`, `MiniMap_Icon_Dying01_Map`, `MiniMap_Icon_Dying02_Map`, `MiniMap_Icon_Dying03_Map`, `MiniMap_JianTou01`, `MiniMap_JianTou02`, `MiniMap_JianTou03`, `MiniMap_JianTou04`, `MiniMap_JianTou05`, `MiniMap_MarkedDi01_Map`, `MiniMap_MarkedDi02_Map`, `MiniMap_MarkedDi03_Map`, `MiniMap_MarkedDi04_Map`, `MiniMap_MarkedDi05_Map`, `MiniMap_Path_End`, `Minimap_Portaleffects_Appear_03`, `Minimap_Portaleffects_Appear_huan`, `MiniMap_Shouyue_Blue_1`, `MiniMap_Shouyue_Blue_2`, `MiniMap_Shouyue_Red_1`, `MiniMap_Shouyue_Red_2`, `MiniMap_SiWang`.
- **NewStyle_ (42)**. `NewStyle_JGS_Base_Bule`, `NewStyle_JGS_Base_Bule_Dying`, `NewStyle_JGS_Base_Bule_Outline`, `NewStyle_JGS_Base_Red`, `NewStyle_JGS_Base_Red_Dying`, `NewStyle_JGS_Base_Red_Outline`, `NewStyle_JGS_Tower_Bule`, `NewStyle_JGS_Tower_Bule_Dead`, `NewStyle_JGS_Tower_Bule_Dying`, `NewStyle_JGS_Tower_Bule_Outline`, `NewStyle_JGS_Tower_Bule_Shield`, `NewStyle_JGS_Tower_Bule_Shield_Dying`, `NewStyle_JGS_Tower_Bule_Shield_Outline`, `NewStyle_JGS_Tower_Capture_Bule`, `NewStyle_JGS_Tower_Capture_Red`, `NewStyle_JGS_Tower_Red`, `NewStyle_JGS_Tower_Red_Dying`, `NewStyle_JGS_Tower_Red_Outline`, `NewStyle_JGS_Tower_Red_Shield`, `NewStyle_JGS_Tower_Red_Shield_Dying`, `NewStyle_JGS_Tower_Red_Shield_Outline`, `NewStyle_JGS_Tower_RedHp`, `NewStyle_MD_Base_Bule`, `NewStyle_MD_Base_Bule_Dying`, `NewStyle_MD_Base_Bule_Outline`, `NewStyle_MD_Base_Red`, `NewStyle_MD_Base_Red_Dying`, `NewStyle_MD_Base_Red_Outline`, `NewStyle_MD_Tower_BlueHp`, `NewStyle_MD_Tower_Bule`, `NewStyle_MD_Tower_Bule_Dead`, `NewStyle_MD_Tower_Bule_Dying`, `NewStyle_MD_Tower_Bule_Outline`, `NewStyle_MD_Tower_Bule_Shield`, `NewStyle_MD_Tower_Bule_Shield_Dying`, `NewStyle_MD_Tower_Bule_Shield_Outline`, `NewStyle_MD_Tower_Red`, `NewStyle_MD_Tower_Red_Dying`, `NewStyle_MD_Tower_Red_Outline`, `NewStyle_MD_Tower_Red_Shield`, `NewStyle_MD_Tower_Red_Shield_Dying`, `NewStyle_MD_Tower_Red_Shield_Outline`.

Portrait filename stems [A]. 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 144, 146, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 159, 162, 163, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 182, 183, 184, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 312, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 513, 514, 515, 517, 518, 519, 521, 522, 523, 524, 525, 527, 528, 529, 531, 533, 534, 536, 537, 538, 540, 542, 544, 545, 547, 548, 549, 550, 558, 563, 564, 577, 581, 582, 583, 584, 585, 631, 632, 635, 640, 646.

## Tools and limits

Read the source APK in place with `unzip -Z1`, `unzip -p` and selective archive extraction into `/tmp`. Used `sha256sum` to identify the input bytes and GNU `strings` (`-a` for DEX/native binary and `-el` for manifest cross-checks), `rg` and shell text filters. Wrote a Python 3 standard-library DEX parser for string/type/prototype/class/method/field tables and class data, plus a lightweight instruction walker resolving calls, field accesses, strings, branches and constants in the inspected code. Used Python `struct` for binary manifest root attributes and PNG IHDR dimensions, and `json` and path enumeration for atlas and portrait inventories.

`apktool`, `jadx` and `dex2jar` were unavailable on PATH. The offline install attempt `PIP_DISABLE_PIP_VERSION_CHECK=1 python3 -m pip install --no-index --target /tmp/radar-ref/deps androguard` failed with “No matching distribution found for androguard.” The pip cache listed no locally built wheels. No download was attempted. Native analysis was limited to strings and the Java-to-JNI boundary. No server was contacted, the APK was never installed or executed, and no APK copy was made.
