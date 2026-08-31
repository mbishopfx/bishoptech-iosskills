package example.metawearables.display

import com.meta.wearable.dat.core.Wearables
import com.meta.wearable.dat.core.selectors.SpecificDeviceSelector
import com.meta.wearable.dat.core.session.DeviceSession
import com.meta.wearable.dat.core.session.DeviceSessionState
import com.meta.wearable.dat.core.types.DeviceIdentifier
import com.meta.wearable.dat.core.types.DeviceSessionError
import com.meta.wearable.dat.display.Display
import com.meta.wearable.dat.display.addDisplay
import com.meta.wearable.dat.display.removeDisplay
import com.meta.wearable.dat.display.types.DisplayState
import com.meta.wearable.dat.display.views.ButtonStyle
import com.meta.wearable.dat.display.views.ContentScope
import com.meta.wearable.dat.display.views.Direction
import com.meta.wearable.dat.display.views.FlexBoxBackground
import com.meta.wearable.dat.display.views.IconName
import com.meta.wearable.dat.display.views.TextColor
import com.meta.wearable.dat.display.views.TextStyle
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.launch

public data class MetaWearablesAndroidDisplaySnapshot(
    val title: String,
    val detail: String,
)

public enum class MetaWearablesAndroidDisplayAction {
  PRIMARY,
  SECONDARY,
}

public enum class MetaWearablesAndroidDisplayFallback {
  NO_DISPLAY,
  DAT_APP_UPDATE_REQUIRED,
  SESSION_UNAVAILABLE,
  SEND_FAILED,
}

public enum class MetaWearablesAndroidDisplayFailure {
  SESSION,
  DISPLAY,
  SEND,
}

public sealed interface MetaWearablesAndroidDisplayEvent {
  public data object SessionStarted : MetaWearablesAndroidDisplayEvent

  public data object DisplayAttached : MetaWearablesAndroidDisplayEvent

  public data object DisplayStarted : MetaWearablesAndroidDisplayEvent

  public data object DisplayStopped : MetaWearablesAndroidDisplayEvent

  public data object ContentSent : MetaWearablesAndroidDisplayEvent

  public data class Action(
      val value: MetaWearablesAndroidDisplayAction,
  ) : MetaWearablesAndroidDisplayEvent

  public data class PhoneFallback(
      val reason: MetaWearablesAndroidDisplayFallback,
  ) : MetaWearablesAndroidDisplayEvent

  public data class Failure(
      val reason: MetaWearablesAndroidDisplayFailure,
  ) : MetaWearablesAndroidDisplayEvent
}

/**
 * A narrow DAT 0.9 Android Display adapter.
 *
 * Registration, permission requests, `Wearables.initialize(context)`, and
 * display-capable device selection belong to the Android app layer. This
 * coordinator owns one selected `DeviceSession`, its Display child, the
 * `Flow` collectors, a session/content epoch, and typed phone fallback.
 */
public class MetaWearablesAndroidDisplayCoordinator(
    private val scope: CoroutineScope,
    private val eventSink: (MetaWearablesAndroidDisplayEvent) -> Unit,
    private val dispatcher: CoroutineDispatcher = Dispatchers.Main.immediate,
) {
  private val resourceLock = Any()

  // All fields below are protected by resourceLock unless accessed from a
  // method that already holds the lock.
  private var sessionEpoch = 0L
  private var contentEpoch = 0L
  private var session: DeviceSession? = null
  private var display: Display? = null
  private var sessionStateJob: Job? = null
  private var sessionErrorJob: Job? = null
  private var displayStateJob: Job? = null

  /**
   * Start a session for a device selected by the app's metadata UI.
   *
   * The caller should only pass a connected, compatible,
   * `Device.isDisplayCapable()` device after registration has reached
   * `RegistrationState.REGISTERED`.
   */
  public fun start(deviceId: DeviceIdentifier) {
    val currentEpoch = synchronized(resourceLock) {
      if (session != null) {
        null
      } else {
        sessionEpoch += 1
        contentEpoch += 1
        sessionEpoch
      }
    } ?: return

    Wearables.createSession(SpecificDeviceSelector(deviceId)).fold(
        onSuccess = { nextSession ->
          if (isCurrentSession(currentEpoch)) {
            synchronized(resourceLock) { session = nextSession }
            observeSession(nextSession, currentEpoch)
            // DAT reports asynchronous start failures through session.errors.
            nextSession.start()
          } else {
            nextSession.stop()
          }
        },
        onFailure = { error, _ ->
          if (isCurrentSessionEpoch(currentEpoch)) {
            handleSessionError(error, currentEpoch)
          }
        },
    )
  }

  /** Present one complete root surface; each send replaces the previous one. */
  public fun present(snapshot: MetaWearablesAndroidDisplaySnapshot) {
    val handle = synchronized(resourceLock) {
      val currentDisplay = display
      if (currentDisplay == null || session == null) {
        null
      } else {
        contentEpoch += 1
        PresentHandle(currentDisplay, sessionEpoch, contentEpoch)
      }
    }

    if (handle == null) {
      eventSink(
          MetaWearablesAndroidDisplayEvent.PhoneFallback(
              MetaWearablesAndroidDisplayFallback.NO_DISPLAY,
          ),
      )
      return
    }

    scope.launch(dispatcher) {
      val result = handle.display.sendContent(
          displayCard(
              snapshot = snapshot,
              sessionEpoch = handle.sessionEpoch,
              contentEpoch = handle.contentEpoch,
          ),
      )
      result.fold(
          onSuccess = {
            if (isCurrentContent(handle)) {
              eventSink(MetaWearablesAndroidDisplayEvent.ContentSent)
            }
          },
          onFailure = { _, _ ->
            if (isCurrentContent(handle)) {
              eventSink(
                  MetaWearablesAndroidDisplayEvent.Failure(
                      MetaWearablesAndroidDisplayFailure.SEND,
                  ),
              )
              eventSink(
                  MetaWearablesAndroidDisplayEvent.PhoneFallback(
                      MetaWearablesAndroidDisplayFallback.SEND_FAILED,
                  ),
              )
            }
          },
      )
    }
  }

  /** Cancel collectors, detach Display, then stop the parent session. */
  public fun stop() {
    val resources = synchronized(resourceLock) {
      sessionEpoch += 1
      contentEpoch += 1
      val current = StopResources(
          session = session,
          display = display,
          sessionStateJob = sessionStateJob,
          sessionErrorJob = sessionErrorJob,
          displayStateJob = displayStateJob,
      )
      session = null
      display = null
      sessionStateJob = null
      sessionErrorJob = null
      displayStateJob = null
      current
    }

    resources.displayStateJob?.cancel()
    resources.sessionStateJob?.cancel()
    resources.sessionErrorJob?.cancel()
    resources.session?.removeDisplay()
    resources.session?.stop()

    if (resources.display != null) {
      eventSink(MetaWearablesAndroidDisplayEvent.DisplayStopped)
    }
    if (resources.session != null) {
      eventSink(MetaWearablesAndroidDisplayEvent.PhoneFallback(
          MetaWearablesAndroidDisplayFallback.SESSION_UNAVAILABLE,
      ))
    }
  }

  private fun observeSession(
      session: DeviceSession,
      currentEpoch: Long,
  ) {
    val stateJob = scope.launch(dispatcher) {
      session.state.collect { state ->
        if (!isCurrentSession(currentEpoch)) return@collect
        when (state) {
          DeviceSessionState.STARTED -> {
            eventSink(MetaWearablesAndroidDisplayEvent.SessionStarted)
            attachDisplay(session, currentEpoch)
          }
          DeviceSessionState.STOPPED -> handleSessionStopped(currentEpoch)
          else -> Unit
        }
      }
    }
    val errorJob = scope.launch(dispatcher) {
      session.errors.collect { error ->
        if (isCurrentSession(currentEpoch)) {
          handleSessionError(error, currentEpoch)
        }
      }
    }

    synchronized(resourceLock) {
      if (isCurrentSessionLocked(currentEpoch)) {
        sessionStateJob?.cancel()
        sessionErrorJob?.cancel()
        sessionStateJob = stateJob
        sessionErrorJob = errorJob
      } else {
        stateJob.cancel()
        errorJob.cancel()
      }
    }
  }

  private fun attachDisplay(
      session: DeviceSession,
      currentEpoch: Long,
  ) {
    val shouldAttach = synchronized(resourceLock) {
      isCurrentSessionLocked(currentEpoch) && display == null
    }
    if (!shouldAttach) return

    session.addDisplay().fold(
        onSuccess = { nextDisplay ->
          val accepted = synchronized(resourceLock) {
            if (isCurrentSessionLocked(currentEpoch) && display == null) {
              display = nextDisplay
              true
            } else {
              false
            }
          }

          if (!accepted) {
            session.removeDisplay()
          } else {
            eventSink(MetaWearablesAndroidDisplayEvent.DisplayAttached)
            val stateJob = scope.launch(dispatcher) {
              nextDisplay.state.collect { state ->
                if (!isCurrentSession(currentEpoch)) return@collect
                when (state) {
                  DisplayState.STARTED -> eventSink(MetaWearablesAndroidDisplayEvent.DisplayStarted)
                  DisplayState.STOPPED -> eventSink(MetaWearablesAndroidDisplayEvent.DisplayStopped)
                  else -> Unit
                }
              }
            }

            synchronized(resourceLock) {
              if (isCurrentSessionLocked(currentEpoch)) {
                displayStateJob?.cancel()
                displayStateJob = stateJob
              } else {
                stateJob.cancel()
              }
            }
          }
        },
        onFailure = { _, _ ->
          if (isCurrentSession(currentEpoch)) {
            eventSink(
                MetaWearablesAndroidDisplayEvent.Failure(
                    MetaWearablesAndroidDisplayFailure.DISPLAY,
                ),
            )
            eventSink(
                MetaWearablesAndroidDisplayEvent.PhoneFallback(
                    MetaWearablesAndroidDisplayFallback.NO_DISPLAY,
                ),
            )
          }
        },
    )
  }

  private fun handleSessionError(
      error: DeviceSessionError,
      currentEpoch: Long,
  ) {
    if (!isCurrentSessionEpoch(currentEpoch)) return

    eventSink(
        MetaWearablesAndroidDisplayEvent.Failure(
            MetaWearablesAndroidDisplayFailure.SESSION,
        ),
    )
    eventSink(
        MetaWearablesAndroidDisplayEvent.PhoneFallback(
            if (error == DeviceSessionError.DAT_APP_ON_THE_GLASSES_UPDATE_REQUIRED) {
              MetaWearablesAndroidDisplayFallback.DAT_APP_UPDATE_REQUIRED
            } else {
              MetaWearablesAndroidDisplayFallback.SESSION_UNAVAILABLE
            },
        ),
    )
  }

  private fun handleSessionStopped(currentEpoch: Long) {
    val resources = synchronized(resourceLock) {
      if (!isCurrentSessionLocked(currentEpoch)) {
        null
      } else {
        val current = StopResources(
            session = session,
            display = display,
            sessionStateJob = sessionStateJob,
            sessionErrorJob = sessionErrorJob,
            displayStateJob = displayStateJob,
        )
        session = null
        display = null
        sessionStateJob = null
        sessionErrorJob = null
        displayStateJob = null
        contentEpoch += 1
        current
      }
    } ?: return

    resources.displayStateJob?.cancel()
    resources.sessionStateJob?.cancel()
    resources.sessionErrorJob?.cancel()

    if (resources.display != null) {
      eventSink(MetaWearablesAndroidDisplayEvent.DisplayStopped)
    }
    eventSink(
        MetaWearablesAndroidDisplayEvent.PhoneFallback(
            MetaWearablesAndroidDisplayFallback.SESSION_UNAVAILABLE,
        ),
    )
  }

  private fun displayCard(
      snapshot: MetaWearablesAndroidDisplaySnapshot,
      sessionEpoch: Long,
      contentEpoch: Long,
  ): ContentScope.() -> Unit = {
    flexBox(
        direction = Direction.COLUMN,
        gap = 12,
        padding = 24,
        background = FlexBoxBackground.CARD,
    ) {
      text(snapshot.title, style = TextStyle.HEADING)
      text(snapshot.detail, style = TextStyle.META, color = TextColor.SECONDARY)
      buttonGroup {
        button(
            "Do it",
            style = ButtonStyle.PRIMARY,
            iconName = IconName.CHECKMARK,
            onClick = {
              handleAction(
                  MetaWearablesAndroidDisplayAction.PRIMARY,
                  sessionEpoch,
                  contentEpoch,
              )
            },
        )
        button(
            "Later",
            style = ButtonStyle.SECONDARY,
            onClick = {
              handleAction(
                  MetaWearablesAndroidDisplayAction.SECONDARY,
                  sessionEpoch,
                  contentEpoch,
              )
            },
        )
      }
    }
  }

  private fun handleAction(
      action: MetaWearablesAndroidDisplayAction,
      sessionEpoch: Long,
      contentEpoch: Long,
  ) {
    if (!isCurrentContent(sessionEpoch, contentEpoch)) return
    eventSink(MetaWearablesAndroidDisplayEvent.Action(action))
  }

  private fun isCurrentSession(currentEpoch: Long): Boolean =
      synchronized(resourceLock) { isCurrentSessionLocked(currentEpoch) }

  private fun isCurrentSessionEpoch(currentEpoch: Long): Boolean =
      synchronized(resourceLock) { sessionEpoch == currentEpoch }

  private fun isCurrentSessionLocked(currentEpoch: Long): Boolean =
      sessionEpoch == currentEpoch && session != null

  private fun isCurrentContent(handle: PresentHandle): Boolean =
      isCurrentContent(handle.sessionEpoch, handle.contentEpoch)

  private fun isCurrentContent(
      currentSessionEpoch: Long,
      currentContentEpoch: Long,
  ): Boolean = synchronized(resourceLock) {
    sessionEpoch == currentSessionEpoch &&
        contentEpoch == currentContentEpoch &&
        session != null &&
        display != null
  }

  private data class PresentHandle(
      val display: Display,
      val sessionEpoch: Long,
      val contentEpoch: Long,
  )

  private data class StopResources(
      val session: DeviceSession?,
      val display: Display?,
      val sessionStateJob: Job?,
      val sessionErrorJob: Job?,
      val displayStateJob: Job?,
  )
}
