# Kite Capture for Android

## Build the debug APK

GitHub Actions is the primary build path. Push this tree to GitHub or run **Build debug APK** from the repository's **Actions** tab. Open the successful run, download the **kite-capture-debug** artifact, and unzip it to get `app-debug.apk`. The workflow uses JDK 17, Gradle 8.7, Android SDK Platform 34, and Build Tools 34.0.0.

For a local build with those same tools installed, set `ANDROID_HOME` to your Android SDK directory and run the following from the repository root.

```sh
sdkmanager "platforms;android-34" "build-tools;34.0.0"
cd android
gradle --no-daemon :app:assembleDebug
```

The APK output path is `android/app/build/outputs/apk/debug/app-debug.apk` relative to the repository root. Install it on Android 8.0 or newer with `adb install -r app-debug.apk` from the directory containing the APK.

This sandbox lacks JDK 17 (`java` and `javac`), Gradle 8.7, and the Android SDK command-line tools (`sdkmanager`), Platform 34 (`android.jar`), and Build Tools 34.0.0. The sandbox could not reach the configured network proxy to fetch tooling. No local APK was built.

## Capture and export

1. Enter the package name of an installed app whose traffic you want to capture. For a controlled smoke test, use your own IPv4 UDP echo client.
2. Enter the server origin. The default is `http://39.96.60.127:18081`. The default uses cleartext HTTP. The server receives UDP payload contents, which can include sensitive data. Use a server you trust and an HTTPS origin when available.
3. Tap **Start** and approve Android's VPN prompt. Generate IPv4 UDP and TCP traffic in the selected app. The status shows captured packets, active TCP connections, acknowledged UDP uploads, and the latest snapshot revision and entity count. An em dash indicates that no snapshot has been received. The stub parser returns zero entities.
4. Tap **Stop** and then **Export PCAP**. Choose a location on your phone. Each session saves a timestamped raw-IP PCAP in app-private storage. Export selects the most recently modified capture, including after restarting the app. Wireshark and tcpdump can read the exported file.

The VPN routes IPv4 for the selected app and relays unfragmented UDP and TCP through protected sockets. IPv6 bypasses capture. The VPN drops IPv4 fragments and other IPv4 protocols. The raw-IP PCAP contains both directions of UDP and TCP, including full IPv4 and transport headers and payloads. Inbound packets are reconstructed for the TUN. All recorded TCP segments contribute to the captured count. The capture should be short enough to fit the phone's available storage.

Only UDP payload bytes and direction go to `/api/client/upload`, which supplies datagrams to the Honor of Kings location parser. TCP login and matchmaking traffic stays in the local PCAP and its exports. Batches hold up to 256 datagrams and 1 MiB of JSON. The upload counter advances only when the server acknowledges a batch. If the queue fills or an upload fails, PCAP recording continues. Stop closes the capture and discards pending uploads, while an HTTP request already in progress can finish.

## IPv4 TCP relay

An app SYN starts a worker that connects a VPN-protected socket to the original remote address and port. The connect timeout is 10 seconds. After connecting, the worker sends a SYN-ACK and enters SYN_RECEIVED. The app's handshake ACK moves the flow to ESTABLISHED. A connect failure sends a reset.

The relay advertises a 65,535-byte window and MSS 1460. It segments remote data within the 1500-byte TUN MTU, the peer's MSS, and the available peer window. It acknowledges in-order app data after writing it to the socket. Duplicate and out-of-order app data is dropped and re-ACKed. Each flow queues up to 64 app segments, each within the TUN MTU. Queue overflow resets the flow. The relay resends SYN-ACK on a duplicate SYN while waiting for the handshake ACK. It has no TUN-side retransmission timers, data or FIN retransmissions, or zero-window probes. The protected socket's TCP stack handles retransmissions on the remote connection.

An app FIN shuts down socket output and enters CLOSE_WAIT so remote bytes can still reach the app. Remote EOF sends FIN after the preceding bytes and enters FIN_WAIT if the app can still send. With both FINs processed, CLOSING waits for acknowledgment of the relay's FIN, then closes the flow. App resets cancel the socket immediately. Socket errors and idle expiry attempt to send a reset. Idle expiry is 60 seconds without TCP activity in either direction. The relay permits 32 concurrent connections, including pending connects, with one worker per connection. Further SYNs receive a reset and a relay error appears in the status. Stopping the session closes TCP sockets and joins their workers.
