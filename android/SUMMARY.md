# Android implementation summary

## Files created

| File | Purpose |
| --- | --- |
| `.github/workflows/build-apk.yml` | Builds the debug APK on GitHub Actions and uploads the artifact. |
| `android/.gitignore` | Excludes Gradle and IDE output. |
| `android/settings.gradle.kts` | Configures the Gradle project and repositories. |
| `android/build.gradle.kts` | Pins the Android and Kotlin Gradle plugins. |
| `android/app/build.gradle.kts` | Configures the Android app with minSdk 26 and targetSdk 34. |
| `android/app/src/main/AndroidManifest.xml` | Declares the activity, VPN foreground service, permissions, and HTTP support. |
| `android/app/src/main/java/com/kite/capture/MainActivity.kt` | Provides server and package inputs, VPN consent, capture controls, status, and PCAP export. |
| `android/app/src/main/java/com/kite/capture/CaptureService.kt` | Runs the TUN, protected UDP and TCP relays, capture counters, upload worker, and snapshot poller. |
| `android/app/src/main/java/com/kite/capture/UdpPacket.kt` | Parses unfragmented IPv4 UDP and reconstructs inbound IPv4 UDP packets. |
| `android/app/src/main/java/com/kite/capture/TcpPacket.kt` | Parses IPv4 TCP and builds replies with IPv4 and TCP checksums and SYN-ACK MSS. |
| `android/app/src/main/java/com/kite/capture/TcpRelay.kt` | Manages virtual TCP connections, protected sockets, flow limits, and timeouts. |
| `android/app/src/main/java/com/kite/capture/ApiClient.kt` | Validates server origins, batches payloads, and reads snapshots. |
| `android/app/src/main/java/com/kite/capture/PcapWriter.kt` | Writes little-endian raw-IP PCAP files. |
| `android/README.md` | Explains how to build, run, and export captures. |
| `android/SUMMARY.md` | Records the files and verification status. |

## Tested

- Parsed the manifest as XML and checked its VPN binding, foreground service type and permission, and cleartext setting. Checked the SDK levels in Gradle configuration.
- Parsed the workflow YAML and checked the triggers, Gradle task, working directory, and artifact output path.
- Exercised the existing Python HTTP handler in memory with representative upload JSON and HTTP headers. Verified both directions, an empty payload, a 256-record batch, a maximum-sized datagram, rejection of oversized requests and records, advancing revisions, matching snapshot headers, and zero entities. The sandbox denied socket creation for a loopback test.

## Untested

- Kotlin compilation, APK assembly, and artifact publication in GitHub Actions. This sandbox lacks JDK 17, Gradle 8.7, Android SDK command-line tools, Platform 34, and Build Tools 34.0.0. The download proxy was unreachable. No local APK was built.
- On-device VPN consent, IPv4 UDP forwarding, live uploads and two-second snapshot polling, stop and revoke behavior, and opening an exported PCAP in Wireshark or tcpdump. The configured public server was not contacted.
- IPv4 TCP relay handshakes, data transfer, half-closes, resets, limits, timeouts, and PCAP playback on a device.
