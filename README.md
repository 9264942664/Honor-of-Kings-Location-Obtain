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

## PCAP analysis tool

Use the analyzer on a classic PCAP from a phone running PCAPdroid or Kite
Capture to identify traffic patterns for the location radar. The working
assumption is that Honor of Kings uses UDP for real-time position data and
TCP for login and matchmaking. The analyzer and synthetic capture generator
require Python 3.10+ and use only its standard library.

```sh
python3 tools/analyze_pcap.py phone.pcap --local-ip 10.0.0.2
python3 tools/analyze_pcap.py phone.pcap --json --top 20
python3 tools/gen_test_pcap.py synthetic.pcap
python3 tools/analyze_pcap.py synthetic.pcap
```

- **Summary** gives the record count, captured frame bytes, earliest and
  latest UTC timestamps, elapsed time, malformed or skipped record count, and
  packet and byte shares for UDP, TCP, and other. Skipped records count toward
  other. A truncated record contributes only the frame bytes actually present.
- **Top remote IPs** ranks peers by packets and by bytes. Set `--local-ip`
  to the phone's IP when known. By default the tool uses the most frequent
  source IP. Only traffic between the local IP and a different IP enters these
  rankings. Use `--top N` to change the default limit of 10.
- **Top remote endpoints** ranks the same peers by IP and TCP or UDP port in
  both directions, using the same limit.
- **Per-flow stats** groups traffic by directional protocol, source IP and
  port, and destination IP and port. Flows are ranked by packet count and
  include captured packet size statistics, bytes, duration, and packets per
  second. The display limit is at least 10. Rate is packet count divided by
  the interval between the earliest and latest packets in that flow, or zero
  for a zero-duration flow. Non-initial fragments with no transport ports
  contribute to IP and protocol totals but have no endpoint or 5-tuple.
- **Likely game-server flows** ranks matching flows by packets per second.
  The rule is: UDP flows with >= 50 packets AND >= 10 packets/sec sustained
  (pps computed over the flow's own duration) AND duration >= 2 seconds.
  The label is **heuristic, unvalidated on real Honor of Kings traffic**.
  Validation requires a real game capture.
- **Per-second summary** counts packets, bytes, UDP packets, and TCP packets
  for each elapsed second from the earliest timestamp. A run of more than
  3,600 empty seconds appears as an inclusive range of zero counts. Records
  without a usable timestamp contribute to the overall totals only.

Use `--json` to get the same six sections as a single JSON object.
The synthetic generator prints its expected counts, sizes, and rates. It
schedules packets at fixed intervals in 4-, 10-, and 2-second windows, with
the last packet one interval before each window ends, and appends one
deliberately truncated record.
