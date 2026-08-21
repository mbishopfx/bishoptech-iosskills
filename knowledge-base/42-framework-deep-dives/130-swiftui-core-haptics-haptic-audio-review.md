# SwiftUI Core Haptics and haptic-audio review

Core Haptics is the physical-feedback layer for custom haptic and synchronized audio patterns. It sits below SwiftUI interaction design but above the device’s haptic hardware and haptic server. The right mental model is:

```text
interaction meaning
        -> capability check and fallback
        -> CHHapticEngine
        -> CHHapticPattern / AHAP
        -> CHHapticPatternPlayer or advanced player
        -> physical haptic/audio result
```

A `CHHapticPattern` can exist without an engine, but an engine is required to play it. A pattern object, a successful player call, and a simulator preview are not proof that a person felt the intended result.

This review is for iOS 26-targeted native apps and games. The recipes remain compile-oriented sketches until they are compiled in a named target and exercised on physical hardware.

## Choose the feedback lane

| Experience | Core Haptics route | Design boundary |
| --- | --- | --- |
| Standard button, picker, switch, or slider | Native SwiftUI/UIKit control feedback | Prefer system behavior; custom haptics are usually unnecessary. |
| One meaningful confirmation or error | `CHHapticEvent.EventType.hapticTransient` | A brief, semantic impulse with a visual and VoiceOver equivalent. |
| Progress, drag, collision, or sustained tension | `hapticContinuous` plus duration/parameters | Start/stop with the interaction and recover when the engine stops. |
| Rich audio-haptic moment | Advanced pattern player and audio events/resources | Synchronize with an owned audio track and verify route/volume behavior. |
| Reusable authored pattern | AHAP file in the bundle | Version, test, and fall back when keys or capabilities are unsupported. |
| Game-controller feedback | Core Haptics game-controller route | Verify the controller capability separately from iPhone haptics. |
| AI-assisted haptic proposal | App-owned semantic event description -> typed proposal -> review | The model proposes intensity, sharpness, timing, and fallback; it does not control the engine without validation. |

The most Apple-like choice is usually a small number of meaningful, restrained feedback moments. Do not replace every animation with a vibration or make haptics the only indication of state.

## Hardware capability is the first gate

Call `CHHapticEngine.capabilitiesForHardware()` before creating a product promise. The capability object exposes whether the device supports haptic events and audio event playback, and it can provide parameter attributes for supported events.

Apple’s preparation guidance notes that some devices do not support haptics, including iPad, iPod touch, and Apple Vision Pro. Those devices need a deliberate alternative such as visual feedback, audio, or a native control state. The correct fallback is not “pretend the haptic played.”

Model capability as a route state:

| State | Behavior |
| --- | --- |
| Haptics and audio supported | Enable the intended pattern within tested limits. |
| Audio only | Replace tactile feedback with a restrained audio or visual cue where appropriate. |
| Neither supported | Use visual, text, animation, or accessibility feedback. |
| Capability unknown/error | Use the deterministic fallback and retry only at a lifecycle boundary. |
| User/system muted or overridden | Respect the result; do not fight system services or create an accessibility failure. |

Capability is not a permission prompt. It is hardware and system state. Keep it separate from the app’s “haptics enabled” preference and from a player’s `isMuted` value.

## Engine ownership and lifecycle

`CHHapticEngine` represents the connection to the haptic server. It is not a singleton. Apple documents that an app can create multiple engines, but each engine behaves independently; a feature should still keep ownership clear so patterns do not fight over lifecycle, audio route, or power.

Create the engine early enough for the feature, store a strong reference, set `resetHandler` and `stoppedHandler` before starting, then create players from that engine. The engine can stop because the app is suspended, an audio session is interrupted, a controller disconnects, an idle timeout occurs, the system destroys the engine, or a system error happens. After an external stop, the app must restart the engine before it can play the next pattern.

When Core Haptics calls the reset handler after media-server recovery:

1. treat existing players as invalid;
2. rebuild the engine-side resources and players;
3. restart only when the current product state still wants feedback; and
4. make the next interaction able to recover if restart fails.

Do not assume the reset handler is a one-time startup callback. Do not start a second engine on every SwiftUI view redraw.

`isAutoShutdownEnabled` is a power/lifecycle choice. Automatic shutdown can produce an idle-timeout stop; if the product needs a long-lived continuous pattern, it still needs an explicit ownership and battery decision.

## Patterns: events, intensity, sharpness, and timing

`CHHapticPattern` is a hierarchical event/parameter description. You can create it from:

- Swift dictionaries;
- an array of `CHHapticEvent` and `CHHapticEventParameter` values; or
- an AHAP file or URL.

`CHHapticEvent` can represent transient or continuous haptic events and custom/continuous audio events. `relativeTime` controls when an event begins. `duration` controls how long a continuous event lasts. Event parameters include haptic intensity and sharpness, plus audio volume, pitch, pan, and other event-specific values.

Intensity controls amplitude/strength. Sharpness changes the character of the sensation—from crisp and mechanical to soft and rounded. These are normalized design controls, not a direct guarantee of identical physical force across hardware. Use them to communicate semantic differences, then verify the result on the target device.

A useful pattern review asks:

- What state or action does this pattern communicate?
- Can a person understand the same state without feeling it?
- Is the event transient or continuous?
- What stops a continuous event if the gesture is cancelled?
- Are intensity and sharpness within the tested range?
- Does audio need a separate volume/route policy?
- What happens when the haptic engine is unavailable or muted?

## Static parameters, dynamic parameters, and curves

Static `CHHapticEventParameter` values define the initial event state. `CHHapticDynamicParameter` values can change a pattern during playback. `CHHapticParameterCurve` schedules a series of parameter values that transition linearly over time.

Use the least powerful mechanism that expresses the interaction:

| Need | Tool |
| --- | --- |
| One fixed strength | Event parameter. |
| Change strength at a specific time | Dynamic parameter sent to the player. |
| Smooth ramp over a duration | Parameter curve. |
| Loop, pause, seek, resume, or sync audio | Advanced player. |

Real-time updates should be driven by a bounded interaction state, not by an unthrottled SwiftUI body update. For a drag, quantize or rate-limit updates and stop the player when the gesture ends or is cancelled. Do not allocate patterns or perform blocking work in a high-frequency interaction path without profiling.

## Standard versus advanced players

Create a standard `CHHapticPatternPlayer` with `makePlayer(with:)` for fixed patterns. It can start, stop, cancel, send dynamic parameters, schedule curves, and mute playback.

Use `CHHapticAdvancedPatternPlayer` from `makeAdvancedPlayer(with:)` when the pattern needs to change during playback or synchronize with a custom audio track. The advanced player supports looping, playback-rate changes, pausing, resuming, seeking, and a completion handler.

The advanced player is not automatically safer. Its loop, seek, and completion state still needs cancellation and stale-generation handling:

```text
gesture generation 7 starts player
gesture ends -> cancel player 7
engine resets -> discard player 7
new gesture generation 8 -> create/reuse a valid player
completion for 7 -> ignored as stale
```

Do not let a completion handler update a SwiftUI view after the feature has been dismissed or after a newer pattern supersedes it.

## AHAP file route

AHAP is a JSON-like file format for haptic patterns that can live in the app bundle. A file can define events, event parameters, dynamic parameters, and parameter curves. It can also define audio events and waveform paths when the app owns the associated audio resource.

Apple documents important versioning behavior:

- `Pattern` and `Version` are the top-level keys;
- a file contains one pattern;
- missing keys receive defaults;
- out-of-range values are clamped; and
- unsupported keys are ignored.

That behavior makes an AHAP file portable, but it can also hide an authoring mistake. Validate files in CI and verify the physical result on the minimum supported hardware. Keep the file resource local and signed; do not download a new haptic definition at runtime unless the product has a separately reviewed asset-delivery and integrity route.

For audio-haptic synchronization, use an advanced player and document:

- audio resource ownership and format;
- the route and volume policy;
- whether audio-only playback is allowed when haptics are unavailable;
- pause/seek/loop behavior;
- interruption and route-change recovery; and
- the proof that audio and tactile timing remain acceptable together.

## SwiftUI and Liquid Glass interaction design

SwiftUI already provides appropriate system feedback for many standard controls. Custom haptics should reinforce a meaningful event such as:

- a completed drag placement;
- a constrained value crossing a meaningful boundary;
- a successful local save;
- a camera or capture shutter moment; or
- a game collision or spatial event.

Pair every haptic with a visible state change and an accessibility-readable state. For a Liquid Glass control cluster:

1. keep the action hierarchy visible without haptics;
2. use a small transient pattern for a discrete confirmation;
3. use a continuous pattern only while the interaction is active;
4. stop and cancel on gesture cancellation or focus loss;
5. respect Reduce Motion and user preferences; and
6. keep the glass surface legible with haptics disabled.

Do not use a haptic to compensate for ambiguous glass affordances. A button that looks decorative should not become understandable only after a vibration.

## Accessibility and privacy

Haptics can be inaccessible or unavailable. Provide a visual and textual equivalent; do not encode a critical warning only in tactile strength. Test VoiceOver, Dynamic Type, Increase Contrast, Reduce Transparency, Reduce Motion, Switch Control, and keyboard/trackpad routes where relevant.

Custom haptics typically do not require location, contacts, or health permission, but audio-haptic patterns may interact with the app’s audio session and external routes. Explain when a feedback event can produce sound, respect system audio behavior, and avoid playing an unexpected audio resource in a communication or accessibility context.

The system can override an app’s haptic request with system services such as notification haptics. Record the intended feedback, not a claim that the app owns every physical vibration.

## Optional on-device AI haptic proposals

Foundation Models can propose a small semantic pattern description from app-owned interaction language:

```text
"Confirm a successful save"
        -> typed proposal: transient, intensity, sharpness, timing
        -> hard-range validation
        -> user/design review
        -> local CHHapticPattern
```

Keep the model away from raw sensor traces, private user identity, and uncontrolled physical-device commands. A typed proposal should be treated as untrusted configuration:

- clamp intensity, sharpness, duration, and event count;
- reject unsupported event types;
- reject continuous patterns without a stop policy;
- discard stale proposals when the screen or interaction changes;
- expose a deterministic fallback when the model is unavailable; and
- keep a human/design review for patterns that can be surprising or repetitive.

AI cannot prove that a person felt a sensation. The physical-device proof remains independent.

## Verification boundary

| Claim | Minimum proof |
| --- | --- |
| Hardware supports haptics | `supportsHaptics` and `supportsAudio` captured on each target device class. |
| Engine starts | Physical-device engine start and first-player evidence, with errors recorded. |
| Pattern is authored correctly | Pattern/AHAP validation, duration/parameter inspection, and deterministic fixture. |
| Player lifecycle works | Start, stop, cancel, loop/pause/seek where used, completion, and stale-generation tests. |
| Reset recovery works | Trigger interruption/background/media-server reset and show engine/player recovery. |
| Audio-haptic sync works | Physical route, volume, timing, interruption, and fallback evidence. |
| SwiftUI design works | Gesture, focus, accessibility, Reduce Motion, and glass-enabled/disabled task proof. |
| AI is safe | Availability, range validation, cancellation, stale proposal rejection, and deterministic fallback. |
| Release works | Archive, TestFlight install, physical device retest, and target capability matrix. |

The [Core Haptics design review](../21-design-deep-dives/158-swiftui-core-haptics-haptic-audio-review-design.md), [route worksheet](../50-capability-recipes/161-swiftui-core-haptics-haptic-audio-review-route.md), [proof matrix](../60-verification/155-swiftui-core-haptics-haptic-audio-proof-matrix.md), and [recipes](../70-code-recipes/173-swiftui-core-haptics-haptic-audio-review-recipes.md) turn these boundaries into reusable project artifacts.

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
- [Delivering Rich App Experiences with Haptics](https://developer.apple.com/documentation/corehaptics/delivering-rich-app-experiences-with-haptics)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Privacy](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
