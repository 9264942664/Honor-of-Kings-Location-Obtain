"""Offline Honor of Kings flow hypothesis from one raw IPv4 capture."""

import argparse
from collections import Counter
from dataclasses import dataclass
from ipaddress import IPv4Address
import struct
from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from .main import Datagram, Entity

PHONE_IP = "10.215.173.1"
PRIME_IP = "180.102.99.167"
PRIME_PORT = 10214
PHONE_PORT = 48605


@dataclass(frozen=True)
class CapturedDatagram:
    direction: str
    payload: bytes


def raw_ipv4_records(path):
    """Yield elapsed seconds, captured length, original length and raw IP bytes."""
    with open(path, "rb") as capture:
        header = capture.read(24)
        formats = {
            bytes.fromhex("d4c3b2a1"): ("<", 10**6),
            bytes.fromhex("a1b2c3d4"): (">", 10**6),
            bytes.fromhex("4d3cb2a1"): ("<", 10**9),
            bytes.fromhex("a1b23c4d"): (">", 10**9),
        }
        if len(header) != 24 or header[:4] not in formats:
            raise ValueError("Expected a classic PCAP")
        endian, scale = formats[header[:4]]
        snaplen, network = struct.unpack_from(endian + "II", header, 16)
        if network & 0xffff != 101:
            raise ValueError("Expected raw IP link type 101")
        origin = None
        while record := capture.read(16):
            seconds, fraction, captured, original = struct.unpack(endian + "IIII", record)
            if captured > min(snaplen, original, 16 * 1024 * 1024) or fraction >= scale:
                raise ValueError("Invalid PCAP record")
            packet = capture.read(captured)
            if len(packet) != captured:
                raise ValueError("Truncated PCAP record")
            ticks = seconds * scale + fraction
            if origin is None:
                origin = ticks
            yield (ticks - origin) / scale, captured, original, packet


def ipv4_transport(packet):
    """Return complete unfragmented IPv4 transport bytes and endpoint metadata."""
    if len(packet) < 20 or packet[0] >> 4 != 4:
        return None
    ihl = (packet[0] & 15) * 4
    total, _, fragment = struct.unpack_from("!HHH", packet, 2)
    if not 20 <= ihl <= total <= len(packet) or fragment & 0x3fff:
        return None
    return (packet[9], str(IPv4Address(packet[12:16])),
            str(IPv4Address(packet[16:20])), ihl, total, packet[ihl:total])


def is_prime_endpoint(remote_ip, remote_port, local_port):
    return (remote_ip, remote_port, local_port) == (PRIME_IP, PRIME_PORT, PHONE_PORT)


# The ranges are capture signatures, with no assumption about future sessions.
SIGNATURE_LENGTHS = {
    ("outbound", bytes.fromhex("002dc15b")): (30, 582),
    ("inbound", bytes.fromhex("00000000")): (24, 524),
    ("inbound", bytes.fromhex("00020000")): (32, 32),
    ("inbound", bytes.fromhex("00030000")): (1400, 1400),
    ("inbound", bytes.fromhex("000b0000")): (35, 270),
    ("inbound", bytes.fromhex("00350000")): (45, 45),
    ("inbound", bytes.fromhex("00400000")): (45, 45),
}


def identify_flow(remote_ip, remote_port, local_port, direction, payload):
    """Classify observed signatures on the capture's UDP tuple."""
    if not is_prime_endpoint(remote_ip, remote_port, local_port):
        return None
    prefix = payload[:4]
    bounds = SIGNATURE_LENGTHS.get((direction, prefix))
    if bounds is not None and bounds[0] <= len(payload) <= bounds[1]:
        return f"prime/{direction}/{prefix.hex()}"
    return None


def observed_counter(remote_ip, remote_port, local_port, direction, payload):
    """Read the observed incrementing value after checking the flow signature."""
    signature = identify_flow(remote_ip, remote_port, local_port, direction, payload)
    if signature == "prime/outbound/002dc15b":
        return int.from_bytes(payload[8:12], "little")
    if signature == "prime/inbound/000b0000":
        return int.from_bytes(payload[6:8], "little")
    return None


def prime_datagrams(path, local_ip=PHONE_IP):
    for _, _, _, packet in raw_ipv4_records(path):
        decoded = ipv4_transport(packet)
        if decoded is None:
            continue
        protocol, source, destination, _, _, udp = decoded
        if protocol != 17 or len(udp) < 8:
            continue
        source_port, destination_port, length = struct.unpack_from("!HHH", udp)
        if not 8 <= length <= len(udp):
            continue
        if source == local_ip and is_prime_endpoint(destination, destination_port, source_port):
            yield CapturedDatagram("outbound", udp[8:length])
        elif destination == local_ip and is_prime_endpoint(source, source_port, destination_port):
            yield CapturedDatagram("inbound", udp[8:length])


class HonorOfKingsParser:
    def parse(self, datagrams: Sequence["Datagram"]) -> list["Entity"]:
        # The wire signatures establish flow membership. Body encoding and
        # coordinate semantics remain unresolved, including possible obfuscation.
        return []


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("pcap")
    cli.add_argument("--local-ip", default=PHONE_IP)
    args = cli.parse_args()
    counts = Counter()
    counter_hits = Counter()
    parser = HonorOfKingsParser()
    entities = 0
    batch = []
    for datagram in prime_datagrams(args.pcap, args.local_ip):
        signature = identify_flow(PRIME_IP, PRIME_PORT, PHONE_PORT, datagram.direction,
                                  datagram.payload)
        counts[(datagram.direction, signature or "unmatched")] += 1
        if observed_counter(PRIME_IP, PRIME_PORT, PHONE_PORT, datagram.direction,
                            datagram.payload) is not None:
            counter_hits[datagram.direction] += 1
        batch.append(datagram)
        if len(batch) == 256:
            entities += len(parser.parse(batch))
            batch.clear()
    if batch:
        entities += len(parser.parse(batch))
    if not counts:
        cli.error("No prime UDP datagrams in capture")
    print(f"Prime UDP datagrams: {sum(counts.values())}")
    for (direction, signature), count in sorted(counts.items()):
        print(f"{direction} {signature}: {count}")
    print(f"Observed counters: {dict(counter_hits)}")
    print(f"Entities: {entities}. Coordinate layout and body encoding are UNKNOWN.")


if __name__ == "__main__":
    main()
