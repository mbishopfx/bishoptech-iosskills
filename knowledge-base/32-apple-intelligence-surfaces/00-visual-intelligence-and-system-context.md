# Visual Intelligence and System Context

Visual Intelligence is a system search surface, not a replacement for an app’s own camera pipeline. People use it to search for places or objects in the environment or onscreen; the system provides captured semantic context to an app, and the app returns matching `AppEntity` values through App Intents.

Apple’s current Visual Intelligence documentation describes this API as preliminary/in development. Treat the route as update-sensitive and verify the final target SDK, supported device/OS combinations, and system invocation before shipping.

## The route

`Visual Intelligence capture -> SemanticContentDescriptor -> IntentValueQuery -> matching AppEntity -> system result -> OpenIntent/deep link`

The app should not assume the system gives it a named object. The documented integration can provide high-level labels and, where available, a pixel buffer. Labels can change over time, may be general terms, and aren’t a guaranteed identifier for the real-world item.

## What the app owns

1. Define a small, privacy-reviewed set of entities worth finding through visual search.
2. Keep entities lightweight and constructible quickly; do not expose the entire database.
3. Implement the documented `IntentValueQuery` route for `SemanticContentDescriptor`.
4. Match labels or image context against deterministic app data or a bounded image-search service.
5. Return localized `DisplayRepresentation` values with a useful title, subtitle, and image.
6. Implement an `OpenIntent` that validates the entity still exists and routes into the correct app destination.
7. Keep matching, authorization, redaction, and domain truth in app-owned code.

## Route sketch

This sketch reflects the shape of Apple’s current integration guidance. Verify protocol names, macros, associated types, and availability against the selected SDK before compiling.

```swift
import AppIntents
import VisualIntelligence

struct LandmarkIntentValueQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [LandmarkEntity] {
        guard let pixelBuffer = input.pixelBuffer else {
            return []
        }

        // Match against the app’s own indexed content.
        return try await LandmarkSearch.matching(pixelBuffer: pixelBuffer)
    }
}

struct OpenLandmarkIntent: OpenIntent {
    static let title: LocalizedStringResource = "Open Landmark"

    @Parameter(title: "Landmark")
    var target: LandmarkEntity

    func perform() async throws -> some IntentResult {
        try await LandmarkActions.openValidated(target)
        return .result()
    }
}
```

If the app supports several entity types, use the current documented union-value route rather than multiple conflicting visual queries. Keep `LandmarkSearch` deterministic or explicitly bounded; do not silently send raw camera frames or personal photos to an unapproved remote service.

## Privacy and product boundaries

- Visual Intelligence supplies context captured from a camera or screenshot. Explain why the app needs that context and minimize retention.
- A high-level label is a search hint, not proof of identity, location, ownership, safety, or a measurement.
- A pixel buffer is sensitive input. Process it only for the requested match, release it when no longer needed, and disclose any persistence or network transfer.
- `AppEntity` results should expose only the fields needed for discovery and opening the record.
- The `OpenIntent` must handle a deleted/stale entity, denied authorization, ambiguous matches, and unavailable system invocation.
- Keep the ordinary in-app search and navigation route useful when Visual Intelligence is unavailable.

## Availability and proof

Record these separately:

| Claim | Evidence required |
| --- | --- |
| The source API exists | Current Visual Intelligence/App Intents documentation and target SDK compile. |
| The route is available to this app | Target OS/device/system settings and the documented preliminary/availability state. |
| Matching is useful | Representative visual fixtures, labels, pixel-buffer cases, false positives, empty results, and latency. |
| The entity opens correctly | Real system result selection, stale/deleted ID handling, and typed deep-link tests. |
| The experience is shippable | Supported physical device/system-surface invocation, accessibility/localization review, signed build, and any required release configuration. |

Do not call a Visual Intelligence integration complete because an `AppIntent` compiles or because the normal app search works.

## Sources

- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [Visual intelligence App Intents integration](https://developer.apple.com/documentation/appintents/visual-intelligence)
- [Visual intelligence app schema domain](https://developer.apple.com/documentation/appintents/app-schema-domain-visual-intelligence)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
