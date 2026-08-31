package com.example.metawearables.targetstarter

import android.Manifest.permission.BLUETOOTH
import android.Manifest.permission.BLUETOOTH_CONNECT
import android.Manifest.permission.INTERNET
import android.app.Activity
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.TextView
import com.meta.wearable.dat.core.Wearables

/**
 * Minimal target-owned DAT bootstrap.
 *
 * Registration, device metadata, capability selection, and the selected
 * adapter belong in the next implementation slice. This activity only proves
 * that the Android target owns permission/init policy at the platform edge.
 */
class MainActivity : Activity() {
  companion object {
    private const val PERMISSION_REQUEST_CODE = 1001
  }

  private lateinit var statusView: TextView
  private var datInitialized = false

  private val requiredPermissions = arrayOf(BLUETOOTH, BLUETOOTH_CONNECT, INTERNET)

  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    statusView = TextView(this).apply {
      text = "Meta Wearables DAT target starter\nWaiting for permissions"
      textSize = 18f
      setPadding(32, 48, 32, 48)
    }
    setContentView(statusView)
  }

  override fun onStart() {
    super.onStart()
    if (requiredPermissions.all(::hasPermission)) {
      initializeDat()
    } else {
      requestPermissions(requiredPermissions, PERMISSION_REQUEST_CODE)
    }
  }

  override fun onRequestPermissionsResult(
      requestCode: Int,
      permissions: Array<out String>,
      grantResults: IntArray,
  ) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults)
    if (requestCode != PERMISSION_REQUEST_CODE) return

    if (grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
      initializeDat()
    } else {
      statusView.text =
          "Required permissions were not granted.\nKeep the phone fallback available."
    }
  }

  private fun hasPermission(permission: String): Boolean =
      checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED

  private fun initializeDat() {
    if (datInitialized) return
    Wearables.initialize(this)
    datInitialized = true
    statusView.text =
        "DAT initialized.\nNext: registration, device capability, and selected adapter."
  }
}
