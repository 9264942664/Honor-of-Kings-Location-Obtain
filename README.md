# Honor of Kings Location · Server prototype

This server accepts UDP payload batches over HTTP and publishes snapshots.
Its Honor of Kings parser is a stub. Every snapshot currently contains
an empty entity array. The server requires Python 3.10+ and PyYAML.

## Run locally

From the project root, use a virtual environment outside the project tree.

```sh
python3 -m venv /tmp/hok-radar-venv
/tmp/hok-radar-venv/bin/python -m pip install -r server/requirements.txt
RADAR_CONFIG=server/config.yaml /tmp/hok-radar-venv/bin/python server/main.py
```

If PyYAML is already installed for your Python, run
`RADAR_CONFIG=server/config.yaml python3 server/main.py`.

```sh
curl -fsS http://localhost:18081/health
curl -fsS http://localhost:18081/api/client/nodes
curl -fsS -i http://localhost:18081/snapshot
curl -fsS http://localhost:18081/api/client/upload \
  -H 'Content-Type: application/json' \
  --data '{"datagrams":[{"direction":"outbound","payload_b64":"AAEC"}]}'
```

Without `RADAR_CONFIG`, the server reads `config.yaml` from the working
directory if it exists. The built-in defaults are bind `0.0.0.0`, port
`18081` and an empty node list. `RADAR_BIND`, `RADAR_PORT` and
`RADAR_NODES_JSON` override the corresponding YAML values. Each advertised
node uses an `id` and an HTTP or HTTPS origin in `base_url`.

See [LEARNING.md](LEARNING.md) for the reference analysis,
[DESIGN.md](DESIGN.md) for the wire contract,
[DEPLOY.md](DEPLOY.md) for Ubuntu deployment and
[SUMMARY.md](SUMMARY.md) for local verification.
