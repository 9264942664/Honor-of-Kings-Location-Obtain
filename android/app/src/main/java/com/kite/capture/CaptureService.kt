package com.kite.capture

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Intent
import android.net.VpnService
import android.os.Handler
import android.os.Looper
import android.os.ParcelFileDescriptor
import android.system.ErrnoException
import android.system.Os
import android.system.OsConstants
import android.system.StructPollfd
import java.io.File
import java.io.IOException
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetSocketAddress
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlin.concurrent.thread

internal class CaptureStatus(val file: File? = null) {
    val captured = AtomicLong()
    val uploaded = AtomicLong()
    val tcpConnections = AtomicLong()
    val queueDrops = AtomicLong()
    @Volatile var snapshot: Snapshot? = null
    @Volatile var uploadError: String? = null
    @Volatile var snapshotError: String? = null
    @Volatile var relayError: String? = null
    @Volatile var message = "Stopped"
    @Volatile var busy = false
}

class CaptureService : VpnService() {
    private val main = Handler(Looper.getMainLooper())
    private var session: Session? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stopCapture()
        } else if (intent?.action == ACTION_START && session == null) {
            val origin = serverOrigin(intent.getStringExtra(EXTRA_ORIGIN).orEmpty())
            val target = intent.getStringExtra(EXTRA_PACKAGE).orEmpty()
            var tun: ParcelFileDescriptor? = null
            try {
                require(origin != null && target.isNotBlank() && target != packageName) {
                    "Enter a server origin and another installed app's package."
                }
                val descriptor = Builder()
                    .setSession("Kite Capture")
                    .setMtu(1500)
                    .addAddress("10.81.0.1", 32)
                    .addRoute("0.0.0.0", 0)
                    .allowFamily(OsConstants.AF_INET6)
                    .addAllowedApplication(target)
                    .establish() ?: throw IOException("VPN permission is unavailable")
                tun = descriptor
                startForeground(1, notification())
                val file = File(filesDir, "capture-${UUID.randomUUID()}.pcap")
                val next = Session(descriptor, ApiClient(origin), CaptureStatus(file))
                session = next
                next.report.busy = true
                next.report.message = "Capturing IPv4 UDP + TCP relay"
                status = next.report
                thread(name = "tun-capture") {
                    next.run()
                    main.post {
                        if (session === next) {
                            session = null
                            next.report.busy = false
                            stopForeground(STOP_FOREGROUND_REMOVE)
                            stopSelf()
                        }
                    }
                }
            } catch (error: Exception) {
                runCatching { tun?.close() }
                status = CaptureStatus().apply { message = "Start failed: ${error.message}" }
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        } else if (session == null) {
            stopSelf()
        }
        return START_NOT_STICKY
    }

    override fun onRevoke() {
        main.post { stopCapture() }
    }

    override fun onDestroy() {
        session?.active = false
        super.onDestroy()
    }

    private fun stopCapture() {
        val running = session
        if (running == null) {
            stopSelf()
        } else {
            running.report.message = "Stopping"
            running.active = false
        }
    }

    private fun notification(): Notification {
        val manager = checkNotNull(getSystemService(NotificationManager::class.java))
        manager.createNotificationChannel(
            NotificationChannel(CHANNEL, "VPN capture", NotificationManager.IMPORTANCE_LOW),
        )
        val open = PendingIntent.getActivity(
            this, 0, Intent(this, MainActivity::class.java), PendingIntent.FLAG_IMMUTABLE,
        )
        return Notification.Builder(this, CHANNEL)
            .setSmallIcon(android.R.drawable.stat_sys_upload)
            .setContentTitle("Kite Capture")
            .setContentText("Capturing traffic from the selected app")
            .setContentIntent(open)
            .setOngoing(true)
            .build()
    }

    private inner class Session(
        private val tun: ParcelFileDescriptor,
        private val api: ApiClient,
        val report: CaptureStatus,
    ) {
        @Volatile var active = true
        @Volatile private var pcapFailure: IOException? = null
        private val flows = ConcurrentHashMap<FlowKey, DatagramSocket>()
        private val outputLock = Any()

        fun run() {
            try {
                PcapWriter(checkNotNull(report.file)).use { pcap ->
                    val upload = thread(name = "capture-upload") {
                        try {
                            api.uploadLoop({ active }) { accepted, error ->
                                report.uploaded.addAndGet(accepted.toLong())
                                report.uploadError = error
                            }
                        } catch (_: InterruptedException) {
                            // Stop interrupted a queue wait.
                        }
                    }
                    val snapshots = thread(name = "capture-snapshot") { pollSnapshots() }
                    val tcp = TcpRelay(
                        protect = { protect(it) },
                        emit = { writeTcp(pcap, it) },
                        error = { if (active) report.relayError = it },
                        count = { report.tcpConnections.set(it) },
                    )
                    try {
                        readTun(pcap, tcp)
                    } finally {
                        active = false
                        upload.interrupt()
                        snapshots.interrupt()
                        flows.values.forEach { it.close() }
                        tcp.close()
                        // Wait for any reply already writing to TUN or the PCAP.
                        synchronized(outputLock) { tun.close() }
                    }
                }
                pcapFailure?.let { throw it }
                report.message = "Stopped"
            } catch (error: Exception) {
                report.message = "Capture failed: ${error.message}"
            } finally {
                active = false
                runCatching { tun.close() }
            }
        }

        private fun readTun(pcap: PcapWriter, tcp: TcpRelay) {
            val descriptor = tun.fileDescriptor
            val poll = arrayOf(StructPollfd().apply {
                fd = descriptor
                events = OsConstants.POLLIN.toShort()
            })
            val bytes = ByteArray(65535)
            while (active) {
                tcp.tick()
                if (Os.poll(poll, 250) == 0 || !active) continue
                if ((poll[0].revents.toInt() and OsConstants.POLLIN) == 0) {
                    throw IOException("TUN is unavailable")
                }
                val size = try {
                    Os.read(descriptor, bytes, 0, bytes.size)
                } catch (error: ErrnoException) {
                    if (error.errno == OsConstants.EAGAIN) continue
                    throw error
                }
                if (size <= 0) throw IOException("TUN closed")
                if (size < 20 || (bytes[0].toInt() and 0xf0) != 0x40) continue
                when (bytes[9].toInt()) {
                    6 -> {
                        val packet = TcpPacket.parse(bytes, size) ?: continue
                        synchronized(outputLock) { recordTcp(pcap, bytes, packet.size) }
                        try {
                            tcp.accept(packet)
                        } catch (error: IOException) {
                            report.relayError = error.message ?: "TCP send failed"
                        } catch (error: ErrnoException) {
                            report.relayError = error.message ?: "TCP TUN write failed"
                        }
                        continue
                    }
                    17 -> Unit // Existing UDP capture and forwarding below.
                    else -> continue
                }
                val packet = UdpPacket.parse(bytes, size) ?: continue
                synchronized(outputLock) {
                    record(pcap, bytes, packet.payload.size + (bytes[0].toInt() and 15) * 4 + 8,
                        "outbound", packet.payload)
                }
                try {
                    val socket = flows[packet.flow] ?: openFlow(packet.flow, pcap)
                    socket.send(DatagramPacket(packet.payload, packet.payload.size))
                } catch (error: IOException) {
                    report.relayError = error.message ?: "UDP send failed"
                }
            }
        }

        private fun openFlow(key: FlowKey, pcap: PcapWriter): DatagramSocket {
            if (flows.size >= 64) throw IOException("UDP flow limit reached")
            val socket = DatagramSocket(null)
            try {
                if (!protect(socket)) throw IOException("Could not protect UDP socket")
                socket.soTimeout = 60_000
                socket.connect(InetSocketAddress(key.remote, key.remotePort))
                flows[key] = socket
                thread(name = "udp-reply") { receive(key, socket, pcap) }
                return socket
            } catch (error: Exception) {
                flows.remove(key, socket)
                socket.close()
                throw error
            }
        }

        private fun receive(key: FlowKey, socket: DatagramSocket, pcap: PcapWriter) {
            val bytes = ByteArray(65507)
            val datagram = DatagramPacket(bytes, bytes.size)
            try {
                while (active) {
                    datagram.length = bytes.size
                    socket.receive(datagram)
                    val reply = UdpPacket.reply(key, bytes, datagram.length)
                    synchronized(outputLock) {
                        if (!active) return
                        try {
                            record(pcap, reply, reply.size, "inbound", bytes.copyOf(datagram.length))
                        } catch (error: IOException) {
                            pcapFailure = error
                            active = false
                            return
                        }
                        if (Os.write(tun.fileDescriptor, reply, 0, reply.size) != reply.size) {
                            throw IOException("Incomplete TUN write")
                        }
                    }
                }
            } catch (_: java.net.SocketTimeoutException) {
                // Idle flow expired.
            } catch (error: Exception) {
                if (active) report.relayError = error.message ?: "UDP receive failed"
            } finally {
                flows.remove(key, socket)
                socket.close()
            }
        }

        private fun writeTcp(pcap: PcapWriter, reply: ByteArray) {
            synchronized(outputLock) {
                if (!active) return
                if (Os.write(tun.fileDescriptor, reply, 0, reply.size) != reply.size) {
                    throw IOException("Incomplete TCP TUN write")
                }
                try {
                    recordTcp(pcap, reply, reply.size)
                } catch (error: IOException) {
                    pcapFailure = error
                    active = false
                    throw error
                }
            }
        }

        private fun recordTcp(pcap: PcapWriter, packet: ByteArray, size: Int) {
            // TCP login and matchmaking packets stay in the PCAP. The upload API takes only
            // UDP datagrams for the Honor of Kings location parser.
            pcap.write(packet, size)
            report.captured.incrementAndGet()
        }

        private fun record(pcap: PcapWriter, packet: ByteArray, size: Int, direction: String, payload: ByteArray) {
            pcap.write(packet, size)
            report.captured.incrementAndGet()
            if (!api.enqueue(Datagram(direction, payload))) report.queueDrops.incrementAndGet()
        }

        private fun pollSnapshots() {
            try {
                while (active) {
                    val started = android.os.SystemClock.elapsedRealtime()
                    try {
                        report.snapshot = api.snapshot()
                        report.snapshotError = null
                    } catch (error: Exception) {
                        report.snapshotError = error.message ?: "Snapshot request failed"
                    }
                    Thread.sleep((2000 - (android.os.SystemClock.elapsedRealtime() - started)).coerceAtLeast(0))
                }
            } catch (_: InterruptedException) {
                // Stop interrupted the polling interval.
            }
        }
    }

    companion object {
        internal const val ACTION_START = "com.kite.capture.START"
        internal const val ACTION_STOP = "com.kite.capture.STOP"
        internal const val EXTRA_ORIGIN = "origin"
        internal const val EXTRA_PACKAGE = "targetPackage"
        private const val CHANNEL = "capture"
        @Volatile internal var status = CaptureStatus()
            private set
    }
}
