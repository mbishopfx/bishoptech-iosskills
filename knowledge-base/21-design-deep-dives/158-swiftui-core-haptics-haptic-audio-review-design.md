# SwiftUI Core Haptics and haptic-audio design review

Core Haptics should make a native interaction feel more coherent, not more noisy. The visual surface, gesture, text state, accessibility output, audio route, and physical haptic should all communicate the same event.

## Start with the meaning

Before choosing intensity or sharpness, write the semantic event:

| Meaning | Visual state | Haptic shape | Fallback |
| --- | --- | --- | --- |
| Confirmed | Saved/checkmark/status text | Short transient | Visual checkmark + VoiceOver announcement |
| Rejected | Inline error/constraint state | Short contrasting transient | Inline text + focus movement |
| Boundary reached | Slider/snapping indicator | Small transient or parameter bump | Value label + animation |
| Drag in progress | Lifted/selected item | Optional restrained continuous | Visual lift/position |
| Collision/impact | Object changes state | Transient with tested intensity | Animation + sound/visual |
| Long-running activity | Progress indicator | Continuous only if meaningful | Progress UI and text |

Do not let a model or a designer choose a haptic in isolation from the state it represents. The haptic is one rendering of the interaction contract.

## Native screen blueprint

For an iOS 26 SwiftUI screen with Liquid Glass controls:

```text
NavigationStack
  -> semantic title and status
  -> primary content / gesture surface
  -> visible action state
  -> optional glass action cluster
  -> accessible text equivalent
```

The haptic engine is a service owned by the feature or scene, not a property constructed in `body`. Create it when the feature becomes active, hold it strongly, and tear it down or mute it when the feature leaves the interaction domain.

## Capability and fallback card

When a feature’s tactile feedback matters, show a compact settings/status affordance rather than a warning on every interaction:

```text
Feedback
Haptics available on this iPhone
Sound follows the current audio setting
[Test feedback]
```

If the device does not support haptics, say “Visual feedback is active on this device.” Do not show a broken haptic toggle or imply a hardware problem the user cannot fix.

The card should distinguish:

- device capability;
- app preference;
- system/audio route behavior; and
- current engine availability.

## Transient feedback design

Transient events work best when they mark a single semantic moment. Use one event at the moment the visual state commits, not at every intermediate drag tick or every SwiftUI state mutation.

Recommended sequence:

1. update the app-owned model;
2. render the visual state;
3. post one transient haptic if capability and preference permit;
4. announce the result through the accessibility path; and
5. allow the next action to cancel or supersede stale feedback.

The haptic should not fire before the action is accepted. A button that fails validation should use the error state, not the success pattern.

## Continuous interaction design

Continuous haptics require an explicit lifecycle:

```text
gesture began
  -> create/start player
gesture changed
  -> bounded dynamic parameter updates
gesture ended
  -> stop player and commit state
gesture cancelled/focus lost
  -> cancel/stop player and restore state
engine stopped/reset
  -> discard player, rebuild, and wait for next valid interaction
```

Do not leave a continuous event running because a view disappeared, a user switched apps, or a gesture recognizer cancelled. Use a generation ID to ignore completion callbacks from older players.

## Liquid Glass and haptic hierarchy

Liquid Glass creates a visual grouping of controls. It does not define the feedback semantics. Use glass for:

- a small toolbar action group;
- a control cluster around a meaningful state;
- a compact “feedback enabled” setting;
- a playback/loop control group; or
- an inspector that lets a designer tune a pattern.

Avoid:

- a glass panel for every individual button;
- a haptic on every glass morph or hover effect;
- a continuous vibration while a glass surface is merely visible; and
- translucent controls whose meaning is only explained by touch feedback.

Test the same screen with glass reduced, Reduce Transparency enabled, Increase Contrast enabled, and haptics disabled. The visual hierarchy must remain complete.

## Authoring surface for patterns

If the app exposes a haptic authoring tool, use a clear two-level model:

### Semantic editor

- event name;
- transient or continuous;
- start time and duration;
- intensity and sharpness;
- optional audio pairing;
- loop/stop policy; and
- fallback behavior.

### Advanced inspector

- event parameters;
- dynamic parameters;
- parameter curves;
- audio resource IDs;
- player rate/seek/loop;
- AHAP export/import; and
- hardware capability constraints.

Keep the advanced inspector out of the primary user flow. A user should be able to choose “soft confirmation” without learning the Core Haptics parameter vocabulary.

## Audio-haptic synchronization

When audio and haptics are paired, present them as one feedback event. The UI should disclose:

- whether the feedback includes sound;
- whether it follows the current audio route;
- whether it can be muted independently; and
- what happens on headphones, a call, or an interrupted audio session.

Do not use a loud custom audio event to compensate for unavailable haptics without testing the accessibility and privacy consequences. If a user is in a communication session, the app must respect that route’s audio policy.

## AI-assisted haptic design surface

An optional AI panel can translate a semantic description into a previewable pattern proposal:

```text
Meaning: "A calm, successful save"
Suggested: transient · medium-soft · 0.08 seconds
Fallback: visual checkmark + spoken status

[Preview] [Edit] [Apply to this action]
```

The proposal view should show:

- the input meaning;
- exact normalized values after validation;
- capability/fallback state;
- a preview and Stop button;
- a non-AI deterministic alternative; and
- a clear note that physical sensation varies by device.

Never hide a continuous loop behind “smart feedback.” Require an explicit duration and stop policy. Treat AI-generated parameters as design suggestions, not a direct hardware command.

## Accessibility and alternate input

Haptics are supplemental. For every feedback event, define:

- a visual state;
- a text label/value;
- an accessibility announcement or focus change where useful; and
- an alternate input path that triggers the same semantic action.

VoiceOver users should not need to feel the pattern to know whether the action succeeded. Reduce Motion and accessibility preferences should reduce unnecessary motion and feedback intensity, not remove state information. Keyboard, Switch Control, and pointer interactions should receive the same semantic state even if the haptic is unavailable.

## Interaction review checklist

- [ ] The haptic meaning is written before the waveform is chosen.
- [ ] Native controls are allowed to provide their system feedback first.
- [ ] Every custom haptic has visual and accessible equivalents.
- [ ] Capability, app preference, and engine state are separate.
- [ ] Transient feedback fires at commit, not every state update.
- [ ] Continuous feedback has start, update, end, cancel, and reset paths.
- [ ] Liquid Glass remains legible with haptics and transparency changes disabled.
- [ ] Audio pairing documents route, volume, interruption, and privacy behavior.
- [ ] AI proposals show exact validated values and a deterministic fallback.
- [ ] Physical iPhone testing captures the actual sensation and timing.
- [ ] TestFlight proof repeats the same interaction on the release build.

## Sources

- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [CHHapticEngine](https://developer.apple.com/documentation/corehaptics/chhapticengine)
- [CHHapticDeviceCapability](https://developer.apple.com/documentation/corehaptics/chhapticdevicecapability)
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
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
