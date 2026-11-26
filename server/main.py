"""HTTP intake and in-memory snapshots for one capture stream."""

import base64
import binascii
import json
import logging
import os
import re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Protocol, Sequence, TypedDict
from urllib.parse import urlsplit

import yaml


UPLOAD_PATH = "/api/client/upload"
SNAPSHOT_PATH = "/snapshot"
SNAPSHOT_HEADER = "X-Kite-Snapshot"
MAX_BODY = 1024 * 1024


@dataclass(frozen=True)
class Datagram:
    direction: str
    payload: bytes


class Entity(TypedDict):
    id: str
    x: float
    y: float


class Parser(Protocol):
    def parse(self, datagrams: Sequence[Datagram]) -> list[Entity]: ...


class HonorOfKingsParser:
    def parse(self, datagrams: Sequence[Datagram]) -> list[Entity]:
        logging.info("Received %d unknown Honor of Kings datagrams", len(datagrams))
        for datagram in datagrams:
            logging.debug("Unknown datagram: %s, %d bytes",
                          datagram.direction, len(datagram.payload))
        return []


class Snapshots:
    def __init__(self, parser: Parser):
        self.parser = parser
        self.lock = Lock()
        self.current = {"revision": 0, "entities": []}

    def read(self):
        with self.lock:
            return self.current

    def ingest(self, datagrams):
        with self.lock:
            entities = self.parser.parse(datagrams)
            revision = self.current["revision"] + 1
            self.current = {"revision": revision, "entities": entities}
            return revision


def load_config():
    explicit_path = os.getenv("RADAR_CONFIG")
    path = Path(explicit_path or "config.yaml")
    config = {}
    if explicit_path or path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        config = {} if loaded is None else loaded
    if not isinstance(config, dict) or config.keys() - {"bind", "port", "nodes"}:
        raise ValueError("config must be a mapping with bind, port and/or nodes")
    bind = os.getenv("RADAR_BIND", config.get("bind", "0.0.0.0"))
    port = os.getenv("RADAR_PORT", config.get("port", 18081))
    nodes = config.get("nodes", [])
    env_nodes = os.getenv("RADAR_NODES_JSON")
    if env_nodes is not None:
        nodes = json.loads(env_nodes)
    if not isinstance(bind, str) or not bind.strip():
        raise ValueError("bind must be a nonempty string")
    if not re.fullmatch(r"[0-9]{1,5}", str(port)) or not 1 <= int(port) <= 65535:
        raise ValueError("port must be an integer from 1 to 65535")
    if not isinstance(nodes, list):
        raise ValueError("nodes must be an array")
    ids = set()
    for node in nodes:
        if (not isinstance(node, dict) or node.keys() != {"id", "base_url"}
                or any(not isinstance(value, str) or not value.strip()
                       for value in node.values())):
            raise ValueError("each node needs nonempty id and base_url strings")
        url = urlsplit(node["base_url"])
        if (url.scheme not in ("http", "https") or not url.hostname
                or url.username is not None or url.path not in ("", "/")
                or url.query or url.fragment or url.port == 0):
            raise ValueError("node base_url must be an HTTP or HTTPS origin")
        if node["id"] in ids:
            raise ValueError("node IDs must be unique")
        ids.add(node["id"])
    return bind, int(port), nodes


def decode_batch(body):
    request = json.loads(body.decode("utf-8"))
    if not isinstance(request, dict) or request.keys() != {"datagrams"}:
        raise ValueError("expected an object containing only datagrams")
    records = request["datagrams"]
    if not isinstance(records, list) or not 1 <= len(records) <= 256:
        raise ValueError("expected 1 to 256 datagrams")
    datagrams = []
    for record in records:
        if not isinstance(record, dict) or record.keys() != {"direction", "payload_b64"}:
            raise ValueError("a datagram requires direction and payload_b64")
        direction = record["direction"]
        payload_b64 = record["payload_b64"]
        if direction not in ("outbound", "inbound") or not isinstance(payload_b64, str):
            raise ValueError("invalid direction or payload_b64")
        try:
            payload = base64.b64decode(payload_b64, validate=True)
        except (ValueError, binascii.Error):
            raise ValueError("invalid Base64 payload") from None
        if base64.b64encode(payload).decode("ascii") != payload_b64:
            raise ValueError("expected standard padded Base64")
        if len(payload) > 65527:
            raise ValueError("decoded datagram exceeds 65527 bytes")
        datagrams.append(Datagram(direction, payload))
    return datagrams


class Handler(BaseHTTPRequestHandler):
    routes = {
        "/health": "GET",
        "/api/client/app-config": "GET",
        "/api/client/nodes": "GET",
        SNAPSHOT_PATH: "GET",
        UPLOAD_PATH: "POST",
    }

    def setup(self):
        self.request.settimeout(10)
        super().setup()

    def log_message(self, format, *args):
        # Log batch outcomes through the parser. Avoid logging request paths.
        pass

    def respond(self, status, data, headers=None):
        body = json.dumps(data, allow_nan=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def handle_api(self):
        path = self.path.partition("?")[0]
        method = self.routes.get(path)
        if method is None:
            return self.respond(404, {"error": "unknown path"})
        if self.command != method:
            return self.respond(405, {"error": "method not allowed"}, {"Allow": method})
        if path == "/health":
            return self.respond(200, {"status": "ok"})
        if path == "/api/client/app-config":
            return self.respond(200, {
                "protocol_version": 1,
                "upload_path": UPLOAD_PATH,
                "snapshot_path": SNAPSHOT_PATH,
                "snapshot_header": SNAPSHOT_HEADER,
            })
        if path == "/api/client/nodes":
            return self.respond(200, {"nodes": self.server.nodes})
        if path == SNAPSHOT_PATH:
            snapshot = self.server.snapshots.read()
            return self.respond(200, snapshot, {SNAPSHOT_HEADER: str(snapshot["revision"])})
        return self.upload()

    do_GET = do_POST = do_HEAD = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = handle_api

    def upload(self):
        if self.headers.get("Transfer-Encoding") is not None:
            return self.respond(400, {"error": "transfer encoding is unsupported"})
        lengths = self.headers.get_all("Content-Length", [])
        if not lengths:
            return self.respond(411, {"error": "Content-Length is required"})
        if len(lengths) != 1 or not re.fullmatch(r"[0-9]+", lengths[0]):
            return self.respond(400, {"error": "invalid Content-Length"})
        digits = lengths[0].lstrip("0") or "0"
        if len(digits) > 7 or int(digits) > MAX_BODY:
            return self.respond(413, {"error": "body exceeds 1 MiB"})
        if self.headers.get_content_type() != "application/json":
            return self.respond(415, {"error": "expected application/json"})
        size = int(digits)
        try:
            body = self.rfile.read(size)
            if len(body) != size:
                raise ValueError("incomplete request body")
            datagrams = decode_batch(body)
        except (ValueError, RecursionError, TimeoutError):
            return self.respond(400, {"error": "invalid datagram batch"})
        try:
            revision = self.server.snapshots.ingest(datagrams)
        except Exception as error:
            logging.error("Parser failed (%s)", type(error).__name__)
            return self.respond(500, {"error": "parser failed"})
        return self.respond(200, {"accepted": len(datagrams), "revision": revision})


class RadarServer(ThreadingHTTPServer):
    def __init__(self, address, nodes, parser: Parser):
        self.nodes = nodes
        self.snapshots = Snapshots(parser)
        super().__init__(address, Handler)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        bind, port, nodes = load_config()
        with RadarServer((bind, port), nodes, HonorOfKingsParser()) as server:
            logging.info("Listening on %s:%d", bind, port)
            server.serve_forever()
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"Startup failed: {error}") from None
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
