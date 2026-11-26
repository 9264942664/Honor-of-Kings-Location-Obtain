#!/usr/bin/env python3
"""Extract reproducible timing and payload evidence from the raw-IP HoK PCAP."""
import argparse
from collections import Counter, defaultdict
from math import isfinite, log2
from pathlib import Path
import re
import statistics as stats
import struct
import sys
from tempfile import TemporaryFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server.hok_parser import PHONE_IP, PRIME_IP, ipv4_transport, raw_ipv4_records


def entropy(counts):
    total = sum(counts.values())
    return -sum(n / total * log2(n / total) for n in counts.values()) if total else 0


def frequency(counts, top=None):
    return ', '.join(f'{key}×{count}' for key, count in counts.most_common(top))


def runs(seconds):
    groups = []
    for second in sorted(seconds):
        if not groups or second > groups[-1][-1] + 1:
            groups.append([])
        groups[-1].append(second)
    return groups


def dns_name(data, offset, seen=()):
    labels = []
    while True:
        length = data[offset]
        offset += 1
        if length == 0:
            return '.'.join(labels), offset
        if length & 192 == 192:
            pointer = (length & 63) * 256 + data[offset]
            if pointer in seen or len(seen) >= 32:
                raise ValueError("DNS compression loop")
            suffix, _ = dns_name(data, pointer, (*seen, pointer))
            return '.'.join([*labels, suffix]), offset + 1
        if length > 63 or offset + length > len(data):
            raise ValueError("Invalid DNS label")
        labels.append(data[offset:offset + length].decode('ascii', 'replace'))
        offset += length


def tls_sni(data):
    """Read SNI from complete plaintext TLS ClientHello records in a prefix."""
    handshake = bytearray()
    offset = 0
    while data[offset:offset+2] == b'\x16\x03' and offset + 5 <= len(data):
        size = int.from_bytes(data[offset+3:offset+5], 'big')
        if offset + 5 + size > len(data):
            break
        handshake.extend(data[offset+5:offset+5+size])
        offset += 5 + size
    if handshake[:1] != b'\x01' or len(handshake) < 39:
        return None
    end = 4 + int.from_bytes(handshake[1:4], 'big')
    if end > len(handshake):
        return None
    p = 39 + handshake[38]
    for width in (2, 1):
        p += width + int.from_bytes(handshake[p:p+width], 'big')
    p += 2
    while p + 4 <= end:
        kind, size = struct.unpack_from('!HH', handshake, p)
        p += 4
        if kind == 0 and size >= 5 and p + size <= end and handshake[p+2] == 0:
            length = int.from_bytes(handshake[p+3:p+5], 'big')
            if length <= size - 5:
                return bytes(handshake[p+5:p+5+length]).decode('ascii', 'replace')
        p += size
    return None


class TcpPrefix:
    """Bound storage to the opening 16 KiB per direction, indexed by sequence."""
    limit = 16384

    def __init__(self):
        self.base = None
        self.syn = False
        self.parts = []
        self.payload_bytes = 0

    def add(self, seq, flags, payload):
        if flags & 2:
            self.base = (seq + 1) & 0xffffffff
            self.syn = True
        if not payload:
            return
        self.payload_bytes += len(payload)
        seq = (seq + bool(flags & 2)) & 0xffffffff
        if self.base is None:
            self.base = seq
        delta = (seq - self.base + 2**31) % 2**32 - 2**31
        if -self.limit <= delta < self.limit:
            self.parts.append((delta, payload[:self.limit - delta]))

    def assemble(self):
        if not self.parts:
            return b''
        start = 0 if self.syn else min(offset for offset, _ in self.parts)
        result = bytearray()
        for offset, payload in sorted(self.parts, key=lambda part: part[0]):
            overlap = start + len(result) - offset
            if overlap < 0:
                break
            result.extend(payload[overlap:])
            if len(result) >= self.limit:
                break
        return bytes(result[:self.limit])


def fixed_offsets(packets, direction):
    prefix = bytes.fromhex("002dc15b" if direction == "outbound" else "000b0000")
    payloads = [payload for _, payload in packets if payload.startswith(prefix)]
    positions = []
    for offset in range(24):
        counts = Counter(payload[offset] for payload in payloads)
        value, count = counts.most_common(1)[0]
        if count / len(payloads) >= 0.95:
            positions.append((offset, f"{value:02x}", count))
    return positions


def check_timestamp_candidates(packets):
    short_family = [(t, p) for t,p in packets if len(p) == 24 and p.startswith(bytes(4))]
    for offset in (4, 8):
        for order in ("big", "little"):
            times, values = zip(*[(t, int.from_bytes(p[offset:offset+4], order))
                                  for t,p in short_family])
            slope, _ = stats.linear_regression(times, values)
            correlation = stats.correlation(times, values)
            print(f"00000000 length 24, offset {offset} {order} uint32, "
                  f"n={len(times)}, r={correlation:.5f}, slope={slope:.3f} units/s, "
                  f"first/last={values[0]}/{values[-1]}.")


def prime_section(direction, packets):
    print(f'\n### Prime {direction}\n')
    sizes = Counter(len(p) for _, p in packets)
    counts = Counter(b for _, p in packets for b in p)
    classes = defaultdict(Counter)
    for _, payload in packets:
        classes[len(payload)].update(payload)
    expected = sum(counts.values()) / 256
    chi = sum((counts[b] - expected)**2 / expected for b in range(256))
    print(f'Aggregate entropy **{entropy(counts):.4f} bits/byte**, Pearson χ² **{chi:.1f}** (255 df, uniform null), {len(counts)} distinct values, {sum(counts.values())} bytes. Common values {frequency(Counter({f"{b:02x}": n for b,n in counts.items()}), 10)}.')
    print('Prefix payload length ranges:', sorted((prefix, len(v), min(v), max(v)) for prefix in {p[:4].hex() for _,p in packets} if (v := [len(p) for _,p in packets if p[:4].hex()==prefix])))
    print('\nFirst bytes:', frequency(Counter(p[:1].hex() or 'empty' for _, p in packets)))
    for width in (4, 8, 16):
        print(f'\nTop {width}-byte prefixes:', frequency(Counter(p[:width].hex() for _, p in packets), 10))
    marker = bytes.fromhex('3d086b17f400')
    print('\nMarker first offsets:', frequency(Counter(p.find(marker) for _, p in packets)))
    for value in ('002dc15b', '00020000', '00020000a7bfb900', '00030000'):
        print(f'- Prefix `{value}`: {sum(p.startswith(bytes.fromhex(value)) for _,p in packets)}')
    print('\n| Offset/width | Order | Positive | Equal | Negative | +1 |\n|---|---|---:|---:|---:|---:|')
    for offset, width in ((0,2), (2,2), (4,4), (4,2), (6,2), (8,2), (8,4), (10,2), (12,2), (16,2), (18,2), (20,2)):
        for order in ('little', 'big'):
            values = [int.from_bytes(p[offset:offset+width], order) if len(p) >= offset+width else None for _,p in packets]
            delta = Counter(b-a for a,b in zip(values, values[1:]) if a is not None and b is not None)
            print(f'| {offset}/{width} | {order} | {sum(n for d,n in delta.items() if d>0)} | {delta[0]} | {sum(n for d,n in delta.items() if d<0)} | {delta[1]} |')
    for prefix in sorted({p[:4].hex() for _,p in packets}):
        times = [t for t,p in packets if p[:4].hex() == prefix]
        print(f'Prefix {prefix} first/last: {min(times):.6f}/{max(times):.6f}')
    length_fields = Counter()
    for _, payload in packets:
        for offset in range(24):
            for width in (1, 2):
                if offset + width > len(payload):
                    continue
                for order in ("little", "big") if width == 2 else ("little",):
                    value = int.from_bytes(payload[offset:offset + width], order)
                    length_fields[offset, width, order, len(payload) - value] += 1
    print("Common length-minus-field relationships (offset, width, order, difference):",
          length_fields.most_common(12))
    print("Fixed offsets 0–23 in dominant signature family (offset, hex, count):",
          fixed_offsets(packets, direction))
    if direction == "outbound":
        print("Offset 8 LE uint32 first/last:", [int.from_bytes(p[8:12], "little")
                                                for _,p in (packets[0], packets[-1])])
    else:
        regular = [p for _,p in packets if p.startswith(bytes.fromhex("000b0000"))]
        seq = [int.from_bytes(p[6:8], "little") for p in regular]
        print("000b0000 sequence first/last/wraps:",
              seq[0], seq[-1], sum(b<a for a,b in zip(seq,seq[1:])))
        check_timestamp_candidates(packets)
        print("000b0000 offset 6 LE uint16 delta histogram:",
              frequency(Counter((b-a)%65536 for a,b in zip(seq,seq[1:])),16))
    for cutoff in (8, 16, 24, 32):
        tail_counts = Counter(b for _,p in packets for b in p[cutoff:])
        print(f"Payload from offset {cutoff}: entropy {entropy(tail_counts):.4f}")
    gaps = [(b-a)*1000 for (a,_),(b,_) in zip(packets,packets[1:])]
    print(f'\nGap median {stats.median(gaps):.3f} ms, most common rounded-ms gaps {frequency(Counter(map(round,gaps)),10)}.')
    print(f'Length/time Pearson r = {stats.correlation([t for t,_ in packets], [len(p) for _,p in packets]):.5f}.')
    periods = defaultdict(list)
    for t,p in packets:
        periods[int(t)//60*60].append(len(p))
    print('Per-minute t/count/median bytes:', ', '.join(f'{t}/{len(v)}/{stats.median(v):g}' for t,v in sorted(periods.items())))
    print('\nPrintable runs ≥8, top ten:', frequency(Counter(s.decode('ascii') for _,p in packets for s in re.findall(rb'[ -~]{8,}', p)), 10))
    print('Literal hits:', {literal: sum(literal.encode() in p for _,p in packets) for literal in ('GET ', 'HTTP/', 'actor_position','entities','map_pos','Unity')})
    for lo,hi in ((0.001,1),(-20000,20000)):
        hits = Counter()
        distinct = defaultdict(set)
        for _, p in packets:
            for off in range(min(64, len(p)-7)):
                x,y = struct.unpack_from('<ff',p,off)
                if (isfinite(x) and isfinite(y) and lo <= x <= hi and lo <= y <= hi
                        and min(abs(x), abs(y)) >= .001):
                    hits[off] += 1
                    distinct[off].add((x,y))
        print(f'Float pairs [{lo},{hi}] with abs ≥0.001, first 64 offsets: {[(off,n,len(distinct[off])) for off,n in hits.most_common(10)]} (offset, hits, distinct).')
    print('\nLength histogram and pooled entropy by length (bytes:count/entropy).\n')
    print(' '.join(f'{size}:{sizes[size]}/{entropy(classes[size]):.3f}' for size in sorted(sizes)))


def udp_section(flow, packets):
    print(f'\n### UDP {flow}\n')
    for direction in ('outbound','inbound'):
        rows = [(t,p) for t,d,p in packets if d == direction]
        if not rows:
            continue
        values = [entropy(Counter(p)) for _,p in rows]
        print(f'- {direction}: {len(rows)} packets, t={rows[0][0]:.6f}–{rows[-1][0]:.6f}, entropy min/median/max {min(values):.3f}/{stats.median(values):.3f}/{max(values):.3f}. Lengths {frequency(Counter(len(p) for _,p in rows),12)}. Prefixes {frequency(Counter(p[:4].hex() for _,p in rows),10)}.')
        rtp = [p for _,p in rows if len(p) >= 12 and p[0] >> 6 == 2]
        steps = Counter((int.from_bytes(b[2:4],'big')-int.from_bytes(a[2:4],'big')) % 65536 for a,b in zip(rtp,rtp[1:]))
        print(f'  80/81 first bytes: {sum(p[:1] in (b"\x80",b"\x81") for _,p in rows)}. RTP-v2 candidates: {len(rtp)}, SSRC {frequency(Counter(p[8:12].hex() for p in rtp),5)}, sequence deltas {frequency(steps,5)}.')
        if flow[0].startswith('59.47.'):
            big = [p for _,p in rows if len(p)==1130]
            if big:
                for offset, width in ((0,8),(12,12),(0,24)):
                    print(f"  Offset {offset}, width {width} normalized by XOR with first byte of slice:",
                          frequency(Counter(bytes(b ^ p[offset] for b in p[offset:offset+width]).hex()
                                            for p in big), 5))
                alternating = sum(p[12] == p[14] == p[16] and p[13] == p[15] == p[17]
                                  for p in big)
                print(f"  Alternating repeat at offsets 12–17: {alternating}/{len(big)}.")
                repeats = Counter(len(m.group()) for p in big for m in re.finditer(rb'(.)\1{7,}',p,re.S))
                xor = Counter(a^b for p,q in zip(big,big[1:]) for a,b in zip(p,q))
                print(f'  1130-byte packets: {len(big)}, median packet entropy {stats.median(entropy(Counter(p)) for p in big):.3f}, run lengths ≥8 {frequency(repeats,8)}, successive packet XOR {frequency(xor,8)} out of {sum(xor.values())} bytes. First 32 bytes: {big[0][:32].hex()}.')
    if flow[0] == '150.139.159.155':
        printable = Counter((d,p.decode('ascii')) for _,d,p in packets if p and all(32<=b<=126 for b in p))
        print(f'\nAll-printable packets {sum(printable.values())}, distinct direction/payload pairs {len(printable)}.')
        for (d,p),n in sorted(printable.items()):
            print(f'- {d} ×{n} `{p!r}`')
        print('Embedded literals:', {v:sum(v.encode() in p for _,_,p in packets) for v in ('ww  ','334082698','7549FF8','91DF40A8')})
        print('Most frequent printable runs:', frequency(Counter(repr(s) for _,_,p in packets for s in re.findall(rb'[ -~]{4,}',p)),25))
        print('Sample payloads:', [(d,p.hex()) for _,d,p in packets[:8]])
    if flow[0] == '101.226.101.213':
        print('\nFull payloads (elapsed seconds, direction, hex):')
        for t,d,p in packets:
            print(f'- {t:.6f} {d} `{p.hex()}`')
        requests, replies = {}, {}
        for t, d, p in packets:
            (requests if d == 'outbound' else replies)[p[2:4],p[8:14]] = t
        delays = [replies[k]-t for k,t in requests.items() if k in replies]
        print(f"Request/response key matches {len(delays)}/{len(requests)}, "
              f"median delay {stats.median(delays)*1000:.3f} ms.")
        print('Signature counts:', [sum(test(p) for _,_,p in packets) for test in (lambda p:p.startswith(bytes.fromhex('0102a1c4')),lambda p:b'S::D' in p,lambda p:b'AA' in p)])


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('pcap')
    cli.add_argument('--local-ip', default=PHONE_IP)
    cli.add_argument('--buckets', type=Path, help='write all nonzero per-flow one-second buckets as TSV')
    args = cli.parse_args()
    target = {PRIME_IP, '59.47.239.78', '59.47.239.223', '150.139.159.155', '101.226.101.213'}
    flows = defaultdict(list)
    udp = defaultdict(list)
    tcp = defaultdict(TcpPrefix)
    lengths = Counter()
    special_packets = []
    first_cdn = None
    first_cdn_segments = {'inbound': [], 'outbound': []}
    cdn_file = {direction: TemporaryFile() for direction in first_cdn_segments}
    dns_queries, dns_replies, a_records, quic, skipped = (Counter() for _ in range(5))
    captured_records = captured_bytes = 0
    first_time = last_time = 0
    for t, cap, orig, packet in raw_ipv4_records(args.pcap):
        captured_records += 1
        captured_bytes += cap
        first_time = min(first_time, t)
        last_time = max(last_time, t)
        decoded = ipv4_transport(packet)
        if decoded is None or decoded[0] not in (6,17):
            skipped[(packet[0]>>4, decoded[0] if decoded else None)] += 1
            continue
        proto, src, dst, ihl, total, l4 = decoded
        if args.local_ip not in (src,dst):
            skipped['non-phone'] += 1
            continue
        sp,dp = struct.unpack_from('!HH',l4)
        outbound = src == args.local_ip
        remote,rp,lp = (dst,dp,sp) if outbound else (src,sp,dp)
        direction = 'outbound' if outbound else 'inbound'
        flow = ('UDP' if proto==17 else 'TCP', remote,rp,lp)
        flows[flow].append((t,cap,direction))
        if proto == 6:
            seq, = struct.unpack_from('!I',l4,4)
            payload = l4[(l4[12]>>4)*4:]
            stream = tcp[flow,direction]
            stream.add(seq,l4[13],payload)
            if flow[:3] == ('TCP', '36.104.134.106', 80) and first_cdn is None:
                first_cdn = flow
            if flow == first_cdn and payload:
                offset = (seq + bool(l4[13]&2) - stream.base) % 2**32
                if offset >= 2**31:
                    raise ValueError("First CDN session has data preceding its sequence origin")
                cdn_file[direction].seek(offset)
                cdn_file[direction].write(payload)
                first_cdn_segments[direction].append((offset, offset+len(payload)))
            continue
        size, = struct.unpack_from('!H',l4,4)
        if not 8 <= size <= len(l4):
            skipped['invalid UDP length'] += 1
            continue
        p = l4[8:size]
        if remote in target:
            udp[flow[1:]].append((t,direction,p))
        if remote == PRIME_IP and rp == 10214 and lp == 48605:
            lengths['consistent' if size == total-ihl and total == cap == orig else 'different'] += 1
            if p.startswith((bytes.fromhex('00030000'),bytes.fromhex('00020000'))):
                if p.startswith(bytes.fromhex("00030000")):
                    special_packets.append(p)
                nonzero = [(i,f"{b:02x}") for i,b in enumerate(p) if b]
                print(f'- Prime nonzero offsets t={t:.6f}: {nonzero}')
                print(f'- Prime special t={t:.6f}, UDP={size}, IP={total}, IHL={ihl}, captured={cap}, original={orig}, prefix={p[:24].hex()}, zeros={p.count(0)}/{len(p)}, trailing zeros={len(p)-len(p.rstrip(bytes(1)))}, entropy={entropy(Counter(p)):.4f}')
        if rp == 53 and len(p)>=12:
            _,flags,questions,answers,_,_ = struct.unpack_from('!6H',p)
            off = 12
            try:
                for _ in range(questions):
                    name,off = dns_name(p,off)
                    qtype,_ = struct.unpack_from('!HH',p,off)
                    off += 4
                    (dns_replies if flags & 0x8000 else dns_queries)[name,qtype] += 1
                for _ in range(answers):
                    name,off = dns_name(p,off)
                    kind,_,_,length = struct.unpack_from('!HHIH',p,off)
                    off += 10
                    if kind == 1 and length == 4:
                        a_records[name,'.'.join(map(str,p[off:off+4]))] += 1
                    off += length
            except (ValueError, IndexError, struct.error):
                skipped['DNS decode error'] += 1
        if len(p)>=7 and p[0]&0xc0==0xc0 and p[1:5] in (bytes.fromhex('00000001'),bytes.fromhex('6b3343cf')) and p[5]<=20 and 6+p[5]<len(p) and p[6+p[5]]<=20:
            quic[remote,rp,lp,p[1:5].hex()] += 1
    print(f"Independent capture totals: {captured_records} packets, {captured_bytes} bytes, "
          f"{last_time-first_time:.6f} seconds.")
    print("Distinct 00030000 payloads:", len(set(special_packets)))
    for direction, intervals in first_cdn_segments.items():
        end = missing = 0
        for offset, stop in sorted(intervals):
            missing += max(0, offset-end)
            end = max(end,stop)
        with cdn_file[direction] as stream:
            stream.seek(0,2)
            print(f"Full first CDN session {first_cdn}, {direction}: {stream.tell()} sequence span bytes, {missing} gap bytes, {len(intervals)} data-bearing segments.")
    print(f'\nPrime length consistency: {dict(lengths)}. Exclusions: {dict(skipped)}.')
    print('UDP 53 query packets/questions:',sum(1 for f,rows in flows.items() if f[0]=='UDP' and f[2]==53 for _,_,d in rows if d=='outbound'),sum(dns_queries.values()))
    print('DNS question names/counts:',sorted(Counter({name:sum(n for (host,_),n in dns_queries.items() if host==name) for name,_ in dns_queries}).items()))
    print('DNS reply questions:',sorted(dns_replies.items()))
    print('DNS A answers:',sorted(a_records.items()))
    print('QUIC v1/v2 long-header candidates:',quic)
    sni = Counter()
    assembled = {}
    for (flow,d), stream in tcp.items():
        prefix = stream.assemble()
        assembled[flow,d] = prefix
        if d=='outbound' and (name:=tls_sni(prefix)):
            sni[name] += 1
    print("DNS and TLS distinct/total:", len({name for name,_ in dns_queries}), sum(dns_queries.values()),
          len({name for name,_ in a_records}),len(sni),sum(sni.values()))
    print('TLS ClientHello SNI:', sorted(sni.items()))
    print("Endpoint totals (packets, bytes, start, stop, connections):")
    endpoints = defaultdict(list)
    for flow, rows in flows.items():
        endpoints[flow[:3]].append(rows)
    for key, connections in sorted(endpoints.items(), key=lambda item: -sum(map(len,item[1])))[:20]:
        rows = [row for connection in connections for row in connection]
        print(f"- {key}: {len(rows)}, {sum(n for _,n,_ in rows)}, "
              f"{min(t for t,_,_ in rows):.3f}, {max(t for t,_,_ in rows):.3f}, {len(connections)}")
    ordered = sorted(flows,key=lambda f:-len(flows[f]))
    print('\n| Flow (remote / local port) | Packets | Bytes | Start | Stop | Duration | Mean pps | Active seconds | Peak second/pps |\n|---|---:|---:|---:|---:|---:|---:|---:|---|')
    required = {'36.104.134.106','42.185.159.107','61.158.144.68','59.47.239.175','42.202.158.116'}
    top_bytes = sorted(flows,key=lambda f:-sum(r[1] for r in flows[f]))[:15]
    chosen = dict.fromkeys(ordered[:16]+top_bytes+[f for f in ordered if f[1] in target and f[0]=='UDP'])
    if args.buckets:
        with args.buckets.open('w') as output:
            print('protocol\tremote\tremote_port\tlocal_port\tsecond\toutbound\tinbound',file=output)
            for f, rows in flows.items():
                bins = Counter((int(t),d) for t,_,d in rows)
                for sec in sorted({s for s,_ in bins}):
                    print(*f,sec,bins[sec,'outbound'],bins[sec,'inbound'],sep='\t',file=output)
    for f in chosen:
        rows = flows[f]
        first,last = min(r[0] for r in rows),max(r[0] for r in rows)
        bins = Counter(int(r[0]) for r in rows)
        peak,n = bins.most_common(1)[0]
        span = last-first
        print(f'| {f[0]} {f[1]}:{f[2]} / {f[3]} | {len(rows)} | {sum(r[1] for r in rows)} | {first:.3f} | {last:.3f} | {span:.3f} | {len(rows)/span if span else 0:.2f} | {len(bins)} | {peak}/{n} |')
    print('\nEndpoint bucket runs (start–end, packet count, peak pps):')
    for proto, ip, port in [('UDP',PRIME_IP,10214),('TCP','36.104.134.106',80),('UDP','59.47.239.78',43815),('UDP','59.47.239.223',31733),('TCP','180.102.190.141',6644)]:
        rows = [row for f in flows if f[:3]==(proto,ip,port) for row in flows[f]]
        bins = Counter(int(t) for t,_,_ in rows)
        groups = runs(bins)
        if port == 6644:
            groups = [g for g in groups if len(g)>2]
        print(f'- {proto} {ip}:{port}:', [(g[0],g[-1],sum(bins[s] for s in g),max(bins[s] for s in g)) for g in groups])
        if ip == PRIME_IP:
            for direction in ('outbound','inbound'):
                b = Counter(int(t) for t,_,d in rows if d==direction)
                print(f'  {direction} t/pps for 30-second bins:', [(s,round(sum(b.get(i,0) for i in range(s,s+30))/30,2)) for s in range(min(b)//30*30,max(b)+1,30)])
        if proto == 'TCP':
            print('  Captured IP lengths:',frequency(Counter(n for _,n,_ in rows),8))
    prime = udp[(PRIME_IP,10214,48605)]
    for d in ('outbound','inbound'):
        prime_section(d,sorted((t,p) for t,direction,p in prime if direction==d))
    for flow, rows in udp.items():
        if flow[0]!=PRIME_IP:
            udp_section(flow,rows)
    print("Deployment host IP-flow packet count:", sum(len(rows) for flow,rows in flows.items() if flow[1]=="39.96.60.127"))
    print('\nTCP reassembled opening bytes (first capture time, SYN seen, contiguous prefix length, first 24 bytes, plaintext HTTP headers):')
    required.update(('180.102.190.141','59.47.239.210','123.244.93.225','36.104.134.109','120.201.109.143','59.47.239.207','218.93.129.146','59.47.239.78'))
    for f in sorted(flows,key=lambda f:flows[f][0][0]):
        if f[0] != 'TCP' or f[1] not in required:
            continue
        for d in ('outbound','inbound'):
            data = assembled.get((f,d),b'')
            if not data:
                continue
            headers, sep, body = data.partition(b'\r\n\r\n')
            text = headers.decode('ascii','replace') if sep and re.match(rb'(?:GET |POST |HEAD |HTTP/1\.)',headers) else ''
            fields = [line for line in text.split('\r\n') if re.match(r'(GET |POST |HEAD |HTTP/|Host:|Content-Type:|Content-Length:|Content-Range:|Range:|Server:|User-Agent:)',line,re.I)]
            print(f'- {flows[f][0][0]:.3f} {f[1]}:{f[2]}/{f[3]} {d} syn={tcp[f,d].syn} prefix={len(data)} payload={tcp[f,d].payload_bytes} hex={data[:24].hex()} body={body[:16].hex() if text else ""} {fields!r} SNI={tls_sni(data)!r}')


if __name__ == '__main__':
    main()
