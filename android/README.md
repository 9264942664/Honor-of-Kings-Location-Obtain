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
3. Tap **Start** and approve Android's VPN prompt. Generate UDP traffic in the selected app. The status shows captured packets, acknowledged uploads, and the latest snapshot revision and entity count. An em dash indicates that no snapshot has been received. The stub parser returns zero entities.
4. Tap **Stop** and then **Export PCAP**. Choose a location on your phone. Each session saves a timestamped raw-IP PCAP in app-private storage. Export selects the most recently modified capture, including after restarting the app. Wireshark and tcpdump can read the exported file.

The VPN routes IPv4 for the selected app and relays unfragmented UDP through protected sockets. IPv4 TCP and other unhandled IPv4 traffic from that app are blocked during capture. IPv6 bypasses this capture. Inbound PCAP records represent reconstructed IP packets delivered through the TUN, with the original UDP reply payload. The capture should be short enough to fit the phone's available storage.

Uploads contain UDP payload bytes and direction. Batches hold up to 256 datagrams and 1 MiB of JSON. The upload counter advances only when the server acknowledges a batch. If the queue fills or an upload fails, PCAP recording continues. Stop closes the capture and discards pending uploads, while an HTTP request already in progress can finish.
