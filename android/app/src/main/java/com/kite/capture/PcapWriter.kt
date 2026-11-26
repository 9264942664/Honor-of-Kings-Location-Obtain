package com.kite.capture

import java.io.Closeable
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder

internal class PcapWriter(file: File) : Closeable {
    private val output = file.outputStream().buffered()

    init {
        try {
            val header = littleEndian(24)
                .putInt(0xa1b2c3d4.toInt()).putShort(2.toShort()).putShort(4.toShort())
                .putInt(0).putInt(0).putInt(65535).putInt(101) // LINKTYPE_RAW
            output.write(header.array())
        } catch (error: Exception) {
            runCatching { output.close() }
            throw error
        }
    }

    fun write(packet: ByteArray, size: Int) {
        val now = System.currentTimeMillis()
        val header = littleEndian(16)
            .putInt((now / 1000).toInt()).putInt(((now % 1000) * 1000).toInt())
            .putInt(size).putInt(size)
        output.write(header.array())
        output.write(packet, 0, size)
    }

    override fun close() = output.close()

    private fun littleEndian(size: Int) = ByteBuffer.allocate(size).order(ByteOrder.LITTLE_ENDIAN)
}
