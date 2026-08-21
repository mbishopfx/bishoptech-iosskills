# Core Motion and Core Haptics proof matrix

This matrix separates a motion/haptic feature’s source route, deterministic logic, physical-device behavior, accessibility, energy, and release proof. A running callback or a haptic call is not enough to claim that the experience is accurate, comfortable, available, or accessible.

## Evidence levels

| Level | Evidence | What it can prove |
| --- | --- | --- |
| L0 | Official source and target review | Selected API, availability, privacy, reference-frame, haptic, and HIG rules are known. |
| L1 | Deterministic fixture/state tests | Sample normalization, filters, threshold logic, stale/interrupted state, haptic throttling, and AI proposal validation. |
| L2 | Preview/simulator/manual route | UI hierarchy, accessibility identifiers, fallback copy, state transitions, and non-hardware behavior. |
| L3 | Signed physical-device run | Sensor availability, permission, orientation/placement, timestamps, noise, haptic output, interruptions, and real ergonomics. |
| L4 | Measured session | CPU, memory, energy, thermal, dropped-sample, latency, and long-session behavior on named hardware. |
| L5 | Release artifact | Target membership, Info.plist usage strings, signing, supported-device declarations, privacy review, and release build configuration. |

## Availability and privacy

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Core Motion service is supported | SDK compile plus runtime availability branch on each device family | A framework import does not prove hardware or service availability. |
| Usage prompt is correct | Archived Info.plist inspection and allow/deny/revoke run | A source key does not prove the signed target contains useful copy. |
| Motion data can be accessed | Signed physical-device authorization and active update | Permission does not make samples accurate, current, or meaningful. |
| Haptics can play | Device capability check and physical playback | A pattern object or simulator cannot prove tactile output. |
| Cross-device support is accurate | Named iPhone/iPad/watch/headphone/visionOS runs where supported | An iPhone result cannot be generalized to every Apple device. |

## Capture lifecycle

| Route | Fixtures | Physical proof |
| --- | --- | --- |
| Start | idle -> checking -> ready -> starting fixture | Start on supported device after permission and confirm first timestamp. |
| Stop | explicit stop, cancellation, navigation away, completion | Verify sensors/engine stop and resources release. |
| Interruption | background, phone call/audio route, app suspension, engine reset | Resume or fail visibly without claiming continuous data. |
| Permission change | denial, revocation in Settings, restricted state | Preserve manual fallback and avoid repeated prompts. |
| Hardware loss | headphones removed, unsupported sensor, route change | Transition to unavailable/interrupted and show next action. |
| Long session | bounded stream with sample count and history cap | Measure energy, thermal, memory, latency, and user attention. |

## Motion correctness

| Claim | Required evidence | Do not infer |
| --- | --- | --- |
| Device motion is stable | Reference-frame fixture, calibration/orientation cases, filtering test | A smooth graph is not physical accuracy. |
| Threshold detects an interaction | Positive/negative/noisy windows and debounce fixtures | One shake/tap sample does not prove intent. |
| Activity classification is useful | Supported activity classes, unknown/ambiguous cases, time-window test | A motion class is not identity, location, medical status, or safety. |
| Steps/distance route works | Historical/live query ranges, no-data/error, device movement, date/time cases | A single pedometer value is not a complete fitness record. |
| Altitude route works | Relative-change fixtures, environmental variation, reset/drift cases | Relative pressure data is not an absolute floor/location claim. |
| Headphone motion works | Supported headphones, pairing/route, removal, orientation, permission | One connected headphone route proves every accessory. |

## Haptics correctness

| Claim | Required evidence | Do not infer |
| --- | --- | --- |
| Semantic feedback is appropriate | SwiftUI trigger/condition fixture and supported-device behavior | A feedback call is not guaranteed output on every device. |
| Custom pattern is meaningful | Transient/continuous parameter fixtures, design review, frequency/throttle test | More intensity or duration is not better feedback. |
| Engine survives lifecycle | Start failure, interruption, reset, stop, restart, background/foreground | A single playback proves no future reset behavior. |
| Audio/haptic route is coherent | Synchronized playback, audio route, mute/settings, accessibility fallback | Haptics alone communicate a critical result. |
| Repetition is comfortable | Repeated-use session with cadence and opt-out | One pleasant tap proves a repeated loop is comfortable. |

## Accessibility and design

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| Motion can be understood without motion | Reduce Motion, static state, visible progress/result | A moving visual is not an accessible label. |
| Haptic result is accessible | VoiceOver/value/result, visible text, optional audio, no-haptics route | Tactile perception varies; never make it the only signal. |
| Dynamic Type works | Largest text sizes, long instructions, live values, localized units | Default-size screenshot is not task proof. |
| Alternate input works | Voice Control, Switch Control, keyboard/pointer where supported | A tap-only motion flow is not complete. |
| Liquid Glass is native | State variants, reduced transparency, contrast, touch/trackpad behavior | Gloss, parallax, or a haptic pulse does not establish native polish. |

## AI and privacy

| Claim | Required evidence | Boundary |
| --- | --- | --- |
| AI can summarize a session | Fixed local window, model/version, typed output, uncertainty | Generated prose does not replace the raw source or domain validation. |
| AI suggests feedback | Bounded input, preference review, reject/disable path | Model output cannot silently start sensors or haptics. |
| Data stays bounded | Prompt/context audit, retention/deletion test, logs scrubbed | “On device” does not eliminate privacy review. |
| Feature is safe | Explicit refusal for medical/safety/identity claims and deterministic fallback | A confident classifier is not a safety authority. |

## Performance and release

| Claim | Required evidence |
| --- | --- |
| Responsive | Named-device latency distribution, dropped samples, UI update cadence. |
| Efficient | Long-session CPU, memory, energy, and thermal measurements. |
| Release-ready | Archive Info.plist/capability inspection, supported-device matrix, privacy review, and release build test. |

## Evidence packet

Record:

~~~text
feature:
target/bundle/build:
sdk/deployment target:
device/OS:
service and capability:
usage description:
reference frame:
update interval:
filter/calibration:
sample window/dropped samples:
interruption/stop reason:
haptic capability/pattern:
accessibility settings:
ai model/context/version:
cpu/memory/energy/thermal:
known failures:
claim supported:
~~~

## Claim language

Use:

- “On the named device, the signed target received device-motion updates after authorization and stopped them when the session ended.”
- “The feature uses a visible state and manual fallback when motion is unavailable or Reduce Motion is enabled.”
- “The custom haptic pattern was exercised on the named hardware; output is supplemented by visual and accessible feedback.”
- “The model summarized a bounded local sample window and produced no direct haptic or sensor side effect.”

Avoid:

- “Works on all iPhones” from one physical run.
- “Accurate activity detection” without tested classes, windows, and uncertainty.
- “The haptic always fires” from a simulator or pattern object.
- “AI knows what the user intended” from a motion classifier.

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
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
