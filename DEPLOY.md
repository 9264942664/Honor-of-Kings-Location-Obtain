# Deploy to Alibaba Cloud Beijing

The target is `39.96.60.127:18081` on Ubuntu 24.04.5. The operator connects
as `root` to hostname `iZ2ze8ngot14yxswvuff97Z` using
`bash ~/workspace/vps-access/ssh-beijing.sh 'command'`.
Ubuntu supplies PyYAML in its `python3-yaml` package.
[Ubuntu package details](https://packages.ubuntu.com/noble/python3-yaml)

From the local project root, run the following. The archive contains only
the three deployment files. Its Base64 encoding lets the wrapper carry it
in the remote command. An existing config is preserved on redeploy.

```sh
hok_release=$(tar -C server -czf - main.py config.yaml hok-radar.service | base64 | tr -d '\n')
bash ~/workspace/vps-access/ssh-beijing.sh "
set -eu
apt-get update
apt-get install -y python3 python3-yaml curl
stage=\$(mktemp -d)
trap 'rm -rf \"\$stage\"' EXIT
printf '%s' '$hok_release' | base64 -d | tar -xz -C \"\$stage\"
install -d -m 0755 /opt/hok-radar /etc/hok-radar
install -m 0644 \"\$stage/main.py\" /opt/hok-radar/main.py
if [ ! -e /etc/hok-radar/config.yaml ]; then
    install -m 0644 \"\$stage/config.yaml\" /etc/hok-radar/config.yaml
fi
install -m 0644 \"\$stage/hok-radar.service\" /etc/systemd/system/hok-radar.service
systemctl daemon-reload
systemctl enable hok-radar.service
systemctl restart hok-radar.service
"
```

Check the service from Beijing through the wrapper, then check the public
address from the operator machine. The public check requires TCP 18081
reachability from that machine.

```sh
bash ~/workspace/vps-access/ssh-beijing.sh 'curl -fsS http://127.0.0.1:18081/health'
curl -fsS http://39.96.60.127:18081/health
bash ~/workspace/vps-access/ssh-beijing.sh 'journalctl -u hok-radar.service -n 50 --no-pager'
```

Both health checks should return `{"status":"ok"}`. Edit
`/etc/hok-radar/config.yaml` to change the default `bind: 0.0.0.0`,
`port: 18081`, or node list. The unit points `RADAR_CONFIG` at that file.
Set `RADAR_BIND`, `RADAR_PORT`, or `RADAR_NODES_JSON` in a systemd drop-in
to override the corresponding YAML values. Adjust the health URLs for a
custom bind or port.

Set each advertised node's `base_url` to the origin assigned to your
deployment. The prototype serves plain HTTP and shares one snapshot for
all callers. For remote phone access, place it behind a private network
or an authenticated HTTPS reverse proxy. For the proxy setup, set
`bind: localhost` and keep the backend port private.

Apply later YAML changes through the wrapper with
`systemctl restart hok-radar.service`. After a drop-in change, run
`systemctl daemon-reload` before restarting. Use
`systemctl status hok-radar.service` to inspect startup failures.

On the Beijing server, the service stores uploaded datagrams in
`/var/lib/hok-radar`. The systemd unit uses `StateDirectory=hok-radar` to
make this path writable under `DynamicUser=yes` and `ProtectSystem=strict`.
The server creates the directory on startup and fails startup if it cannot
write there. Set `data_dir` or `RADAR_DATA_DIR` to override the path. A custom
path must also be writable within the unit's filesystem protections.

Files use append-only JSON Lines (JSONL), with one record per datagram.
Each record contains the UTC receipt timestamp `ts`, the batch's snapshot
`revision`, the `direction`, and the original standard padded Base64
`payload_b64`. Uploads flush and sync capture data before returning success.
Snapshot revisions restart at zero when the process restarts.

Each UTC day starts a file named `captures-YYYY-MM-DD.jsonl`. When a file
would exceed 100 MiB, the service rolls to `captures-YYYY-MM-DD-N.jsonl`,
starting at suffix 1. The default total cap for capture files is 500 MiB.
The server deletes whole capture files in order from the oldest to reclaim
space. Override the defaults with `max_file_bytes` (104857600) and
`max_total_bytes` (524288000), or with `RADAR_MAX_FILE_BYTES` and
`RADAR_MAX_TOTAL_BYTES`.

`GET /api/captures` lists capture names, byte sizes and UTC modification
timestamps. `GET /api/captures/<name>` returns the capture as
`application/x-ndjson` with a `Content-Length` header. Use a filename
from the listing in the download command.

```sh
bash ~/workspace/vps-access/ssh-beijing.sh 'curl -fsS http://127.0.0.1:18081/api/captures'
bash ~/workspace/vps-access/ssh-beijing.sh 'curl -fsS http://127.0.0.1:18081/api/captures/captures-2026-11-26.jsonl'
```
