# SwiftUI Core Haptics and haptic-audio proof matrix

Use this matrix to distinguish authored haptic content from physical feedback. A pattern object, a player, a `supportsHaptics` Boolean, a simulator run, or a completion handler does not prove that a person felt the intended sensation.

Related pages:

- [Core Haptics framework review](../42-framework-deep-dives/130-swiftui-core-haptics-haptic-audio-review.md)
- [Core Haptics design review](../21-design-deep-dives/158-swiftui-core-haptics-haptic-audio-review-design.md)
- [Core Haptics route worksheet](../50-capability-recipes/161-swiftui-core-haptics-haptic-audio-review-route.md)
- [Core Haptics code recipes](../70-code-recipes/173-swiftui-core-haptics-haptic-audio-review-recipes.md)

## Evidence ladder

| Level | Proves | Does not prove |
| --- | --- | --- |
| Source review | The route follows documented Core Haptics engine, pattern, player, AHAP, SwiftUI, and release guidance. | Hardware supports the pattern or a person felt it. |
| Capability check | The target reports haptic/audio support and parameter attributes. | A specific player started or the sensation was perceptible. |
| Pattern validation | Event types, timing, parameters, curves, AHAP version, and fallback are valid. | Hardware output, route timing, or accessibility. |
| Engine/player proof | The engine and player accepted start/stop/cancel commands. | Physical sensation or user comprehension. |
| Physical-device proof | A named device/OS/route produced an observed result. | Every supported device, release build, or accessibility mode. |
| TestFlight proof | The distributed artifact preserves the haptic route and fallback. | A Debug run or simulator preview. |

## Matrix

| Claim | Positive evidence | Negative/edge evidence | Owner |
| --- | --- | --- | --- |
| Device supports haptics | Capture `CHHapticEngine.capabilitiesForHardware().supportsHaptics` on the target iPhone. | iPad, iPod touch, Vision Pro, simulator, unsupported/limited capability. | Device QA |
| Device supports audio events | Capture `supportsAudio` and audio route. | Muted route, communication session, headphones/Bluetooth change, unavailable resource. | Audio QA |
| Fallback is complete | Disable haptics and show visual/text/audio alternative with the same meaning. | Critical state only exists as vibration. | Design/QA |
| Engine owns the feature | Strong engine lifetime and one documented feature owner. | Engine constructed in `body`, deallocated before playback, competing owners. | App |
| Handlers are configured | `resetHandler` and `stoppedHandler` are set before `start()`. | Engine reset or stop produces no recovery path. | App |
| Engine starts | Physical device starts engine and creates a player without error. | Simulator success or engine Boolean without output. | Device QA |
| Reset recovery works | Simulate media-server/audio disruption; reset rebuilds engine/player and next interaction works. | Old player reused after reset or restart loops indefinitely. | App |
| Stoppage recovery works | Exercise app suspension, audio interruption, idle timeout, controller disconnect where relevant. | App assumes haptics continue while suspended or interrupted. | App |
| Transient pattern is correct | Fixture verifies event type, relative time, intensity, sharpness, and commit timing. | Haptic fires on every render/drag tick or before action commit. | App |
| Continuous pattern is safe | Start/update/stop/cancel/timeout are captured for a gesture. | Continuous haptic leaks after cancellation or view dismissal. | App |
| Dynamic updates are bounded | Parameter sends are rate-limited and stale generations are ignored. | Blocking allocations or unbounded updates on the gesture path. | App |
| Curves are correct | Curve control points, timing, and parameter IDs match the intended ramp. | Curve continues after action cancellation or exceeds capability assumptions. | App |
| Advanced player is justified | Loop, pause, seek, playback rate, or audio sync requires it. | Advanced player used without lifecycle/cancel policy. | App |
| AHAP resource is packaged | Bundle contains the intended AHAP file, version, and target membership. | File missing in archive, wrong target resource, or runtime download without integrity plan. | Release |
| AHAP fallback is understood | Missing/defaulted/out-of-range/unsupported keys are tested on target devices. | Clamping/ignored keys silently changes the semantic event. | Design/QA |
| Audio-haptic sync works | Physical route captures relative audio/haptic timing and interruption behavior. | Audio plays on a different route, volume, or timing than expected. | Audio QA |
| Native design works | Glass-enabled/disabled, gesture, loading, success, error, and fallback states are coherent. | Haptic is required to interpret an ambiguous control. | Design |
| Accessibility works | VoiceOver/text, Dynamic Type, Increase Contrast, Reduce Motion, keyboard, and Switch Control tasks pass. | Haptic is the only success/error signal or focus is lost. | Accessibility |
| AI proposal is bounded | Typed values are clamped, event count/duration limited, previewable, cancellable, and reviewable. | Model directly controls engine, suggests infinite loop, or exposes private traces. | AI/app |
| Physical sensation is confirmed | Observer or test artifact identifies device, OS, pattern revision, route, and perceived result. | Simulator screenshot or player completion used as physical evidence. | Device QA |
| Release works | Archive -> TestFlight -> physical iPhone retest shows pattern and fallback. | Debug-only resource or unsigned/incorrect target membership. | Release |

## Fixture plan

```text
CH-01 capability: iPhone haptics/audio, unsupported device fallback
CH-02 transient: confirmation/error timing and semantic equivalent
CH-03 continuous: drag start/update/end/cancel/focus loss
CH-04 dynamic: intensity/sharpness update rate and stale generation
CH-05 curve: control points, duration, cancellation
CH-06 advanced: loop/pause/resume/seek/rate/completion
CH-07 engine: start, stoppedHandler, resetHandler, rebuild
CH-08 AHAP: bundle resource, version, defaults, clamping, unsupported keys
CH-09 audio: speaker, headphones, Bluetooth, communication interruption
CH-10 SwiftUI: Liquid Glass enabled/disabled, Reduce Motion, accessibility
CH-11 AI: unavailable, invalid range, cancellation, stale proposal, fallback
CH-12 release: archive, TestFlight, physical iPhone, observed sensation
```

Record the device model, iOS build, audio route, haptic preference, pattern/AHAP revision, engine/player generation, app build, and observer result. Do not describe “felt correctly” without a named physical device and a reproducible interaction.

## Stop conditions

Stop before release if:

- the feature has no capability fallback;
- the engine is created from SwiftUI rendering or loses ownership during playback;
- reset/stopped/interruption recovery is untested;
- a continuous player has no cancellation or timeout;
- an AHAP resource is not in the signed target bundle;
- audio-haptic behavior changes across routes without a documented policy;
- accessibility has no visual/text equivalent;
- an AI proposal can exceed tested ranges or apply without review; or
- TestFlight has not been exercised on a physical iPhone.

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
