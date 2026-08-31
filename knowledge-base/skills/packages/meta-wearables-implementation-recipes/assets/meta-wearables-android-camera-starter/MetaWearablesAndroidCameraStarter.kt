package example.metawearables.camera

import com.meta.wearable.dat.camera.Camera
import com.meta.wearable.dat.camera.Stream
import com.meta.wearable.dat.camera.addCamera
import com.meta.wearable.dat.camera.types.PhotoData
import com.meta.wearable.dat.camera.types.StreamConfiguration
import com.meta.wearable.dat.camera.types.StreamState
import com.meta.wearable.dat.camera.types.VideoQuality
import com.meta.wearable.dat.core.Wearables
import com.meta.wearable.dat.core.selectors.DeviceSelector
import com.meta.wearable.dat.core.session.DeviceSession
import com.meta.wearable.dat.core.session.DeviceSessionState
import com.meta.wearable.dat.core.types.Permission
import com.meta.wearable.dat.core.types.PermissionStatus
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch

public enum class MetaWearablesAndroidCameraFallback {
  NO_SESSION,
  PERMISSION_DENIED,
  CAMERA_UNAVAILABLE,
  CAPTURE_FAILED,
  SESSION_UNAVAILABLE,
  DAT_APP_UPDATE_REQUIRED,
}

public enum class MetaWearablesAndroidCameraFailure {
  SESSION,
  STREAM,
  PERMISSION,
}

public sealed interface MetaWearablesAndroidCameraEvent {
  public data object SessionStarted : MetaWearablesAndroidCameraEvent

  public data object StreamStarted : MetaWearablesAndroidCameraEvent

  public data object FirstFrameReceived : MetaWearablesAndroidCameraEvent

  public data object PhotoReceived : MetaWearablesAndroidCameraEvent

  public data object StreamStopped : MetaWearablesAndroidCameraEvent

  public data class PhoneFallback(
      val reason: MetaWearablesAndroidCameraFallback,
  ) : MetaWearablesAndroidCameraEvent

  public data class Failure(
      val reason: MetaWearablesAndroidCameraFailure,
  ) : MetaWearablesAndroidCameraEvent
}

/**
 * A narrow DAT 0.9 Android camera/photo adapter.
 *
 * Raw VideoFrame values stay inside this adapter. The photo sink is an explicit
 * phone-local boundary; callers must decide whether to decode, retain, delete,
 * or transmit captured media.
 */
public class MetaWearablesAndroidCameraCoordinator(
    private val scope: CoroutineScope,
    private val eventSink: (MetaWearablesAndroidCameraEvent) -> Unit,
    private val photoSink: (PhotoData) -> Unit = {},
    private val dispatcher: CoroutineDispatcher = Dispatchers.Main.immediate,
) {
  private val resourceLock = Any()

  private var sessionEpoch = 0L
  private var session: DeviceSession? = null
  private var camera: Camera? = null
  private var stream: Stream? = null
  private var sessionStateJob: Job? = null
  private var sessionErrorJob: Job? = null
  private var streamStateJob: Job? = null
  private var streamErrorJob: Job? = null
  private var frameJob: Job? = null

  public fun startSession(deviceSelector: DeviceSelector) {
    val currentEpoch = synchronized(resourceLock) {
      if (session != null) {
        null
      } else {
        sessionEpoch += 1
        sessionEpoch
      }
    } ?: return

    Wearables.createSession(deviceSelector).fold(
        onSuccess = { nextSession ->
          if (!isCurrentSession(currentEpoch)) {
            nextSession.stop()
            return@fold
          }
          synchronized(resourceLock) { session = nextSession }
          observeSession(nextSession, currentEpoch)
          nextSession.start()
        },
        onFailure = { _, _ ->
          if (isCurrentSessionEpoch(currentEpoch)) {
            eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.SESSION))
            eventSink(
                MetaWearablesAndroidCameraEvent.PhoneFallback(
                    MetaWearablesAndroidCameraFallback.SESSION_UNAVAILABLE,
                ),
            )
          }
        },
    )
  }

  /** Query permission without initiating the Meta AI app redirect. */
  public fun startCameraIfPermitted() {
    val currentEpoch = synchronized(resourceLock) { sessionEpoch }
    if (!isCurrentSession(currentEpoch)) {
      eventSink(
          MetaWearablesAndroidCameraEvent.PhoneFallback(
              MetaWearablesAndroidCameraFallback.NO_SESSION,
          ),
      )
      return
    }

    scope.launch(dispatcher) {
      Wearables.checkPermissionStatus(Permission.CAMERA).fold(
          onSuccess = { status ->
            if (status == PermissionStatus.Granted) {
              attachCamera(currentEpoch)
            } else {
              eventSink(
                  MetaWearablesAndroidCameraEvent.PhoneFallback(
                      MetaWearablesAndroidCameraFallback.PERMISSION_DENIED,
                  ),
              )
            }
          },
          onFailure = { _, _ ->
            eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.PERMISSION))
            eventSink(
                MetaWearablesAndroidCameraEvent.PhoneFallback(
                    MetaWearablesAndroidCameraFallback.PERMISSION_DENIED,
                ),
            )
          },
      )
    }
  }

  /** Use only after an app-owned confirmation of the Meta AI permission redirect. */
  public fun requestCameraPermissionAndStart(
      requestPermission: suspend (Permission) -> PermissionStatus,
  ) {
    scope.launch(dispatcher) {
      val status = requestPermission(Permission.CAMERA)
      if (status == PermissionStatus.Granted) {
        attachCamera(synchronized(resourceLock) { sessionEpoch })
      } else {
        eventSink(
            MetaWearablesAndroidCameraEvent.PhoneFallback(
                MetaWearablesAndroidCameraFallback.PERMISSION_DENIED,
            ),
        )
      }
    }
  }

  public fun capturePhoto() {
    val currentStream = synchronized(resourceLock) { stream }
    if (currentStream == null) {
      eventSink(
          MetaWearablesAndroidCameraEvent.PhoneFallback(
              MetaWearablesAndroidCameraFallback.CAMERA_UNAVAILABLE,
          ),
      )
      return
    }

    scope.launch(dispatcher) {
      currentStream.capturePhoto().fold(
          onSuccess = { photo ->
            photoSink(photo)
            eventSink(MetaWearablesAndroidCameraEvent.PhotoReceived)
          },
          onFailure = { _, _ ->
            eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.STREAM))
            eventSink(
                MetaWearablesAndroidCameraEvent.PhoneFallback(
                    MetaWearablesAndroidCameraFallback.CAPTURE_FAILED,
                ),
            )
          },
      )
    }
  }

  /** Cancel collectors, close the camera child, then stop the parent session. */
  public fun stop() {
    val resources = synchronized(resourceLock) {
      sessionEpoch += 1
      val current = StopResources(
          session = session,
          camera = camera,
          sessionStateJob = sessionStateJob,
          sessionErrorJob = sessionErrorJob,
          streamStateJob = streamStateJob,
          streamErrorJob = streamErrorJob,
          frameJob = frameJob,
      )
      session = null
      camera = null
      stream = null
      sessionStateJob = null
      sessionErrorJob = null
      streamStateJob = null
      streamErrorJob = null
      frameJob = null
      current
    }

    resources.sessionStateJob?.cancel()
    resources.sessionErrorJob?.cancel()
    resources.streamStateJob?.cancel()
    resources.streamErrorJob?.cancel()
    resources.frameJob?.cancel()
    resources.camera?.close()
    resources.session?.stop()
    if (resources.camera != null) {
      eventSink(MetaWearablesAndroidCameraEvent.StreamStopped)
    }
  }

  private fun attachCamera(currentEpoch: Long) {
    val currentSession = synchronized(resourceLock) { session }
    if (currentSession == null || !isCurrentSession(currentEpoch)) {
      eventSink(
          MetaWearablesAndroidCameraEvent.PhoneFallback(
              MetaWearablesAndroidCameraFallback.SESSION_UNAVAILABLE,
          ),
      )
      return
    }

    currentSession
        .addCamera(
            StreamConfiguration(
                videoQuality = VideoQuality.MEDIUM,
                frameRate = 24,
                compressVideo = true,
            ),
        )
        .fold(
            onSuccess = { nextCamera ->
              if (!isCurrentSession(currentEpoch)) {
                nextCamera.close()
                return@fold
              }
              val nextStream = nextCamera.stream
              synchronized(resourceLock) {
                camera = nextCamera
                stream = nextStream
              }
              observeStream(nextCamera, nextStream, currentEpoch)
              nextStream.start().onFailure { _, _ ->
                eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.STREAM))
                clearStreamResources()
              }
            },
            onFailure = { _, _ ->
              eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.STREAM))
              eventSink(
                  MetaWearablesAndroidCameraEvent.PhoneFallback(
                      MetaWearablesAndroidCameraFallback.CAMERA_UNAVAILABLE,
                  ),
              )
            },
        )
  }

  private fun observeSession(session: DeviceSession, currentEpoch: Long) {
    sessionStateJob?.cancel()
    sessionErrorJob?.cancel()
    sessionStateJob = scope.launch(dispatcher) {
      session.state.collect { state ->
        if (!isCurrentSession(currentEpoch)) return@collect
        if (state == DeviceSessionState.STARTED) {
          eventSink(MetaWearablesAndroidCameraEvent.SessionStarted)
        } else if (state == DeviceSessionState.STOPPED) {
          clearStreamResources()
          eventSink(
              MetaWearablesAndroidCameraEvent.PhoneFallback(
                  MetaWearablesAndroidCameraFallback.SESSION_UNAVAILABLE,
              ),
          )
        }
      }
    }
    sessionErrorJob = scope.launch(dispatcher) {
      session.errors.collect { error ->
        if (!isCurrentSession(currentEpoch)) return@collect
        eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.SESSION))
        if (error == com.meta.wearable.dat.core.types.DeviceSessionError.DAT_APP_ON_THE_GLASSES_UPDATE_REQUIRED) {
          eventSink(
              MetaWearablesAndroidCameraEvent.PhoneFallback(
                  MetaWearablesAndroidCameraFallback.DAT_APP_UPDATE_REQUIRED,
              ),
          )
        } else {
          eventSink(
              MetaWearablesAndroidCameraEvent.PhoneFallback(
                  MetaWearablesAndroidCameraFallback.SESSION_UNAVAILABLE,
              ),
          )
        }
      }
    }
  }

  private fun observeStream(
      camera: Camera,
      stream: Stream,
      currentEpoch: Long,
  ) {
    streamStateJob?.cancel()
    streamErrorJob?.cancel()
    frameJob?.cancel()
    var firstFrameSeen = false
    frameJob = scope.launch(dispatcher) {
      stream.videoStream.collect {
        if (isCurrentSession(currentEpoch) && !firstFrameSeen) {
          firstFrameSeen = true
          eventSink(MetaWearablesAndroidCameraEvent.FirstFrameReceived)
        }
      }
    }
    streamStateJob = scope.launch(dispatcher) {
      stream.state.collect { state ->
        if (!isCurrentSession(currentEpoch)) return@collect
        if (state == StreamState.STREAMING) {
          eventSink(MetaWearablesAndroidCameraEvent.StreamStarted)
        } else if (state == StreamState.STOPPED || state == StreamState.CLOSED) {
          eventSink(MetaWearablesAndroidCameraEvent.StreamStopped)
          clearStreamResources()
        }
      }
    }
    streamErrorJob = scope.launch(dispatcher) {
      stream.errorStream.collect {
        if (isCurrentSession(currentEpoch)) {
          eventSink(MetaWearablesAndroidCameraEvent.Failure(MetaWearablesAndroidCameraFailure.STREAM))
          eventSink(
              MetaWearablesAndroidCameraEvent.PhoneFallback(
                  MetaWearablesAndroidCameraFallback.CAMERA_UNAVAILABLE,
              ),
          )
        }
      }
    }
  }

  private fun clearStreamResources() {
    val resources = synchronized(resourceLock) {
      val current = StreamResources(
          camera = camera,
          streamStateJob = streamStateJob,
          streamErrorJob = streamErrorJob,
          frameJob = frameJob,
      )
      camera = null
      stream = null
      streamStateJob = null
      streamErrorJob = null
      frameJob = null
      current
    }
    resources.streamStateJob?.cancel()
    resources.streamErrorJob?.cancel()
    resources.frameJob?.cancel()
    resources.camera?.close()
  }

  private fun isCurrentSession(currentEpoch: Long): Boolean =
      synchronized(resourceLock) {
        session != null && sessionEpoch == currentEpoch
      }

  private fun isCurrentSessionEpoch(currentEpoch: Long): Boolean =
      synchronized(resourceLock) { sessionEpoch == currentEpoch }

  private data class StreamResources(
      val camera: Camera?,
      val streamStateJob: Job?,
      val streamErrorJob: Job?,
      val frameJob: Job?,
  )

  private data class StopResources(
      val session: DeviceSession?,
      val camera: Camera?,
      val sessionStateJob: Job?,
      val sessionErrorJob: Job?,
      val streamStateJob: Job?,
      val streamErrorJob: Job?,
      val frameJob: Job?,
  )
}
