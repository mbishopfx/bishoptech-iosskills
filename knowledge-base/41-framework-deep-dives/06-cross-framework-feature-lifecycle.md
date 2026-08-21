# Cross-Framework Feature Lifecycle

## Compose capabilities without hiding ownership

The most useful iOS features cross framework boundaries: a capture surface feeds Vision, a transcript feeds Foundation Models, a location selects a MapKit result, a HealthKit query informs a chart, or an App Intent launches the same use case as a SwiftUI button. The feature remains maintainable when each layer owns one responsibility and reports its state explicitly.

Use this composition shape:

```text
SwiftUI/system surface
        -> feature coordinator
        -> capability adapters
        -> normalized app-owned evidence
        -> deterministic domain use case
        -> persistence/export/system handoff
```

The coordinator should orchestrate. It should not become a second persistence layer, permission store, business-rule engine, or universal “manager” that owns every device resource forever.

## Ownership matrix

| Layer | Owns | Must not own |
| --- | --- | --- |
| SwiftUI/UIKit/system surface | User intent, presentation, semantic controls, accessibility, loading/error/review states | Raw framework sessions, secrets, duplicated authorization policy, irreversible side effects. |
| Feature coordinator | Sequencing, cancellation, replacement, progress, stale-result suppression, route selection | Long-lived global state or domain truth that bypasses the repository/use case. |
| Capability adapter | One Apple framework’s API, permission/availability mapping, input/output conversion, teardown | Product-specific validation or direct UI mutation. |
| Evidence/normalization layer | Source reference, observation/prediction/transcript/location/result, provenance, confidence, normalized units | Approval, authorization, or claims beyond the source. |
| Domain use case | Current-state read, authorization, validation, idempotency, commit/rollback, side-effect policy | Model prompt construction, view lifecycle, or system-surface presentation. |
| Persistence/sync/export | Durable state, migration, conflict/deletion, representations, retention | Assuming a source is true because a framework returned a value. |
| System/extension adapter | App Intent, widget/control, Live Activity, Watch, CarPlay, App Clip, or background contract | In-memory app state, hidden long-running work, or bypassing shared authorization. |

## Feature state machine

Make the state contract visible before adding styling:

`idle -> preparing -> permission/availability -> ready -> running -> partial/updated -> review -> committing -> completed`

Failure and replacement branches are first-class:

- `permissionDenied`, `restricted`, or `notDetermined`;
- `unsupported`, `notReady`, `assetMissing`, `accountUnavailable`, or `hardwareUnavailable`;
- `interrupted`, `backgrounded`, `processTerminated`, or `routeChanged`;
- `cancelled`, `superseded`, `stale`, or `timedOut`;
- `invalid`, `unauthorized`, `conflict`, `quota`, `resourceFailure`, or `serviceFailure`.

Do not display all of these as “Something went wrong.” The recovery action should follow the owner: request/recheck permission, install an asset, choose another input, retry a query, review a conflict, reopen the app, or use a manual route.

## Coordinator rules

1. **Start at user intent.** Do not activate camera, microphone, location, motion, radio, health, or background work during app launch just because the feature might be used later.
2. **Acquire the smallest capability.** Prefer a picker or one-shot query before broad library, continuous sensor, or background access.
3. **Make every asynchronous source cancellable.** A disappearing view, new source, logout, account switch, or task replacement should cancel or supersede work.
4. **Version the source.** Attach a source/request ID to every result so old work cannot overwrite newer state.
5. **Normalize at the boundary.** Convert framework-specific values to app-owned types while preserving provenance, freshness, units, coordinate systems, confidence, and authorization state.
6. **Validate again before commit.** Current domain state may have changed while a framework request was running.
7. **Use one use case for every entry point.** SwiftUI, App Intents, widgets, Watch, CarPlay, and model tools should converge on the same authorization and state transition.
8. **Stop resources deliberately.** Capture sessions, audio sessions, location streams, sensors, radio scans, AR sessions, haptic engines, and background tasks need explicit teardown or completion.

## Evidence and freshness

Every derived value should carry enough metadata for the UI and domain policy to answer:

- What source produced it?
- When was it captured or observed?
- Which device/OS/model/request/revision generated it?
- Is it partial, final, stale, approximate, user-edited, or confirmed?
- What permission/account/asset state was in effect?
- Can the person inspect or correct it?

A `CLLocation`, weather forecast, HealthKit statistic, speech transcript, Core ML prediction, or system entity can be valid and still be stale, approximate, incomplete, or unsuitable for the next action. Make that distinction visible instead of hiding it behind a generic model.

## Native UI composition

Use a screen route that expresses the user’s decision:

- `NavigationStack` for a source-to-detail workflow;
- `NavigationSplitView` for browse/inspect on larger widths;
- `Form` for editable settings, permissions, language, and structured review;
- `List` for records, search results, and explicit loading/empty/error states;
- `Map` for map content, with detail controls outside the map when possible;
- `sheet` for bounded review/confirmation that returns to the source;
- a system picker or system-owned confirmation when Apple provides one;
- a widget/control/Live Activity/Watch/CarPlay template only for the small subset of state the surface can safely own.

Use Liquid Glass through standard system surfaces first. A custom glass group can clarify a related functional action cluster, but it must not cover evidence, obscure text, replace semantic controls, or carry the only meaning of a state change.

## Resource and concurrency matrix

| Resource | Start | Stop/cancel | Common proof |
| --- | --- | --- | --- |
| Camera session | User enters capture and permission is granted. | View leaves, capture ends, interruption, replacement. | Physical camera, frame rate/backpressure, thermal, privacy. |
| Audio/speech | User starts recording and audio route is configured. | Stop, interruption, route change, cancellation, analyzer finish. | Physical microphone/speaker, locale/assets, background/phone-call behavior. |
| Location | User requests location or selected feature needs it. | Accuracy/goal satisfied, view leaves, authorization changes. | Permission/accuracy, freshness, power, physical movement/background. |
| Motion/haptics | Feature starts and hardware supports it. | Feature ends, engine stops, sensor unavailable, interruption. | Physical motion/haptic behavior and fallback. |
| Radio/accessory | Pair/discover/control flow begins. | Session ends, accessory disconnects, trust revoked, app closes. | Two-device/accessory protocol and side-effect safety. |
| AR/graphics/game | Scene owns camera/GPU/game session. | Scene leaves, tracking fails, thermal/input failure. | Physical device, frame budget, tracking/input/accessibility. |
| Background/extension | System schedules or person starts an allowed task. | Expiration, cancellation, resource failure, host termination. | Signed capability, system invocation, expiration/relaunch, release config. |

## Verification sequence

1. Source the exact API and record availability/entitlement/permission assumptions.
2. Compile the smallest adapter in the target project.
3. Unit-test the adapter’s state mapping and deterministic domain policy.
4. Fixture-test empty, stale, partial, denied, unavailable, cancelled, and replacement states.
5. UI-test the main route, review/confirmation, accessibility, and deep link.
6. Run the named device/system/two-device/vehicle surface for the claim.
7. Measure performance and resource teardown with the target workload.
8. Record signed/release/server/account evidence separately; do not promote a local result into a production claim.

## Sources

- [Swift Concurrency](https://developer.apple.com/documentation/swift/concurrency)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Managing user interface state](https://developer.apple.com/documentation/swiftui/managing-user-interface-state)
- [AVCaptureSession](https://developer.apple.com/documentation/avfoundation/avcapturesession)
- [Core Location](https://developer.apple.com/documentation/corelocation)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [HealthKit](https://developer.apple.com/documentation/healthkit/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [Vision](https://developer.apple.com/documentation/vision/)
- [SpeechAnalyzer](https://developer.apple.com/documentation/speech/speechanalyzer)
- [TranslationSession](https://developer.apple.com/documentation/translation/translationsession)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [BackgroundTasks](https://developer.apple.com/documentation/backgroundtasks/)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
