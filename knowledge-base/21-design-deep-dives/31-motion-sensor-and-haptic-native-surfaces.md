# Motion, sensor, and haptic native surfaces

Physical input can make an app feel unusually native because the interface responds to the device a person is already holding. It can also make an app tiring, inaccessible, or misleading when it turns noisy samples into constant decoration. The design contract is simple:

~~~text
physical signal -> meaningful state change -> visible/semantic feedback
               -> optional haptic/audio reinforcement -> accessible fallback
~~~

## Start with a human task

Good sensor-driven outcomes include:

- align or level a physical object;
- guide a short movement sequence;
- show a live orientation or tilt state;
- detect a bounded interaction such as a shake or threshold crossing;
- provide a tactile confirmation for a control;
- help a person understand a local, user-started movement session.

Weak outcomes include “make the dashboard wobble,” “make glass float with every gyro sample,” or “infer the person’s intent from one accelerometer spike.” The first set gives the signal a job; the second makes physical input decorative or overconfident.

Before choosing a sensor, write:

1. What decision does the signal improve?
2. How fresh must it be?
3. What happens when the signal is noisy, absent, or denied?
4. What visual, audio, and tactile feedback communicate the same state?
5. When does the feature stop collecting?

## State hierarchy for a sensor surface

A sensor surface should expose the state that matters to the person:

| State | Visual language | Haptic/audio behavior |
| --- | --- | --- |
| Ready | Clear instruction and stable baseline | Optional start feedback. |
| Sampling | Calm progress or live value with units/context | Sparse feedback at meaningful thresholds, not every sample. |
| Calibrating | Explain what the person should do | Avoid repeated pulses that obscure calibration. |
| Stable/within target | Strong semantic success state | One concise confirmation when the target is reached. |
| Noisy/uncertain | “Move closer,” “hold steady,” or an uncertainty cue | Do not signal false success. |
| Interrupted | Preserve last known result and show resume | Optional interruption feedback once. |
| Unavailable | Explain device/permission limitation | Use manual or visual-only fallback. |
| Complete | Summarize the result and next action | A short completion pattern if appropriate. |

Do not let a continuous animation imply that the sensor is receiving fresh data when the stream stopped. The state label, timestamp, and control availability should remain truthful when the device is in a pocket, covered, disconnected, or backgrounded.

## Motion and Liquid Glass

Liquid Glass already responds to interaction and adapts to platform context. Additional sensor-driven parallax or tilt should be rare:

- Keep the content’s reading position stable.
- Use a small, bounded transform only when it reveals a relationship such as alignment or orientation.
- Never move a destructive control away from the person’s expected touch target.
- Do not tie the visual identity of a glass action to a raw, high-frequency sample.
- Let Reduce Motion replace physical movement with a stable progress indicator or discrete state.
- Use contrast, text, and semantic labels so the feature remains understandable without animation.

A good “native” motion surface feels like a tool responding to a physical task. It does not feel like the entire app is floating in a sensor-driven aquarium.

## Haptic vocabulary

Haptics should have a consistent causal vocabulary:

| Moment | Preferred feedback |
| --- | --- |
| A discrete option changes | SwiftUI selection/level-change feedback or a light, consistent custom response. |
| A threshold is crossed | One brief success/transition response, with visible state. |
| A drag aligns | Alignment feedback only while the relationship is clear. |
| A long-running process starts/stops | Start/stop feedback plus visible status. |
| A validation failure | Visible error and optional distinct response; never rely on a buzz alone. |
| A safety-sensitive action is pending | Clear confirmation UI; haptics may support but never replace the confirmation. |
| A repeated live signal changes | Throttle feedback; avoid a pulse on every sample. |

Apple’s HIG recommends using system-provided haptic meanings consistently, pairing haptics with visual and audio feedback, and avoiding overuse. Use SwiftUI sensoryFeedback for ordinary semantic interactions. Use Core Haptics for a real custom pattern, dynamic parameter curve, or synchronized audio/haptic experience.

## Sensor-driven interaction patterns

### Align and settle

For a level, alignment, or placement task:

1. Explain the target orientation.
2. Show a stable reference line or shape.
3. Filter samples enough to prevent jitter.
4. Distinguish “near,” “aligned,” and “lost signal.”
5. Provide one threshold haptic and visual confirmation.
6. Let the person pause and resume.

Do not call a noisy “near” state exact. Preserve the unit/reference frame and let the person understand the tolerance.

### Gesture or threshold

For shake, tap, tilt, or movement detection:

- define the signal window and threshold;
- debounce consecutive events;
- avoid accidental activation from ordinary handling;
- offer a visible alternative action;
- log sample metadata in testing rather than personal raw traces by default.

### Live physical instrument

For a live motion graph or orientation tool:

- make the axes and units explicit;
- expose start/stop and reset;
- show the sample time or “paused” state;
- cap history and memory;
- use Canvas or Charts only if they add comprehension;
- ensure VoiceOver gets a summary and exact values when the visual graph is essential.

## Haptics and accessibility

Haptic output is not universally available, equally perceived, or safe to overuse. Every meaningful state needs a visible and/or audible equivalent:

- success text or icon;
- current value and units;
- spoken label/value for VoiceOver;
- reduced-motion state;
- no-haptics or unsupported-device fallback;
- a way to retry, cancel, or continue manually.

Do not announce every sensor sample through accessibility. Announce material state transitions and make the current value available on demand. When a person is editing or reading, do not steal focus because a remote or background sensor changed.

Test large text with live values, localized units, long instructions, VoiceOver rotor behavior, Voice Control names, Switch Control, Full Keyboard Access, and reduced transparency. A beautiful haptic loop is not an accessible feature if a person cannot know whether the task completed.

## Energy and attention

Continuous sensors and haptic engines can consume energy and attention. Design a session boundary:

~~~text
user starts -> warm up -> active window -> pause/interrupt
                                      -> complete/stop -> release resources
~~~

Avoid starting motion in an initializer or when a dashboard merely appears. Explain the active session and provide stop. Lower sampling when the user is reading static content. Stop haptics and sensors on completion, navigation away, cancellation, permission change, and route loss.

Use a calm default. Continuous motion, audio, and haptics should be opt-in when they could distract or fatigue. Record a tested energy budget for the specific device and session duration rather than using “real time” as a quality claim.

## On-device AI and physical signals

AI can help make a sensor surface understandable:

- summarize a short user-started motion session;
- classify one of a small, tested set of movement patterns;
- suggest a personalized haptic intensity preference;
- explain why a sample window was too noisy;
- draft a visual or haptic feedback mapping for the user to approve.

The review UI should show the window, source, model/version, and uncertainty. Keep personal raw sensor data local when possible, and do not infer medical, emotional, identity, safety, or intent claims without a domain-specific validated workflow. If a model proposes haptic output, the person should be able to preview, reject, limit, or disable it.

## Native polish checklist

- Uses a standard SwiftUI control or semantic interaction where it fits.
- Gives motion a task-specific role.
- Uses one consistent haptic vocabulary.
- Keeps visible state truthful during stale, paused, and unsupported states.
- Adapts to Reduce Motion, reduced transparency, Dynamic Type, VoiceOver, and alternate input.
- Stops hardware streams and engines when no longer needed.
- Does not use sensor data as hidden analytics or an unexplained AI prompt.
- Preserves a manual route.
- Verifies the physical device before claiming the feel is correct.

## Sources

- [Motion HIG](https://developer.apple.com/design/human-interface-guidelines/motion)
- [Playing haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [Core Motion](https://developer.apple.com/documentation/coremotion/)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
- [CMPedometer](https://developer.apple.com/documentation/coremotion/cmpedometer)
- [CMAltimeter](https://developer.apple.com/documentation/coremotion/cmaltimeter)
- [CMHeadphoneMotionManager](https://developer.apple.com/documentation/coremotion/cmheadphonemotionmanager)
- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticPattern](https://developer.apple.com/documentation/corehaptics/chhapticpattern)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [SensoryFeedback](https://developer.apple.com/documentation/swiftui/sensoryfeedback)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
