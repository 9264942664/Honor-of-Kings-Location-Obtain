package com.kite.capture

import java.net.InetAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder

internal data class TcpPacket(
    val flow: FlowKey,
    val sequence: Int,
    val acknowledgment: Int,
    val flags: Int,
    val window: Int,
    val mss: Int?,
    val payload: ByteArray,
    val size: Int,
) {
    fun has(flag: Int): Boolean = (flags and flag) != 0

    fun reset(): ByteArray = if (has(ACK)) {
        reply(flow, acknowledgment, 0, RST)
    } else {
        val length = payload.size + (if (has(SYN)) 1 else 0) + (if (has(FIN)) 1 else 0)
        reply(flow, 0, sequence + length, RST or ACK)
    }

    companion object {
        const val FIN = 0x01
        const val SYN = 0x02
        const val RST = 0x04
        const val PSH = 0x08
        const val ACK = 0x10
        const val MSS = 1460
        const val WINDOW = 65535

        fun parse(bytes: ByteArray, size: Int): TcpPacket? {
            if (size < 40 || (bytes[0].toInt() and 0xf0) != 0x40 || bytes[9].toInt() != 6) return null
            val ipLength = (bytes[0].toInt() and 15) * 4
            val totalLength = bytes.u16(2)
            if (ipLength < 20 || totalLength < ipLength + 20 || totalLength > size) return null
            if ((bytes.u16(6) and 0x3fff) != 0) return null
            val tcpLength = ((bytes[ipLength + 12].toInt() and 0xff) ushr 4) * 4
            val start = ipLength + tcpLength
            if (tcpLength < 20 || start > totalLength) return null

            val flags = bytes[ipLength + 13].toInt() and 0xff
            var mss: Int? = null
            if ((flags and SYN) != 0) {
                var offset = ipLength + 20
                while (offset < start) {
                    when (val kind = bytes[offset].toInt() and 0xff) {
                        0 -> break
                        1 -> offset++
                        else -> {
                            if (offset + 1 >= start) return null
                            val length = bytes[offset + 1].toInt() and 0xff
                            if (length < 2 || offset + length > start) return null
                            if (kind == 2 && length == 4) {
                                mss = bytes.u16(offset + 2).takeIf { it > 0 }
                            }
                            offset += length
                        }
                    }
                }
            }
            val flow = FlowKey(
                InetAddress.getByAddress(bytes.copyOfRange(12, 16)),
                bytes.u16(ipLength),
                InetAddress.getByAddress(bytes.copyOfRange(16, 20)),
                bytes.u16(ipLength + 2),
            )
            val header = ByteBuffer.wrap(bytes).order(ByteOrder.BIG_ENDIAN)
            return TcpPacket(
                flow, header.getInt(ipLength + 4), header.getInt(ipLength + 8), flags,
                bytes.u16(ipLength + 14), mss, bytes.copyOfRange(start, totalLength), totalLength,
            )
        }

        fun reply(
            flow: FlowKey,
            sequence: Int,
            acknowledgment: Int,
            flags: Int,
            payload: ByteArray = ByteArray(0),
            size: Int = payload.size,
        ): ByteArray {
            val syn = (flags and SYN) != 0
            val tcpLength = (if (syn) 24 else 20) + size
            val packet = ByteBuffer.allocate(20 + tcpLength).order(ByteOrder.BIG_ENDIAN)
            packet.put(0x45.toByte()).put(0.toByte()).putShort(packet.capacity().toShort())
            packet.putShort(0.toShort()).putShort(0x4000.toShort()).put(64.toByte()).put(6.toByte())
            packet.putShort(0.toShort()).put(flow.remote.address).put(flow.local.address)
            packet.putShort(flow.remotePort.toShort()).putShort(flow.localPort.toShort())
            packet.putInt(sequence).putInt(acknowledgment)
            packet.put((if (syn) 0x60 else 0x50).toByte()).put(flags.toByte())
            packet.putShort((if ((flags and RST) != 0) 0 else WINDOW).toShort())
            packet.putShort(0.toShort()).putShort(0.toShort())
            if (syn) packet.put(2.toByte()).put(4.toByte()).putShort(MSS.toShort())
            packet.put(payload, 0, size)

            val bytes = packet.array()
            packet.putShort(10, checksum(bytes, 0, 20))
            // The pseudo-header includes both IPv4 addresses, protocol and TCP length.
            val pseudoSum = bytes.u16(12) + bytes.u16(14) + bytes.u16(16) + bytes.u16(18) + 6 + tcpLength
            packet.putShort(36, checksum(bytes, 20, bytes.size, pseudoSum))
            return bytes
        }

        private fun checksum(bytes: ByteArray, start: Int, end: Int, initial: Int = 0): Short {
            var sum = initial
            for (offset in start until (end - 1) step 2) sum += bytes.u16(offset)
            if ((end - start) % 2 != 0) sum += (bytes[end - 1].toInt() and 0xff) shl 8
            while (sum > 0xffff) sum = (sum and 0xffff) + (sum ushr 16)
            return sum.inv().toShort()
        }

        private fun ByteArray.u16(offset: Int): Int =
            ((this[offset].toInt() and 0xff) shl 8) or (this[offset + 1].toInt() and 0xff)
    }
}
