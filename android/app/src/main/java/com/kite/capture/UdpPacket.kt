package com.kite.capture

import java.net.InetAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder

internal const val MAX_PAYLOAD = 65527

internal data class FlowKey(
    val local: InetAddress,
    val localPort: Int,
    val remote: InetAddress,
    val remotePort: Int,
)

internal data class UdpPacket(val flow: FlowKey, val payload: ByteArray) {
    companion object {
        fun parse(bytes: ByteArray, size: Int): UdpPacket? {
            if (size < 28 || (bytes[0].toInt() and 0xf0) != 0x40 || bytes[9].toInt() != 17) return null
            val headerLength = (bytes[0].toInt() and 0x0f) * 4
            val totalLength = bytes.u16(2)
            if (headerLength < 20 || totalLength < headerLength + 8 || totalLength > size) return null
            if ((bytes.u16(6) and 0x3fff) != 0) return null

            val udpLength = bytes.u16(headerLength + 4)
            if (udpLength < 8 || headerLength + udpLength != totalLength) return null
            val flow = FlowKey(
                InetAddress.getByAddress(bytes.copyOfRange(12, 16)),
                bytes.u16(headerLength),
                InetAddress.getByAddress(bytes.copyOfRange(16, 20)),
                bytes.u16(headerLength + 2),
            )
            return UdpPacket(flow, bytes.copyOfRange(headerLength + 8, totalLength))
        }

        fun reply(flow: FlowKey, payload: ByteArray, size: Int): ByteArray {
            val packet = ByteBuffer.allocate(28 + size).order(ByteOrder.BIG_ENDIAN)
            packet.put(0x45.toByte()).put(0.toByte()).putShort(packet.capacity().toShort())
            packet.putShort(0.toShort()).putShort(0.toShort()).put(64.toByte()).put(17.toByte())
            packet.putShort(0.toShort()).put(flow.remote.address).put(flow.local.address)
            // IPv4 permits a zero UDP checksum. The IPv4 header still needs its checksum.
            packet.putShort(flow.remotePort.toShort()).putShort(flow.localPort.toShort())
            packet.putShort((size + 8).toShort()).putShort(0.toShort()).put(payload, 0, size)
            val bytes = packet.array()
            var sum = 0
            for (offset in 0 until 20 step 2) sum += bytes.u16(offset)
            while (sum > 0xffff) sum = (sum and 0xffff) + (sum ushr 16)
            packet.putShort(10, sum.inv().toShort())
            return bytes
        }

        private fun ByteArray.u16(offset: Int): Int =
            ((this[offset].toInt() and 0xff) shl 8) or (this[offset + 1].toInt() and 0xff)
    }
}
