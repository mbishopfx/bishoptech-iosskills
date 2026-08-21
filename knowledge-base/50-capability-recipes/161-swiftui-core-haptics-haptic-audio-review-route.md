# SwiftUI Core Haptics and haptic-audio route worksheet

Use this worksheet before adding custom tactile feedback to a SwiftUI app, game, capture flow, or Liquid Glass control surface.

Related references:

- [Core Haptics framework review](../42-framework-deep-dives/130-swiftui-core-haptics-haptic-audio-review.md)
- [Core Haptics design review](../21-design-deep-dives/158-swiftui-core-haptics-haptic-audio-review-design.md)
- [Core Haptics proof matrix](../60-verification/155-swiftui-core-haptics-haptic-audio-proof-matrix.md)
- [Core Haptics code recipes](../70-code-recipes/173-swiftui-core-haptics-haptic-audio-review-recipes.md)

## Route record

| Field | Decision |
| --- | --- |
| Product outcome | `TBD` |
| Target / deployment | `TBD / iOS 26` |
| Feedback lane | transient / continuous / audio-haptic / AHAP / controller: `TBD` |
| Semantic meaning | `TBD` |
| Native control already provides feedback | yes / no / `TBD` |
| Hardware capability | `supportsHaptics` / `supportsAudio` / `TBD` |
| App preference | enabled / reduced / disabled: `TBD` |
| Engine owner | feature/service/scene: `TBD` |
| Audio-session owner | app / media / communication / none: `TBD` |
| Pattern source | inline / event array / AHAP / asset: `TBD` |
| Pattern revision | `TBD` |
| Player type | standard / advanced: `TBD` |
| Timing | relative time / duration / loop / rate: `TBD` |
| Parameters | intensity / sharpness / audio / dynamic / curve: `TBD` |
| Stop policy | gesture end / cancellation / timeout / lifecycle: `TBD` |
| Reset policy | recreate engine/players / fallback: `TBD` |
| Accessibility equivalent | visual / text / VoiceOver / alternate input: `TBD` |
| Reduce Motion behavior | `TBD` |
| Liquid Glass surface | app-owned cluster / none: `TBD` |
| AI proposal | fields / range validation / review: `TBD` |
| Physical device matrix | iPhone models / routes / OS builds: `TBD` |
| Release artifact | archive / TestFlight / production: `TBD` |

## Step 1: meaning and fallback

- [ ] Write the semantic event in plain language.
- [ ] Document the visual state that commits with the haptic.
- [ ] Document the VoiceOver/text equivalent.
- [ ] Decide whether a native SwiftUI/UIKit control already provides the appropriate feedback.
- [ ] Define the fallback for no haptic hardware, muted system state, engine error, and accessibility settings.
- [ ] Define whether audio is part of the feedback or haptics-only.

Example:

```text
meaning: save succeeded
visual: saved badge and updated timestamp
haptic: one hapticTransient event at commit
accessibility: announce "Saved"
fallback: visual badge + announcement
```

## Step 2: capability and device matrix

Capture `CHHapticEngine.capabilitiesForHardware()` on the target devices. Record:

- `supportsHaptics`;
- `supportsAudio`;
- supported parameter attributes where the pattern depends on them;
- device model and OS build;
- audio route and mute state; and
- whether the feature is running on iPhone, iPad, iPod touch, Apple Vision Pro, or a game controller route.

Do not infer that an iPad or simulator can prove iPhone haptic behavior. The fallback must be a first-class route.

## Step 3: engine ownership

- [ ] Create one deliberate engine owner for the feature.
- [ ] Store a strong engine reference.
- [ ] Set `resetHandler` before starting.
- [ ] Set `stoppedHandler` before starting.
- [ ] Define `isAutoShutdownEnabled` policy.
- [ ] Define how the owner starts and stops with the scene/feature lifecycle.
- [ ] Define how a media/audio-session interruption affects haptics.
- [ ] Rebuild players after a reset.
- [ ] Ignore callbacks from stale player generations.

Engine record:

```text
engineRevision: UUID
started: Bool
lastStoppedReason: String?
lastResetAt: Date?
currentPlayerGeneration: Int
fallbackActive: Bool
```

This record is diagnostics, not physical proof.

## Step 4: pattern and player

- [ ] Choose transient or continuous event type.
- [ ] Set relative time and duration deliberately.
- [ ] Choose intensity and sharpness based on semantic meaning.
- [ ] Add static event parameters only when needed.
- [ ] Use dynamic parameters for bounded runtime changes.
- [ ] Use parameter curves for scheduled ramps.
- [ ] Use an advanced player only when loop/pause/seek/sync is needed.
- [ ] Define cancel/stop behavior for every continuous pattern.
- [ ] Define maximum duration and repeat count.
- [ ] Validate normalized values and hardware limits.

Do not author a pattern as a list of arbitrary sensations. Keep a pattern catalog with names, semantic meaning, fallback, and physical-device sign-off.

## Step 5: AHAP and audio route

For an AHAP file:

- [ ] Add the resource to the intended target bundle.
- [ ] Record AHAP `Version` and supported OS/hardware expectations.
- [ ] Validate `Pattern`, events, parameters, dynamic parameters, and curves.
- [ ] Test missing/defaulted keys and out-of-range clamping explicitly.
- [ ] Test unsupported keys and decide whether ignoring them is acceptable.

For audio-haptic playback:

- [ ] Document resource registration and lifetime.
- [ ] Document audio format and route.
- [ ] Document volume/mute policy.
- [ ] Use an advanced player for synchronization where required.
- [ ] Test headphones, speaker, Bluetooth, communication audio, interruption, and background transitions.
- [ ] Provide haptics-only and audio-only fallback where appropriate.

## Step 6: SwiftUI gesture and state bridge

Use a small state machine:

```text
idle
  -> preparing
  -> playingTransient
  -> playingContinuous
  -> stopping
  -> unavailable/fallback
  -> resetRequired
```

State rules:

- a SwiftUI redraw does not create a new engine;
- an interaction generation owns its player;
- gesture cancellation stops or cancels continuous playback;
- view disappearance stops feature-owned playback;
- engine reset invalidates players and waits for a valid next action; and
- accessibility/UI state remains correct if the haptic is unavailable.

## Step 7: AI proposal route

Keep the proposal input app-owned:

```text
semantic event + style label + device capability summary
        -> typed pattern proposal
        -> range clamp and event-count limit
        -> preview/Stop/Edit
        -> explicit Apply
```

- [ ] Do not provide raw sensor traces or private identity unless separately justified.
- [ ] Reject unsupported event types and excessive duration/looping.
- [ ] Require a stop policy for continuous proposals.
- [ ] Invalidate on screen dismissal, newer interaction, or capability change.
- [ ] Provide deterministic default patterns when the model is unavailable.
- [ ] Never claim the model can predict a person’s sensation across devices.

## Step 8: proof package

- [ ] Capability snapshots for each supported device class.
- [ ] Engine start, stopped, reset, and recovery logs.
- [ ] Pattern/AHAP fixture and revision.
- [ ] Player start/stop/cancel/loop/pause/seek evidence as applicable.
- [ ] Gesture commit/cancel/focus-loss evidence.
- [ ] Audio route/interruption evidence if sound is included.
- [ ] VoiceOver, Dynamic Type, Reduce Motion, contrast, and alternate-input proof.
- [ ] AI availability, validation, cancellation, stale-proposal, and fallback tests.
- [ ] Physical iPhone audio/haptic recording or observer sign-off.
- [ ] Archive and TestFlight release retest.

## Sources

- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticDeviceCapability](https://developer.apple.com/documentation/corehaptics/chhapticdevicecapability)
- [CHHapticEngine.capabilitiesForHardware()](https://developer.apple.com/documentation/corehaptics/chhapticengine/capabilitiesforhardware%28%29)
- [CHHapticPattern](https://developer.apple.com/documentation/corehaptics/chhapticpattern)
- [CHHapticEvent](https://developer.apple.com/documentation/corehaptics/chhapticevent)
- [CHHapticEvent.EventType](https://developer.apple.com/documentation/corehaptics/chhapticevent/eventtype)
- [CHHapticEvent.ParameterID](https://developer.apple.com/documentation/corehaptics/chhapticevent/parameterid)
- [CHHapticEventParameter](https://developer.apple.com/documentation/corehaptics/chhapticeventparameter)
- [CHHapticDynamicParameter](https://developer.apple.com/documentation/corehaptics/chhapticdynamicparameter)
- [CHHapticParameterCurve](https://developer.apple.com/documentation/corehaptics/chhapticparametercurve)
- [CHHapticPatternPlayer](https://developer.apple.com/documentation/corehaptics/chhapticpatternplayer)
- [CHHapticAdvancedPatternPlayer](https://developer.apple.com/documentation/corehaptics/chhapticadvancedpatternplayer)
- [Preparing your app to play haptics](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics)
- [Playing a custom haptic pattern from a file](https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file)
- [Representing haptic patterns in AHAP files](https://developer.apple.com/documentation/corehaptics/representing-haptic-patterns-in-ahap-files)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
