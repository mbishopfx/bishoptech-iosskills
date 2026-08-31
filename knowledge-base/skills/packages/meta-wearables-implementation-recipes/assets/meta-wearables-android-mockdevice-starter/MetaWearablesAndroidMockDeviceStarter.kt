package example.metawearables.mockdevice

import android.content.Context
import android.net.Uri
import com.meta.wearable.dat.core.types.Permission
import com.meta.wearable.dat.core.types.PermissionStatus
import com.meta.wearable.dat.mockdevice.MockDeviceKit
import com.meta.wearable.dat.mockdevice.api.GlassesModel
import com.meta.wearable.dat.mockdevice.api.MockDeviceKitConfig
import com.meta.wearable.dat.mockdevice.api.MockDeviceKitInterface
import com.meta.wearable.dat.mockdevice.api.MockGlasses
import com.meta.wearable.dat.mockdevice.api.camera.CameraFacing

public sealed interface MetaWearablesAndroidMockDeviceEvent {
  public data object Enabled : MetaWearablesAndroidMockDeviceEvent
  public data object Disabled : MetaWearablesAndroidMockDeviceEvent
  public data object PairedRayBanMeta : MetaWearablesAndroidMockDeviceEvent
  public data object UnpairedRayBanMeta : MetaWearablesAndroidMockDeviceEvent
  public data object LifecycleChanged : MetaWearablesAndroidMockDeviceEvent
  public data object CameraPermissionConfigured : MetaWearablesAndroidMockDeviceEvent
  public data object CameraFeedConfigured : MetaWearablesAndroidMockDeviceEvent
  public data object CapturedImageConfigured : MetaWearablesAndroidMockDeviceEvent
  public data object CaptouchTriggered : MetaWearablesAndroidMockDeviceEvent
  public data object NoPairedDevice : MetaWearablesAndroidMockDeviceEvent
  public data object PairFailed : MetaWearablesAndroidMockDeviceEvent
}

/**
 * A small target-owned MockDeviceKit harness for deterministic DAT tests.
 *
 * URIs are used only as inputs to the mock camera service. They are never
 * logged or emitted as test events, and mock results remain mock evidence.
 * Android runtime permission grants belong in the instrumentation target; this
 * reusable harness deliberately does not execute shell commands.
 */
public class MetaWearablesAndroidMockDeviceHarness(
    private val mockDeviceKit: MockDeviceKitInterface,
    private val eventSink: (MetaWearablesAndroidMockDeviceEvent) -> Unit = {},
) {
  public constructor(
      context: Context,
      eventSink: (MetaWearablesAndroidMockDeviceEvent) -> Unit = {},
  ) : this(MockDeviceKit.getInstance(context), eventSink)

  private var glasses: MockGlasses? = null

  public val isEnabled: Boolean
    get() = mockDeviceKit.isEnabled

  public val hasPairedRayBanMeta: Boolean
    get() = glasses != null

  public fun enable(
      initiallyRegistered: Boolean = true,
      initialPermissionsGranted: Boolean = true,
  ) {
    mockDeviceKit.enable(
        MockDeviceKitConfig(
            initiallyRegistered = initiallyRegistered,
            initialPermissionsGranted = initialPermissionsGranted,
        ),
    )
    eventSink(MetaWearablesAndroidMockDeviceEvent.Enabled)
  }

  public fun pairRayBanMeta(): Boolean {
    if (glasses != null) return true

    return mockDeviceKit.pairGlasses(GlassesModel.RAYBAN_META).fold(
        onSuccess = { device ->
          glasses = device
          eventSink(MetaWearablesAndroidMockDeviceEvent.PairedRayBanMeta)
          true
        },
        onFailure = { _, _ ->
          eventSink(MetaWearablesAndroidMockDeviceEvent.PairFailed)
          false
        },
    )
  }

  public fun unpairRayBanMeta() {
    val device = glasses
    if (device == null) {
      eventSink(MetaWearablesAndroidMockDeviceEvent.NoPairedDevice)
      return
    }
    mockDeviceKit.unpairDevice(device)
    glasses = null
    eventSink(MetaWearablesAndroidMockDeviceEvent.UnpairedRayBanMeta)
  }

  public fun powerOn() = performLifecycle { it.powerOn() }
  public fun powerOff() = performLifecycle { it.powerOff() }
  public fun unfold() = performLifecycle { it.unfold() }
  public fun fold() = performLifecycle { it.fold() }
  public fun don() = performLifecycle { it.don() }
  public fun doff() = performLifecycle { it.doff() }

  public fun setCameraPermission(
      status: PermissionStatus,
      requestResult: PermissionStatus,
  ) {
    mockDeviceKit.permissions.set(Permission.CAMERA, status)
    mockDeviceKit.permissions.setRequestResult(Permission.CAMERA, requestResult)
    eventSink(MetaWearablesAndroidMockDeviceEvent.CameraPermissionConfigured)
  }

  public fun setCameraFeed(uri: Uri) {
    val device = glasses ?: return noPairedDevice()
    device.services.camera.setCameraFeed(uri)
    eventSink(MetaWearablesAndroidMockDeviceEvent.CameraFeedConfigured)
  }

  public fun setCameraFeed(cameraFacing: CameraFacing) {
    val device = glasses ?: return noPairedDevice()
    device.services.camera.setCameraFeed(cameraFacing)
    eventSink(MetaWearablesAndroidMockDeviceEvent.CameraFeedConfigured)
  }

  public fun setCapturedImage(uri: Uri) {
    val device = glasses ?: return noPairedDevice()
    device.services.camera.setCapturedImage(uri)
    eventSink(MetaWearablesAndroidMockDeviceEvent.CapturedImageConfigured)
  }

  public fun tap() = performInput { it.services.captouch.tap() }
  public fun tapAndHold() = performInput { it.services.captouch.tapAndHold() }

  /** Release the paired mock before disabling the shared kit. */
  public fun disable() {
    glasses?.let(mockDeviceKit::unpairDevice)
    glasses = null
    mockDeviceKit.disable()
    eventSink(MetaWearablesAndroidMockDeviceEvent.Disabled)
  }

  private fun performLifecycle(operation: (MockGlasses) -> Unit) {
    val device = glasses ?: return noPairedDevice()
    operation(device)
    eventSink(MetaWearablesAndroidMockDeviceEvent.LifecycleChanged)
  }

  private fun performInput(operation: (MockGlasses) -> Unit) {
    val device = glasses ?: return noPairedDevice()
    operation(device)
    eventSink(MetaWearablesAndroidMockDeviceEvent.CaptouchTriggered)
  }

  private fun noPairedDevice() {
    eventSink(MetaWearablesAndroidMockDeviceEvent.NoPairedDevice)
  }
}
