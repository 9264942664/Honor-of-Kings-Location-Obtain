"""Offline checks for the capture-specific Honor of Kings hypothesis."""
import os
from pathlib import Path
import unittest

from server.hok_parser import HonorOfKingsParser, PHONE_PORT, PRIME_IP, PRIME_PORT
from server.hok_parser import identify_flow, observed_counter, prime_datagrams


class HonorOfKingsParserTest(unittest.TestCase):
    def test_observed_signatures(self):
        for direction, prefix, length in (
            ("outbound", "002dc15b", 61),
            ("inbound", "00000000", 24),
            ("inbound", "00020000", 32),
            ("inbound", "00030000", 1400),
            ("inbound", "000b0000", 158),
            ("inbound", "00350000", 45),
            ("inbound", "00400000", 45),
        ):
            with self.subTest(direction=direction, prefix=prefix):
                self.assertEqual(
                    identify_flow(PRIME_IP, PRIME_PORT, PHONE_PORT, direction,
                                  bytes.fromhex(prefix).ljust(length, bytes(1))),
                    f"prime/{direction}/{prefix}",
                )

    def test_unknown_signature_or_tuple(self):
        payload = bytes.fromhex("002dc15b").ljust(61, bytes(1))
        for remote, port, local, direction, body in (
            (PRIME_IP, PRIME_PORT, PHONE_PORT, "inbound", payload),
            (PRIME_IP, PRIME_PORT, PHONE_PORT, "outbound", payload[:3]),
            (PRIME_IP, PRIME_PORT, PHONE_PORT, "inbound", bytes.fromhex("deadbeef")),
            (PRIME_IP, PRIME_PORT, PHONE_PORT, "inbound", bytes.fromhex("00030000")),
            ("192.0.2.1", PRIME_PORT, PHONE_PORT, "outbound", payload),
            (PRIME_IP, PRIME_PORT + 1, PHONE_PORT, "outbound", payload),
            (PRIME_IP, PRIME_PORT, PHONE_PORT + 1, "outbound", payload),
        ):
            with self.subTest(remote=remote, port=port, local=local, direction=direction):
                self.assertIsNone(identify_flow(remote, port, local, direction, body))

    def test_observed_counters(self):
        up = bytes.fromhex("002dc15b0000000078563412").ljust(61, bytes(1))
        down = bytes.fromhex("000b000000007856").ljust(158, bytes(1))
        self.assertEqual(observed_counter(PRIME_IP, PRIME_PORT, PHONE_PORT, "outbound", up),
                         0x12345678)
        self.assertEqual(observed_counter(PRIME_IP, PRIME_PORT, PHONE_PORT, "inbound", down),
                         0x5678)
        self.assertIsNone(observed_counter(PRIME_IP, PRIME_PORT, PHONE_PORT, "inbound", up))

    def test_real_prime_datagrams_return_no_entities(self):
        fixture = Path(os.environ.get(
            "HOK_PCAP", "~/workspace/hok-capture/pcapdroid-20261126.pcap"
        )).expanduser()
        if not fixture.is_file():
            self.skipTest(f"Capture fixture unavailable: {fixture}")
        parser = HonorOfKingsParser()
        count = 0
        batch = []
        for datagram in prime_datagrams(fixture):
            self.assertIsNotNone(identify_flow(PRIME_IP, PRIME_PORT, PHONE_PORT,
                                               datagram.direction, datagram.payload))
            batch.append(datagram)
            count += 1
            if len(batch) == 256:
                self.assertEqual(parser.parse(batch), [])
                batch.clear()
        self.assertEqual(parser.parse(batch), [])
        self.assertEqual(count, 32574)
