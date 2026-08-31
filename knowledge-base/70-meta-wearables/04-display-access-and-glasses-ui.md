# Display Access and glasses UI

`MWDATDisplay` is a device capability, not a SwiftUI window. It renders a
structured display tree or a video player on a display-capable Meta glasses
device after a `DeviceSession` has started.

## Capability lifecycle

The safe order is:

```text
configure -> register -> select device with supportsDisplay()
  -> create/start DeviceSession -> wait for .started
  -> addDisplay() -> start Display -> wait for DisplayState.started
  -> send one root DisplayableView -> observe errors/playback
  -> stop Display -> stop DeviceSession
```

Keep a listener token alive for the entire observation lifetime. The official
Display guidance also recommends observing `session.errorStream()` and handling
the specific “DAT app on the glasses update required” error separately from a
generic failure.

## Device selection

Use a capability predicate instead of a frame-name switch:

```swift
let selector = AutoDeviceSelector(
    wearables: Wearables.shared,
    filter: { $0.supportsDisplay() }
)
```

If the person explicitly selects a device, use its `DeviceIdentifier` with a
specific selector. Present link state, compatibility, and update actions from
the SDK's device metadata. A device model string is useful for display, but it
is not the authorization or capability decision.

## Display tree rules

Each `send(_:)` call replaces the previous content and active tap handlers. A
UI send has one root `FlexBox`; a video send has one root `VideoPlayer`. Child
components include the public Display DSL types such as `Text`, `Button`,
`Image`, `Icon`, and `ButtonGroup` in the current release. If a file imports
SwiftUI, qualify Display names to avoid confusing `MWDATDisplay.Text` with
`SwiftUI.Text`.

Use typed built-in `IconName` values rather than raw icon strings. Use HTTPS
image URLs and validate them before sending. For video, use the documented
HTTP(S) URL/codec path, install the playback callback before sending, clear it
after terminal playback, and call the stop operation when a person exits early.
The current API also includes `clearDisplay()`; verify the availability and
error behavior against the pinned package.

## Glanceable interaction contract

Display content should be short, high-signal, and recoverable:

- one primary action per card or step;
- visible progress for multi-step content;
- no hidden dependence on the phone being in the foreground;
- explicit unavailable, updating, paused, stopped, and send-failed states;
- idempotent button actions and a phone-side confirmation for consequential
  work;
- no claim that a button tap proves the intended domain action completed.

The glasses display surface and interaction model are not identical to a
SwiftUI screen. Design the phone companion as the detailed, accessible control
surface and the glasses as a glanceable projection with clear recovery.
For cross-surface input ownership, sensor claims, stale-event handling, and
physical gesture evidence, use the [input, sensors, and physical interaction
route](24-input-sensors-and-physical-interaction.md).

## Display-specific configuration

The official Display sample includes the core URL scheme and wearable accessory
configuration plus background and local-network/Bonjour entries for the
feature's link-lease needs. Inspect the current sample's `Info.plist` and the
target's privacy configuration before adding keys; do not cargo-cult sample
metadata into a camera-only target.

## What a Display test proves

| Test | What it proves | What it does not prove |
| --- | --- | --- |
| Display DSL builds | Source/compile compatibility with a package revision | Physical legibility or link performance. |
| Mock display or fixture | State/error/content reducer behavior | The real display, ambient light, or EMG interaction. |
| Display Access sample on a named pair | The exact app/build/device/firmware task | Other models, regions, release channels, or production. |
| Signed release-channel build | Distribution path for that configured project | Meta public eligibility or App Store approval. |

## Sources

- [DAT iOS Display Access skill](https://github.com/facebook/meta-wearables-dat-ios/blob/main/plugins/mwdat-ios/skills/display-access/SKILL.md)
- [DAT iOS Display Access sample](https://github.com/facebook/meta-wearables-dat-ios/tree/main/samples/DisplayAccess)
- [DAT iOS changelog](https://github.com/facebook/meta-wearables-dat-ios/blob/main/CHANGELOG.md)
- [DAT iOS API reference](https://wearables.developer.meta.com/docs/reference/ios_swift/dat/latest)
- [Meta Wearables Display documentation](https://wearables.developer.meta.com/docs/develop/)
- [Apple SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
