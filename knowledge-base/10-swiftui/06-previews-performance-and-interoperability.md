# Previews, Performance, and Interoperability

## Previews as a design instrument

Use the preview system to exercise meaningful states, not only the happy-path screen. A useful preview matrix includes empty, loading, populated, error, long text, dark mode, large Dynamic Type, and reduced motion. Preview with realistic content lengths and representative images.

~~~swift
#Preview("Large type, dark") {
    InboxView(model: .previewLoaded)
        .preferredColorScheme(.dark)
        .environment(\.sizeCategory, .accessibilityExtraExtraLarge)
}
~~~

If an environment value is version-specific, keep the preview configuration close to the feature and record the minimum OS used by the target.

## Performance habits

- Keep expensive work out of body and view initializers.
- Use lazy containers for large repeated collections.
- Avoid creating unstable IDs during every render.
- Downsample or stream large media before displaying it.
- Measure before optimizing; use Instruments and SwiftUI performance tools for slow updates or excessive body evaluation.
- Treat custom blur, shader, and glass layers as real rendering costs.

## UIKit and other framework bridges

SwiftUI can host UIKit views/controllers when a system capability is not represented by a native SwiftUI view. Keep the bridge small, map lifecycle and permission state explicitly, and expose a SwiftUI-friendly model rather than leaking controller details throughout the feature.

## Preview is not proof

A preview proves a controlled render. It does not prove camera authorization, a real model, an App Intent launched from Siri, StoreKit transactions, background execution, or device-specific performance. Promote the scenario to simulator, physical device, and release validation as needed.

## Sources

- [Previews in Xcode](https://developer.apple.com/documentation/swiftui/previews-in-xcode)
- [Performance analysis](https://developer.apple.com/documentation/swiftui/performance-analysis)
- [UIKit integration](https://developer.apple.com/documentation/swiftui/uikit-integration)
- [UIViewControllerRepresentable](https://developer.apple.com/documentation/swiftui/uiviewcontrollerrepresentable)
