# Honor of Kings PCAP analysis

## Capture and baseline

The fixture is `~/workspace/hok-capture/pcapdroid-20261126.pcap`, a 233,935,599-byte classic raw-IP PCAP. The phone is `10.215.173.1`. Time zero is **2026-11-26T14:06:53.208784Z** and the last packet is **2026-11-26T14:22:21.441719Z**. The baseline analyzer reported **92,545 packets, 232,454,855 captured IP bytes, 928.233 seconds, and zero malformed/skipped records**. The independent probe reproduced the count, byte total and exact span of 928.232935 seconds. It excluded 48 IPv4 ICMP packets from its TCP/UDP analysis.

| Protocol | Packets | Packet share | Captured IP bytes | Byte share |
|---|---:|---:|---:|---:|
| UDP | 43,511 | 47.02% | 9,235,319 | 3.97% |
| TCP | 48,986 | 52.93% | 223,215,504 | 96.03% |
| ICMP | 48 | 0.05% | 4,032 | <0.01% |

The prime flow matches the supplied count, duration and directional IP medians. Outbound is **18,068 packets**, median **89 IP bytes / 61 UDP payload bytes**, and **22.02 pps**. Inbound is **14,506 packets**, median **180 IP bytes / 152 UDP payload bytes**, and **17.68 pps**. The two directions together average **39.70 pps** across 820.538 s. TCP `36.104.134.106:80` matches the supplied 22,581 packets and approximately 128 MB. Its 10,000-byte figure refers to captured IP records (10,915 records of that size), which include IP and TCP headers. All 10,915 correspond to 9,960-byte TCP payloads, out of 14,334 inbound packets for the endpoint. The two suspected voice peers do have 1,130-byte UDP payloads, but their inbound rates differ (219.00 and 319.14 pps) and their codec and application attribution require separate evidence.

## Timing and phase inference

The table ranks individual bidirectional tuples by packet count, with additional tuples from the top by captured bytes and the named UDP peers. Stop is the last observed packet, which can include a keepalive or teardown. Active seconds and peak pps come from integer-second buckets. The TSV command in Reproducibility emits directional counts for every occupied second per tuple. An absent bucket represents zero packets.


| Flow (remote / local port) | Packets | Bytes | Start | Stop | Duration | Mean pps | Active seconds | Peak second/pps |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| UDP 180.102.99.167:10214 / 48605 | 32574 | 4145443 | 58.950 | 879.488 | 820.538 | 39.70 | 822 | 59/162 |
| TCP 36.104.134.106:80 / 40104 | 6124 | 35179121 | 38.380 | 79.863 | 41.483 | 147.63 | 12 | 43/765 |
| UDP 59.47.239.78:43815 / 28743 | 5775 | 3532197 | 23.426 | 54.795 | 31.369 | 184.10 | 20 | 39/1765 |
| TCP 36.104.134.106:80 / 40114 | 3926 | 21548393 | 41.627 | 79.864 | 38.237 | 102.68 | 8 | 46/1010 |
| TCP 180.102.190.141:6644 / 48976 | 3801 | 2217007 | 24.453 | 926.585 | 902.132 | 4.21 | 440 | 25/185 |
| TCP 36.104.134.106:80 / 48238 | 3526 | 18189139 | 44.296 | 79.864 | 35.568 | 99.13 | 6 | 47/1156 |
| TCP 36.104.134.106:80 / 40120 | 3294 | 21106248 | 41.655 | 76.833 | 35.178 | 93.64 | 6 | 42/979 |
| TCP 42.185.159.107:80 / 43858 | 2955 | 18779600 | 21.859 | 95.084 | 73.225 | 40.36 | 9 | 48/1211 |
| TCP 36.104.134.106:80 / 48246 | 1989 | 10566850 | 44.301 | 77.833 | 33.533 | 59.32 | 5 | 46/1046 |
| TCP 36.104.134.106:80 / 48260 | 1948 | 10599413 | 44.965 | 49.403 | 4.438 | 438.98 | 5 | 47/761 |
| UDP 59.47.239.223:31733 / 28743 | 1887 | 978470 | 23.422 | 45.388 | 21.966 | 85.90 | 10 | 40/815 |
| TCP 36.104.134.106:80 / 37346 | 1774 | 11040691 | 21.664 | 39.322 | 17.658 | 100.46 | 3 | 38/1201 |
| TCP 59.47.239.175:49155 / 37788 | 1711 | 10555088 | 41.610 | 74.794 | 33.184 | 51.56 | 5 | 43/917 |
| TCP 42.202.158.116:80 / 48842 | 1692 | 10554832 | 41.649 | 74.794 | 33.145 | 51.05 | 5 | 43/917 |
| TCP 59.47.239.210:49155 / 49318 | 1554 | 10548806 | 38.377 | 70.737 | 32.360 | 48.02 | 3 | 39/1246 |
| UDP 150.139.159.155:16285 / 38142 | 1392 | 146070 | 59.471 | 876.962 | 817.491 | 1.70 | 449 | 60/35 |
| TCP 61.158.144.68:55001 / 43470 | 1017 | 5351118 | 42.520 | 69.613 | 27.093 | 37.54 | 7 | 44/334 |
| TCP 123.244.93.225:443 / 49054 | 697 | 5265789 | 34.351 | 45.975 | 11.624 | 59.96 | 3 | 34/672 |
| TCP 36.104.134.109:443 / 46426 | 666 | 4090606 | 31.823 | 45.977 | 14.154 | 47.05 | 7 | 34/544 |
| UDP 101.226.101.213:5010 / 38649 | 342 | 52298 | 59.219 | 888.861 | 829.642 | 0.41 | 167 | 59/10 |


Key endpoint timing across phone ports (inclusive one-second buckets).

Endpoint bucket runs (start–end, packet count, peak pps). The TCP 6644 row shows runs of at least three consecutive occupied seconds.

- UDP 180.102.99.167:10214: [(58, 879, 32574, 162)]
  outbound t/pps for 30-second bins: [(30, 2.73), (60, 8.7), (90, 5.53), (120, 26.43), (150, 17.37), (180, 37.5), (210, 22.5), (240, 27.33), (270, 33.77), (300, 25.23), (330, 29.43), (360, 27.57), (390, 31.77), (420, 30.47), (450, 14.5), (480, 19.67), (510, 27.4), (540, 27.73), (570, 23.93), (600, 4.1), (630, 24.53), (660, 7.4), (690, 17.67), (720, 28.87), (750, 30.2), (780, 22.5), (810, 10.73), (840, 13.23), (870, 3.47)]
  inbound t/pps for 30-second bins: [(30, 2.7), (60, 8.7), (90, 5.53), (120, 26.43), (150, 15.2), (180, 17.93), (210, 17.83), (240, 17.6), (270, 17.6), (300, 17.63), (330, 17.6), (360, 17.53), (390, 17.67), (420, 17.57), (450, 18.63), (480, 18.43), (510, 17.6), (540, 17.9), (570, 18.3), (600, 19.27), (630, 17.97), (660, 19.73), (690, 18.83), (720, 17.77), (750, 17.87), (780, 18.03), (810, 19.07), (840, 19.67), (870, 6.93)]
- TCP 36.104.134.106:80: [(21, 21, 131, 131), (38, 39, 2387, 1791), (41, 49, 20048, 3770), (76, 77, 6, 3), (79, 79, 9, 9)]
  Captured IP lengths: 10000×10915, 40×8254, 5848×601, 8752×550, 4396×324, 2944×323, 7300×250, 1696×129
- UDP 59.47.239.78:43815: [(23, 23, 1, 1), (26, 26, 1, 1), (29, 29, 1, 1), (32, 32, 1, 1), (34, 45, 5617, 1765), (48, 49, 152, 106), (51, 51, 1, 1), (54, 54, 1, 1)]
- UDP 59.47.239.223:31733: [(23, 23, 1, 1), (26, 26, 1, 1), (29, 29, 1, 1), (32, 32, 1, 1), (36, 36, 1, 1), (39, 42, 1881, 815), (45, 45, 1, 1)]
- TCP 180.102.190.141:6644: [(27, 35, 265, 111), (37, 44, 213, 62), (47, 49, 102, 48), (51, 63, 868, 119), (65, 87, 180, 18), (93, 99, 35, 9), (101, 103, 19, 8), (105, 108, 22, 6), (114, 117, 27, 9), (158, 160, 18, 12), (257, 259, 8, 4), (322, 325, 12, 4), (622, 625, 14, 4), (874, 879, 113, 64), (883, 885, 15, 7), (890, 912, 203, 30), (914, 926, 198, 34)]
  Captured IP lengths: 40×1646, 97×431, 113×345, 209×233, 161×149, 10000×121, 225×117, 145×98

- **t=0–23 s, startup or lobby candidate.** The first request to the largest CDN endpoint begins at 21.664 s. Exact UI state is UNKNOWN.
- **t=23–58 s, bulk loading or update candidate.** The two UDP bursts and the largest HTTP range transfers overlap. The biggest HTTP run is t=41–49 (20,048 packets and a peak of 3,770 pps across the endpoint). The observed 1,130-byte UDP streams stop before the prime flow starts. This timing and the download evidence below favor bulk transport over match voice for those bursts.
- **t=58.950–120 s, likely session setup or loading.** The prime flow starts during HTTP tail activity, with three zero-filled datagrams near t=59. Its directional 30-second means are 8.70 pps at t=60 and 5.53 pps at t=90. Exact lobby and loading boundaries are UNKNOWN.
- **From t≈120 to 879.488 s, likely match transport.** Rates rise at t=120 (26.43 pps in each direction over that bucket). From t=180 through the t=840 bucket, inbound averages 17.53–19.73 pps per 30-second bucket while outbound varies from 4.10 to 37.50 pps. The high sustained rate and independent counters support a gameplay-transport hypothesis. No screen recording or event log grounds exact match start, actions, kills, or match end.
- **After t=879.488 s**, the prime tuple stops. The long TCP control candidate continues to t=926.585 s, consistent with a return to lobby or session teardown. UI state is UNKNOWN.

## Prime UDP structure and encoding verdict

**Verdict: likely game logic transport.** The base rates, duration and counter behavior provide the evidence. The payload begins after the eight-byte UDP header. Prefix labels below are byte signatures. A formal message-type enumeration, lengths inside the payload, and a timestamp field are UNKNOWN.

- **Outbound counter.** The LE uint32 at payload offsets 8–11 progresses from 1,795,702,073 to 1,795,720,140 with **18,067 of 18,067** consecutive steps equal to +1. The low uint16 at offsets 8–9 behaves identically in this sample. Offsets 10 and 11 remain constant, so the flow shows at least a low-16-bit counter and does not establish the field width across a carry. The parser exposes the observed four-byte LE value.
- **Inbound counter.** On the `000b0000` family alone the LE uint16 at offsets 6–7 has **12,181 of 12,181** modular steps equal to +1 across 12,182 packets. Across inbound families, only 11,071 consecutive pairs have a literal +1 there. This field can be read on that specific family. The inbound value starts at 1 and ends at 12,182 with zero wraps in this trace. No timestamp semantics are established by either counter.
- **Outbound marker.** `3d086b17f400` first occurs at zero-based offset **9** in **199** outbound packets and is absent from **17,869** outbound and all **14,506** inbound. It overlaps the outbound counter. Its suffix `08 6b 17 f4 00` at offsets 10–14 occurs in all 18,068 outbound packets. Outbound bytes 18–21 individually have modal values `a7 bf b9 00`, each with 17,741 occurrences. On the dominant inbound family, offsets 8–10 have modal values `01 08 7b`, each with 12,180 of 12,182 occurrences. The roles of these patterns are UNKNOWN.
- **Clock candidate.** The first outbound counter value interpreted as Unix seconds is 2026-11-26T14:07:53Z, about 0.84 s after the first prime packet. The value then increments once per captured packet, suggesting a possible time-derived seed. The seed mechanism is UNKNOWN. On 890 inbound `00000000` payloads of length 24, a BE uint32 at offset 8 correlates with elapsed time (r=0.99089, linear slope 75.387 units/s, endpoints 811,491,454 and 811,562,169). Its little-endian interpretation has r=−0.00503. The field is a clock or counter candidate with UNKNOWN units or purpose, so the parser omits it.
- **Zero-filled inbound packets.** The one `00020000a7bfb900` packet occurs at t=59.003301 s. It has 32 payload bytes, UDP length 40, IP length 60, captured and original record lengths 60, and entropy 4.1875 bits/byte. Three **identical** `00030000` payloads occur at t=59.048504, 59.050092 and 59.050307 s. Each has UDP length 1,408, IPv4 header length 20, IP total 1,428, and captured/original lengths 1,428. Each has 1,395 zero bytes out of 1,400, with `03` at offset 1 and `c3 f6 81 35` at offsets 1396–1399. The entropy is 0.0425 bits/byte. The contiguous zero run at offsets 2–1395 is in the captured UDP payload. All 32,574 prime records satisfy `UDP length = IP total length − IHL` and `IP total length = captured length = original length`. The packet's purpose is UNKNOWN.
- **Encoding.** The complete byte distributions are strongly nonuniform in both directions. From offset 32 onward the inbound aggregate rises to **7.9892 bits/byte**, versus **7.0768** outbound. Fixed headers, sequence fields and actual zero runs establish visible structure. The high-entropy inbound tail is consistent with encryption, obfuscation, compression, or a mixture. The specific encoding and presence of cryptographic encryption are **UNKNOWN**. No decryption or coordinate extraction is implemented.
- **Known-plaintext and coordinates.** There are zero hits in either direction for the exact byte strings `GET `, `HTTP/`, `actor_position`, `entities`, `map_pos` and `Unity`. One outbound printable token includes the same `91DF40A8` prefix seen on the ancillary UDP flow. Its role is UNKNOWN. The float scan tests overlapping pairs of adjacent little-endian float32 values at offsets 0–63, when eight bytes are available. The best normalized-range offsets match only 16 outbound and 41 inbound packets. Using a broad signed range gives 9,231 hits at inbound offset 10, all the same pair, and at outbound offset 16 gives 1,478 hits with 1,281 distinct pairs. These are byte interpretations without corroborating positions or entity IDs. Positions and coordinate format remain UNKNOWN. Length/time Pearson r is +0.12687 outbound and −0.05794 inbound. Per-minute medians show a setup-to-sustained-traffic shift, while correlations with specific game events are UNKNOWN.

Entropy is empirical Shannon entropy in bits per byte. Per-length estimates pool bytes from all datagrams of that exact length. Chi-square compares pooled byte frequencies with a flat 256-value distribution. Protocol fields and adjacent bytes are dependent, so the statistic describes deviation from flatness and does not identify the encoding. Delta tables count consecutive time-ordered packet pairs for each offset and integer width, with signed subtraction unless explicitly marked modular.


### Prime outbound

Aggregate entropy **6.9679 bits/byte**, Pearson χ² **4121314.6** (255 df, uniform null), 256 distinct values, 1197187 bytes. Common values 00×110556, 12×31264, 2d×25592, a7×21380, 08×21146, 5b×21093, b9×19958, 6b×19813, 17×19790, bf×19588.
Prefix payload length ranges: [('002dc15b', 18068, 30, 582)]

First bytes: 00×18068

Top 4-byte prefixes: 002dc15b×18068

Top 8-byte prefixes: 002dc15bba76cf62×1, 002dc15b83ffed00×1, 002dc15b3b55a8dd×1, 002dc15bf1eda8c4×1, 002dc15b4947ed19×1, 002dc15b70cecf7b×1, 002dc15bc8648aa6×1, 002dc15bb54529dc×1, 002dc15b0def6c01×1, 002dc15b34664e63×1

Top 16-byte prefixes: 002dc15bba76cf62393d086b17f4002e×1, 002dc15b83ffed003a3d086b17f40005×1, 002dc15b3b55a8dd3b3d086b17f40005×1, 002dc15bf1eda8c43c3d086b17f40004×1, 002dc15b4947ed193d3d086b17f40004×1, 002dc15b70cecf7b3e3d086b17f40004×1, 002dc15bc8648aa63f3d086b17f40005×1, 002dc15bb54529dc403d086b17f40005×1, 002dc15b0def6c01413d086b17f40005×1, 002dc15b34664e63423d086b17f40005×1

Marker first offsets: -1×17869, 9×199
- Prefix `002dc15b`: 18068
- Prefix `00020000`: 0
- Prefix `00020000a7bfb900`: 0
- Prefix `00030000`: 0

| Offset/width | Order | Positive | Equal | Negative | +1 |
|---|---|---:|---:|---:|---:|
| 0/2 | little | 0 | 18067 | 0 | 0 |
| 0/2 | big | 0 | 18067 | 0 | 0 |
| 2/2 | little | 0 | 18067 | 0 | 0 |
| 2/2 | big | 0 | 18067 | 0 | 0 |
| 4/4 | little | 9035 | 0 | 9032 | 0 |
| 4/4 | big | 9028 | 0 | 9039 | 0 |
| 4/2 | little | 9039 | 0 | 9028 | 0 |
| 4/2 | big | 9028 | 0 | 9039 | 0 |
| 6/2 | little | 9035 | 0 | 9032 | 0 |
| 6/2 | big | 9033 | 0 | 9034 | 0 |
| 8/2 | little | 18067 | 0 | 0 | 18067 |
| 8/2 | big | 17997 | 0 | 70 | 0 |
| 8/4 | little | 18067 | 0 | 0 | 18067 |
| 8/4 | big | 17997 | 0 | 70 | 0 |
| 10/2 | little | 0 | 18067 | 0 | 0 |
| 10/2 | big | 0 | 18067 | 0 | 0 |
| 12/2 | little | 0 | 18067 | 0 | 0 |
| 12/2 | big | 0 | 18067 | 0 | 0 |
| 16/2 | little | 0 | 18066 | 1 | 0 |
| 16/2 | big | 0 | 18066 | 1 | 0 |
| 18/2 | little | 268 | 17532 | 267 | 0 |
| 18/2 | big | 268 | 17532 | 267 | 0 |
| 20/2 | little | 267 | 17532 | 268 | 0 |
| 20/2 | big | 268 | 17532 | 267 | 0 |
Prefix 002dc15b first/last: 58.950089/879.443294
Common length-minus-field relationships (offset, width, order, difference): [((0, 1, 'little', 61), 10352), ((0, 2, 'little', -11459), 10352), ((0, 2, 'big', 16), 10352), ((1, 1, 'little', 16), 10352), ((1, 2, 'little', -49392), 10352), ((1, 2, 'big', -11652), 10352), ((2, 1, 'little', -132), 10352), ((2, 2, 'little', -23428), 10352), ((2, 2, 'big', -49438), 10352), ((3, 1, 'little', -30), 10352), ((10, 1, 'little', 53), 10352), ((10, 2, 'little', -27339), 10352)]
Offset 8 LE uint32 first/last: [1795702073, 1795720140]
Payload from offset 8: entropy 6.9176
Payload from offset 16: entropy 6.9264
Payload from offset 24: entropy 7.0740
Payload from offset 32: entropy 7.0768

Gap median 23.847 ms, most common rounded-ms gaps 22×1491, 23×1235, 0×1053, 21×951, 24×631, 33×478, 1×434, 20×423, 34×396, 89×391.
Length/time Pearson r = 0.12687.
Per-minute t/count/median bytes: 0/82/46, 60/427/46, 120/1314/60, 180/1800/61, 240/1833/61, 300/1640/61, 360/1780/61, 420/1349/61, 480/1412/63, 540/1550/61, 600/859/61, 660/752/61, 720/1772/61, 780/997/61, 840/501/61

Printable runs ≥8, top ten: 8%sq_`|?×3, p|vqEB0u\×3, l"d$S%rQ×2, ,AwNGGj&Z×2, _,8PX '!×2, !91DF40A8C5E7F6F6EBEE8306E6D3912F×1, /"#$(c_G×1, c"_$E5mQ×1, s&b(EW~0×1, 1/ 13Z3I×1
Literal hits: {'GET ': 0, 'HTTP/': 0, 'actor_position': 0, 'entities': 0, 'map_pos': 0, 'Unity': 0}
Float pairs [0.001,1] with abs ≥0.001, first 64 offsets: [(41, 16, 11), (2, 12, 12), (1, 9, 9), (48, 9, 9), (52, 7, 7), (53, 6, 6), (42, 6, 5), (49, 2, 2), (43, 2, 1), (55, 2, 1)] (offset, hits, distinct).
Float pairs [-20000,20000] with abs ≥0.001, first 64 offsets: [(16, 1478, 1281), (50, 962, 962), (53, 285, 285), (2, 225, 225), (42, 222, 217), (1, 172, 172), (48, 127, 126), (52, 98, 98), (46, 91, 90), (38, 38, 37)] (offset, hits, distinct).

Length histogram and pooled entropy by length (bytes:count/entropy).

30:3/4.458 38:1/4.445 46:1141/6.306 53:1/5.322 54:16/6.227 55:94/6.466 59:1/5.370 60:96/6.445 61:10352/6.708 63:1900/6.627 64:19/6.414 65:69/6.621 66:11/6.619 67:63/6.939 68:295/6.880 69:182/6.842 70:866/7.026 71:32/6.611 72:271/6.776 73:22/6.851 74:1448/6.716 75:59/6.685 76:3/6.085 81:3/6.741 82:24/7.198 83:188/6.901 84:25/6.958 85:30/6.800 103:718/6.577 119:21/6.750 135:2/5.800 167:4/7.057 183:10/7.330 191:1/6.779 207:5/7.551 223:6/7.661 239:4/7.445 243:1/6.965 255:4/7.562 271:10/7.772 287:3/7.527 295:1/7.019 311:1/7.088 327:5/7.645 343:2/7.540 359:1/7.213 375:6/7.757 391:3/7.664 407:3/7.676 582:42/7.934

### Prime inbound

Aggregate entropy **7.8686 bits/byte**, Pearson χ² **732091.1** (255 df, uniform null), 256 distinct values, 2036184 bytes. Common values 00×70959, 01×21359, 0b×21158, 7b×19237, 08×19099, ab×18292, 06×17319, 1f×17281, 72×17215, 41×17058.
Prefix payload length ranges: [('00000000', 1994, 24, 524), ('00020000', 1, 32, 32), ('00030000', 3, 1400, 1400), ('000b0000', 12182, 35, 270), ('00350000', 163, 45, 45), ('00400000', 163, 45, 45)]

First bytes: 00×14506

Top 4-byte prefixes: 000b0000×12182, 00000000×1994, 00350000×163, 00400000×163, 00030000×3, 00020000×1

Top 8-byte prefixes: 00000000691432b1×34, 000000006914367d×34, 0000000069143268×33, 00000000691432fa×33, 0000000069143343×33, 000000006914338c×33, 000000006914308d×31, 00000000691443ed×31, 000000006914515e×29, 0000000069142f7b×26

Top 16-byte prefixes: 0000000069143a76305eedf05010ffff×8, 000000006913bccd305e65de50185544×4, 000000006913cb0d305e66c250185544×4, 000000006913cb46305e66c250185544×4, 000000006913cb7f305e66c250185544×4, 000000006913cbb8305e66c250185544×4, 00000000691433d4305ecdd95010ffff×4, 0000000069143abf305eef825010ffff×4, 000000006914515e305f65c05010ffff×4, 00030000000000000000000000000000×3

Marker first offsets: -1×14506
- Prefix `002dc15b`: 0
- Prefix `00020000`: 1
- Prefix `00020000a7bfb900`: 1
- Prefix `00030000`: 3

| Offset/width | Order | Positive | Equal | Negative | +1 |
|---|---|---:|---:|---:|---:|
| 0/2 | little | 1190 | 12177 | 1138 | 0 |
| 0/2 | big | 1190 | 12177 | 1138 | 1 |
| 2/2 | little | 0 | 14505 | 0 | 0 |
| 2/2 | big | 0 | 14505 | 0 | 0 |
| 4/4 | little | 12755 | 255 | 1495 | 0 |
| 4/4 | big | 10441 | 255 | 3809 | 1 |
| 4/2 | little | 12168 | 1190 | 1147 | 14 |
| 4/2 | big | 9575 | 1190 | 3740 | 6 |
| 6/2 | little | 12755 | 255 | 1495 | 11071 |
| 6/2 | big | 12994 | 255 | 1256 | 1 |
| 8/2 | little | 1134 | 12234 | 1137 | 0 |
| 8/2 | big | 1134 | 12234 | 1137 | 0 |
| 8/4 | little | 2098 | 10364 | 2043 | 0 |
| 8/4 | big | 2129 | 10364 | 2012 | 0 |
| 10/2 | little | 2098 | 10364 | 2043 | 0 |
| 10/2 | big | 2130 | 10364 | 2011 | 0 |
| 12/2 | little | 2523 | 9529 | 2453 | 11 |
| 12/2 | big | 2514 | 9529 | 2462 | 0 |
| 16/2 | little | 4116 | 7247 | 3142 | 81 |
| 16/2 | big | 3991 | 7247 | 3267 | 0 |
| 18/2 | little | 4154 | 7203 | 3148 | 58 |
| 18/2 | big | 4052 | 7203 | 3250 | 0 |
| 20/2 | little | 3447 | 7652 | 3406 | 0 |
| 20/2 | big | 3428 | 7652 | 3425 | 0 |
Prefix 00000000 first/last: 59.052396/879.488067
Prefix 00020000 first/last: 59.003301/59.003301
Prefix 00030000 first/last: 59.048504/59.050307
Prefix 000b0000 first/last: 59.216897/879.169837
Prefix 00350000 first/last: 64.019538/874.805920
Prefix 00400000 first/last: 64.063276/874.850397
Common length-minus-field relationships (offset, width, order, difference): [((3, 2, 'big', -81), 926), ((4, 1, 'little', -81), 926), ((12, 1, 'little', -56), 914), ((0, 2, 'big', 24), 911), ((1, 1, 'little', 24), 911), ((1, 2, 'little', 24), 911), ((15, 1, 'little', 13), 911), ((13, 1, 'little', 8), 899), ((13, 2, 'little', -65272), 891), ((0, 1, 'little', 24), 890), ((0, 2, 'little', 24), 890), ((1, 2, 'big', 24), 890)]
000b0000 offset 6 LE uint16 delta histogram: 1×12181
Payload from offset 8: entropy 7.9259
Payload from offset 16: entropy 7.9561
Payload from offset 24: entropy 7.9789
Payload from offset 32: entropy 7.9892

Gap median 64.382 ms, most common rounded-ms gaps 66×1463, 67×1414, 65×1402, 64×1007, 68×973, 69×553, 70×485, 63×484, 60×350, 1×284.
Length/time Pearson r = -0.05794.
Per-minute t/count/median bytes: 0/81/524, 60/427/97, 120/1249/81, 180/1073/169, 240/1056/177, 300/1057/152, 360/1056/165, 420/1086/164, 480/1081/154, 540/1086/157, 600/1117/155, 660/1157/133, 720/1069/157, 780/1113/148, 840/798/117

Printable runs ≥8, top ten: UD@'|%3f×5, UD!,]*3f×3, TB~$aKwj==×2, 2^B8[;28×2, #|O\f|H)×2, +MXh&K9)CD×2, Pb*~+1`tR×2, EK6MjXMiPMHdHR6v×1, UD$$a"3f×1, UD%$c"3f×1
Literal hits: {'GET ': 0, 'HTTP/': 0, 'actor_position': 0, 'entities': 0, 'map_pos': 0, 'Unity': 0}
Float pairs [0.001,1] with abs ≥0.001, first 64 offsets: [(48, 41, 41), (26, 21, 20), (46, 20, 20), (49, 14, 13), (44, 10, 10), (61, 8, 6), (63, 8, 7), (45, 7, 7), (20, 6, 6), (57, 6, 6)] (offset, hits, distinct).
Float pairs [-20000,20000] with abs ≥0.001, first 64 offsets: [(10, 9231, 1), (52, 741, 115), (23, 195, 195), (48, 193, 192), (8, 164, 17), (56, 164, 156), (40, 157, 92), (36, 157, 157), (59, 143, 141), (49, 142, 141)] (offset, hits, distinct).

Length histogram and pooled entropy by length (bytes:count/entropy).

24:890/6.272 29:9/5.649 32:1/4.188 35:21/5.959 36:2/5.541 38:36/6.264 40:12/6.167 41:128/6.571 42:128/6.564 43:27/6.761 44:128/6.791 45:410/5.979 46:120/6.872 47:129/6.866 48:89/6.970 49:171/6.938 50:62/6.881 51:161/6.911 52:4/6.076 55:1/5.536 56:1/5.457 57:1/5.622 58:1/5.548 59:4/6.503 60:6/6.738 61:3/6.478 62:3/6.428 63:9/6.816 65:3/6.398 66:1/5.791 67:2/6.191 68:1/5.764 69:3/6.528 70:1/5.776 71:1/5.896 72:3/6.668 73:3/6.677 74:3/6.670 75:4/6.908 76:6/6.975 77:9/7.186 78:3/6.796 79:1/6.041 80:2/6.503 81:638/6.362 82:2/6.331 84:2/6.510 85:8/7.221 86:3/6.951 87:8/7.240 88:9/7.351 89:8/7.345 91:1/6.104 92:1/6.172 93:19/7.619 94:8/7.381 95:4/7.164 96:3/6.984 97:117/7.033 98:8/7.444 99:7/7.369 100:9/7.430 101:22/7.620 102:10/7.499 103:12/7.584 104:8/7.479 105:18/7.620 106:19/7.644 107:19/7.670 108:22/7.693 109:36/7.757 110:26/7.720 111:17/7.659 112:26/7.684 113:94/7.458 114:30/7.711 115:24/7.701 116:31/7.729 117:43/7.754 118:37/7.743 119:40/7.766 120:46/7.773 121:47/7.767 122:47/7.774 123:54/7.785 124:45/7.779 125:74/7.790 126:58/7.794 127:57/7.798 128:78/7.800 129:93/7.806 130:78/7.804 131:85/7.813 132:103/7.815 133:102/7.813 134:108/7.820 135:92/7.827 136:106/7.836 137:109/7.831 138:108/7.835 139:112/7.835 140:122/7.842 141:132/7.855 142:121/7.844 143:133/7.842 144:122/7.848 145:146/7.814 146:128/7.851 147:155/7.858 148:144/7.859 149:146/7.855 150:153/7.858 151:127/7.861 152:144/7.864 153:184/7.865 154:154/7.874 155:148/7.872 156:140/7.874 157:172/7.887 158:184/7.890 159:161/7.875 160:169/7.885 161:170/7.887 162:149/7.883 163:173/7.891 164:170/7.899 165:163/7.894 166:139/7.898 167:152/7.898 168:165/7.896 169:150/7.904 170:148/7.907 171:173/7.907 172:134/7.904 173:145/7.908 174:137/7.908 175:139/7.913 176:142/7.910 177:127/7.914 178:142/7.913 179:116/7.924 180:128/7.910 181:111/7.911 182:127/7.922 183:112/7.923 184:98/7.921 185:111/7.924 186:92/7.926 187:108/7.926 188:86/7.928 189:116/7.935 190:85/7.923 191:95/7.929 192:91/7.937 193:99/7.921 194:74/7.932 195:63/7.924 196:70/7.932 197:86/7.932 198:53/7.924 199:58/7.922 200:48/7.917 201:63/7.917 202:52/7.926 203:33/7.923 204:38/7.912 205:41/7.921 206:32/7.909 207:25/7.902 208:29/7.907 209:53/7.879 210:36/7.916 211:25/7.901 212:28/7.904 213:24/7.901 214:17/7.890 215:18/7.892 216:22/7.887 217:25/7.916 218:28/7.911 219:17/7.878 220:14/7.866 221:29/7.918 222:19/7.901 223:13/7.888 224:11/7.893 225:23/7.824 226:15/7.878 227:12/7.895 228:15/7.898 229:10/7.872 230:10/7.852 231:9/7.862 232:12/7.899 233:9/7.860 234:6/7.821 235:7/7.826 236:7/7.826 237:11/7.878 238:11/7.872 239:6/7.846 240:2/7.546 241:12/7.769 242:6/7.799 243:3/7.667 245:5/7.811 246:1/7.111 247:3/7.684 248:4/7.794 249:2/7.590 250:3/7.728 251:2/7.521 253:3/7.700 254:1/7.143 255:2/7.568 256:3/7.699 257:1/7.121 259:2/7.603 260:1/7.247 262:1/7.240 263:1/7.139 267:1/7.175 268:1/7.194 270:1/7.218 401:2/7.661 481:3/7.760 524:158/7.968 1400:3/0.042

## Other flow verdicts

| Flow | Verdict and packet evidence |
|---|---|
| UDP `59.47.239.78:43815` and `59.47.239.223:31733` | **Likely bulk transfer.** Inbound has 2,850 and 772 payloads of exactly 1,130 bytes, while outbound is dominated by 42 bytes (1,823 and 806 packets). Main bidirectional bursts are t=34–45 and t=39–42, with inbound means 219.00 and 319.14 pps. Across both directions on both tuples there are zero first-byte `80/81` packets and zero version-2 RTP header candidates, so there is no RTP sequence or SSRC to validate. Packet entropy spans 1.614–7.805 across the two endpoints, wider than the proposed 2.4–7.5 range. Median entropy for the 1,130-byte class is 7.741 and 7.739. The repeated and alternating bytes, recurring relative-XOR prefixes, and approximately spread adjacent-packet XOR histogram support structured headers with variable bodies. They do not identify a key or encoding. Short high-volume downloads overlapping the resource update make bulk transport plausible. Opus, SILK, the exact content and the relationship to the HTTP resource are UNKNOWN. |
| TCP `36.104.134.106:80` | **Game resource CDN.** First connection, phone port 37346, was reassembled in full by TCP sequence in both directions. The span was 1,319 outbound and 10,968,384 inbound bytes with zero sequence gaps. Opening request is plaintext `GET /sgame/1212338883/2402103/res/12.1.1.42/1212338883_2402103_12.1.1.39_12.1.1.42_20261125151949_961193197_resdiff?… HTTP/1.1`, `Host: downupdate.aly.tcdnos.com`, `Range: bytes=2686976-2716744`. Opening response is `HTTP/1.1 206 Partial Content`, Tengine, `application/octet-stream`, `Content-Length: 29769`, `Content-Range: bytes 2686976-2716744/146001718`. Body starts `5c0000001e0e0000680e0000b20e0000`. The `sgame` resource-diff path and matching ranges establish resource delivery even though the User-Agent is `vodJcenzz-200046-0(4)`. Subsequent tuple openings include the same HTTP GET/206 pattern. |
| UDP `150.139.159.155:16285` | **Likely ancillary session/control traffic.** 1,392 packets over 817.491 s, with 0 wholly printable payloads. Embedded `334082698` occurs in 325 packets, `7549FF8` in 79, `91DF40A8` in 965 and `ww  ` in 83, all 83 as the first four bytes. The flow carries structured binary records with repeating decimal and hex identifiers and the printable run `close@` 85 times. The loose RTP bit test selects 85 packets per direction with constant sequence values and fixed four-byte strings at the SSRC position. This does not establish RTP. Role of identifiers, affiliation with voice, and precise protocol are UNKNOWN. |
| UDP `101.226.101.213:5010` | **Likely network-quality or telemetry exchange.** DNS maps `speed.ino.qq.com` to this address. 171 outbound and 171 inbound packets, with 167 inbound packets of 18 bytes. Matching on bytes 2–3 plus 8–13 gives 167 of 171 distinct request keys and median reply delay 45.777 ms under that matching rule. Two packets start `0102a1c4`, four contain `S::D`, and five contain `AA`. The first outbound payload is `0102a1c400000001000100030d4100040002533a3a44`. Exact vendor protocol and role of those strings are UNKNOWN. Full payloads are in the appendix. |
| TCP `180.102.190.141:6644` | **Likely game session/control.** `aqq.smoba.qq.com` returned this IP twice. The 3,801-packet, 902.132-second connection starts before the prime tuple and ends afterward. Sequence-reassembled SYN-origin prefixes start `3366000a000a100100000000010000005f00000000020300` outbound and `3366000a000a100201000000010000003000000010021048` inbound. Opening is binary without a TLS record or HTTP request/response signature. Framing and any internal encryption are UNKNOWN. |
| TCP `42.185.159.107:80` | **Game resource CDN.** The 18,779,600-byte top tuple (43858) starts with `Host: downupdate.csysw.tcdnos.com`, an `sgame` resource-diff GET, and HTTP 206 with range 21135360–21346481 of 146001718, the same resource size as the first `36.104.134.106` response. |
| TCP `61.158.144.68:55001` | **Likely ancillary bulk transfer, protocol UNKNOWN.** 9,604,572 captured bytes across the endpoint. Port 43470 alone carries 5,351,118 bytes with opening hex `6c4f21232323932222321a23` outbound and `4c6b4e6b4c6b036a4d7a766b` inbound. Other tuples on 55001 including `59.47.239.78` have similar alternating byte motifs. No HTTP or TLS opener on the sampled `61.158.144.68` connection. Relationship to the UDP bursts or game resource is UNKNOWN. |
| TCP `59.47.239.175:49155`, `59.47.239.210:49155`, `59.47.239.207:49155` | **Game resource CDN/edge.** Plain HTTP paths rooted at `/down-update.qq.com/sgame/`, 206 range responses and `Lego Server` header. The .175 response has `Content-Range: bytes 26354909184-26365394943/27184641115` and `Content-Length: 10485760`. |
| TCP `120.201.109.143:55001` | **Likely ancillary bulk transfer, protocol UNKNOWN.** 671 packets and 3,170,425 captured bytes across two connections. Port 42998 has binary opening bytes `241e1c241e24ae251f352724` outbound and `277d257d277d687c266c1d7d` inbound, with no HTTP or TLS opener. |
| TCP `42.202.158.116:80` | **Game resource CDN.** `Host: downupdate.csy.tcdnos.com`, `sgame` resource GET, openresty 206 with range 26386366464–26396852223 of 27184641115 and `Content-Length: 10485760`. |
| TCP `36.104.134.109:443`, `123.244.93.225:443` | **TLS CDN/service candidates.** Largest tuples expose ClientHello SNI `pandora.aly.tcdnos.com` and `pandora.bdy.tcdnos.com`, respectively, and receive over 4 MB of TCP payload each. HTTP paths and delivered objects are UNKNOWN. |
| TCP `218.93.129.146:8081` | **Likely telemetry.** 615 packets, DNS A answer for `game.eve.mdt.qq.com`, and the captured outbound opening includes `TYPE_COMPRESS`. Application message schema is UNKNOWN. |


Detailed statistics for the named UDP peers follow.

### UDP ('59.47.239.223', 31733, 28743)

- outbound: 926 packets, t=23.422099–45.388319, entropy min/median/max 2.316/4.230/5.168. Lengths 42×806, 69×62, 73×23, 47×8, 77×8, 34×7, 211×5, 65×3, 81×2, 124×1, 117×1. Prefixes 722b5159×3, 5b545354×3, 520c0452×3, 54115c11×3, 47434b47×3, 0d252d0d×3, 657e6d7e×3, 1d41545c×3, 5822727a×3, 4c56121a×3.
  80/81 first bytes: 0. RTP-v2 candidates: 0, SSRC , sequence deltas .
- inbound: 961 packets, t=39.037423–42.048635, entropy min/median/max 2.316/7.731/7.797. Lengths 1130×772, 52×90, 42×56, 48×28, 34×7, 101×5, 293×1, 1071×1, 99×1. Prefixes 51336a62×2, 1d091c14×2, 0f45424a×2, 21404821×2, 7d7e757e×2, 39767e39×2, 5a30385a×2, 26737b26×2, 5f287f77×2, 53702b23×2.
  80/81 first bytes: 0. RTP-v2 candidates: 0, SSRC , sequence deltas .
  Offset 0, width 8 normalized by XOR with first byte of slice: 00040c0004046c01×12, 00070f0007046f01×12, 0061690061040901×11, 0066086600626867×9, 00555d0055043d01×9
  Offset 12, width 12 normalized by XOR with first byte of slice: 0000000000000004544140b8×165, 0000000000000004542714f9×95, 0007000700070003544640bf×8, 0012001200120016545340aa×7, 0004000400040000544540bc×7
  Offset 0, width 24 normalized by XOR with first byte of slice: 001208120016681301e828120012001200120016545340aa×4, 00767e0076041e0177fa5e007600760076007604224136b8×4, 00222a0022044a0123fa0a002200220022002204764162b8×4, 00090809000d680801151b09000900090009000d544840b1×4, 005708570053685601f657570057005700570053547014ae×4
  Alternating repeat at offsets 12–17: 772/772.
  1130-byte packets: 772, median packet entropy 7.739, run lengths ≥8 8×275, 12×263, 9×207, 13×2, 14×1, successive packet XOR 122×4083, 10×4082, 113×4071, 15×4056, 70×4048, 85×4027, 68×4016, 110×4013 out of 871230 bytes. First 32 bytes: 261a2e1a261e4e1b2762141a261a261a261a261e7263255b831a261a264a200a.

### UDP ('59.47.239.78', 43815, 28743)

- outbound: 2384 packets, t=23.425648–54.794544, entropy min/median/max 1.614/4.291/5.213. Lengths 42×1823, 69×319, 73×92, 77×55, 81×21, 85×21, 34×12, 211×12, 47×11, 89×11, 65×7. Prefixes 37231c14×4, 4b51121a×4, 0b3d033d×4, 07181007×3, 29292129×3, 47723d35×3, 6d06636b×3, 0e150615×3, 604e4660×3, 3b0d330d×3.
  80/81 first bytes: 0. RTP-v2 candidates: 0, SSRC , sequence deltas .
- inbound: 3391 packets, t=34.056545–49.540864, entropy min/median/max 1.969/7.734/7.805. Lengths 1130×2850, 52×353, 42×113, 48×42, 34×12, 101×12, 598×1, 641×1, 432×1, 256×1, 1055×1, 331×1. Prefixes 5d194c44×4, 60771f17×3, 2e131b2e×3, 32261c14×3, 32523a52×3, 7e22545c×3, 4f0f074f×3, 4e1c144e×3, 57575f57×3, 28082820×3.
  80/81 first bytes: 0. RTP-v2 candidates: 0, SSRC , sequence deltas .
  Offset 0, width 8 normalized by XOR with first byte of slice: 0075087500716874×36, 0049410049042101×36, 00090809000d6808×33, 0040480040042801×32, 004c44004c042401×32
  Offset 12, width 12 normalized by XOR with first byte of slice: 0000000000000004549c5798×344, 000000000000000454748859×336, 000000000000000454eee928×124, 00000000000000045455f60e×37, 000000000000000454c14091×33
  Offset 0, width 24 normalized by XOR with first byte of slice: 0070780070041801710a450070007000700070042474f859×7, 006a62006a0402016b0a5f006a006a006a006a043e74e259×5, 0049410049042101480a7c0049004900490049041d74c159×5, 00464e0046042e01470a730046004600460046041274ce59×5, 006f086f006b686e01c0296f006f006f006f006b54f357f7×4
  Alternating repeat at offsets 12–17: 2850/2850.
  1130-byte packets: 2850, median packet entropy 7.741, run lengths ≥8 8×913, 12×910, 9×167, 13×14, 11×4, successive packet XOR 0×14749, 121×14519, 27×14435, 40×14322, 41×14303, 55×14243, 19×14217, 59×14215 out of 3219370 bytes. First 32 bytes: 337e454d4d49254c4cac044d4d4d4d4d4d4d4d49198c0ddc434d4d4d4d1d4b5d.
### UDP ('150.139.159.155', 16285, 38142)

- outbound: 643 packets, t=59.471359–876.884545, entropy min/median/max 4.989/5.083/5.683. Lengths 110×162, 67×146, 66×127, 142×81, 65×54, 158×40, 64×26, 70×6, 160×1. Prefixes 29091820×157, bbbb0311×85, 77772020×42, 28287900×6, 2828fd00×4, 28288b00×4, 2828ad00×4, 28284500×4, 2828ba00×4, 28281500×4.
  80/81 first bytes: 0. RTP-v2 candidates: 85, SSRC 34303832×85, sequence deltas 0×84.
- inbound: 749 packets, t=59.523372–876.962467, entropy min/median/max 4.329/5.154/6.601. Lengths 61×162, 67×144, 65×138, 66×128, 27×85, 70×45, 64×16, 115×4, 110×4, 69×3, 104×3, 200×3. Prefixes bbbb0311×85, 77772020×41, 29299200×26, 28283c00×8, 28282300×6, 2828aa00×6, 28284900×6, 28287b00×6, 28285500×5, 28280500×5.
  80/81 first bytes: 0. RTP-v2 candidates: 85, SSRC b9c0be95×85, sequence deltas 0×84.

All-printable packets 0, distinct direction/payload pairs 0.
Embedded literals: {'ww  ': 83, '334082698': 325, '7549FF8': 79, '91DF40A8': 965}

## DNS, TLS and mixed services

The probe found 182 outbound UDP/53 queries with 182 response questions and 92 distinct queried names. IPv4 answer records include 91 distinct owner names, including aliases. Examples include `aqq.smoba.qq.com → 180.102.190.141`, `speed.ino.qq.com → 101.226.101.213`, and `cn.voice.gcloudcs.com → 180.101.246.28, 180.101.246.33, 222.94.109.19, 222.94.109.250`. The voice DNS answers do not match either of the candidate bulk UDP peers.

The probe recovered 168 TCP ClientHello SNI observations for 50 distinct hostnames. UDP inspection found zero standard QUIC v1/v2 long-header candidates under the version and connection-ID checks. QUIC SNI is UNKNOWN. The check does not cover unknown QUIC versions or short headers. The capture includes telemetry, Tencent push and WeChat-related services. For example, `access1.tpns.sh.tencent.com` appears in 13 DNS questions and 15 SNI observations, `game.weixin.qq.com` in two DNS questions and one SNI observation, and `wx.qlogo.cn` in two questions and four SNI observations. `ipv4only.arpa` appears in two queries and has two IPv4 answers. The originating Android process for those packets is UNKNOWN.

Queried names and counts (A and AAAA pooled).


- `0046c9a1b90646518ea837091bdebf7c.tgpa.imtmp.net` ×1
- `access1.tpns.sh.tencent.com` ×13
- `android.crashsight.qq.com` ×1
- `android.perfsight.qq.com` ×2
- `apd-pcdniegwzlogin.teg.tencent-cloud.net` ×2
- `apd-pcdnvodstat.teg.tencent-cloud.net` ×2
- `apd-vodp2plogin.teg.tencent-cloud.net` ×2
- `apd-vodp2pnat.teg.tencent-cloud.net` ×2
- `apd-vodp2preport.teg.tencent-cloud.net` ×2
- `apd-vodp2ptracker.teg.tencent-cloud.net` ×2
- `api.pr.weixin.qq.com` ×1
- `api.unipay.qq.com` ×1
- `api.xunyou.mobi` ×1
- `apm3437-5-1258344700.cos.ap-nanjing-dev.myqcloud.com` ×1
- `app.ingame.qq.com` ×2
- `aqq.smoba.qq.com` ×2
- `cc.map.qq.com` ×1
- `cfg.imtt.qq.com` ×2
- `cloudctrl.gcloud.qq.com` ×1
- `cn.voice.gcloudcs.com` ×2
- `control.mna.qq.com` ×2
- `cqaqq.smoba.qq.com` ×2
- `cqawx.smoba.qq.com` ×2
- `cqiqq.smoba.qq.com` ×2
- `csy.pandora.tcdnos.com` ×2
- `dir.1212338883-2-1.gcloudsvcs.com` ×2
- `dldir1.qq.com` ×1
- `dlied5.qq.com` ×2
- `down-update.qq.com` ×2
- `down.anticheatexpert.com` ×2
- `down.pandora.qq.com` ×3
- `download.2.1212338883.wz.gcloudgbs.com` ×2
- `downupdate.aly.tcdnos.com` ×2
- `downupdate.bdy.tcdnos.com` ×2
- `downupdate.csy.tcdnos.com` ×2
- `downupdate.csysw.tcdnos.com` ×2
- `estv-op.tga.qq.com` ×1
- `faasyxzj.native.qq.com` ×9
- `flow.qq.com` ×2
- `galileotelemetry.tencent.com` ×2
- `game.eve.mdt.qq.com` ×6
- `game.gtimg.cn` ×1
- `game.str.mdt.qq.com` ×2
- `game.weixin.qq.com` ×2
- `guid.tpns.sh.tencent.com` ×1
- `h.trace.qq.com` ×1
- `hc2.tdm.qq.com` ×1
- `idcconfig.gcloudsdk.com` ×1
- `image.ecology.smoba.qq.com` ×6
- `image.smoba.qq.com` ×2
- `img.ssl.msdk.qq.com` ×2
- `ipv4only.arpa` ×2
- `isp-map.xunyou.mobi` ×1
- `jsonatm.broker.tplay.qq.com` ×1
- `kohcloud.tgpa.qq.com` ×3
- `log.tbs.qq.com` ×1
- `measurement.cq.prod.smoba.qq.com` ×1
- `measurement.gz.prod.smoba.qq.com` ×1
- `measurement.sh.prod.smoba.qq.com` ×1
- `measurement.tj.prod.smoba.qq.com` ×1
- `msdk.qq.com` ×6
- `mtcls.qq.com` ×1
- `nj.cschannel.anticheatexpert.com` ×1
- `njawx.smoba.qq.com` ×2
- `op.tv.kohesport.qq.com` ×2
- `pandora.aly.tcdnos.com` ×2
- `pandora.bdy.tcdnos.com` ×2
- `pandora.csysw.tcdnos.com` ×2
- `pay.xunyou.mobi` ×1
- `pop-release.itop.qq.com` ×1
- `portal.xunyou.mobi` ×1
- `prodsgamehub.ecology.smoba.qq.com` ×2
- `pvp.ingame.qq.com` ×4
- `qosidc.gcloudsdk.com` ×2
- `qt.qq.com` ×1
- `receiver.tdm.qq.com` ×1
- `sgame.itop.qq.com` ×1
- `smobatv-pic.tga.qq.com` ×2
- `speed.ino.qq.com` ×1
- `static-estv.tga.qq.com` ×1
- `superr.game.qq.com` ×2
- `szmg.qq.com` ×1
- `tbsrecovery.imtt.qq.com` ×1
- `thirdqq.qlogo.cn` ×2
- `tiem-cdn.qq.com` ×2
- `tools.tmga.qq.com` ×3
- `tux.qq.com` ×2
- `welive.qq.com` ×2
- `wuji-1254960240.file.myqcloud.com` ×1
- `www.baidu.com` ×1
- `wx.qlogo.cn` ×2
- `yxzj.broker.tplay.qq.com` ×1

TCP ClientHello SNI names and counts.

- `access1.tpns.sh.tencent.com` ×15
- `android.crashsight.qq.com` ×1
- `android.perfsight.qq.com` ×2
- `api.unipay.qq.com` ×1
- `api.xunyou.mobi` ×1
- `apm3437-5-1258344700.cos.ap-nanjing-dev.myqcloud.com` ×2
- `app.ingame.qq.com` ×1
- `cc.map.qq.com` ×1
- `cfg.imtt.qq.com` ×2
- `cloudctrl.gcloud.qq.com` ×1
- `csy.pandora.tcdnos.com` ×2
- `dldir1.qq.com` ×2
- `dlied5.qq.com` ×1
- `down.anticheatexpert.com` ×2
- `down.pandora.qq.com` ×5
- `estv-op.tga.qq.com` ×3
- `faasyxzj.native.qq.com` ×8
- `flow.qq.com` ×1
- `galileotelemetry.tencent.com` ×1
- `game.gtimg.cn` ×1
- `game.weixin.qq.com` ×1
- `h.trace.qq.com` ×12
- `hc2.tdm.qq.com` ×1
- `idcconfig.gcloudsdk.com` ×1
- `image.ecology.smoba.qq.com` ×11
- `image.smoba.qq.com` ×2
- `img.ssl.msdk.qq.com` ×5
- `kohcloud.tgpa.qq.com` ×6
- `log.tbs.qq.com` ×1
- `op.tv.kohesport.qq.com` ×1
- `pandora.aly.tcdnos.com` ×3
- `pandora.bdy.tcdnos.com` ×1
- `pandora.csysw.tcdnos.com` ×1
- `pop-release.itop.qq.com` ×3
- `portal.xunyou.mobi` ×7
- `prodsgamehub.ecology.smoba.qq.com` ×2
- `pvp.ingame.qq.com` ×2
- `receiver.tdm.qq.com` ×20
- `sgame.itop.qq.com` ×7
- `smobatv-pic.tga.qq.com` ×1
- `static-estv.tga.qq.com` ×1
- `superr.game.qq.com` ×1
- `szmg.qq.com` ×3
- `tbsrecovery.imtt.qq.com` ×1
- `thirdqq.qlogo.cn` ×10
- `tiem-cdn.qq.com` ×4
- `tux.qq.com` ×1
- `welive.qq.com` ×1
- `wuji-1254960240.file.myqcloud.com` ×1
- `wx.qlogo.cn` ×4

## Server contract recommendation

**Keep v1** for this implementation. Use `GET /snapshot` and `POST /api/client/upload`, Base64 payloads and the decimal revision in the `X-Kite-Snapshot` response header. This PCAP records phone-to-game-server traffic and ancillary services. It does not record phone-to-our-server traffic. The configured deployment IP `39.96.60.127` appears in zero probed TCP/UDP phone-flow packets. The capture therefore cannot directly prove the reference contract and supplies no reason to migrate v1.

The separate APK evidence establishes a reference client contract with `GET /v1/rooms/{room}/snapshot`, `POST /v1/rooms/{room}/datagrams`, hex payloads, `accepted_batch` and fixed **request** header `X-Kite-Snapshot: radar-v1`. The reference build is `com.xiaobu.fengzheng` 1.4.7 (versionCode 21, SHA-256 `0ddd6b94ba5baca44dd4e797ceb8afba706588cc91a45a4b047fc619baf547a2`). Compatibility with that client would be a separate requirement backed by the APK evidence. [RADAR_REFERENCE.md](RADAR_REFERENCE.md)

The new offline parser filters the captured UDP tuple by direction, four-byte signature and observed payload length ranges. It exposes the two counters under those signatures. `parse(datagrams)` returns an empty entity array. Current HTTP input has only direction and payload, so the endpoint-dependent helper remains an offline operation. `server/main.py` and the deployed service were left untouched.

## Methods

The baseline and independent probes used only Python 3 standard-library modules. The probe streams raw IPv4 records, checks IP and transport bounds, groups directional observations by bidirectional tuple, and retains payloads for selected UDP flows. It writes the first CDN session at TCP sequence offsets in temporary disk files and measures coverage. Other TCP flows use a sequence-sorted contiguous prefix of up to 16 KiB per direction, sufficient for the reported HTTP headers and TLS ClientHellos. DNS names are decoded from UDP question and answer records with compression-pointer handling. QUIC was checked by header signature only. The HTTP smoke check exercised the existing server with its installed YAML dependency and in-memory connection objects, with no socket or deployment access.

The initial deep-probe run stopped with a `NameError` in the DNS query count. After replacing the undefined summand with a per-query increment, the complete probe ran successfully. The capture was streamed throughout.

## Reproducibility

Run from the workspace root.

```bash
capture=~/workspace/hok-capture/pcapdroid-20261126.pcap
python3 tools/analyze_pcap.py "$capture" --local-ip 10.215.173.1 --top 20 > /tmp/hok-baseline.txt
python3 tools/probe_hok_pcap.py "$capture" --local-ip 10.215.173.1 --buckets /tmp/hok-buckets.tsv > /tmp/hok-probe.txt
python3 -m py_compile server/main.py server/hok_parser.py tools/probe_hok_pcap.py server/test_hok_parser.py
HOK_PCAP="$capture" python3 -m unittest -v server.test_hok_parser
python3 -m server.hok_parser "$capture" --local-ip 10.215.173.1
```

Compilation exited zero. The in-memory HTTP smoke check passed initial `GET /snapshot` with revision header 0, standard Base64 `POST /api/client/upload` returning `{"accepted":1,"revision":1}`, and `GET /snapshot` with revision header 1 and body `{"revision":1,"entities":[]}`.

Unit test output.

```text
test_observed_counters (server.test_hok_parser.HonorOfKingsParserTest.test_observed_counters) ... ok
test_observed_signatures (server.test_hok_parser.HonorOfKingsParserTest.test_observed_signatures) ... ok
test_real_prime_datagrams_return_no_entities (server.test_hok_parser.HonorOfKingsParserTest.test_real_prime_datagrams_return_no_entities) ... ok
test_unknown_signature_or_tuple (server.test_hok_parser.HonorOfKingsParserTest.test_unknown_signature_or_tuple) ... ok

----------------------------------------------------------------------
Ran 4 tests in 1.554s

OK
```

Offline PCAP self-check output.

```text
Prime UDP datagrams: 32574
inbound prime/inbound/00000000: 1994
inbound prime/inbound/00020000: 1
inbound prime/inbound/00030000: 3
inbound prime/inbound/000b0000: 12182
inbound prime/inbound/00350000: 163
inbound prime/inbound/00400000: 163
outbound prime/outbound/002dc15b: 18068
Observed counters: {'outbound': 18068, 'inbound': 12182}
Entities: 0. Coordinate layout and body encoding are UNKNOWN.
```

## Appendix · Full UDP 5010 payloads

Each row has elapsed seconds, direction and the captured UDP payload in hex.

```text
59.218871 outbound 0102a1c400000001000100030d4100040002533a3a44
59.266118 inbound 0102a1c4000003e9000400030d41000200004141
59.380219 outbound 010226ad00000001000100030d4200040002533a3a44
59.425439 inbound 010226ad000003e9000400030d42000200004141
59.426114 outbound 01025b8a00000001000100030d4300040002533a3a44
59.477050 inbound 01025b8a000003e9000400030d43000200004141
59.477591 outbound 01025e8e00000001000100030d4400040002533a3a44
59.523131 inbound 01025e8e000003e9000400030d44000200004141
59.628405 outbound 0102fb7700000001000c00030d4500a200122db3b1afc78a764a41d4d38400000001009038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33ae1375ac4b2acde229b858f6eee25c9dfd4e20b6f0d296e26bf543db58ec702dcbc6e9c5e6a11140882b5c73836ab7f66fe218783f33dc9a4e0b38d1b7af2179ce9281e2e9bb9b30f60ff11d58cede94664a1c524c5d0cb35a7127a207350774
59.675690 inbound 0102fb77000003e9000c00030d4500000000
64.625139 outbound 0102ac7400000001000c00030d4600c200122db3b1afc78a764a41d4d3840000000200b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
64.669380 inbound 0102ac74000003e9000c00030d4600000000
69.624938 outbound 0102d15300000001000c00030d4700c200122db3b1afc78a764a41d4d3840000000300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
69.671212 inbound 0102d153000003e9000c00030d4700000000
74.624558 outbound 0102b8b800000001000c00030d4800d200122db3b1afc78a764a41d4d3840000000400c038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984332b9f79ba00e41a367773cfee889d84dfd9de2ad385322d62f00c18e38023056e4594eac21bb6e08c84875f0d48bb8504859ca76d67d3252a91222454fd008b40810eed0fd64a2ea46f83365209395c67
74.673214 inbound 0102b8b8000003e9000c00030d4800000000
79.624822 outbound 0102adaa00000001000c00030d4900c200122db3b1afc78a764a41d4d3840000000500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
79.693339 inbound 0102adaa000003e9000c00030d4900000000
84.624601 outbound 01029ae500000001000c00030d4a00e200122db3b1afc78a764a41d4d3840000000600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36cb22cd125063e3188df88ebd5e7ed6f97be3fb8f28d289329b560bc44e96035f1ac610a31f5fb5e6fd345b990e21f4ab8b86b077d3930cf98464206892e14c252deaedce7c7e440a64dc202c8f45e99dd6ba03491c15359901160f0769c3c094fb0b5efd87b8f8f113824addaa1b055a
84.696224 inbound 01029ae5000003e9000c00030d4a00000000
89.625800 outbound 010257e400000001000c00030d4b00c200122db3b1afc78a764a41d4d3840000000700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c36f2bfc818399e2e0da2aaa7e326ea032f3b0b68b9e2327acc2c077ac671b6b1339d69972b0706d8f30cbabd90c862fa877937b504a88a24c0bcea2b4bbebc929b570e0c9ea628a80c6bba01a157cac
89.692898 inbound 010257e4000003e9000c00030d4b00000000
94.624506 outbound 0102e2c600000001000c00030d4c00e200122db3b1afc78a764a41d4d3840000000800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36cb22cd125063e3188df88ebd5e7ed6f9d44c85d909445ef05b84989189211051410f64bbfd6e817e18e25a9442781b981d1b0ae246f7a76ae12a1a76a5545ebace2d637b3d9ad2301fa3f8f6d8c46abb3fcb57de7dd6889686c652e1090fc181cd669ebfd76bff7df24b50f7a14310da
94.703073 inbound 0102e2c6000003e9000c00030d4c00000000
99.625309 outbound 01022fc700000001000c00030d4d00c200122db3b1afc78a764a41d4d3840000000900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36fb0b16e609f0f266022b97011020ca115276d5dde5e24c189e181349b5d5e184f8ea5a7a141f509f69169f9d994cccb986f8dfe4479baac429cfb8443b3ca6a6cfdfe09274135a72b1e320aba858e576
99.699372 inbound 01022fc7000003e9000c00030d4d00000000
104.624933 outbound 0102188800000001000c00030d4e00e200122db3b1afc78a764a41d4d3840000000a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36f870083fc5185a85db26848d26b95c89fe6eae77eaf829ae8f3bcce51f69fcf679dc79fcb4ce82de0eced8669c9edd0f594e4604d63a6ecb41570282ef2f82322bf66e651f8e1c43e9074ab928d20edf708f4de498e8558c57ca87c6d2be26e75452e6457264e0bd5e76ec4065969504
104.684018 inbound 01021888000003e9000c00030d4e00000000
109.624651 outbound 0102d58900000001000c00030d4f00c200122db3b1afc78a764a41d4d3840000000b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360f00a2c67e5e16bf6fa02b98990697a95f7e88b6401b2ecc5d98c0dbf33f3769f18829ae8a7b3744869ce6fb2c55eb8ae82b19412cfe373a676ebfd3857f086200784d4ef01bda4464dde3f8a52b6a86
109.673148 inbound 0102d589000003e9000c00030d4f00000000
114.624649 outbound 01026dc500000001000c00030d5000e200122db3b1afc78a764a41d4d3840000000c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ff3afd9a21d153515ab9d8ec508d66864dce873c7e8630351d8eca6fc0935292e1b0d8f9c24029c879e801f9dd10bed196b5f3fc91434717dabbe64fb984ee64c246b7e4ee3392ca4bb1bb5720269ff0f16300bddb78b102cfc3d75aa236e92434
114.673416 inbound 01026dc5000003e9000c00030d5000000000
119.624409 outbound 0102a0c400000001000c00030d5100c200122db3b1afc78a764a41d4d3840000000d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
119.670097 inbound 0102a0c4000003e9000c00030d5100000000
124.624776 outbound 0102978b00000001000c00030d5200e200122db3b1afc78a764a41d4d3840000000e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f98433907c72ead1499b681a485c9e0e3a2ee44f32fa59bf07e8ec3671d2ba14f72647f4014cafea85adac7095e6e83e48ff575f043c3f67fc06a2b3da0a0a9f43f585dece0fcaf7ec3b318c96cebfc9bf35e733304d74484570b5f1bfc15d864be0d4
124.709482 inbound 0102978b000003e9000c00030d5200000000
129.624483 outbound 01025a8a00000001000c00030d5300c200122db3b1afc78a764a41d4d3840000000f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c1aa96fcd1147ddb14de35b15bc0856473d7b96908c191479e18bb56eb87d6a917005663ac161e430bc5694842f855608e745ec9a91eeed801f53356b7b0cc5fcf4ba38cd886df7302bfd7bfcab38e94
129.669811 inbound 01025a8a000003e9000c00030d5300000000
134.624548 outbound 0102efa800000001000c00030d5400e200122db3b1afc78a764a41d4d3840000001000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49052396a9ff6f2d92eeb889361c54e908291708884321a686887df137b5b3400088b34afcc5908731fd755f72d5aee6814def15577c0ddcd590794b923b0a6d9e13f05c7c46ff1e4a19fdb9e30475ed1be994e5dba25f30145638e012470d62a4
134.672596 inbound 0102efa8000003e9000c00030d5400000000
139.624648 outbound 010222a900000001000c00030d5500c200122db3b1afc78a764a41d4d3840000001100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
139.671368 inbound 010222a9000003e9000c00030d5500000000
144.624982 outbound 010215e600000001000c00030d5600e200122db3b1afc78a764a41d4d3840000001200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843324441f44c21b48976d5ac7717fe424965172c5f05dd3b448e7539d7423cec47a6b08a55b69c56957575e019a57b6167fe4ca66d5336c30bdbba37de46d4e0fba8b155450b22e32b2ebe0f031135b46a57f460199fcd516fc8aba8ab1968e371c
144.679949 inbound 010215e6000003e9000c00030d5600000000
149.624789 outbound 0102d8e700000001000c00030d5700c200122db3b1afc78a764a41d4d3840000001300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36d2b99eb36c8f2784edec0a635e3dbec88635aef87f5402541dff0e31c2ce354fec4be361bb5e296f3100c2701d42c8f796a0d78bafcf580f2c8bc8a40ac8e7e5b15d0275fbbc02c642751b72000ed582
149.681030 inbound 0102d8e7000003e9000c00030d5700000000
154.625024 outbound 0102691f00000001000c00030d5800e200122db3b1afc78a764a41d4d3840000001400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36d8d89ee70a054d48abe3cc4929819d00f4db1cdeb91e090627b8ff05ac69367acd43cc4ec3008cedb5585e8376b3aa34de3da12b5c7d88120294c2e24f603ac2ceb570ad9e5d0ae4024cc8f64c556634b9ac96cbd0bb4552119f06074b4e034024deef90720b7c469b1cc4cef0aab6b2
154.671612 inbound 0102691f000003e9000c00030d5800000000
159.633001 outbound 0102a41e00000001000c00030d5900c200122db3b1afc78a764a41d4d3840000001500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
159.677857 inbound 0102a41e000003e9000c00030d5900000000
164.624700 outbound 0102935100000001000c00030d5a00e200122db3b1afc78a764a41d4d3840000001600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365a9dc15f5912831f21add30c9d48192421ad97a7206c1efad6f75dea97e9c01ba5c81dd62ac48e12bba82a90d713e81d97a5328e777cd2fe952bebeec9ced15e3b11c50f50b7f7283b2fdec5de02ac7d8e93b486854b4fcc8a2e7482f418226c9c7560f8d355be37aabbcb4a78988ea4
164.673779 inbound 01029351000003e9000c00030d5a00000000
169.624447 outbound 01025e5000000001000c00030d5b00c200122db3b1afc78a764a41d4d3840000001700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
169.669122 inbound 01025e50000003e9000c00030d5b00000000
174.624442 outbound 0102eb7200000001000c00030d5c00e200122db3b1afc78a764a41d4d3840000001800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b491744f445c3dc3bd0ac9b2945c4dee9ea2600527cc8d4f1eaeceb17e0c16061bd0346ae459dc4217ad87f13a210188fac66a939998bb2e6216aaab262778cdee3765341aeb42b56f7206ca53e1e8a6b78c51a180cc2f3245025991e93bd8f2d71
174.673659 inbound 0102eb72000003e9000c00030d5c00000000
179.625142 outbound 0102267300000001000c00030d5d00c200122db3b1afc78a764a41d4d3840000001900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
179.672111 inbound 01022673000003e9000c00030d5d00000000
184.624586 outbound 0102113c00000001000c00030d5e00e200122db3b1afc78a764a41d4d3840000001a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586cf3da63b3992f1b02d2b9f20e8feeffb3862f6890d0352032b0d7e3060fac33c0c440280091d13e35ab9597a66c2a60c47b76e843cba9c973c52e804c560a5f188b168162808de7f67bbdb6acd264a5c124be084d532f5428b57bb721fdace34e
184.669237 inbound 0102113c000003e9000c00030d5e00000000
189.624452 outbound 0102dc3d00000001000c00030d5f00c200122db3b1afc78a764a41d4d3840000001b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
189.673559 inbound 0102dc3d000003e9000c00030d5f00000000
194.624745 outbound 01023ec800000001000c00030d6000f200122db3b1afc78a764a41d4d3840000001c00e038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ff7de4fe2f45fc4c27720e9c27d31a8707829ee747fc0f8236ba1915c7f8b9a611564eb4e4c8ffaec2f0547362b54c01190edf23df9ad0f41c9a28442c6af2b50d6c69fdd73a7e3ce16d3548e969a6c7a5978cd4cad3eb6346cbd78ca87a77783d67ddd5e717c9a7ac510b3396c1e14692
194.669303 inbound 01023ec8000003e9000c00030d6000000000
199.624509 outbound 0102cce900000001000c00030d6100c200122db3b1afc78a764a41d4d3840000001d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
199.671500 inbound 0102cce9000003e9000c00030d6100000000
204.624437 outbound 0102fba600000001000c00030d6200e200122db3b1afc78a764a41d4d3840000001e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984334220e3ad9646a2b5e8ee9f3af3f4ef7851bc1adf151251de833bd82aa8fecd56cc1add987be5e78b41b5894f36758b5c3cfe81e3fc734125a8d5d818423e88e0d080c73ab7f1c69d4bf067d8f78252667e3de3887f378aaba75d66f3b6211cb3
204.670469 inbound 0102fba6000003e9000c00030d6200000000
209.624504 outbound 010236a700000001000c00030d6300c200122db3b1afc78a764a41d4d3840000001f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
209.673170 inbound 010236a7000003e9000c00030d6300000000
214.624483 outbound 0102838500000001000c00030d6400e200122db3b1afc78a764a41d4d3840000002000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffc1113e2696b1730c7703e2c98f83bb284a906082c2c75af09c8f6d9f3e6c8646eb71a3ab2970f817c943e9564110f765a7f349c6b32c87aa7af5b3e4d9b659ff8fc82bdda9e8a3f1f134bd16f2d9470c12165f6dd6b3fa63c40a9dee8ab4316b
214.673278 inbound 01028385000003e9000c00030d6400000000
219.624457 outbound 01024e8400000001000c00030d6500c200122db3b1afc78a764a41d4d3840000002100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
219.669581 inbound 01024e84000003e9000c00030d6500000000
224.625209 outbound 010279cb00000001000c00030d6600e200122db3b1afc78a764a41d4d3840000002200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49d02523dfb39057753ba18ad65fa4be345bcfd0693b7d87d578fc4627e82406d2aac3df652fb01430097388c429c247f8c39168eb683ec47f02dcee802cd153a94f9320f0af1098d28afa0b003a9d23776c4e4cdbdb1dc2a5a11359d52a2cdcab
224.673573 inbound 010279cb000003e9000c00030d6600000000
229.624637 outbound 0102b4ca00000001000c00030d6700c200122db3b1afc78a764a41d4d3840000002300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
229.669485 inbound 0102b4ca000003e9000c00030d6700000000
234.624639 outbound 0102053200000001000c00030d6800e200122db3b1afc78a764a41d4d3840000002400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49b561ccc3534b1b1aaee9437f152f2785f19d761c9a15b4df5765d10695672b8de5c3f941298c1ec2816c92c6539f6637f91fc0b3babbd3707d6101f72312eec5258156f1eccdcdd800ee94df2f57d85c148f0a2b8ed8cbbf9403a8b984e5dda8
234.669679 inbound 01020532000003e9000c00030d6800000000
239.624642 outbound 0102c83300000001000c00030d6900c200122db3b1afc78a764a41d4d3840000002500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
239.669990 inbound 0102c833000003e9000c00030d6900000000
244.624604 outbound 0102ff7c00000001000c00030d6a00e200122db3b1afc78a764a41d4d3840000002600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b5d4d7dbeac665f1f589d1f22bbd76f7f50d3ca535740c07a39d0fdaea62691d7b59d36a5e35de624ce9cb6caf594b51fa9ddc1ff8758809e0f0e1dfb683088c95cbbccae5c2650b580b13b05d0cc211b8a0919ef4cfe23610721f0d283287f5b
244.669909 inbound 0102ff7c000003e9000c00030d6a00000000
249.624428 outbound 0102327d00000001000c00030d6b00c200122db3b1afc78a764a41d4d3840000002700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
249.669926 inbound 0102327d000003e9000c00030d6b00000000
254.624543 outbound 0102875f00000001000c00030d6c00e200122db3b1afc78a764a41d4d3840000002800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab03f5f10f0dee520d213f62ad9798cefe56de6e67afebbaeb54dd1cb3dbe65da69e6b8207a268497a16ca62374abf4274c19f277c3b25016d808eef0eb7efd2356fce1dfcf8ea8a0908bdd414ab3651d1b
254.674123 inbound 0102875f000003e9000c00030d6c00000000
259.625983 outbound 01024a5e00000001000c00030d6d00c200122db3b1afc78a764a41d4d3840000002900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b362417c83712cc1357a6fa04b79c50f697acc875f84a385e3185c0018626ba7084e1cad6d0befbf593bc00ee0dd59376873fd4d230e90cbfcecf081ff56d087fbfc3a972224cdb9c5f263512acfa207afa
259.671816 inbound 01024a5e000003e9000c00030d6d00000000
264.624493 outbound 01027d1100000001000c00030d6e00e200122db3b1afc78a764a41d4d3840000002a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984337c8c5121692b20b232839f58ff36f597d0782b6d0cc49ef0bdbe10e890ac900f4511a1440a0da37bb1fd1a075021f38fb958b6f48d75a2ab41763b9e4ef471127e7ca625a4d86e08104b4e56b8e156b07f1a7d0f64a0a25197ea94efdb1f80b3
264.669774 inbound 01027d11000003e9000c00030d6e00000000
269.625529 outbound 0102b01000000001000c00030d6f00c200122db3b1afc78a764a41d4d3840000002b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
269.675347 inbound 0102b010000003e9000c00030d6f00000000
274.624595 outbound 0102085c00000001000c00030d7000e200122db3b1afc78a764a41d4d3840000002c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36abb44f997bb367f962d145d4a474b51d6b0c965a0ea8dfe2015a0e333066ca762f6ac74f9a78e9d5bf8cadb43387332c98b66c57eae34f065b495a7e5ea2b4ca2c71bf09a5c5ebd2a47521fb5aa0db05401be31283346ca3fb3452e186148db5253cae68236d976e3217f5fbb0579fd6
274.670715 inbound 0102085c000003e9000c00030d7000000000
279.624574 outbound 0102c55d00000001000c00030d7100c200122db3b1afc78a764a41d4d3840000002d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
279.671924 inbound 0102c55d000003e9000c00030d7100000000
284.624563 outbound 0102f21200000001000c00030d7200e200122db3b1afc78a764a41d4d3840000002e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586cc09c660ab170e05594989488955f781edee97ec474ea0e137615742da55ea867d86eee15e8f212d8ef801905b6c2b1986650b023d6b3a052ac0818864cd028e8b245fca6692b6d405b612da686fd1774584dd32ea620d1a87b8ec9644f38b322
284.670081 inbound 0102f212000003e9000c00030d7200000000
289.625697 outbound 01023f1300000001000c00030d7300c200122db3b1afc78a764a41d4d3840000002f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
289.672867 inbound 01023f13000003e9000c00030d7300000000
294.625270 outbound 01028a3100000001000c00030d7400e200122db3b1afc78a764a41d4d3840000003000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffefc01687a6cb267c3056f84ec756d6700674342f71c492e7a1456f2a656724c05fdd173a8b09f68040081e3d2d12e8f5e25ec899c555a9b8c5080c16c63608ebcf9e8577c9f79f142b83581502fd68c41943b7c47334fb2a3b092a4d41ed7e02
294.670610 inbound 01028a31000003e9000c00030d7400000000
299.624511 outbound 0102473000000001000c00030d7500c200122db3b1afc78a764a41d4d3840000003100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
299.668981 inbound 01024730000003e9000c00030d7500000000
304.624487 outbound 0102ff7900000001000c00030d76011200122db3b1afc78a764a41d4d38400000032010038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49b561ccc3534b1b1aaee9437f152f27850397b3bd98fc0a353d391c847551cb2ad1235724c7c3e5485043d1a805cd4c31b39c4d020228ec1ac92bb5e5d2440c6e129c829d72327469c736ca9d68e4001edb542ff845f76169ad970a2f0762fb9923a3c6a32d969c89fa6af6e26939c72f15e9a9a1cb91570931b19705d54e4110905674511bc1f2305d160b936dadac8e
304.669379 inbound 0102ff79000003e9000c00030d7600000000
309.628233 outbound 0102327800000001000c00030d7700f200122db3b1afc78a764a41d4d3840000003300e038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff443012572fe3788b804939d27c5c546ae8318e226965930bcfe4084c25e9d05ffcc862ab6b02145bf5ebd5132595d6ff2db8abaae8a71ca00adb3c615022458d2e156cc1456f38ff3186aeb04576cc748b91
309.673748 inbound 01023278000003e9000c00030d7700000000
314.631585 outbound 01020c8600000001000c00030d7800e200122db3b1afc78a764a41d4d3840000003400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849bd5496ab1669bdcb314bab451c64e384755cc6ab925a245edb6c5bbc9046c94f75a9383fe8e3d78147d683130f8e06204fd40497cecd074b82af8acc7a52c65a3bf573c79cbe16cf1b32a6d2301270b85d6a2c439063b9cf5ae1949361714d18b
314.677053 inbound 01020c86000003e9000c00030d7800000000
319.625279 outbound 0102c18700000001000c00030d7900c200122db3b1afc78a764a41d4d3840000003500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365a9dc15f5912831f21add30c9d481924c575c4f86562dbfd860c2bd07b8769981504d6774aaa24982cb264e21b886061681bc10c1cdb733bd88c82eb20179bf8db15df4757ef1914827d861ca7c8dd99
319.670055 inbound 0102c187000003e9000c00030d7900000000
324.624426 outbound 0102f6c800000001000c00030d7a00e200122db3b1afc78a764a41d4d3840000003600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b5d4d7dbeac665f1f589d1f22bbd76f7f807d20a272239c4639f3974d32e6cba30bd3fec36d7a259d523c6b5d18089110ca45474ec2442fbd331d2d738267a786026e0b7ae507e040da07a6e1254b3b49294b7041411c94a23d74efb4d33e4df7
324.669685 inbound 0102f6c8000003e9000c00030d7a00000000
329.624650 outbound 0102b4cf00000001000c00030d7b00f200122db3b1afc78a764a41d4d3840000003700e038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff44301c2497a9ff644896e99fe8f913bc081bd7978d27f5f5e8e56b2d17025be80df35f6dd998f51cb34db602ec280614e5ef28c9b9f84091574f3a1b129786dae51dc85f32399cb0f7be184411c81566e0eb
329.670836 inbound 0102b4cf000003e9000c00030d7b00000000
334.624520 outbound 01028eeb00000001000c00030d7c00e200122db3b1afc78a764a41d4d3840000003800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b6148b6ffa3cbdadb19389e62646a332318d3c82b771d9c7bf422c1abf1eb1f9e2df28a50498ecb3c601a698dc5a1d72c8e0d04483c59565b993eb64e908da82956a379e3410e87de2d99b841d136117acee75f661319c80a0f78ca359c03372d
334.669849 inbound 01028eeb000003e9000c00030d7c00000000
339.625923 outbound 010243ea00000001000c00030d7d00c200122db3b1afc78a764a41d4d3840000003900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
339.671473 inbound 010243ea000003e9000c00030d7d00000000
344.626914 outbound 010274a500000001000c00030d7e00e200122db3b1afc78a764a41d4d3840000003a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984334220e3ad9646a2b5e8ee9f3af3f4ef78d556179d32183b99f8ade591efc36eea4e4a113c47dfb2ed50119716aafa3834d9a6d5d5347bd6475c7e9306e9d66d46dd74967289339e7e871335edf56d600abae7dae3719216c43f12a90722db5479
344.676302 inbound 010274a5000003e9000c00030d7e00000000
349.624650 outbound 0102b9a400000001000c00030d7f00c200122db3b1afc78a764a41d4d3840000003b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b362417c83712cc1357a6fa04b79c50f697acc875f84a385e3185c0018626ba7084e1cad6d0befbf593bc00ee0dd59376873fd4d230e90cbfcecf081ff56d087fbfc3a972224cdb9c5f263512acfa207afa
349.669740 inbound 0102b9a4000003e9000c00030d7f00000000
354.625084 outbound 0102392700000001000c00030d8000e200122db3b1afc78a764a41d4d3840000003c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49581b4067694dc03e4a42556bafeff6dbe3c40119b44b03b8ac80c4924d52992dc3dde2f53f736d597a9fe70a7e95e57544cc5e9d5f349ed03c83b39056e15e27a56f0c0ef78393d42b1c44ec3aeb6727093377bd3d3246e22e44221c0e321185
354.670154 inbound 01023927000003e9000c00030d8000000000
359.624328 outbound 0102f42600000001000c00030d8100c200122db3b1afc78a764a41d4d3840000003d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
359.667751 inbound 0102f426000003e9000c00030d8100000000
364.624991 outbound 0102c36900000001000c00030d8200e200122db3b1afc78a764a41d4d3840000003e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36fdd630699f6f787a77050d4050b111a8b4f65aaf551220932411389387e6f9d5bcb67f916ee8088271acc60ba7a31dcd33ae496f72825d4c1f0a08e92c42aa924ef9404bbb0bb5bd02a0725f5ac7a6929bb75ac606c919bb4f70788d9e39e172c765ac71f6126c1964b3c6b8979a0e08
364.670037 inbound 0102c369000003e9000c00030d8200000000
369.624574 outbound 01020e6800000001000c00030d8300c200122db3b1afc78a764a41d4d3840000003f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
369.669351 inbound 01020e68000003e9000c00030d8300000000
374.628487 outbound 0102bb4a00000001000c00030d8400e200122db3b1afc78a764a41d4d3840000004000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab078cc42196de26ef0e60ca1b32762f3e472fac74a78652ca19badcec429e821f5ad27f94830fd93caf4f1483db46df576992c7e259b40e6c761016b5949c782bf344b39b7834d927a6689bee8ecc357cd
374.676848 inbound 0102bb4a000003e9000c00030d8400000000
379.624317 outbound 0102764b00000001000c00030d8500c200122db3b1afc78a764a41d4d3840000004100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365a9dc15f5912831f21add30c9d481924c575c4f86562dbfd860c2bd07b8769981504d6774aaa24982cb264e21b886061681bc10c1cdb733bd88c82eb20179bf8db15df4757ef1914827d861ca7c8dd99
379.669704 inbound 0102764b000003e9000c00030d8500000000
384.627787 outbound 0102410400000001000c00030d8600e200122db3b1afc78a764a41d4d3840000004200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab0657c18a1eced46d17b2652f114cd53290daa4e4a189453adb2c4d4580069d34e87d3c787f85c7aec0539565df06ea38f424da9d37d94f0af9381f8c9556c673dd8d104dfe92686a05d25b2408abf209d
384.673190 inbound 01024104000003e9000c00030d8600000000
389.624603 outbound 01028c0500000001000c00030d8700c200122db3b1afc78a764a41d4d3840000004300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
389.670084 inbound 01028c05000003e9000c00030d8700000000
394.624505 outbound 01023dfd00000001000c00030d8800e200122db3b1afc78a764a41d4d3840000004400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b69a0b166088fc9dffd97873f939b2c6c4a048aee127dc8a95b223236c86dd771f3112d67bf54ca8ec697aa23acc78ab7c6c67aa53517a4108eef29d3b32f7db6b7b4af1c604f6e986e5199e277cd5d3a44b6b7e3c5310d377b8d96d0e4b3e36b
394.677879 inbound 01023dfd000003e9000c00030d8800000000
399.629857 outbound 0102f0fc00000001000c00030d8900c200122db3b1afc78a764a41d4d3840000004500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ef3ed8a10c6b4041ccefc70192dbb0b05d822cbed9460c5e7f246e07b93982f85555c666b861fd69ec32b540b58d6a5a67cf29d1fb67b69fcf7709c57be55e0e83d4b1a0e4e2d378c365d02add9b68b1
399.675938 inbound 0102f0fc000003e9000c00030d8900000000
404.624399 outbound 0102c7b300000001000c00030d8a00e200122db3b1afc78a764a41d4d3840000004600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c2c1be8716ba2170dc12a463fa33b2f0e7a572fc6623fa4af76fd56ac7bc304b1b3a992bc5e341e9268e7bcb98da3ce4e441f1768f93225b492f63d9841761f67793e2a887566eb1cbdf2c58692d0cfb289da6d340b3ac5177918ad7b8d9e61032a55c5d015591a8e339b183f7c0cc2d
404.669266 inbound 0102c7b3000003e9000c00030d8a00000000
409.624725 outbound 01020ab200000001000c00030d8b00c200122db3b1afc78a764a41d4d3840000004700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
409.672526 inbound 01020ab2000003e9000c00030d8b00000000
414.624415 outbound 0102bf9000000001000c00030d8c00e200122db3b1afc78a764a41d4d3840000004800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586c9bf6d65062f8b59d3da21453ec8ab6d4f27d3d67aecd6c2f0cabb20ad883685fd8e1445bf72fe36b81db113a98223c120b460eee02759014e100e6742d09d86876637b339efcf43e5028733288fb37a90fb5197b53f4598a404cd379e19b759b
414.669679 inbound 0102bf90000003e9000c00030d8c00000000
419.625078 outbound 0102729100000001000c00030d8d00c200122db3b1afc78a764a41d4d3840000004900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
419.669316 inbound 01027291000003e9000c00030d8d00000000
424.624459 outbound 010245de00000001000c00030d8e00e200122db3b1afc78a764a41d4d3840000004a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b499cf2f6e1c25d79a6fa72e4fbc8629f74356ef8ab44a74bab7bf7a5b67377d4dcc1c8a23ccbe25c332793ab204a7ca29f76eb17ff2880db3a21c2e5b6f16b2332d8d0c78858f8d0be562efc3197b62a4f3eac1f73656f5a30b693c1bad12587cf
424.669266 inbound 010245de000003e9000c00030d8e00000000
429.624362 outbound 010288df00000001000c00030d8f00c200122db3b1afc78a764a41d4d3840000004b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
429.681641 inbound 010288df000003e9000c00030d8f00000000
434.624587 outbound 0102309300000001000c00030d9000e200122db3b1afc78a764a41d4d3840000004c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36d8d89ee70a054d48abe3cc4929819d00cf56d69844a5ae83643d5a150a17c0aeb34f0dc08c1c7154699494a567bae8c1e18ed4494d6b78192b3b1400de2f4459563df4d673d9442fa31ec469912c8c61576fb6dc2f9c54bf9a78de1c423a780f7a7ec384134570f324e07bb92b8f1ec1
434.669300 inbound 01023093000003e9000c00030d9000000000
439.624443 outbound 0102fd9200000001000c00030d9100c200122db3b1afc78a764a41d4d3840000004d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
439.670440 inbound 0102fd92000003e9000c00030d9100000000
444.624495 outbound 0102cadd00000001000c00030d9200e200122db3b1afc78a764a41d4d3840000004e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b325c6695cb58c0e79ce261f22198b3f279294fa1d000d17caa0aa53f92f6da25be72448b1155331580764183825f7060ad587d93cd9cd2aaa7bdac7d0f2b450b4b90a7fc18c1d5865fccfbfab4dd10d870f67d95c8f7415e71a100fcf2947dfc
444.669267 inbound 0102cadd000003e9000c00030d9200000000
449.624488 outbound 010207dc00000001000c00030d9300c200122db3b1afc78a764a41d4d3840000004f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
449.668625 inbound 010207dc000003e9000c00030d9300000000
454.625113 outbound 0102b2fe00000001000c00030d9400e200122db3b1afc78a764a41d4d3840000005000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b368e53a1140468db2a4a5e33e57e15bdbdcad98194fa29f95f5719af403941fa3ca11bf8b38e0eac5ea1e653c21c588d521183f2f9322dbee0771a2d0649718815d974dae5eaec94f582de5e03585b4147b8880f29cc89e47185e4e04ebfbf624c5f13d937714aa66c4ddf0630ceb5e22c
454.671415 inbound 0102b2fe000003e9000c00030d9400000000
459.627196 outbound 01027fff00000001000c00030d9500c200122db3b1afc78a764a41d4d3840000005100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
459.672973 inbound 01027fff000003e9000c00030d9500000000
464.624684 outbound 010248b000000001000c00030d9600e200122db3b1afc78a764a41d4d3840000005200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586cab9e1d172c4c84183e5b63ddbf90182b0a842bb705a80d665681b8a087cc099d5bb32ac6aea2173e1bc3a57659dd554de3a83a87ba5f9abf4ebe9072706b3154a193df14bf331a0c345caa6541e29f637ce53d5e2683b8d5a84de820f942436a
464.670246 inbound 010248b0000003e9000c00030d9600000000
469.624525 outbound 010285b100000001000c00030d9700c200122db3b1afc78a764a41d4d3840000005300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
469.669166 inbound 010285b1000003e9000c00030d9700000000
474.624497 outbound 0102344900000001000c00030d9800e200122db3b1afc78a764a41d4d3840000005400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49ad7b2402ac3d5b212448fdd603b7f829ff47af711e10dc609a9d4efb272e85f5dfbf0637042ff93b0b895c1356ecdfec0c0539052101bee76346d93bb41091add29718eb15bc55308fae5e84f6c9304ca4ac55dc3371aa8c14d227f257c9ad2a
474.669866 inbound 01023449000003e9000c00030d9800000000
479.624448 outbound 0102f94800000001000c00030d9900c200122db3b1afc78a764a41d4d3840000005500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
479.669772 inbound 0102f948000003e9000c00030d9900000000
484.625069 outbound 0102ce0700000001000c00030d9a00e200122db3b1afc78a764a41d4d3840000005600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b4900cb116eba8e2dcf9183659c2964e0f194d1d1efdafecb11e156f4f1a481994d6256669863c9de4e1d5e5e128efb8d1591631b44a68b902d2745f487cf66a300c82d250fdbf2e2a72db6c4d2fa0d88a64c3c3d728819674f1628bba5453de97c
484.671581 inbound 0102ce07000003e9000c00030d9a00000000
489.624537 outbound 0102030600000001000c00030d9b00c200122db3b1afc78a764a41d4d3840000005700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
489.669084 inbound 01020306000003e9000c00030d9b00000000
494.624494 outbound 0102b62400000001000c00030d9c00e200122db3b1afc78a764a41d4d3840000005800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b4977d56f26452cd2eaee1dee76613ed35542004740e84966e7e35d2aaba1529c4e8d6f4f18639536ca71b610c4864939a352c6bc0419389afaca5c5cc60d26f958140a245689b52087b81060e1146f14084552c264330f93b2f063c57e293f1683
494.669104 inbound 0102b624000003e9000c00030d9c00000000
499.624485 outbound 01027b2500000001000c00030d9d00c200122db3b1afc78a764a41d4d3840000005900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
499.669297 inbound 01027b25000003e9000c00030d9d00000000
504.624836 outbound 01024c6a00000001000c00030d9e00e200122db3b1afc78a764a41d4d3840000005a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab07e657ee5463eadd2069988cd3ecd056b8a1b9f1852d6a629c5b7e2b8a9c7aca25fe3e5e6c25b1126d8415db0308e918128d70d5eb5e888f5401cc6ebd540ad7fa347cee9390370f49584cd1fe8dc4cc7
504.679682 inbound 01024c6a000003e9000c00030d9e00000000
509.624489 outbound 0102816b00000001000c00030d9f00c200122db3b1afc78a764a41d4d3840000005b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36d2b99eb36c8f2784edec0a635e3dbec88635aef87f5402541dff0e31c2ce354fec4be361bb5e296f3100c2701d42c8f796a0d78bafcf580f2c8bc8a40ac8e7e5b15d0275fbbc02c642751b72000ed582
509.669020 inbound 0102816b000003e9000c00030d9f00000000
514.624767 outbound 01025cbe00000001000c00030da000e200122db3b1afc78a764a41d4d3840000005c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b496c716ee02bf35e4005b170a94a596198927bb8212731148c550dd30d7ee4c123e8616862564e6eff15d3ba1fd82ee4dcb8cb990c6282ea5dd6e883851bcf22307e928ffccf869e269a508e56f12adedc3aa01301109a39ca33ac7c5a08de2b62
514.680902 inbound 01025cbe000003e9000c00030da000000000
519.624421 outbound 010291bf00000001000c00030da100c200122db3b1afc78a764a41d4d3840000005d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b368876387d9fe1c1dec890370b349d38f5c7b9d24cba0adbea64050336f1e7263249ba8cd16d7bec96ffac5ffc8021f7c809f00f69a7f7964914f4b80132630f9e7281352b66f9c106caa8e1be9e21c804
519.678954 inbound 010291bf000003e9000c00030da100000000
524.629030 outbound 0102a6f000000001000c00030da200e200122db3b1afc78a764a41d4d3840000005e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ef3ed8a10c6b4041ccefc70192dbb0b03c3184b360e9874aee00b9baac25ec401bead1c40f666c7a373975bfc4fe00c740e7a320156a000e688aa9516d4431093b9644e74b45ab3f7bffdf62f6651b091fb6a4095fdb763ccd352a6093a43d286b53cd6e1fff7207588bf5583a2d11c9
524.674803 inbound 0102a6f0000003e9000c00030da200000000
529.624592 outbound 01026bf100000001000c00030da300c200122db3b1afc78a764a41d4d3840000005f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b362417c83712cc1357a6fa04b79c50f697acc875f84a385e3185c0018626ba7084e1cad6d0befbf593bc00ee0dd59376873fd4d230e90cbfcecf081ff56d087fbfc3a972224cdb9c5f263512acfa207afa
529.669818 inbound 01026bf1000003e9000c00030da300000000
534.624535 outbound 0102ded300000001000c00030da400e200122db3b1afc78a764a41d4d3840000006000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b4977d56f26452cd2eaee1dee76613ed355c0d35237272e71a5c186d28b1e1170e810c6e21c562a10a1ad4d14e882c2a0fbcb97f14a3a64ff8ce8e97a946507acf2141c127e05864f65cb5b3c7a0cd62c8e6e367b13c851bce7d3d6898581927b37
534.669797 inbound 0102ded3000003e9000c00030da400000000
539.624819 outbound 010213d200000001000c00030da500c200122db3b1afc78a764a41d4d3840000006100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
539.670233 inbound 010213d2000003e9000c00030da500000000
544.624529 outbound 0102249d00000001000c00030da600e200122db3b1afc78a764a41d4d3840000006200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849bd967adf70c229a9e17ecd7e53fd06aeb93cc41c61a69240604172fa8c8dc2ef88f12825034ef0545540d27168dbd9ed0a646d436e18da2a6ee8bbb8036e94e7a58bb50a9f422bb8f5b01d82722f095b0e502a5133aa6ec838f9ced702b16c588
544.669490 inbound 0102249d000003e9000c00030da600000000
549.624493 outbound 0102e99c00000001000c00030da700c200122db3b1afc78a764a41d4d3840000006300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
549.684896 inbound 0102e99c000003e9000c00030da700000000
554.624505 outbound 0102586400000001000c00030da800e200122db3b1afc78a764a41d4d3840000006400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360f00a2c67e5e16bf6fa02b98990697a938de762818d9e27257035f13725d695e11ecb95f5f428833072686428e4d68791455b4cc3415a73bc4f3c69b5ca10cbcce554fd3f5d0e7cee5df52929c744192cff0eb7185ac9a4e9504c33d4fca38aaed6d9579c5afed61b6c806165e17097e
554.673313 inbound 01025864000003e9000c00030da800000000
559.624568 outbound 0102956500000001000c00030da900c200122db3b1afc78a764a41d4d3840000006500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
559.668889 inbound 01029565000003e9000c00030da900000000
564.624378 outbound 0102a22a00000001000c00030daa00e200122db3b1afc78a764a41d4d3840000006600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b368e53a1140468db2a4a5e33e57e15bdbd094512685d3b7d3f86fecb89aef314cc49b8dee6525e71ce9aa65bcbce356cdfa41ba3faff0da1bfa08bb61ba27b45c1027809a32655a00e2216fd3adfd145d5c343b688e09ee0114e9cb9e7debca77cb3e9ba916803fa6a06247a6a56511274
564.671585 inbound 0102a22a000003e9000c00030daa00000000
569.624712 outbound 01026f2b00000001000c00030dab00c200122db3b1afc78a764a41d4d3840000006700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
569.670155 inbound 01026f2b000003e9000c00030dab00000000
574.624506 outbound 0102da0900000001000c00030dac00e200122db3b1afc78a764a41d4d3840000006800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849bcde6e828f03785ae97e04411cd3fe5bb1898a798abccb80a07b6df5f4cc2604886d93606543b4f1c7636cf27d804779c189c97088071d449beb7f85df07bf1867907b9068ef31f4b14150aee1434dc041d3b0a0b17847098c052b2306b7c6366
574.669634 inbound 0102da09000003e9000c00030dac00000000
579.624515 outbound 0102170800000001000c00030dad00c200122db3b1afc78a764a41d4d3840000006900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
579.669670 inbound 01021708000003e9000c00030dad00000000
584.624655 outbound 0102204700000001000c00030dae00e200122db3b1afc78a764a41d4d3840000006a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab01e3335e15ae322a49f877558bc71e22fd4fdff24b6f72372c6c0e98a4d411634830ec10bdad85098a847dbbad848fadf012108c6b7dfd5ac67fe153a7a078342dc77caaf7b30598ce1ff6312449df5f8
584.671464 inbound 01022047000003e9000c00030dae00000000
589.624349 outbound 0102ed4600000001000c00030daf00c200122db3b1afc78a764a41d4d3840000006b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
589.669608 inbound 0102ed46000003e9000c00030daf00000000
594.624534 outbound 0102550a00000001000c00030db000e200122db3b1afc78a764a41d4d3840000006c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49b561ccc3534b1b1aaee9437f152f2785c4daf0f21bd2ce4d9561e333ebec9dee66eb77a77c01bc912d43bb7af1a29fa183a26c03ecce6fe79bd64eba108ae771d0b8dbd008d6b90ebee5c45c0b2add857f81da7519832e8c49adfbdc3eb02a64
594.669385 inbound 0102550a000003e9000c00030db000000000
599.624547 outbound 0102980b00000001000c00030db100c200122db3b1afc78a764a41d4d3840000006d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
599.671116 inbound 0102980b000003e9000c00030db100000000
604.625147 outbound 0102af4400000001000c00030db200e200122db3b1afc78a764a41d4d3840000006e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984335de0763a844098030faa702fada4a24f56df40c9e246c0a1efa27589d2604515e6ac3f845ee3db46267b98637ec8ffc0fab36b301108a015a1e7a4b543138a8446ae76444c0fe61131d58cf31de016caa042e173aa46910f2e9a1469c8ccc693
604.672353 inbound 0102af44000003e9000c00030db200000000
609.624521 outbound 0102624500000001000c00030db300c200122db3b1afc78a764a41d4d3840000006f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
609.679929 inbound 01026245000003e9000c00030db300000000
614.624602 outbound 0102d76700000001000c00030db400e200122db3b1afc78a764a41d4d3840000007000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b368876387d9fe1c1dec890370b349d38f539169540e5d4e7211c170fc29a20f741f6199ccbdbea5387209b4dcad06f6fb44804d42375c975f9439d4c3bf5389d786961a419244cb05e6bbbd7dbf6601c571e38bdf3a9fb60b7512fa985bab5442b1ef86371917059618b75e029c4b6dc32
614.669359 inbound 0102d767000003e9000c00030db400000000
619.624610 outbound 01021a6600000001000c00030db500c200122db3b1afc78a764a41d4d3840000007100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
619.669399 inbound 01021a66000003e9000c00030db500000000
624.624471 outbound 01022d2900000001000c00030db600e200122db3b1afc78a764a41d4d3840000007200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b496c716ee02bf35e4005b170a94a596198fa5cd682dbd5b91ec12832cafc1470b25785faef7cc725feb7ed240767ac7b1f695e5f36ced373d109e3f1037c57c62b5b002bd17239de09eb5456fdf2c0ab3ec471ac38bcc0b2c807646a1b82adf14c
624.669848 inbound 01022d29000003e9000c00030db600000000
629.624520 outbound 0102e02800000001000c00030db700c200122db3b1afc78a764a41d4d3840000007300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
629.673354 inbound 0102e028000003e9000c00030db700000000
634.624473 outbound 010251d000000001000c00030db800e200122db3b1afc78a764a41d4d3840000007400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ff8c18c8b54b0b7cf26e0a33d95667aeefdd2850602b01f2321a5f97310c0b20e592e6f9e758dfe45673b13060122dc25310f228d25dfd3ba8cc5696d1ce72719393dde77397d94c7e2ab12fc12493fb552a91c7ba53cea7a1e40b3764e8a5b79f
634.669143 inbound 010251d0000003e9000c00030db800000000
639.624505 outbound 01029cd100000001000c00030db900c200122db3b1afc78a764a41d4d3840000007500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
639.669698 inbound 01029cd1000003e9000c00030db900000000
644.624847 outbound 0102ab9e00000001000c00030dba00e200122db3b1afc78a764a41d4d3840000007600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b496c716ee02bf35e4005b170a94a596198a18c9c60810d7ef68e440e07d75260fedad21ca26193149f53fc621ea47c095a3ecdaaed01d04cb69bc4fb2ba065968ed324bcf8ee200f3fa98a4336b6912686d9f4bab9a846d1152c79e08413675316
644.672573 inbound 0102ab9e000003e9000c00030dba00000000
649.627103 outbound 0102669f00000001000c00030dbb00c200122db3b1afc78a764a41d4d3840000007700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
649.680533 inbound 0102669f000003e9000c00030dbb00000000
654.633153 outbound 0102d3bd00000001000c00030dbc00e200122db3b1afc78a764a41d4d3840000007800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b368876387d9fe1c1dec890370b349d38f5e4c2be7c7c84f542c443ac924dac53d88968a4d6ba7924150b839342e752b6d9d1a691241422d1fe3728a4ce3818a90aba92c85587444e74cb577f8f7fbfbdcfc6e4be96f962a418bec4e381d8880197dd1c1b05caf6d1a199d263685d1d2218
654.677683 inbound 0102d3bd000003e9000c00030dbc00000000
659.624569 outbound 01021ebc00000001000c00030dbd00c200122db3b1afc78a764a41d4d3840000007900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365a9dc15f5912831f21add30c9d481924c575c4f86562dbfd860c2bd07b8769981504d6774aaa24982cb264e21b886061681bc10c1cdb733bd88c82eb20179bf8db15df4757ef1914827d861ca7c8dd99
659.669737 inbound 01021ebc000003e9000c00030dbd00000000
664.625011 outbound 01027ee600000001000c00030dbe012200122db3b1afc78a764a41d4d3840000007a011038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab0f1db3bb1c3c0241a6c93a5e91c9caf06a033fbdd228a886dc237fb5f92b7e426d866c7b927d4d23849464e84e0685aaba4744af7781c8f7ed8879ba4b178b4e0666d288b775ec97c1bff9d669894808c06c31f0bee6de0ecd690a15e505fd3bd090fd56e800816056bbd3b39a053c576c1c007a016c9dd0bb22ef041d7fc4b88ea7e8fe1edc19a8ebad3f589fa4b5c0c
664.669702 inbound 01027ee6000003e9000c00030dbe00000000
669.627343 outbound 0102e4f200000001000c00030dbf00c200122db3b1afc78a764a41d4d3840000007b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
669.676038 inbound 0102e4f2000003e9000c00030dbf00000000
674.624535 outbound 0102f21500000001000c00030dc000e200122db3b1afc78a764a41d4d3840000007c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c2c1be8716ba2170dc12a463fa33b2f03c7c3fa18b0877e508661fc1b7f5717e953231dcb370e690c5777ef4a8ec4ff3a311f29f699a57854b3ab0d0a315c72abbd469ae63c005c4bdcd13f1316c8d3e937339b24761eb0b9a6dd2b7d280d07d0be43db88d6956cadf6110a726cfba1e
674.672533 inbound 0102f215000003e9000c00030dc000000000
679.624498 outbound 01023f1400000001000c00030dc100c200122db3b1afc78a764a41d4d3840000007d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
679.671027 inbound 01023f14000003e9000c00030dc100000000
684.624434 outbound 0102085b00000001000c00030dc200e200122db3b1afc78a764a41d4d3840000007e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984336dd52582d624c727fc6a63fb122d3790937ceeaa23c836b85a41713fcbdbb5ab804f69ba6144ec4bc5808cafe0364533b8648b3c9545246db628a847b692c229b8648eaafd4de784f81265e971e83f5233ab9f2326d8d14de04908c2e4d2f3e8
684.669967 inbound 0102085b000003e9000c00030dc200000000
689.625002 outbound 0102c55a00000001000c00030dc300c200122db3b1afc78a764a41d4d3840000007f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
689.669469 inbound 0102c55a000003e9000c00030dc300000000
694.625611 outbound 0102707800000001000c00030dc400e200122db3b1afc78a764a41d4d3840000008000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab07936b6fb8f03d187db14e7b0dde2b5b58e609e5ae14bdc745bc69ce936a7758ac55b21cfb9d1bc9dccd4f63574f48dfea64bc3d4208cee351a379976f867cf2c373f1e83cd9871184fcc1011310b3ec7
694.676559 inbound 01027078000003e9000c00030dc400000000
699.624643 outbound 0102bd7900000001000c00030dc500c200122db3b1afc78a764a41d4d3840000008100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c2c1be8716ba2170dc12a463fa33b2f0e690b11f56fc9e116eca7d0f45518c36a787a4b33abb469b9c31faf541f81563614744709edbd74d449340676e89f3504bb12e53fec2079591986d8f080ea158
699.669362 inbound 0102bd79000003e9000c00030dc500000000
704.624631 outbound 01028a3600000001000c00030dc600e200122db3b1afc78a764a41d4d3840000008200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49653a8f5d1d401e16b9767f5a5e1fcab07936b6fb8f03d187db14e7b0dde2b5b58e609e5ae14bdc745bc69ce936a7758ac55b21cfb9d1bc9dccd4f63574f48dfea64bc3d4208cee351a379976f867cf2c373f1e83cd9871184fcc1011310b3ec7
704.684100 inbound 01028a36000003e9000c00030dc600000000
709.624409 outbound 0102473700000001000c00030dc700c200122db3b1afc78a764a41d4d3840000008300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3683f36ca33adde7bd039d5a34f1ef69627742b5a7eda1b84101a96e5a38e3f20b2a11b0f6b07923c292bff7bab00c8f3532deaccf8dd7689e1ac9a9697a8ceb78643eab5970f8e656e7842f634a99f65b
709.669442 inbound 01024737000003e9000c00030dc700000000
714.624638 outbound 0102f6cf00000001000c00030dc800e200122db3b1afc78a764a41d4d3840000008400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49b561ccc3534b1b1aaee9437f152f2785a09621d91acd8adeb0d10ab22369f76e210699102d1861ef5e850e79a5b88c845903357f36f3fe3383785857b92d8be36e2b32403bbc6ac4b35b616d7a97b113cd9144e31f2d346bc3db01e04ce0bc4c
714.669075 inbound 0102f6cf000003e9000c00030dc800000000
719.624898 outbound 01023bce00000001000c00030dc900c200122db3b1afc78a764a41d4d3840000008500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
719.671083 inbound 01023bce000003e9000c00030dc900000000
724.629540 outbound 01020c8100000001000c00030dca00e200122db3b1afc78a764a41d4d3840000008600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843356e9ca08e3dd0f2c1b35b0a6713162a5caed70ad9f876a88b25e13b0969c6ba277570eb6bc9137c0b24e2403993c4de595f0f215e222024a3b5ba2a807f3a9beea8b969aca545f7c299265bb2a385840789bbfe4a6eea80a58809cee07e79720
724.676653 inbound 01020c81000003e9000c00030dca00000000
729.624440 outbound 0102c18000000001000c00030dcb00c200122db3b1afc78a764a41d4d3840000008700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
729.671699 inbound 0102c180000003e9000c00030dcb00000000
734.624460 outbound 010274a200000001000c00030dcc00e200122db3b1afc78a764a41d4d3840000008800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984331f3b0d10f0efd74ab849712bc16f35a018cbcbef6a7396bc37f9d8523f03212b450a514d840a9770b71091b99634e6f6afdc07733c32a2c1b3b968469160bbb8f23543b966b4baf4c200091e2a48976946a1f0d43fcc6ed917bcde1657c73115
734.668682 inbound 010274a2000003e9000c00030dcc00000000
739.625400 outbound 0102b9a300000001000c00030dcd00c200122db3b1afc78a764a41d4d3840000008900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
739.671066 inbound 0102b9a3000003e9000c00030dcd00000000
744.624469 outbound 01028eec00000001000c00030dce00e200122db3b1afc78a764a41d4d3840000008a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843351a8e4de30640e305e6d7f1f5fe990b992a6cc48f624885b5e51d047c93ef9ecf6766edc21796b9fc2db7d2182077ad16d1fe258e2a9331be48a59f9131ff076044df5868a1520c94c8b5f3faae3dcdf54bf6803860791178f2da266db2069a0
744.669925 inbound 01028eec000003e9000c00030dce00000000
749.625094 outbound 010243ed00000001000c00030dcf00c200122db3b1afc78a764a41d4d3840000008b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
749.672024 inbound 010243ed000003e9000c00030dcf00000000
754.624515 outbound 0102fba100000001000c00030dd000e200122db3b1afc78a764a41d4d3840000008c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586c9bf6d65062f8b59d3da21453ec8ab6d4cfba954107b225a2cac848f1290fd13488c6ef86ac02ca59c7ad5396ece7ec8777b94ff1b0622064342bd6cdb1a42b95427d60ac192800e0fe496dc679496676edf837ece18b2db528807c9ac275ef12
754.673471 inbound 0102fba1000003e9000c00030dd000000000
759.624529 outbound 010236a000000001000c00030dd100c200122db3b1afc78a764a41d4d3840000008d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
759.672881 inbound 010236a0000003e9000c00030dd100000000
764.624550 outbound 010201ef00000001000c00030dd200e200122db3b1afc78a764a41d4d3840000008e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586cc09c660ab170e05594989488955f781e322a14170199edc66cd545483d647723a74582b1f69787391916efaedfb10b3909d188e4897cd321aac63224de1a69f79e8b77b4a13ba4b4976fdde94ebc7da1f8038de328f20a384860df6c437cd274
764.670153 inbound 010201ef000003e9000c00030dd200000000
769.624706 outbound 0102ccee00000001000c00030dd300c200122db3b1afc78a764a41d4d3840000008f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
769.671682 inbound 0102ccee000003e9000c00030dd300000000
774.639320 outbound 010279cc00000001000c00030dd400e200122db3b1afc78a764a41d4d3840000009000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f984334220e3ad9646a2b5e8ee9f3af3f4ef78eac5004f8aff39d99ce4e372877fd7d7349028a0f6dcd884631342456f79780a48f891d114a12ea55ea63e762a96a473af7cc85bb1157da22b32cefcc2d70ae640ec300c3a56ba1de4f6db6540718ac9
774.685430 inbound 010279cc000003e9000c00030dd400000000
779.625023 outbound 01023bcb00000001000c00030dd500f200122db3b1afc78a764a41d4d3840000009100e038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3683f36ca33adde7bd039d5a34f1ef69627742b5a7eda1b84101a96e5a38e3f20b2a11b0f6b07923c292bff7bab00c8f35a5cb4a7ba0c904cd20f2766b76d7fdd7c7f3c78a4c377cae0795c7354d325123980c960c418316e9c0a1baca2fea70d5d49ad6f9aae0ea67bff67531f57195f701bb0fd8882b9de6905ad81c3e201656
779.672159 inbound 01023bcb000003e9000c00030dd500000000
784.624734 outbound 0102838200000001000c00030dd600e200122db3b1afc78a764a41d4d3840000009200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586c3370cc79633cb7fbec87da32f6db8d09305b2fab9fd75742bb3451a399aad27943de8cffbd1b9ad5a6fc8d388a1d87d2b9ad77773ff9481eccd1f789c4f9e548ea8cfe3c81747a278103644981df6ed457503443bd53eab48723d6a2f2a54a39
784.673447 inbound 01028382000003e9000c00030dd600000000
789.624401 outbound 01024e8300000001000c00030dd700c200122db3b1afc78a764a41d4d3840000009300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36abb44f997bb367f962d145d4a474b51d1d12437df638ef496e29089361778638b4b79de652710c8e21f57b57f23cbefe89d412e69ff26bd994650a156de8eb085a6d8c19a4b7942076467c684cc6d397
789.670612 inbound 01024e83000003e9000c00030dd700000000
794.624571 outbound 0102ff7b00000001000c00030dd800e200122db3b1afc78a764a41d4d3840000009400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849bcfa8bdd44a9c299c33b9b175876711dcdb30d04fbfd348b6008901890c54785b8877f8f53b7f7fd03f127e73cef662e0cb294abce4752908d94624e9d5417d61b87cfedffbc716d6c3cabc004a223daaa647c085251140b11ff2fb631b2bd224
794.669688 inbound 0102ff7b000003e9000c00030dd800000000
799.625350 outbound 0102327a00000001000c00030dd900c200122db3b1afc78a764a41d4d3840000009500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
799.672999 inbound 0102327a000003e9000c00030dd900000000
804.624433 outbound 0102053500000001000c00030dda00e200122db3b1afc78a764a41d4d3840000009600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586cb12153b8ec1824a5e7cf4711a228b13167049ab228d77b4f0833e52a63dfee3cc052d861bd7205f98e38a59fb19a76272bd0c9946ef728f3e7df93cc80350e684aaa239f88716e40ca0834f928afee0e5d7f972832745c034c188b6c7549f815
804.672687 inbound 01020535000003e9000c00030dda00000000
809.624555 outbound 0102c83400000001000c00030ddb00c200122db3b1afc78a764a41d4d3840000009700b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36c5048dd2b6398299c9e393ed7587a4ffe0ff949b8c2603f7cd0cc1e456b991bdc6fdd41fe921dd10a14c81ba8ac1e6c7491e22de04fa19037645808da2e73704a446448f60056cee719d6ced8d8327ff
809.669760 inbound 0102c834000003e9000c00030ddb00000000
814.624565 outbound 01027d1600000001000c00030ddc00e200122db3b1afc78a764a41d4d3840000009800d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49ac2727a0d41c884b39a1d390cf3ed67ec693de7899a5b1735c61bcf2657fdf64fdc1b9047c8f159088e558bb3e4755b423c4c397e385c2607c5e55ece39719f3a641194c4bcbeb7ff9fcb463b6fd02170b11a352f58672eda650c10d2f44ffb6
814.670068 inbound 01027d16000003e9000c00030ddc00000000
819.632649 outbound 0102b01700000001000c00030ddd00c200122db3b1afc78a764a41d4d3840000009900b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
819.678204 inbound 0102b017000003e9000c00030ddd00000000
824.624558 outbound 0102875800000001000c00030dde00e200122db3b1afc78a764a41d4d3840000009a00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ef3ed8a10c6b4041ccefc70192dbb0b0f14544ce925e1de9bea8959d30bbffd056db25eaf2998c254622d525b17af477d8788e6e35c84cd7bd5131bf0b4ae7f3f2950152f70f7ebb499e7bcb32af77ddea2f95a33df39e62dffd2d45471819fb89930075393faec28d226dec5c93ab9f
824.672825 inbound 01028758000003e9000c00030dde00000000
829.624503 outbound 01024a5900000001000c00030ddf00c200122db3b1afc78a764a41d4d3840000009b00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
829.670089 inbound 01024a59000003e9000c00030ddf00000000
834.624767 outbound 0102978c00000001000c00030de000e200122db3b1afc78a764a41d4d3840000009c00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b2b68c88e06a6332246903d7eeb2351b16ceb6ebb360f27021a719d52479c5171582784fb247de30b48cb28a4798a7e98a1e513a379d9316299f99955456665658624e113ec7696077d7929ec0bc3272cc88bddfb2c6810c8d4e5db4f13fe2242
834.670296 inbound 0102978c000003e9000c00030de000000000
839.624646 outbound 01025a8d00000001000c00030de100c200122db3b1afc78a764a41d4d3840000009d00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
839.672742 inbound 01025a8d000003e9000c00030de100000000
844.624663 outbound 01026dc200000001000c00030de200e200122db3b1afc78a764a41d4d3840000009e00d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586c09c15d0bf8f792a32ced7b84da0f23e5b94e974bbda1501bcc78867bb3375ee6cfe7b7f66f5fde899fe37d3153ea53f5f0949d080b60179bb74ca31cc261b8d4502bb8ecc6dea84bcb5579c969efc35de55f5c1fa6284de4904e3a403a03276b
844.672019 inbound 01026dc2000003e9000c00030de200000000
849.624583 outbound 0102a0c300000001000c00030de300c200122db3b1afc78a764a41d4d3840000009f00b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b365f8a410564147f1c7bdf99d33918586ca28af11f3e0b4ea18a9ab8ef2ca6ac6fa445fd2e5a3b2834457db313f692de453e832264809c455dd2797eee74d1e26d14daf19b631c69e22bd1bf67835054a0
849.674122 inbound 0102a0c3000003e9000c00030de300000000
854.624741 outbound 010215e100000001000c00030de400e200122db3b1afc78a764a41d4d384000000a000d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b362417c83712cc1357a6fa04b79c50f6972111297d34f9f7385b985b00fd1a6ef6fbad87d556ec1768041640cb3f111ec97c37a5affc782c5b8060c1ea5ca1875cb492d34dd33fc5780aac352228d54092ccbf4b0317b60ecef914d13962459e7551244eed4b2ecd24e9762a34bd5b76dd
854.670864 inbound 010215e1000003e9000c00030de400000000
859.624618 outbound 0102d8e000000001000c00030de500c200122db3b1afc78a764a41d4d384000000a100b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b53ecdc3374af08f438a294bb89f6d4a896dbd65dd0915fea4bd670d6c566111e31726aae9bcb32aee0c0688f8cde9ad1079fb7f420858a1f1d7df7a0a4045ff5
859.670753 inbound 0102d8e0000003e9000c00030de500000000
864.625719 outbound 0102efaf00000001000c00030de600e200122db3b1afc78a764a41d4d384000000a200d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b3675da049d1ad1a844440eb5a7096d849b2b68c88e06a6332246903d7eeb2351b1438b61ff654ced0008028a759cbe021008587119e9d2716e5e6db125a6cc003163fdc2da1f6cd5c2963586dcac9cd252c4e1a0152bb6c865a2a952b25899e12fd90c43b8543384768736db3cede97043
864.671515 inbound 0102efaf000003e9000c00030de600000000
869.624812 outbound 010222ae00000001000c00030de700c200122db3b1afc78a764a41d4d384000000a300b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36ab011d1b92458014f701dad148f9843364a3ca600de3d164420d4e2564f6caad738befc2eebfd56059252afa8ad640dc0574f9446b0880f6d998523067790763d8ebb33e70efc60184dd9751aed994fd
869.675166 inbound 010222ae000003e9000c00030de700000000
874.624398 outbound 0102935600000001000c00030de800e200122db3b1afc78a764a41d4d384000000a400d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b36abb44f997bb367f962d145d4a474b51d13c52f6575636c6af18eb296207d5c8e908b98d2e839cb63974e3bf2bd60d3a994b1a17ec80ed6fa4448a7a0364d13d98cbed26201a2d7f55dc1e814ff41a30b31027c83b2ee2c72f37331a982d059e258a126174ba752b42b4c3913b3c18c3c
874.669393 inbound 01029356000003e9000c00030de800000000
879.624749 outbound 01025e5700000001000c00030de900c200122db3b1afc78a764a41d4d384000000a500b038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b49fb55618e410a7cf56fc8bc6efd18f37650cd660d87d787a07a85d38805ff4430b0c5ec64a0ec0e568c5778d35944b3263edd4870f045bb81ebfb28759dc014c6
879.669501 inbound 01025e57000003e9000c00030de900000000
884.624864 outbound 0102691800000001000c00030dea00e200122db3b1afc78a764a41d4d384000000a600d038b5aea9cb160361247c5cec450017babc0c361f35f996e5502543af85e2cc051916a54099d87da3c781bad1166e2b33f5c1fb317bbe11f26693704960df492c75396199c130607f5254b43e972398bf30d08429c614ef6eea738e6f73345b360af86d4b8d2d445e6238d39aea1e6b496640e49b32bfcf8e5d7f2fc1233a2a3a74d9b1bb9c1766b2badcce8f90c4438f81a8b5fd19d1ab41b70add7c1be0858cf0d4064f6b3203b500214af9f6316c8e1853ef126d99cf102e2787b62c48f74b4e1333130df70e5379a50a5ff502a676
884.692766 inbound 01026918000003e9000c00030dea00000000
888.807664 outbound 0102090b00000001000d00030deb05d200122db3b1afc78a764a41d4d384000000a705c067344155703abd6f428d3480570feec35d4124c51f82222c400b7ee29eab188ecdf555c810f3410fe631a21ddd1b3988d464d406732ad533017c2ab7241ba50dc6d98a963a8cc9d4e5859f5904e6c8680d1351fd31e1e2dba2a7c8bcca22bbf3063b8c2d389df0bd7af657a6bf44c4f9ae70d4b4bbeb6f99a23ca66f5ce56910f34abdc17b318c642752724886b5b23404277d9839b84261c8d44a103df4cc9562485c8dfa6435cd39423e3082aaacceaed9dbd2f0fbfd12a0a59723711b96c4a42f3741f5a20e313523b1ac0b86026675714c8a98b836cf01bf97cd0dbe3c0cba482983a54b2d8ba3876324ad38e03a7b9c694bd1280ed86a7824c8bd18a5c2b5da80def562674564f0fe5c110ce370840afcc05c77d54309d8bac1c266f8d3bc5671d9795a65b25526edf417cfc3f48b05bb9c015d772e2b00649bffd9585e16e7b7c96174febd169d52aac8f0377f3cafbc6368164d166aad5cf7ab3369d0c6fa898703cb058883dd8a3745007a5381b9766821a279a63940d940215bacadd02b5a96a2a0543539678383f6af0a004064f3ef8e8d3cc2a347f351dd22cc790a13b4029d5a86706ea560b2335731d4bf506d9b772f6d59f95eefeb1753887b0bd91955479cfeb0e4f5a537bba142796089f5d37cfb55b7052c551912388e9084ac0940d54c9a370ae9f7c152276aa30cf22119352073bd9f39a3920b1eaab69375830508e0522c2d89da4e77ba36ab17dcd47b5a0045ce0333630866904a03cbee6414c70ceef8aafebbd0225ea5684f46e3e296f31ed38441ae9b9c703cbdfbfc7a4546ec35f6ef5ec0037fb048c95da715f964c3eb55f612fe395a551690006ef60e540f3ae76ee78efe59ce1c143c8d685cca7cd318ab58fa0b8325f4fa8451e729829d14d53d9cdf8d0276c0dea2a92218d67a0b91beaefa50fe819d18558f9e9637d68e36174d065e67dabc0fbe8fa5ba47304a4bff50b4eed9f73ba2f1509338bdb22f85421f26d3e9d62350fb6ed29605b99b7a6fd0a304084c7cf18bd3d8690ed1aee75d85795b701ad9ac6312caa177126481616003c953d76d54027dce87fc9d16a66b2029404d7880f00a963efe90e568e09749682a3e7f8e684adb1a9dd06b26cea54ae5e93dfbb5e376fe8c59079a0f3fd7934ddbf38c237de06934431273c676e39d7e9e404c0b188653ed35af0af161b0be054342883b001543206223a069b3bbabf78bd5181a7baf7ce92643266da263ec9a6b97e28c9e52cbfe8ad86e704ef027483aa34673b4a162afb902dd9959bd21d7afcf30c8b90b194bfce3f4288b7aa1209be9c9692ae7b9672443f563710f29727f6f9bd00c41e345f1f6383f0f95ec4a6a77cd62c78cacf00f485dd42dd2afc00ca50f777d0d14999d65db46320e394f2fc5b24c0d3ff4a520da5495bb4467454a26acb7691317cd99c707f0134c6faa0579b046f9901fa65465d73b0ab60b0a4626a9a14d4886db35bc40c2cff6f93a476ec1ae13ae5d08ea794c6015a034348c52b0ee61a293e89445abb5ac56e97c1027d288088419a4e4ba8baf95a3dd81db362577e03447376160afb993fb5f1e806dad836b240f1d234244007e215a8095f434e0e6727a0aaa145a62226a1f6da8a1c8ab0927ccf8aa38fb5527eb70c135c52fc25cd2c711b1155fcbe853be490861c59d90b6a8c66d4f2080e650e52db97eaaee3277f486a773a54c09c6814eb85d9f9834b8d0cfc46168c14379ee3d119b1728e4b796ed9a31bb7743234344a5e46ebef94b092d900d0cd2160dc3ce4fac1d2d4b5275617b5864d97467395ef3b735e553a946a2af190d51df45fa4c84daf1eb704abdec54c41ef27e444889ba3dfeb1c8e7666a4e434a92230de4c1bb070d3869898ae7dca60f5dfba208e1e886cc71de104cf9f4e8fc8c76a071a89040ed0f5fe4e4baa5246c8cd0c21f6e13f2ae29a8ad024d6bdbb9ae046a938bcfb9170f54c8f32355f490a9b6f7e9967d417df87718745a4c835626f93170aafa51c1056553147771d4b58f25966c07064224a179ebd470812be8bab5283c7895e9758d28
888.860893 inbound 0102090b000003e9000d00030deb00000000
```
