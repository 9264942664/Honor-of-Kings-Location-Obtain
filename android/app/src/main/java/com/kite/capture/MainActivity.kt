package com.kite.capture

import android.app.Activity
import android.content.Intent
import android.net.VpnService
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.text.InputType
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast
import java.io.File
import java.io.IOException
import kotlin.concurrent.thread

class MainActivity : Activity() {
    private val main = Handler(Looper.getMainLooper())
    private lateinit var server: EditText
    private lateinit var target: EditText
    private lateinit var start: Button
    private lateinit var stop: Button
    private lateinit var export: Button
    private lateinit var statusLine: TextView
    private lateinit var details: TextView
    private var pendingOrigin: String? = null
    private var pendingPackage: String? = null
    private var exportFile: File? = null

    private val refresh = object : Runnable {
        override fun run() {
            render()
            main.postDelayed(this, 500)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        pendingOrigin = savedInstanceState?.getString("pendingOrigin")
        pendingPackage = savedInstanceState?.getString("pendingPackage")
        exportFile = savedInstanceState?.getString("exportFile")?.let(::File)
        val prefs = getSharedPreferences("capture", MODE_PRIVATE)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            val padding = (20 * resources.displayMetrics.density).toInt()
            setPadding(padding, padding, padding, padding)
        }
        root.addView(TextView(this).apply { text = "Server base URL" })
        server = EditText(this).apply {
            id = 101
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
            setSingleLine()
            setText(prefs.getString("server", DEFAULT_URL))
        }
        root.addView(server)
        root.addView(TextView(this).apply { text = "Installed app package to capture" })
        target = EditText(this).apply {
            id = 102
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_NO_SUGGESTIONS
            setSingleLine()
            hint = "com.example.app"
            setText(prefs.getString("target", ""))
        }
        root.addView(target)
        root.addView(TextView(this).apply {
            text = "IPv4 UDP payloads are sent to the server. The selected app's IPv4 TCP traffic is relayed and saved in the PCAP."
        })
        val buttons = LinearLayout(this)
        start = Button(this).apply {
            text = "Start"
            setOnClickListener { requestCapture() }
        }
        stop = Button(this).apply {
            text = "Stop"
            setOnClickListener { startService(Intent(this@MainActivity, CaptureService::class.java).setAction(CaptureService.ACTION_STOP)) }
        }
        buttons.addView(start)
        buttons.addView(stop)
        root.addView(buttons)
        statusLine = TextView(this)
        details = TextView(this)
        root.addView(statusLine)
        root.addView(details)
        export = Button(this).apply {
            text = "Export PCAP"
            setOnClickListener { chooseExportLocation() }
        }
        root.addView(export)
        setContentView(ScrollView(this).apply { addView(root) })
    }

    override fun onStart() {
        super.onStart()
        refresh.run()
    }

    override fun onStop() {
        main.removeCallbacks(refresh)
        super.onStop()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("pendingOrigin", pendingOrigin)
        outState.putString("pendingPackage", pendingPackage)
        outState.putString("exportFile", exportFile?.absolutePath)
    }

    private fun requestCapture() {
        val origin = serverOrigin(server.text.toString())
        val selectedPackage = target.text.toString().trim()
        if (origin == null) {
            server.error = "Enter an HTTP or HTTPS origin"
            return
        }
        if (selectedPackage.isBlank() || selectedPackage == packageName) {
            target.error = "Enter another installed app's package name"
            return
        }

        pendingOrigin = origin
        pendingPackage = selectedPackage
        val permission = VpnService.prepare(this)
        if (permission == null) startCapture() else startActivityForResult(permission, VPN_PERMISSION)
    }

    private fun startCapture() {
        val origin = pendingOrigin ?: return
        val selectedPackage = pendingPackage ?: return
        pendingOrigin = null
        pendingPackage = null
        getSharedPreferences("capture", MODE_PRIVATE).edit()
            .putString("server", origin).putString("target", selectedPackage).apply()
        startForegroundService(Intent(this, CaptureService::class.java).apply {
            action = CaptureService.ACTION_START
            putExtra(CaptureService.EXTRA_ORIGIN, origin)
            putExtra(CaptureService.EXTRA_PACKAGE, selectedPackage)
        })
    }

    private fun render() {
        val status = CaptureService.status
        val snapshot = status.snapshot
        statusLine.text = "Captured ${status.captured.get()} · Uploaded ${status.uploaded.get()} · " +
            "TCP active ${status.tcpConnections.get()} · Revision ${snapshot?.revision ?: "—"} · Entities ${snapshot?.entityCount ?: "—"}"
        details.text = listOfNotNull(
            status.message,
            status.file?.takeIf { it.isFile }?.name,
            status.uploadError?.let { "Upload: $it" },
            status.snapshotError?.let { "Snapshot: $it" },
            status.relayError?.let { "Relay: $it" },
            status.queueDrops.get().takeIf { it > 0 }?.let { "Upload queue drops: $it" },
        ).joinToString("\n")
        start.isEnabled = !status.busy
        stop.isEnabled = status.busy
        server.isEnabled = !status.busy
        target.isEnabled = !status.busy
        export.isEnabled = !status.busy && latestCapture() != null
    }

    private fun latestCapture(): File? =
        filesDir.listFiles { file -> file.isFile && file.name.startsWith("capture-") && file.extension == "pcap" }
            ?.maxByOrNull { it.lastModified() }

    private fun chooseExportLocation() {
        val file = latestCapture() ?: return
        exportFile = file
        startActivityForResult(Intent(Intent.ACTION_CREATE_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/vnd.tcpdump.pcap"
            putExtra(Intent.EXTRA_TITLE, file.name)
        }, EXPORT_PCAP)
    }

    @Deprecated("Uses platform activity results without an AndroidX dependency")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        when (requestCode) {
            VPN_PERMISSION -> if (resultCode == RESULT_OK) {
                startCapture()
            } else {
                pendingOrigin = null
                pendingPackage = null
                Toast.makeText(this, "VPN permission was declined", Toast.LENGTH_SHORT).show()
            }
            EXPORT_PCAP -> {
                val file = exportFile
                exportFile = null
                val destination = data?.data
                if (resultCode != RESULT_OK || file == null || destination == null) return
                thread(name = "pcap-export") {
                    val message = try {
                        val output = contentResolver.openOutputStream(destination)
                            ?: throw IOException("Could not open the selected document")
                        output.use { dest -> file.inputStream().use { it.copyTo(dest) } }
                        "PCAP exported"
                    } catch (error: Exception) {
                        "Export failed: ${error.message}"
                    }
                    main.post { Toast.makeText(this, message, Toast.LENGTH_SHORT).show() }
                }
            }
        }
    }

    private companion object {
        const val VPN_PERMISSION = 1
        const val EXPORT_PCAP = 2
    }
}
