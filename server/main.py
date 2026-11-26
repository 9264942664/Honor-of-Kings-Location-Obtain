"""HTTP intake, persistent captures and snapshots for one capture stream."""

import base64
import binascii
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from tempfile import TemporaryFile
from typing import Protocol, Sequence, TypedDict
from urllib.parse import urlsplit

import yaml


UPLOAD_PATH = "/api/client/upload"
SNAPSHOT_PATH = "/snapshot"
SNAPSHOT_HEADER = "X-Kite-Snapshot"
MAX_BODY = 1024 * 1024
CAPTURES_PATH = "/api/captures"
CAPTURE_NAME = re.compile(r"captures-([0-9]{4}-[0-9]{2}-[0-9]{2})(?:-([1-9][0-9]*))?\.jsonl")


class CaptureStore:
    def __init__(self, directory, max_total_bytes, max_file_bytes):
        self.directory = Path(directory)
        self.max_total_bytes = max_total_bytes
        self.max_file_bytes = max_file_bytes
        self.lock = Lock()
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            with TemporaryFile(dir=self.directory):
                pass
            self.trim(self.files())
        except OSError as error:
            raise OSError(f"Cannot initialize capture directory {self.directory}: {error}") from error

    def files(self):
        captures = {}
        for path in self.directory.iterdir():
            if CAPTURE_NAME.fullmatch(path.name) and not path.is_symlink() and path.is_file():
                captures[path] = path.stat()
        return captures

    @staticmethod
    def order(path):
        day, suffix = CAPTURE_NAME.fullmatch(path.name).groups()
        return day, int(suffix or 0)

    def trim(self, captures, protected=()):
        total = sum(info.st_size for info in captures.values())
        expired = []
        for path in sorted(captures, key=self.order):
            if total <= self.max_total_bytes:
                break
            if path in protected:
                raise OSError("Retention limit would immediately expire an uploaded capture")
            expired.append(path)
            total -= captures[path].st_size
        for path in expired:
            path.unlink()

    def append(self, datagrams, revision, received):
        lines = [(json.dumps({
            "ts": received.isoformat(),
            "revision": revision,
            "direction": datagram.direction,
            "payload_b64": base64.b64encode(datagram.payload).decode("ascii"),
        }, separators=(",", ":")) + "\n").encode() for datagram in datagrams]
        batch_size = sum(map(len, lines))
        if batch_size > self.max_total_bytes or max(map(len, lines)) > self.max_file_bytes:
            raise OSError("Upload exceeds configured capture capacity")

        day = received.date().isoformat()
        with self.lock:
            captures = self.files()
            suffix = max((index for date, index in map(self.order, captures) if date == day),
                         default=0)
            path = self.path_for(day, suffix)
            size = captures[path].st_size if path in captures else 0
            if size + batch_size > self.max_total_bytes:
                suffix += 1
                path = self.path_for(day, suffix)
                size = 0
            pending = {}
            for line in lines:
                if size + len(line) > min(self.max_file_bytes, self.max_total_bytes):
                    suffix += 1
                    path = self.path_for(day, suffix)
                    size = 0
                pending.setdefault(path, bytearray()).extend(line)
                size += len(line)

            written = {}
            try:
                for path, data in pending.items():
                    original = captures.get(path)
                    flags = os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW
                    if original is None:
                        flags |= os.O_CREAT | os.O_EXCL
                    with os.fdopen(os.open(path, flags, 0o600), "ab") as output:
                        written[path] = original
                        output.write(data)
                        output.flush()
                        os.fsync(output.fileno())
                    captures[path] = path.stat()
                self.trim(captures, written)
            except OSError:
                for path, original in reversed(written.items()):
                    try:
                        if original is None:
                            path.unlink()
                        else:
                            with path.open("r+b") as output:
                                output.truncate(original.st_size)
                    except OSError:
                        logging.exception("Could not roll back capture %s", path)
                raise

    def path_for(self, day, suffix):
        part = f"-{suffix}" if suffix else ""
        return self.directory / f"captures-{day}{part}.jsonl"

    def list(self):
        with self.lock:
            return [
                {"name": path.name, "size_bytes": info.st_size,
                 "modified": datetime.fromtimestamp(info.st_mtime, timezone.utc).isoformat()}
                for path, info in sorted(self.files().items())
            ]

    def open(self, name):
        with self.lock:
            path = self.directory / name
            if path.is_symlink() or not path.is_file():
                raise FileNotFoundError(name)
            capture = path.open("rb")
            return capture, os.fstat(capture.fileno()).st_size


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
    def __init__(self, parser: Parser, captures: CaptureStore):
        self.parser = parser
        self.captures = captures
        self.lock = Lock()
        self.current = {"revision": 0, "entities": []}

    def read(self):
        with self.lock:
            return self.current

    def ingest(self, datagrams, received):
        with self.lock:
            try:
                entities = self.parser.parse(datagrams)
            except Exception as error:
                raise RuntimeError("parser failed") from error
            revision = self.current["revision"] + 1
            self.captures.append(datagrams, revision, received)
            self.current = {"revision": revision, "entities": entities}
            return revision


def load_config():
    explicit_path = os.getenv("RADAR_CONFIG")
    path = Path(explicit_path or "config.yaml")
    config = {}
    if explicit_path or path.exists():
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        config = {} if loaded is None else loaded
    keys = {"bind", "port", "nodes", "data_dir", "max_total_bytes", "max_file_bytes"}
    if not isinstance(config, dict) or config.keys() - keys:
        raise ValueError(f"config must be a mapping with keys from {', '.join(sorted(keys))}")
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
    data_dir = os.getenv("RADAR_DATA_DIR", config.get("data_dir", "/var/lib/hok-radar"))
    if not isinstance(data_dir, str) or not data_dir.strip():
        raise ValueError("data_dir must be a nonempty string")
    limits = []
    for key, default in (("max_total_bytes", 524288000), ("max_file_bytes", 104857600)):
        value = os.getenv(f"RADAR_{key.upper()}", config.get(key, default))
        if not re.fullmatch(r"[0-9]+", str(value)) or int(value) < 1:
            raise ValueError(f"{key} must be a positive integer")
        limits.append(int(value))
    return bind, int(port), nodes, data_dir, *limits


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
        CAPTURES_PATH: "GET",
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
        capture_name = path.removeprefix(CAPTURES_PATH + "/")
        if CAPTURE_NAME.fullmatch(capture_name) and path.startswith(CAPTURES_PATH + "/"):
            method = "GET"
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
        if path == CAPTURES_PATH:
            try:
                captures = self.server.captures.list()
            except OSError:
                logging.exception("Could not list capture files")
                return self.respond(500, {"error": "capture list failed"})
            return self.respond(200, {"captures": captures})
        if method == "GET":
            return self.download(capture_name)
        return self.upload()

    do_GET = do_POST = do_HEAD = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = handle_api

    def __getattr__(self, name):
        # BaseHTTPRequestHandler returns 501 for unknown methods by default.
        if name.startswith("do_"):
            path = self.path.partition("?")[0]
            if path == CAPTURES_PATH or path.startswith(CAPTURES_PATH + "/"):
                return self.handle_api
        raise AttributeError(name)

    def download(self, name):
        try:
            capture, remaining = self.server.captures.open(name)
        except FileNotFoundError:
            return self.respond(404, {"error": "capture not found"})
        except OSError:
            logging.exception("Could not open capture %s", name)
            return self.respond(500, {"error": "capture download failed"})
        with capture:
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson")
            self.send_header("Content-Length", str(remaining))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            while remaining:
                block = capture.read(min(remaining, 64 * 1024))
                if not block:
                    break
                self.wfile.write(block)
                remaining -= len(block)

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
            received = datetime.now(timezone.utc)
            if len(body) != size:
                raise ValueError("incomplete request body")
            datagrams = decode_batch(body)
        except (ValueError, RecursionError, TimeoutError):
            return self.respond(400, {"error": "invalid datagram batch"})
        try:
            revision = self.server.snapshots.ingest(datagrams, received)
        except OSError:
            logging.exception("Could not persist datagram batch")
            return self.respond(500, {"error": "capture write failed"})
        except RuntimeError as error:
            logging.error("Parser failed (%s)", type(error.__cause__).__name__)
            return self.respond(500, {"error": "parser failed"})
        return self.respond(200, {"accepted": len(datagrams), "revision": revision})


class RadarServer(ThreadingHTTPServer):
    def __init__(self, address, nodes, parser: Parser, captures: CaptureStore):
        self.nodes = nodes
        self.captures = captures
        self.snapshots = Snapshots(parser, captures)
        super().__init__(address, Handler)


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        bind, port, nodes, data_dir, max_total_bytes, max_file_bytes = load_config()
        captures = CaptureStore(data_dir, max_total_bytes, max_file_bytes)
        with RadarServer((bind, port), nodes, HonorOfKingsParser(), captures) as server:
            logging.info("Listening on %s:%d", bind, port)
            server.serve_forever()
    except (OSError, ValueError, yaml.YAMLError) as error:
        raise SystemExit(f"Startup failed: {error}") from None
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
