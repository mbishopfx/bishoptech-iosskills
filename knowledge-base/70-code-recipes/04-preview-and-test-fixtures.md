# Preview and Test Fixtures

## Preview matrix

Create previews around state and environment, not only one “happy path” screenshot:

```swift
#Preview("Normal") {
    NoteList()
}

#Preview("Large text and dark mode") {
    NoteList()
        .environment(\.sizeCategory, .accessibilityExtraExtraExtraLarge)
        .preferredColorScheme(.dark)
}
```

Use an in-memory model container and deterministic fake services for any preview that reads data. Do not make previews depend on network, camera, HealthKit, StoreKit, or an available Foundation Model.

## Dependency fixture

```swift
protocol NotesActions: Sendable {
    func add(text: String) async throws
}

struct PreviewNotesActions: NotesActions {
    func add(text: String) async throws { }
}
```

Use the real protocol boundary in the feature, then inject a predictable fake for loading, error, empty, and success states. The protocol shape should remain small enough that the view’s behavior is obvious.

## Test levels

| Level | Proves | Does not prove |
| --- | --- | --- |
| Unit test | Domain rules, parsing, validation, state reducers | Rendering, permissions, real device behavior |
| SwiftUI preview | A supplied state can render in the canvas | Entitlements, model availability, network, camera |
| UI test | A repeatable user flow in a controlled app | Every hardware/lifecycle/store condition |
| Simulator | Many layout, navigation, permission, and deterministic input paths | Physical camera, sensors, actual Apple Intelligence availability, thermal/battery behavior |
| Physical device | Real hardware/system integration under the tested configuration | All device families, production traffic, App Store review |

## Fixture checklist

- Empty, loading, success, partial, stale, denied, unavailable, error, and destructive states.
- Long text, localization, right-to-left, large Dynamic Type, dark mode, high contrast, reduced transparency, and Reduce Motion.
- Model unavailable/not ready, generation failure, context overflow, tool failure, and manual fallback.
- StoreKit pending/unverified, sync offline/conflict, camera/location denied, and extension process behavior.
- Deterministic clocks, IDs, random seeds, and sample data with no personal information.

## Compile/device gate

- Confirm previews have explicit dependency/container setup.
- Run unit and UI tests with a controlled data reset.
- Capture physical-device evidence for every feature whose correctness depends on hardware, entitlement, background execution, model readiness, or a real system surface.
- Keep screenshot tests subordinate to semantic/accessibility tests; visual similarity alone is not correctness.

## Sources

- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Build, device, and release checklist](../60-verification/01-build-device-and-release-checklist.md)
- [Source review checklist](../60-verification/00-source-review-checklist.md)
