package com.kite.capture

import android.os.SystemClock
import com.kite.capture.TcpPacket.Companion.ACK
import com.kite.capture.TcpPacket.Companion.FIN
import com.kite.capture.TcpPacket.Companion.PSH
import com.kite.capture.TcpPacket.Companion.RST
import com.kite.capture.TcpPacket.Companion.SYN
import java.io.IOException
import java.io.OutputStream
import java.net.InetSocketAddress
import java.net.Proxy
import java.net.Socket
import java.net.SocketTimeoutException
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.ThreadLocalRandom
import java.util.concurrent.TimeUnit
import kotlin.concurrent.thread

// The TUN thread owns the flow table. Each worker owns its TCP sequence and close state.
internal class TcpRelay(
    private val protect: (Socket) -> Boolean,
    private val emit: (ByteArray) -> Unit,
    private val error: (String) -> Unit,
    private val count: (Long) -> Unit,
) {
    private val flows = mutableMapOf<FlowKey, Connection>()

    fun tick() {
        val now = SystemClock.elapsedRealtime()
        val iterator = flows.values.iterator()
        while (iterator.hasNext()) {
            val connection = iterator.next()
            if (!connection.worker.isAlive) iterator.remove()
            else if (now - connection.lastActivity >= IDLE_TIMEOUT) connection.cancel("TCP idle timeout")
        }
        count(flows.size.toLong())
    }

    fun accept(packet: TcpPacket) {
        val connection = flows[packet.flow]
        if (connection != null && connection.worker.isAlive) {
            connection.accept(packet)
            return
        }
        flows.remove(packet.flow)
        if (packet.has(RST)) return
        if (packet.size > MTU || !packet.has(SYN) || packet.has(ACK) || packet.has(FIN)) {
            emit(packet.reset())
            return
        }
        if (flows.size >= MAX_CONNECTIONS) {
            error("TCP connection limit reached ($MAX_CONNECTIONS)")
            emit(packet.reset())
            return
        }
        flows[packet.flow] = Connection(packet)
        count(flows.size.toLong())
    }

    fun close() {
        flows.values.forEach { it.cancel() }
        flows.values.forEach { it.worker.join() }
        flows.clear()
        count(0)
    }

    private enum class State {
        CONNECTING, SYN_RECEIVED, ESTABLISHED, CLOSE_WAIT, FIN_WAIT, CLOSING, CLOSED,
    }

    private inner class Connection(private val syn: TcpPacket) {
        private val socket = Socket(Proxy.NO_PROXY)
        private val pending = ArrayBlockingQueue<TcpPacket>(64)
        private val initial = ThreadLocalRandom.current().nextInt()
        private val peerMss = minOf(TcpPacket.MSS, syn.mss ?: 536)
        private var state = State.CONNECTING
        private var sendNext = initial
        private var sendAcked = initial
        private var receiveNext = syn.sequence + 1
        private var peerWindow = syn.window
        private var windowSequence = syn.sequence
        private var windowAck = initial
        @Volatile var lastActivity = SystemClock.elapsedRealtime()
            private set
        @Volatile private var cancelled = false
        @Volatile private var cancelError: String? = null
        val worker = thread(name = "tcp-relay") { run() }

        fun accept(packet: TcpPacket) {
            if (packet.has(RST)) {
                cancel()
            } else if (!cancelled) {
                if (packet.size > MTU) cancel("TCP segment exceeds TUN MTU")
                else if (!pending.offer(packet)) cancel("TCP receive queue full")
            }
        }

        fun cancel(reason: String? = null) {
            if (!cancelled || reason == null) {
                cancelError = reason
                cancelled = true
                runCatching { socket.close() }
                worker.interrupt()
            }
        }

        private fun run() {
            try {
                if (!protect(socket)) throw IOException("Could not protect TCP socket")
                socket.tcpNoDelay = true
                socket.soTimeout = POLL_MS
                socket.connect(InetSocketAddress(syn.flow.remote, syn.flow.remotePort), CONNECT_TIMEOUT)
                if (cancelled) return
                val input = socket.getInputStream()
                val output = socket.getOutputStream()
                val bytes = ByteArray(peerMss)
                send(TcpPacket.reply(syn.flow, initial, receiveNext, SYN or ACK))
                sendNext++
                state = State.SYN_RECEIVED

                while (!cancelled && state != State.CLOSED) {
                    val canRead = (state == State.ESTABLISHED || state == State.CLOSE_WAIT) &&
                        remainingWindow() > 0
                    val packet = if (canRead) pending.poll() else pending.poll(POLL_MS.toLong(), TimeUnit.MILLISECONDS)
                    if (packet != null && !cancelled) {
                        receive(packet, output)
                        for (i in 1 until RECEIVE_BATCH) {
                            if (cancelled || state == State.CLOSED) break
                            receive(pending.poll() ?: break, output)
                        }
                    }
                    if (cancelled || (state != State.ESTABLISHED && state != State.CLOSE_WAIT)) continue
                    val size = minOf(bytes.size, remainingWindow())
                    if (size <= 0) continue
                    val read = try {
                        input.read(bytes, 0, size)
                    } catch (_: SocketTimeoutException) {
                        continue
                    }
                    if (cancelled) break
                    if (read < 0) {
                        send(TcpPacket.reply(syn.flow, sendNext, receiveNext, FIN or ACK))
                        sendNext++
                        state = if (state == State.CLOSE_WAIT) State.CLOSING else State.FIN_WAIT
                    } else if (read > 0) {
                        send(TcpPacket.reply(syn.flow, sendNext, receiveNext, PSH or ACK, bytes, read))
                        sendNext += read
                    }
                }
            } catch (failure: Exception) {
                if (!cancelled) abort(failure.message ?: "TCP relay failed")
            } finally {
                cancelError?.let { abort(it) }
                state = State.CLOSED
                runCatching { socket.close() }
            }
        }

        private fun receive(packet: TcpPacket, output: OutputStream) {
            if (packet.has(SYN)) {
                if (state == State.SYN_RECEIVED && packet.sequence == syn.sequence && !packet.has(ACK)) {
                    send(TcpPacket.reply(syn.flow, initial, receiveNext, SYN or ACK))
                }
                return
            }
            if (!packet.has(ACK)) return
            if (state == State.SYN_RECEIVED) {
                if (packet.acknowledgment != sendNext || packet.sequence != receiveNext) return
                state = State.ESTABLISHED
            }
            // Signed differences compare wrapping TCP sequence numbers within a window.
            if (packet.sequence != receiveNext || packet.acknowledgment - sendNext > 0) {
                acknowledge()
                return
            }
            if (packet.acknowledgment - sendAcked >= 0) {
                sendAcked = packet.acknowledgment
                if (packet.sequence - windowSequence > 0 ||
                    (packet.sequence == windowSequence && packet.acknowledgment - windowAck >= 0)
                ) {
                    peerWindow = packet.window
                    windowSequence = packet.sequence
                    windowAck = packet.acknowledgment
                }
            }
            lastActivity = SystemClock.elapsedRealtime()
            if (state == State.ESTABLISHED || state == State.FIN_WAIT) {
                if (packet.payload.isNotEmpty()) {
                    output.write(packet.payload)
                    receiveNext += packet.payload.size
                }
                if (packet.has(FIN)) {
                    socket.shutdownOutput()
                    receiveNext++
                    state = if (state == State.FIN_WAIT) State.CLOSING else State.CLOSE_WAIT
                }
            }
            if (packet.payload.isNotEmpty() || packet.has(FIN)) acknowledge()
            if (state == State.CLOSING && sendAcked == sendNext) state = State.CLOSED
        }

        private fun remainingWindow(): Int = peerWindow - (sendNext - sendAcked)

        private fun acknowledge() = send(TcpPacket.reply(syn.flow, sendNext, receiveNext, ACK))

        private fun send(packet: ByteArray) {
            if (cancelled) return
            emit(packet)
            lastActivity = SystemClock.elapsedRealtime()
        }

        private fun abort(message: String) {
            error(message)
            runCatching {
                val reset = if (state == State.CONNECTING) syn.reset()
                else TcpPacket.reply(syn.flow, sendNext, receiveNext, RST or ACK)
                emit(reset)
            }
        }
    }

    private companion object {
        const val MTU = 1500
        const val RECEIVE_BATCH = 16
        const val MAX_CONNECTIONS = 32
        const val IDLE_TIMEOUT = 60_000L
        const val CONNECT_TIMEOUT = 10_000
        const val POLL_MS = 25
    }
}
