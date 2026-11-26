#!/usr/bin/env python3
"""Analyze classic PCAP captures without external dependencies."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import ipaddress
import json
import statistics
import struct


MAGIC = {
    b"\xd4\xc3\xb2\xa1": ("<", 1_000_000),
    b"\xa1\xb2\xc3\xd4": (">", 1_000_000),
    b"\x4d\x3c\xb2\xa1": ("<", 1_000_000_000),
    b"\xa1\xb2\x3c\x4d": (">", 1_000_000_000),
}
RULE = ("UDP flows with >= 50 packets AND >= 10 packets/sec sustained "
        "(pps computed over the flow's own duration) AND duration >= 2 seconds")
CAVEAT = "heuristic, unvalidated on real Honor of Kings traffic"


def decode_packet(data, linktype, sliced):
    """Return source, destination, protocol and optional transport ports."""
    if linktype == 1:
        offset = 14
        ether_type, = struct.unpack_from("!H", data, 12)
        while ether_type in (0x8100, 0x88A8, 0x9100):
            ether_type, = struct.unpack_from("!H", data, offset + 2)
            offset += 4
    elif linktype == 113:
        offset = 16
        ether_type, = struct.unpack_from("!H", data, 14)
    elif linktype == 108:
        offset = 4
        family, = struct.unpack_from("!I", data)
        ether_type = {2: 0x0800, 10: 0x86DD, 24: 0x86DD,
                      28: 0x86DD, 30: 0x86DD}.get(family)
    elif linktype == 101:
        offset = 0
        ether_type = {4: 0x0800, 6: 0x86DD}.get(data[0] >> 4)
    else:
        return None
    if ether_type not in (0x0800, 0x86DD):
        return None

    ip = memoryview(data)[offset:]
    version = 4 if ether_type == 0x0800 else 6
    if ip[0] >> 4 != version:
        raise ValueError("IP version mismatch")
    more_fragments = False
    if version == 4:
        offset = (ip[0] & 15) * 4
        length, _, fragment = struct.unpack_from("!HHH", ip, 2)
        if offset < 20 or offset > min(length, len(ip)):
            raise ValueError("invalid IPv4 header length")
        src, dst = struct.unpack_from("!4s4s", ip, 12)
        protocol = ip[9]
        non_initial = bool(fragment & 0x1FFF)
        more_fragments = bool(fragment & 0x2000)
    else:
        length = 40 + struct.unpack_from("!H", ip, 4)[0]
        src, dst = struct.unpack_from("!16s16s", ip, 8)
        protocol = ip[6]
        offset = 40
        non_initial = False
        limit = min(length, len(ip))
        while protocol in (0, 43, 44, 51, 60):
            if offset + 2 > limit:
                raise ValueError("truncated IPv6 extension")
            next_protocol, size = struct.unpack_from("!BB", ip, offset)
            if protocol == 44:
                fragment, = struct.unpack_from("!H", ip, offset + 2)
                non_initial = bool(fragment & 0xFFF8)
                more_fragments = bool(fragment & 1)
                extension_length = 8
            elif protocol == 51:
                extension_length = (size + 2) * 4
            else:
                extension_length = (size + 1) * 8
            offset += extension_length
            if offset > limit:
                raise ValueError("truncated IPv6 extension")
            protocol = next_protocol
            if non_initial:
                break

    if length > len(ip) and not sliced:
        raise ValueError("truncated IP packet")

    src, dst = str(ipaddress.ip_address(src)), str(ipaddress.ip_address(dst))
    name = {6: "TCP", 17: "UDP"}.get(protocol, "other")
    if name == "other" or non_initial:
        return src, dst, name, None, None

    transport = ip[offset:length]
    if name == "UDP":
        sport, dport, udp_length, _ = struct.unpack_from("!HHHH", transport)
        if udp_length < 8 or (udp_length > length - offset and not more_fragments):
            raise ValueError("invalid UDP length")
    else:
        sport, dport = struct.unpack_from("!HH", transport)
        tcp_length = (transport[12] >> 4) * 4
        if tcp_length < 20 or tcp_length > len(transport):
            raise ValueError("invalid TCP header length")
    return src, dst, name, sport, dport


def records(capture, notes, decode=True):
    capture.seek(0)
    header = capture.read(24)
    if len(header) < 24:
        notes.append("Truncated or missing PCAP global header.")
        return
    if header[:4] not in MAGIC:
        notes.append("Unrecognized classic PCAP magic.")
        return
    endian, scale = MAGIC[header[:4]]
    _, _, _, _, snaplen, network = struct.unpack(endian + "HHIIII", header[4:])
    linktype = network & 0xFFFF
    if linktype not in (1, 101, 108, 113):
        notes.append(f"Unsupported link type {linktype}.")
    remaining = capture.seek(0, 2) - 24
    capture.seek(24)
    while remaining:
        record = capture.read(16)
        if len(record) < 16:
            notes.append("Truncated PCAP record header.")
            yield None, 0, None
            break
        remaining -= 16
        seconds, fraction, captured, original = struct.unpack(endian + "IIII", record)
        timestamp = seconds * 1_000_000_000 + fraction * (1_000_000_000 // scale)
        if fraction >= scale:
            timestamp = None
        if captured > remaining:
            notes.append("Truncated PCAP record data.")
            yield timestamp, remaining, None
            break
        # A 16 MiB ceiling bounds memory even for hostile record lengths.
        if not decode or timestamp is None or captured > min(snaplen, original, 16 * 1024 * 1024):
            capture.seek(captured, 1)
            packet = None
        else:
            data = capture.read(captured)
            try:
                packet = decode_packet(data, linktype, captured < original)
            except (ValueError, IndexError, struct.error):
                packet = None
        remaining -= captured
        yield timestamp, captured, packet


def timestamp_text(timestamp):
    if timestamp is None:
        return None
    seconds, nanos = divmod(timestamp, 1_000_000_000)
    date = datetime.fromtimestamp(seconds, timezone.utc)
    return f"{date:%Y-%m-%dT%H:%M:%S}.{nanos:09d}Z"


def add(totals, size):
    totals[0] += 1
    totals[1] += size


def rankings(totals, top):
    def rows(index):
        keys = sorted(totals, key=lambda key: (-totals[key][index], str(key)))
        return [dict(ip=key[0], **({"port": key[1]} if len(key) == 2 else {}),
                     packets=totals[key][0], bytes=totals[key][1])
                for key in keys[:top]]
    return {"by_packets": rows(0), "by_bytes": rows(1)}


def analyze(capture, local_ip, top):
    notes = []
    protocols = {name: [0, 0] for name in ("UDP", "TCP", "other")}
    pairs = defaultdict(lambda: [0, 0])
    flows = defaultdict(lambda: [[], None, None])
    sources = Counter()
    buckets = defaultdict(lambda: [0, 0, 0, 0])
    first = last = None
    skipped = 0

    # Find the time origin before bucketing, including out-of-order records.
    for stamp, _, _ in records(capture, [], decode=False):
        if stamp is not None:
            first = stamp if first is None else min(first, stamp)
            last = stamp if last is None else max(last, stamp)

    for stamp, size, packet in records(capture, notes):
        name = packet[2] if packet else "other"
        add(protocols[name], size)
        if stamp is not None:
            bucket = buckets[(stamp - first) // 1_000_000_000]
            add(bucket, size)
            bucket[2] += name == "UDP"
            bucket[3] += name == "TCP"
        if packet is None:
            skipped += 1
            continue
        src, dst, name, sport, dport = packet
        sources[src] += 1
        add(pairs[(src, dst, dport, sport)], size)
        if sport is not None:
            flow = flows[(name, src, sport, dst, dport)]
            flow[0].append(size)
            flow[1] = stamp if flow[1] is None else min(flow[1], stamp)
            flow[2] = stamp if flow[2] is None else max(flow[2], stamp)

    method = "explicit" if local_ip else "auto: most frequent source IP"
    if local_ip is None and sources:
        local_ip = min(sources, key=lambda ip: (-sources[ip], ip))
    ips = defaultdict(lambda: [0, 0])
    endpoints = defaultdict(lambda: [0, 0])
    for (src, dst, dport, sport), (count, size) in pairs.items():
        if src == local_ip and dst != local_ip:
            remote, port = dst, dport
        elif dst == local_ip and src != local_ip:
            remote, port = src, sport
        else:
            continue
        ips[(remote,)][0] += count
        ips[(remote,)][1] += size
        if port is not None:
            endpoints[(remote, port)][0] += count
            endpoints[(remote, port)][1] += size

    flow_rows = []
    for key, (sizes, start, end) in flows.items():
        name, src, sport, dst, dport = key
        duration = (end - start) / 1_000_000_000
        flow_rows.append(dict(protocol=name, src_ip=src, src_port=sport,
                              dst_ip=dst, dst_port=dport, packets=len(sizes),
                              bytes=sum(sizes), min_size=min(sizes),
                              median_size=statistics.median(sizes), max_size=max(sizes),
                              mean_size=statistics.mean(sizes), duration_seconds=duration,
                              pps=len(sizes) / duration if duration else 0.0))
    def flow_key(row):
        return tuple(str(row[key]) for key in
                     ("src_ip", "src_port", "dst_ip", "dst_port", "protocol"))

    flow_rows.sort(key=lambda row: (-row["packets"], flow_key(row)))
    likely = [row for row in flow_rows if row["protocol"] == "UDP"
              and row["packets"] >= 50 and row["pps"] >= 10
              and row["duration_seconds"] >= 2]
    likely.sort(key=lambda row: (-row["pps"], flow_key(row)))

    total_packets = sum(count for count, _ in protocols.values())
    total_bytes = sum(size for _, size in protocols.values())
    split = {name: dict(packets=count, bytes=size,
                        packet_percent=100 * count / total_packets if total_packets else 0,
                        byte_percent=100 * size / total_bytes if total_bytes else 0)
             for name, (count, size) in protocols.items()}

    per_second = []
    previous = -1
    for second, (count, size, udp, tcp) in sorted(buckets.items()):
        gap = second - previous - 1
        if gap > 3600:
            per_second.append(dict(second=previous + 1, through_second=second - 1,
                                   packets=0, bytes=0, udp_packets=0, tcp_packets=0))
        else:
            per_second.extend(dict(second=empty, packets=0, bytes=0,
                                   udp_packets=0, tcp_packets=0)
                              for empty in range(previous + 1, second))
        per_second.append(dict(second=second, packets=count, bytes=size,
                               udp_packets=udp, tcp_packets=tcp))
        previous = second

    return {
        "summary": dict(total_packets=total_packets, total_bytes=total_bytes,
                        first_timestamp=timestamp_text(first), last_timestamp=timestamp_text(last),
                        duration_seconds=(last - first) / 1_000_000_000 if first is not None else 0,
                        malformed_or_skipped_packets=skipped, protocols=split,
                        local_ip=local_ip, local_ip_method=method, notes=notes),
        "top_remote_ips": rankings(ips, top),
        "top_remote_endpoints": rankings(endpoints, top),
        "top_flows": flow_rows[:max(top, 10)],
        "likely_game_server_flows": dict(rule=RULE, caveat=CAVEAT, flows=likely),
        "per_second": per_second,
    }


def print_flow(row):
    print("  {protocol} [{src_ip}]:{src_port} -> [{dst_ip}]:{dst_port}  "
          "{packets} packets  {bytes} bytes  sizes min/median/max/mean "
          "{min_size}/{median_size:g}/{max_size}/{mean_size:g}  "
          "{duration_seconds:g} s  {pps:.6f} pps".format(**row))


def print_report(report):
    summary = report["summary"]
    print("Summary")
    print(f"  Total packets: {summary['total_packets']}")
    print(f"  Total bytes (captured): {summary['total_bytes']}")
    print(f"  First timestamp: {summary['first_timestamp'] or 'none'}")
    print(f"  Last timestamp: {summary['last_timestamp'] or 'none'}")
    print(f"  Duration: {summary['duration_seconds']:g} s")
    print(f"  Malformed/skipped packets: {summary['malformed_or_skipped_packets']}")
    for name, row in summary["protocols"].items():
        print(f"  {name}: {row['packets']} packets ({row['packet_percent']:.2f}%), "
              f"{row['bytes']} bytes ({row['byte_percent']:.2f}%)")
    for note in summary["notes"]:
        print(f"  {note}")
    print(f"  Local IP: {summary['local_ip'] or 'undetermined'} ({summary['local_ip_method']})")

    for title, key in (("Top remote IPs", "top_remote_ips"),
                       ("Top remote endpoints", "top_remote_endpoints")):
        print(f"\n{title}")
        for order in ("packets", "bytes"):
            print(f"  By {order}")
            rows = report[key][f"by_{order}"]
            if not rows:
                print("    None.")
            for row in rows:
                address = f"[{row['ip']}]:{row['port']}" if "port" in row else row["ip"]
                print(f"    {address}  {row['packets']} packets  {row['bytes']} bytes")
    print("\nPer-flow stats (top by packets)")
    for row in report["top_flows"]:
        print_flow(row)
    if not report["top_flows"]:
        print("  No TCP or UDP flows with ports.")
    likely = report["likely_game_server_flows"]
    print("\nLikely game-server flows")
    print(f"  {likely['rule']}")
    print(f"  {likely['caveat']}")
    for row in likely["flows"]:
        print_flow(row)
    if not likely["flows"]:
        print("  No flows match.")
    print("\nPer-second summary")
    for row in report["per_second"]:
        label = str(row["second"])
        if "through_second" in row:
            label += f"–{row['through_second']}"
        print(f"  {label} s  {row['packets']} packets/sec  {row['bytes']} bytes/sec  "
              f"UDP {row['udp_packets']}  TCP {row['tcp_packets']}")
    if not report["per_second"]:
        print("  No timestamped records.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pcap_file", help="path to a classic PCAP file")
    parser.add_argument("--json", action="store_true", help="emit a single JSON report")
    parser.add_argument("--top", type=int, default=10, metavar="N",
                        help="limit remote rankings and top flows (default 10, at least 10 flows)")
    parser.add_argument("--local-ip", type=ipaddress.ip_address, metavar="IP",
                        help="phone IPv4 or IPv6 address (default: most frequent source IP)")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be at least 1")
    try:
        with open(args.pcap_file, "rb") as capture:
            report = analyze(capture, str(args.local_ip) if args.local_ip else None, args.top)
    except OSError as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()
