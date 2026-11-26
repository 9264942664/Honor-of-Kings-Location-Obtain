#!/usr/bin/env python3
"""Generate a deterministic Ethernet PCAP with three flows and a broken record."""

import argparse
import ipaddress
import struct


START = 1_700_000_000
PHONE = "10.0.0.2"
FLOWS = (
    ("UDP", 40000, "203.0.113.10", 8001, 200, 120, 20_000),
    ("TCP", 50000, "93.184.216.34", 443, 10, 60, 1_000_000),
    ("UDP", 40001, "198.51.100.7", 9000, 20, 40, 100_000),
)
ETHERNET = bytes.fromhex("0200000000020200000000010800")
BROKEN_DATA = b"\x00" * 8


def checksum(data):
    total = sum(word for (word,) in struct.iter_unpack("!H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def frame(protocol, sport, dst, dport, payload_size, index):
    src_bytes = ipaddress.IPv4Address(PHONE).packed
    dst_bytes = ipaddress.IPv4Address(dst).packed
    payload = bytes([index % 256]) * payload_size
    if protocol == "UDP":
        number = 17
        transport = struct.pack("!HHHH", sport, dport, 8 + payload_size, 0) + payload
    else:
        number = 6
        transport = struct.pack("!HHIIBBHHH", sport, dport, index * payload_size,
                                0, 0x50, 0x18, 65535, 0, 0) + payload
        pseudo_header = struct.pack("!4s4sBBH", src_bytes, dst_bytes, 0, number, len(transport))
        transport = transport[:16] + struct.pack("!H", checksum(pseudo_header + transport)) + transport[18:]
    ip = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(transport), index,
                     0, 64, number, 0, src_bytes, dst_bytes)
    ip = ip[:10] + struct.pack("!H", checksum(ip)) + ip[12:]
    return ETHERNET + ip + transport


def generate(capture):
    capture.write(struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
    events = []
    for proto, sport, dst, dport, count, payload, interval in FLOWS:
        for index in range(count):
            data = frame(proto, sport, dst, dport, payload, index)
            events.append((index * interval, data))
    for stamp, data in sorted(events, key=lambda event: event[0]):
        seconds, micros = divmod(stamp, 1_000_000)
        capture.write(struct.pack("<IIII", START + seconds, micros, len(data), len(data)))
        capture.write(data)
    capture.write(struct.pack("<IIII", START + 10, 0, 64, 64))
    capture.write(BROKEN_DATA)


def print_truth():
    totals = {"UDP": [0, 0], "TCP": [0, 0], "other": [1, len(BROKEN_DATA)]}
    print("Ground truth (captured Ethernet bytes, excluding PCAP headers)")
    for proto, sport, dst, dport, count, payload, interval in FLOWS:
        size = 14 + 20 + (8 if proto == "UDP" else 20) + payload
        byte_count = size * count
        duration = (count - 1) * interval / 1_000_000
        totals[proto][0] += count
        totals[proto][1] += byte_count
        print(f"  {proto} {PHONE}:{sport} -> {dst}:{dport}  {count} packets  "
              f"{byte_count} bytes  size {size}  {duration:g} s  {count / duration:.6f} pps")
    packets = sum(count for count, _ in totals.values())
    size = sum(byte_count for _, byte_count in totals.values())
    print(f"Total: {packets} packets, {size} bytes, 1 malformed/skipped packet")
    for proto, (count, byte_count) in totals.items():
        print(f"  {proto}: {count} packets ({100 * count / packets:.2f}%), "
              f"{byte_count} bytes ({100 * byte_count / size:.2f}%)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="path to the generated PCAP file")
    args = parser.parse_args()
    try:
        with open(args.output, "wb") as capture:
            generate(capture)
    except OSError as error:
        parser.error(str(error))
    print_truth()


if __name__ == "__main__":
    main()
