# iOS 27, iOS 26, and SDK Versioning

The current stable major-version lane is iOS 27/Xcode 27. Apple currently lists
Xcode 27.2 beta 2 with the iOS 27.2 SDK as its newest prerelease lane. Keep the
prerelease separate from the stable major-version documentation and from the
toolchain selected on the local machine. iOS 26 remains a supported
compatibility lane, not an API claim to replace blindly.

## Four versions to keep separate

When an implementation says “iOS 27” or “iOS 26,” ask which version it means:

- **Deployment target** — the oldest OS the app promises to run on.
- **SDK** — the API surface used to compile the app.
- **Installed runtime** — the OS currently running on the simulator or device.
- **Device capability** — hardware, settings, language assets, Apple Intelligence state, camera support, or entitlements that determine whether a feature can actually run.

An API may compile because the SDK is new while still requiring a runtime check. A feature may pass an OS check and still be unavailable because the device lacks hardware, a person denied permission, a model is not ready, or required assets are not installed.

## Availability pattern

Use availability annotations and runtime branches intentionally:

```swift
if #available(iOS 27.0, *) {
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

## Current iOS 27 route

Use the [iOS 27 SwiftUI and SDK refresh](../10-swiftui/13-ios27-swiftui-refresh.md)
for the current toolbar, document, collection, image/text-selection,
MetricKit, adaptive-arrangement, reserved-region, and Liquid Glass overlay
matrix. As of 2026-10-01, Apple's requirements page lists Xcode 27.2 beta 2,
the iOS 27.2 SDK, and Swift 6.4 as the newest prerelease combination. The
selected local toolchain remains Xcode 27.0 with the iOS 27.0 SDK and Swift
6.4; that local observation does not prove the newer beta APIs compile. The
latest documented Xcode 26 fallback is Xcode 26.6 with the iOS 26.5 SDK and
Swift 6.3. Keep the exact deployment target, selected SDK, beta/final status,
and fallback beside every guarded API. Recheck Apple's [SDK and system
requirements](https://developer.apple.com/xcode/system-requirements) before
version-sensitive work.

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Foundation Models updates](https://developer.apple.com/documentation/Updates/FoundationModels)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Running code on a specific platform or OS version](https://developer.apple.com/documentation/xcode/running-code-on-a-specific-version)
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
