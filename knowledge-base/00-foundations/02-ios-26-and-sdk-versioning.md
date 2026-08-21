# iOS 26 and SDK Versioning

## Four versions to keep separate

When an implementation says “iOS 26,” ask which version it means:

- **Deployment target** — the oldest OS the app promises to run on.
- **SDK** — the API surface used to compile the app.
- **Installed runtime** — the OS currently running on the simulator or device.
- **Device capability** — hardware, settings, language assets, Apple Intelligence state, camera support, or entitlements that determine whether a feature can actually run.

An API may compile because the SDK is new while still requiring a runtime check. A feature may pass an OS check and still be unavailable because the device lacks hardware, a person denied permission, a model is not ready, or required assets are not installed.

## Availability pattern

Use availability annotations and runtime branches intentionally:

```swift
if #available(iOS 26.0, *) {
    NewSystemExperience()
} else {
    ExistingExperience()
}
```

Keep the fallback useful. Avoid an empty placeholder that makes the app unusable on the supported lower target.

## Treat documentation as versioned input

Apple’s APIs and on-device models evolve. Record the date researched, the SDK/OS assumption, and the exact source URL in a note. For Foundation Models prompts, store the prompt version and test against the model available on the target OS rather than assuming identical behavior after a system update.

## Platform routing

When a view is intended for iPhone, iPad, Mac, or another Apple platform, first decide whether the behavior is shared or platform-specific. SwiftUI can share view composition, but navigation containers, window behavior, pointer/keyboard input, Live Activities, widgets, and permissions vary by platform.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Running code on a specific platform or OS version](https://developer.apple.com/documentation/xcode/running-code-on-a-specific-version)
