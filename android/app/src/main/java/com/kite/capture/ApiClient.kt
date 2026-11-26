package com.kite.capture

import java.io.IOException
import java.net.HttpURLConnection
import java.net.URI
import java.net.URL
import java.nio.charset.StandardCharsets.UTF_8
import java.util.Base64
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.TimeUnit
import org.json.JSONObject

internal const val DEFAULT_URL = "http://39.96.60.127:18081"
internal data class Datagram(val direction: String, val payload: ByteArray)
internal data class Snapshot(val revision: Long, val entityCount: Int)

internal fun serverOrigin(input: String): String? {
    val uri = runCatching { URI(input.trim()) }.getOrNull() ?: return null
    if (uri.scheme !in listOf("http", "https") || uri.host == null || uri.userInfo != null ||
        uri.rawPath !in listOf("", "/") || uri.rawQuery != null || uri.rawFragment != null ||
        (uri.port != -1 && uri.port !in 1..65535)
    ) return null
    return "${uri.scheme}://${uri.rawAuthority}"
}

internal class ApiClient(private val origin: String) {
    private val pending = ArrayBlockingQueue<Datagram>(512)

    fun enqueue(datagram: Datagram): Boolean = pending.offer(datagram)

    fun uploadLoop(active: () -> Boolean, result: (Int, String?) -> Unit) {
        var carry: Datagram? = null
        while (active()) {
            val first = carry ?: pending.poll(250, TimeUnit.MILLISECONDS) ?: continue
            carry = null
            val body = StringBuilder(PREFIX)
            appendRecord(body, first)
            var count = 1
            val deadline = System.nanoTime() + TimeUnit.MILLISECONDS.toNanos(250)
            while (active() && count < 256) {
                val remaining = deadline - System.nanoTime()
                val next = pending.poll(remaining.coerceAtLeast(0), TimeUnit.NANOSECONDS) ?: break
                val record = StringBuilder().also { appendRecord(it, next) }
                if (body.length + 1 + record.length + SUFFIX.length > MAX_BODY) {
                    carry = next
                    break
                }
                body.append(',').append(record)
                count++
            }
            if (!active()) break

            val bytes = body.append(SUFFIX).toString().toByteArray(UTF_8)
            try {
                val accepted = request("/api/client/upload", bytes).first.getInt("accepted")
                if (accepted != count) throw IOException("Unexpected accepted count")
                result(count, null)
            } catch (error: Exception) {
                if (active()) result(0, error.message ?: "Upload failed")
            }
        }
    }

    fun snapshot(): Snapshot {
        val (body, header) = request("/snapshot")
        val revision = body.getLong("revision")
        if (header != revision.toString()) throw IOException("Snapshot revision header mismatch")
        return Snapshot(revision, body.getJSONArray("entities").length())
    }

    private fun request(path: String, body: ByteArray? = null): Pair<JSONObject, String?> {
        val connection = URL(origin + path).openConnection() as HttpURLConnection
        try {
            connection.connectTimeout = 4000
            connection.readTimeout = 4000
            connection.instanceFollowRedirects = false
            connection.useCaches = false
            if (body != null) {
                connection.requestMethod = "POST"
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.setFixedLengthStreamingMode(body.size)
                connection.outputStream.use { it.write(body) }
            }
            val status = connection.responseCode
            if (status != 200) throw IOException("HTTP $status")
            val json = connection.inputStream.bufferedReader(UTF_8).use { it.readText() }
            return JSONObject(json) to connection.getHeaderField("X-Kite-Snapshot")
        } finally {
            connection.disconnect()
        }
    }

    private fun appendRecord(body: StringBuilder, datagram: Datagram) {
        require(datagram.payload.size <= MAX_PAYLOAD)
        val encoded = Base64.getEncoder().encodeToString(datagram.payload)
        body.append("""{"direction":"${datagram.direction}","payload_b64":"$encoded"}""")
    }

    private companion object {
        const val MAX_BODY = 1024 * 1024
        const val PREFIX = """{"datagrams":["""
        const val SUFFIX = "]}"
    }
}
