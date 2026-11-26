# Deliverables and verification

## Files created

| File | Purpose |
| --- | --- |
| `LEARNING.md` | Upstream research, supplied APK observations and evidence needed for unresolved protocols |
| `DESIGN.md` | Phone/server architecture and v1 JSON and header contracts |
| `README.md` | Local startup, configuration and example requests |
| `DEPLOY.md` | Ubuntu 24.04 installation and operation |
| `server/main.py` | HTTP server, configuration loader, parser interface and Honor of Kings stub |
| `server/config.yaml` | Default bind, port and node list |
| `server/requirements.txt` | PyYAML dependency for local environments |
| `server/hok-radar.service` | systemd unit |
| `SUMMARY.md` | File inventory and test results |
| `CHANGELOG.md` | Versioned milestones and verification history |

## Versioning / rollback

[CHANGELOG.md](CHANGELOG.md) records each increment as a dated milestone.
Keep `honor-of-kings-location/` clean and ready for the operator to push to
GitHub commit-by-commit, with one commit per version. Those separate commits
provide rollback points. On a shared branch, revert the relevant commit
to roll back its changes while preserving history. The milestone entries
describe the file history. Git rollback points exist once the corresponding
commits have been made.

## Test results

Python was selected because Go was unavailable and the toolchain
download failed through the workspace proxy. The Python source compiled.
YAML defaults and environment overrides for the bind, port and node list
passed. `systemd-analyze verify server/hok-radar.service` exited zero and
reported diagnostics for three unrelated host timers. The unit was
verified without installing or starting it.

The local server startup printed
`Startup failed: [Errno 1] Operation not permitted`. The execution
sandbox denied creation of TCP and Unix sockets. Each requested
`curl` check against `http://localhost:18081` returned exit code 7
with no HTTP response.

```text
/health
curl: (7) Failed to connect to localhost port 18081 after 0 ms: Couldn't connect to server
/api/client/nodes
curl: (7) Failed to connect to localhost port 18081 after 0 ms: Couldn't connect to server
/snapshot
curl: (7) Failed to connect to localhost port 18081 after 0 ms: Couldn't connect to server
```

Raw HTTP requests passed through the production handler using an
in-memory connection. These are the observed responses.

| Request | Status | Response body | X-Kite-Snapshot |
| --- | --- | --- | --- |
| GET /health | 200 | `{"status":"ok"}` | |
| GET /api/client/nodes | 200 | `{"nodes":[]}` | |
| GET /api/client/app-config | 200 | `{"protocol_version":1,"upload_path":"/api/client/upload","snapshot_path":"/snapshot","snapshot_header":"X-Kite-Snapshot"}` | |
| GET /snapshot before upload | 200 | `{"revision":0,"entities":[]}` | `0` |
| POST /api/client/upload with one synthetic datagram | 200 | `{"accepted":1,"revision":1}` | |
| POST /api/client/upload with invalid Base64 | 400 | `{"error":"invalid datagram batch"}` | |
| GET /snapshot after both upload attempts | 200 | `{"revision":1,"entities":[]}` | `1` |

The stub logged `Received 1 unknown Honor of Kings datagrams`.
Live socket and deployment verification require a runtime that permits
network listeners. APK interoperability and game decoding remain open.

### v0.3 verification · 2026-11-26

- Python compilation passed. YAML defaults and the `RADAR_BIND`,
  `RADAR_PORT`, and `RADAR_NODES_JSON` overrides passed.
- In-memory requests to the production handler returned 200 for
  `GET /health`, `GET /api/client/nodes`, `GET /api/client/app-config`,
  `GET /snapshot` and a valid `POST /api/client/upload`. A malformed
  Base64 upload returned 400. The valid upload accepted one synthetic
  datagram. The snapshot body and `X-Kite-Snapshot` header moved from
  revision 0 to 1, then stayed at 1 after the rejected upload.
- `systemd-analyze verify server/hok-radar.service` exited zero and
  reported diagnostics for the same three unrelated host timers.
- Deployment shell syntax and the contents of the three-file release
  archive passed local checks.
- Local startup failed with `[Errno 1] Operation not permitted` during
  socket creation. Local `curl` to `http://localhost:18081/health`
  returned exit 7. The Beijing health checks are pending operator deployment.
