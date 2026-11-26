# Phase 2 · Server design

A future phone client uses Android's TUN interface to observe selected UDP
traffic while continuing to forward the original flow. It discovers the
upload and snapshot paths from its configured server, posts bounded batches
of UDP payloads and polls snapshots for display. The deployment target is
`39.96.60.127:18081` on Alibaba Cloud Beijing. The server defaults to bind
`0.0.0.0` and port `18081`. Both settings remain configurable through YAML
or environment overrides. See [DEPLOY.md](DEPLOY.md) for the operator runbook.
The API below defines a new client contract.

The HTTP handler validates and decodes a complete batch before invoking the
parser. `Parser.parse` accepts a sequence of datagrams and returns a complete
list of entities. The Honor of Kings stub logs the number of unknown
datagrams at INFO and each decoded length at DEBUG, then returns an empty
list. The server publishes the complete result atomically, incrementing a
revision. Parser calls and publication are serialized. Parser failures keep
the previous snapshot. Payloads are processed in memory and are neither
persisted nor logged.

## HTTP contract v1

| Request | Successful response |
| --- | --- |
| `GET /health` | `200 {"status":"ok"}` |
| `GET /api/client/app-config` | `200 {"protocol_version":1,"upload_path":"/api/client/upload","snapshot_path":"/snapshot","snapshot_header":"X-Kite-Snapshot"}` |
| `GET /api/client/nodes` | `200 {"nodes":[]}` by default. Configured nodes have string fields `id` and `base_url` (HTTP or HTTPS). Paths in app config are relative to the selected server's origin. |
| `POST /api/client/upload` | `200 {"accepted":1,"revision":1}` for one valid datagram on a fresh server. Acceptance means the parser received the batch. |
| `GET /snapshot` | `200 {"revision":0,"entities":[]}` before the first accepted upload. The response sends `X-Kite-Snapshot: 0` at startup and the current decimal revision thereafter. |

Send uploads as UTF-8 `application/json` with a content length. The request
object contains only `datagrams`, an array of 1–256 records. Each record
contains exactly the fields shown below.

```json
{"datagrams":[{"direction":"outbound","payload_b64":"AAEC"}]}
```

`direction` is `outbound` or `inbound`, relative to the phone.
`payload_b64` is standard padded Base64 of the UDP payload with decoded
length 0–65,527 bytes. The entire HTTP body may be at most 1 MiB. Upload
failures return an `error` string with status 400 (invalid input), 411
(missing length), 413 (body too large), 415 (wrong media type), or 500
(parser failure). Unknown paths return 404 and unsupported methods return
405 with an `Allow` header.

Future entity records use `{"id":"entity-id","x":0.0,"y":0.0}`, where
`id` is a string and the coordinates are finite numbers in the parser's
documented coordinate system. The stub cannot derive any of these values.

Snapshots are in-memory, process-wide and non-cacheable. Restart resets the
revision. Upload retries are treated as new batches. Use one logical capture
stream per server instance. The header name matches the supplied APK
observation. The numeric value and response placement are v1 design
choices. Legacy header semantics and APK interoperability are unverified.
