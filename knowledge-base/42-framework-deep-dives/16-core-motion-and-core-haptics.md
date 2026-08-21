# Core Motion and Core Haptics deep dive

Core Motion and Core Haptics let an app respond to the physical device and answer with physical feedback. They are complementary but different boundaries:

- Core Motion reports motion- and environment-related data from available onboard hardware.
- Core Haptics composes haptic and audio events and asks the haptic server to play them on supported hardware.
- SwiftUI sensoryFeedback provides semantic system feedback for view state changes without requiring a custom haptic engine.

None of these APIs turns a sensor sample into ground truth, or a haptic request into a guaranteed sensation. Availability, privacy strings, device capabilities, interruptions, sampling cost, user settings, and physical context remain part of the product route.

## Capability map

| User outcome | API route | Boundary |
| --- | --- | --- |
| Read acceleration, rotation, magnetic field, or processed device motion | CMMotionManager, CMDeviceMotion, CMAttitude, accelerometer/gyro/magnetometer/device-motion updates | Availability, coordinate frame, sampling interval, calibration, queue ownership, and physical-device noise. |
| Infer walking or stationary activity | CMMotionActivityManager and CMMotionActivity | A system activity classification is not identity, intent, location, health diagnosis, or proof of safe movement. |
| Read steps or distance | CMPedometer and CMPedometerData | Availability, authorization, time range, device movement, historical-query boundaries, and approximate interpretation. |
| Read relative altitude changes | CMAltimeter and CMAltitudeData | Hardware/permission availability, pressure/environment changes, drift, and no assumption of absolute floor or location. |
| Respond to spatial headphone motion | CMHeadphoneMotionManager and headphone motion data | Supported headphones, pairing/route, permission, session lifecycle, and physical orientation. |
| Add a short semantic interaction response | SwiftUI sensoryFeedback | System-selected feedback and device support; do not use it as the only communication channel. |
| Compose custom tactile/audio feedback | CHHapticEngine, CHHapticPattern, CHHapticEvent, players, parameters, curves, AHAP | Haptic hardware capability, audio route, interruption/reset, resource cost, and pattern meaning. |

## Availability and privacy

Apple’s Core Motion documentation says not all services are available on every device and recommends checking service availability before starting them. iOS apps need the usage description keys for the motion data they access; for motion and fitness data this includes NSMotionUsageDescription. Missing required keys can cause a runtime failure when the service is accessed.

Treat availability as a state, not a compile-time footnote:

~~~text
sdk symbol available
  -> service available on this device?
  -> required usage description present?
  -> user/system authorization permits access?
  -> session can start?
  -> updates arrive with acceptable freshness?
~~~

The route needs a device family and deployment target decision. A service available on an iPhone does not automatically behave the same on iPad, Apple Watch, headphones, visionOS, or a Mac Catalyst destination. Check the selected SDK documentation and target configuration rather than copying a global device assumption.

## Raw and processed motion

CMMotionManager can start accelerometer, gyroscope, magnetometer, and processed device-motion updates. Device motion combines sensor signals into values such as user acceleration, attitude, rotation rate, magnetic orientation, and gravity-relative orientation. Choose the smallest signal that satisfies the product:

- Use accelerometer data for a bounded change detector when raw three-axis acceleration is sufficient.
- Use gyroscope data for rotation rate.
- Use magnetometer data only when a calibrated magnetic reference is genuinely needed.
- Use device motion when the product needs a gravity- or attitude-aware interpretation and can explain coordinate frames.

Make these choices explicit:

- reference frame and coordinate-system convention;
- update interval and maximum tolerated latency;
- handler/operation-queue or concurrency ownership;
- smoothing, filtering, debouncing, and calibration policy;
- stop behavior when leaving the feature;
- behavior during interruption, permission change, route change, or app lifecycle transition.

The latest sample is not a universal fact. It has a timestamp, accuracy/context, sensor placement, device orientation, and noise. Preserve that metadata where downstream decisions depend on it.

## Activity, pedometer, altitude, and headphone routes

CMMotionActivityManager exposes system motion-activity updates. CMPedometer exposes live and historical walking data. CMAltimeter reports relative altitude changes. CMHeadphoneMotionManager manages supported headphone motion services. Each has its own availability and lifecycle; do not wrap them all in one “sensor available” Boolean.

Model separate states:

~~~text
service
  unavailable
  available but unauthorized
  ready
  updating
  interrupted
  stopped
  failed
~~~

For historical queries, show the time range and source. For live updates, stop the service when the feature ends. For headphone motion, establish the audio/headphone route and account for a person removing or changing the headphones. For altitude, present relative change rather than implying an absolute elevation when the API does not provide that product truth.

Avoid using motion data to make sensitive claims about a person. Motion can suggest that the device moved; it does not prove who moved it, why it moved, whether a person is safe, or whether a medical event occurred.

## Sampling, backpressure, and energy

Sensor streams can be high frequency and continuous. Use one owned capture pipeline:

~~~text
hardware update
  -> bounded queue/actor
  -> timestamp and normalize
  -> drop/coalesce stale samples when safe
  -> deterministic feature extraction
  -> UI projection / haptic decision / optional AI proposal
  -> stop and release when feature ends
~~~

Do not start a new unbounded task per sample. Choose an update interval from the user outcome and test energy, CPU, memory, and thermal behavior on representative hardware. A preview, simulator, or short run on a new device does not prove continuous use is acceptable.

For UI, project the latest bounded state to the main actor and keep raw streams out of the view hierarchy. If the product needs a history, define a retention window, sampling reduction, deletion action, and privacy rationale.

## Core Haptics

Core Haptics lets the app create haptic and audio patterns from transient and continuous CHHapticEvent values, parameters, curves, or AHAP files. A CHHapticEngine connects the app to the haptic server; a CHHapticPattern defines the waveform; a standard or advanced player plays it.

The engine lifecycle is not one-and-done:

~~~text
capability check -> create engine -> start
                 -> create pattern/player -> play
                 -> interruption/reset/route change
                 -> stop or restart when appropriate
~~~

Handle engine start failure, hardware without the required capability, system interruption, engine reset, application backgrounding, and user settings. Use transient patterns for precise moments and continuous patterns only when the sustained sensation has a clear purpose. Match intensity and sharpness to the meaning and avoid a pattern that becomes annoying when repeated.

SwiftUI sensoryFeedback is often the correct route for a native selection, start, stop, alignment, increase, decrease, or level-change response. It lets the system provide feedback based on a trigger. Use Core Haptics when the product genuinely needs a custom pattern, synchronized audio/haptic timeline, or dynamic parameter control.

Haptics complement visual and audio feedback. They should not be the only way to communicate success, failure, a safety warning, or an AI result.

## Motion-driven UI and Liquid Glass

Motion can make a native surface feel tactile, but it must not become the only state channel. With Liquid Glass:

- Use a sensor or touch signal to support a clear interaction, not to add perpetual parallax.
- Keep glass controls anchored to content and use small, reversible motion.
- Let system components and SwiftUI controls provide familiar feedback where possible.
- Use haptics when they clarify a causal event: selection, threshold crossing, completion, or an intentional control response.
- Pair motion/haptics with text, shape, color, and accessible state.
- Respect Reduce Motion, reduced transparency, and other accessibility settings.
- Let people cancel or interrupt long motion or continuous haptic output.

The HIG says custom motion should be purposeful, brief, precise, and optional, and that visual feedback should be supplemented with haptics or audio rather than relying on motion alone.

## On-device AI with sensor context

On-device AI can operate on a bounded, user-started sensor summary:

- classify a fixed set of tested interaction patterns;
- explain a motion trace in plain language;
- suggest a haptic pattern for a user-approved interaction;
- summarize a short, local movement session;
- propose an adaptive UI mode from explicit preferences and measured interaction signals.

Keep raw sensor streams out of prompts unless the product has a strong reason and a retention policy. Convert to an explicit feature vector or time-bounded summary, record the model/version and source window, and validate the output deterministically. Never present a motion classification as a medical, safety, identity, or guaranteed intent claim. Never let a model silently start sensors, play a startling haptic, or trigger a physical-world side effect.

## Failure and fallback contract

| Failure | Fallback |
| --- | --- |
| Sensor unavailable | Use touch, manual entry, static content, or a non-sensor route. |
| Permission denied | Explain the feature, preserve non-motion workflows, and avoid repeated prompts. |
| Stream interrupted | Mark the state interrupted/stale and offer restart. |
| High latency/noisy samples | Lower update rate, filter, show uncertainty, or pause the derived feature. |
| Haptic hardware unavailable | Use semantic visual/audio feedback and preserve the action. |
| Haptic engine reset | Recreate/restart only when the user action still warrants it. |
| Reduce Motion enabled | Remove decorative motion and use state changes that remain legible. |
| AI unavailable/uncertain | Use deterministic thresholds or a manual path. |

## Proof checklist

Before claiming a motion/haptic feature is ready, verify:

- selected service availability on every supported device family;
- Info.plist privacy strings and target membership;
- allow/deny/restricted and Settings-change behavior;
- start/stop, interruption, background/foreground, route change, and teardown;
- timestamps, frame/reference conventions, filtering, sample dropping, and history retention;
- physical device orientation, movement, calibration, distance, noise, and placement;
- haptic capability, engine start, pattern playback, interruption/reset, and output settings;
- SwiftUI sensoryFeedback behavior on supported controls and custom Core Haptics patterns where needed;
- VoiceOver, reduced motion, reduced transparency, audio alternative, and no-haptics comprehension;
- AI model availability, bounded context, deterministic output validation, uncertainty, and privacy;
- measured CPU, memory, battery, thermal, and latency behavior on representative hardware;
- signed archive, usage descriptions, entitlements, and release configuration.

## Sources

- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMDeviceMotion](https://developer.apple.com/documentation/coremotion/cmdevicemotion)
- [CMMotionActivityManager](https://developer.apple.com/documentation/coremotion/cmmotionactivitymanager)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [CMAltimeter](https://developer.apple.com/documentation/coremotion/cmaltimeter)
- [CMHeadphoneMotionManager](https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticPattern](https://developer.apple.com/documentation/corehaptics/chhapticpattern)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [Playing a single-tap haptic pattern](https://developer.apple.com/documentation/corehaptics/playing-a-single-tap-haptic-pattern)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [Motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
