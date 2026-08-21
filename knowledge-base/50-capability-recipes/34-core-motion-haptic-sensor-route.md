# Core Motion and haptic sensor route

Use this route when a feature reads motion, activity, steps, relative altitude, headphone orientation, or physical-device state and communicates with visual, audio, or haptic feedback. Keep the sensor session, derived state, UI, optional AI proposal, and haptic side effect separate.

~~~text
user starts a bounded task
  -> availability/privacy gate
  -> owned sensor session
  -> timestamped normalized samples
  -> deterministic derived state
  -> native UI + optional sensory feedback
  -> optional AI explanation/proposal
  -> stop, summarize, and release
~~~

## Choose the narrowest API

| Outcome | Choose | Primary proof |
| --- | --- | --- |
| Tap/press/selection feedback | SwiftUI sensoryFeedback | Semantic trigger, supported device, visual/audio fallback. |
| A custom transient or continuous haptic | Core Haptics CHHapticEngine and CHHapticPattern | Physical haptic capability, engine lifecycle, pattern meaning, interruption/reset. |
| Device rotation/attitude | CMMotionManager device-motion updates | Reference frame, calibration, orientation, sampling, physical device. |
| Raw acceleration or rotation | CMMotionManager accelerometer/gyro updates | Axis convention, filtering, backpressure, power, sensor placement. |
| Walking/activity classification | CMMotionActivityManager | Authorization, supported device, classification uncertainty, stop behavior. |
| Steps/distance | CMPedometer | Historical/live query, availability, time range, device movement, privacy. |
| Relative elevation change | CMAltimeter | Availability, environmental drift, relative-only wording, physical test. |
| Headphone pose/activity | CMHeadphoneMotionManager | Supported headphone route, pairing, permission, removal/interruption. |

Do not select raw Core Motion because it sounds more powerful. A high-frequency stream adds energy, filtering, testing, and privacy responsibilities.

## Configuration gate

Before the first sensor request:

1. Confirm the framework and symbol availability for the deployment target.
2. Check the service’s hardware/runtime availability.
3. Add and inspect the exact Info.plist usage description for the selected data.
4. Explain the user outcome before asking for access.
5. Decide whether the feature works with no permission or unavailable hardware.
6. Decide where the session is owned and how it stops.

For Core Haptics, check device capabilities and create a fallback. For SwiftUI sensoryFeedback, prefer a semantic trigger and let the system choose the supported output. For custom haptics, decide whether the pattern should be transient or continuous and how to stop it.

## Motion session state

Use a state machine instead of one Boolean:

~~~text
idle
  -> checking
  -> unavailable
  -> requestingPermission
  -> ready
  -> starting
  -> sampling
  -> paused/interrupted
  -> completed
  -> failed
  -> stopping
~~~

The state owns:

- service kind and hardware availability;
- timestamp and reference frame;
- update interval;
- active sample window;
- filter/calibration version;
- dropped/coalesced sample count;
- energy/session budget;
- cancellation and stop reason;
- derived state confidence/uncertainty;
- last haptic event time.

The view owns a projection of this state. It does not own the sensor manager, raw stream, or haptic engine.

## Capture and derive

Normalize every incoming sample:

~~~text
sample
  -> timestamp validation
  -> reference-frame normalization
  -> finite/range validation
  -> filter or feature window
  -> derived result with confidence and source window
  -> bounded UI update
~~~

Record enough metadata to debug:

- device model and OS;
- service and reference frame;
- requested and actual update interval;
- sample window and dropped samples;
- filter/calibration version;
- physical orientation/placement;
- interruption and stop reason.

Avoid retaining raw streams when a derived result is sufficient. If a history is a product feature, define retention, deletion, export, and user explanation.

## Haptic route

Use this decision:

1. Is the event a standard selection, start, stop, alignment, increase, decrease, or level change? Use SwiftUI sensoryFeedback where appropriate.
2. Is the event custom, synchronized with audio, continuous, or dynamically parameterized? Use Core Haptics.
3. Is the feedback frequent? Throttle or remove it.
4. Is the feedback important? Add text, visual, and accessible state.
5. Can the haptic engine stop/reset? Test restart and fallback.

Treat the haptic as a side effect after a state transition, not as a direct response to every sensor sample:

~~~text
raw samples -> stable threshold transition -> haptic request
                                  -> visible state
                                  -> spoken/accessible result
~~~

## AI route

Use AI only after deterministic capture and feature extraction:

~~~text
bounded local window
  -> tested feature representation
  -> on-device model/session
  -> typed interpretation or feedback proposal
  -> uncertainty and source window
  -> user review
~~~

Useful proposal types:

- MotionSummary(window, dominantPattern, caveats)
- HapticPreferenceSuggestion(intensity, sharpness, reason)
- InteractionModeSuggestion(mode, evidence, expiresAt)

Reject or re-review a proposal when the source window is stale, the user changes the task, the device changes orientation, or model availability changes. Never infer medical status, safety, identity, emotion, or consent from a generic motion classification.

## Fallback route

| Gate | Fallback |
| --- | --- |
| No sensor hardware | Manual control, static illustration, or a different input. |
| Permission denied | Explain, preserve the core task, and do not repeatedly prompt. |
| Stream interrupted | Pause and resume with a visible timestamp. |
| Noisy/ambiguous | Ask the person to hold steady or offer manual confirmation. |
| Haptics unavailable | Use visible/audio confirmation and accessible state. |
| Reduce Motion | Discrete transitions and no decorative sensor parallax. |
| AI unavailable | Deterministic thresholds and manual interpretation. |
| Energy budget exceeded | Stop, summarize, and let the person restart intentionally. |

## Build slices

1. Add usage descriptions and availability checks.
2. Build one deterministic fixture-driven state reducer.
3. Start one service with explicit stop and interruption handling.
4. Render a visible state with timestamps and a manual fallback.
5. Add semantic SwiftUI feedback.
6. Add custom Core Haptics only if the semantic route is insufficient.
7. Add physical-device calibration, noise, energy, and thermal evidence.
8. Add optional on-device AI only after the deterministic feature is reviewable.
9. Add Liquid Glass, motion, accessibility, and localization polish.
10. Record signed release and device evidence.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMMotionActivityManager](https://developer.apple.com/documentation/coremotion/cmmotionactivitymanager)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [CMAltimeter](https://developer.apple.com/documentation/coremotion/cmaltimeter)
- [CMHeadphoneMotionManager](https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticPattern](https://developer.apple.com/documentation/corehaptics/chhapticpattern)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [Motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
