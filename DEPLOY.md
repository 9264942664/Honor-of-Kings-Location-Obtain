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
