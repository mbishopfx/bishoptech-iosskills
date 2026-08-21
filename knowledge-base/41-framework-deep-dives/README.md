# Framework Deep Dives

This tranche turns the broad framework catalog into narrower implementation routes. Each page answers four questions:

1. What user capability does this framework provide?
2. What is the smallest native route to implement it?
3. Which permissions, capabilities, account state, or extension boundaries matter?
4. What evidence is required before calling the feature ready?

These are route recipes, not replacements for the current SDK headers or Apple’s living documentation. Re-check the linked sources when the deployment target, device family, or selected SDK changes.

## Deep dives

- [SwiftData and local persistence](00-swiftdata-and-local-persistence.md)
- [CloudKit and sync](01-cloudkit-and-sync.md)
- [StoreKit and entitlements](02-storekit-and-entitlements.md)
- [App Intents, widgets, and Live Activities](03-app-intents-widgets-and-live-activities.md)
- [MapKit and location](04-mapkit-and-location.md)
- [VisionKit and reviewable capture](05-visionkit-and-reviewable-capture.md)
- [Cross-framework feature lifecycle](06-cross-framework-feature-lifecycle.md)
- [Swift Charts and data visualization](07-swift-charts-and-data-visualization.md)
- [SwiftUI ImageRenderer and user-approved export](08-swiftui-image-renderer-and-export.md)
- [PaperKit and structured markup](09-paperkit-and-structured-markup.md)
- [Interactive App Intent snippets](10-interactive-app-intent-snippets.md)
- [App Intents schema and entity interoperability](11-app-intents-schema-and-entity-interoperability.md)
- [App Intents, Visual Intelligence, and scene routing](14-app-intents-visual-intelligence-and-scene-routing.md)
- [App Intents semantic indexing, in-app search, onscreen context, and cross-device identity](15-app-intents-semantic-index-search-and-onscreen-context.md)
- [App Intents transfer, ownership, relevance, and execution contracts](16-app-intents-transfer-ownership-and-execution.md)
- [WidgetKit, ActivityKit, and control surfaces](17-widgetkit-activitykit-and-control-surfaces.md)
- [BackgroundTasks, continued processing, and process boundaries](18-backgroundtasks-and-continued-processing.md)
- [CloudKit, CKSyncEngine, and SwiftData synchronization](19-cloudkit-cksyncengine-and-swiftdata-sync.md)
- [URLSession, Network Framework, and streaming](20-urlsession-network-and-streaming.md)
- [CloudKit, CKSyncEngine, and SwiftData synchronization](12-cloudkit-syncengine-and-swiftdata.md)
- [MapKit for SwiftUI advanced composition and place exploration](13-mapkit-swiftui-advanced-composition.md)

## Route rule

Keep the capability boundary visible in the architecture. A SwiftData record is not automatically a CloudKit record, a StoreKit transaction is not itself an entitlement policy, a widget is not an always-running app process, and a camera recognition result is not user-confirmed domain data. Model those transitions explicitly.

For system surfaces, model the handoff as its own boundary: an App Intent is a system-facing use case, a widget is an archived/timeline-driven extension view, a Live Activity is a time-bounded ActivityKit state machine, and a control is a compact action/value provider. Each surface needs its own stale, unavailable, privacy, and device-proof path.

## Specialized route matrix

| Route | Concrete symbols and state to model | Evidence that is still required |
| --- | --- | --- |
| App Intents and system intelligence | `AppIntent`, `AppEntity`, `EntityQuery`, `AppShortcutsProvider`, parameter resolution, `perform()`, authorization, stale/deleted identifiers, and confirmation | Invoke from the app, Shortcuts, Siri/Apple Intelligence where supported, Spotlight, and a terminated process; verify localization, account scope, and mutation authorization. |
| Widget timelines and configuration | `TimelineEntry`, `Timeline`, `TimelineProvider`, `AppIntentTimelineProvider`, `AppIntentConfiguration`, `WidgetCenter`, placeholder/snapshot/timeline/reload state | Test every family, preview versus real data, stale/error/privacy states, deep links, extension termination, reload budgets, and signed system-surface behavior. |
| Controls and Live Activities | `ControlWidget`, `ControlWidgetButton`, `ControlWidgetToggle`, `ActivityAttributes`, `Activity`, `ActivityConfiguration`, ActivityKit push/update/end | Test locked-device and extension execution, idempotent actions, push token/server state, stale/end transitions, Dynamic Island/Lock Screen/paired surfaces, and target entitlements. |
| Accessibility and alternate input | semantic SwiftUI controls, `AccessibilityFocusState`, `DynamicTypeSize`, `accessibilityReduceMotion`, reduced transparency, VoiceOver/Voice Control/Switch Control, keyboard/controller paths | Use audits as diagnostics, then test complete tasks with actual assistive settings and physical devices; record known reading-order, focus, hit-region, and localization gaps. |
| Test and performance evidence | previews/fixtures, Swift Testing or XCTest, XCUIAutomation, `XCTClockMetric`, `XCTMemoryMetric`, `XCTHitchMetric`, `XCTOSSignpostMetric`, MetricKit/signposts | Separate deterministic regression metrics, real-device performance, aggregate production diagnostics, thermal/battery behavior, and release-build evidence. |

Do not turn a system invocation, timeline request, accessibility audit, performance baseline, or local fixture into proof that the app is available on every device, accessible to every person, delivered by the OS, or ready for App Store release.

## iOS 26 SDK, target, and runtime register

Use this register when choosing a deployment target. “Available in the SDK” is only the first gate; compiler availability, target membership, entitlement/usage configuration, account/service state, and hardware/system invocation remain separate checks.

| Route | Compile/deployment gate | Runtime/configuration gate | Proof that closes the route |
| --- | --- | --- | --- |
| SwiftData local persistence | `SwiftData` symbols and macros must be available for the selected deployment target; compile model/schema/migration fixtures in the app’s package/target | Container configuration, store location, schema migration, file protection, and process ownership | Relaunch, migration, save/error/delete, actor-isolated write, and physical-device interruption tests. |
| SwiftData automatic sync | Compatible SwiftData/CloudKit route must be available in the selected SDK and target | iCloud + Background Modes capabilities, container identifier, compatible schema, account state, environment/schema deployment | Signed entitlement inspection, development sync, two-device offline/conflict test, and production-schema record. |
| `CKSyncEngine` / CloudKit | CloudKit symbols and async delegate signatures must compile for the deployment target | Private/shared database choice, persisted engine state, record-zone mapping, account and push configuration | Process restart, account change, delayed/partial sync, conflict merge, deletion, and two-device proof. |
| App Intents and entities | Intent/entity/query declarations must compile in the owning app/extension target | Parameter resolution, localization, authorization, account scope, and process route | App, Shortcuts, Siri/system invocation, terminated-process behavior, and signed target proof. |
| WidgetKit and controls | Widget/ControlWidget APIs must compile in the extension target for each supported family/OS | Timeline/projection, extension resources, App Intents, reload policy, locked-device constraints | Placeholder/snapshot/timeline, interaction, refresh, privacy, family, and physical system-surface tests. |
| ActivityKit | `ActivityAttributes`/activity UI/push APIs must compile in the app + widget extension route | Live Activity capability, stale/end state, push token/server configuration, supported system surface | Local start/update/end, interruption/stale behavior, paired/Lock Screen/Dynamic Island route, and push delivery if used. |
| MapKit SwiftUI | `Map`/content/camera/selection/overlay APIs must compile for each destination and input family | Map content, camera bounds, MapReader conversion, map-feature selection, search/POI service state, optional location authorization, Look Around, directions, and cancellation/freshness | Fixed map without permission, camera/selection, search/POI, Look Around, directions, accessibility/input, network failure, and physical destination tests. |
| Core Location | `CLLocationManager` APIs compile for the selected platform | Usage descriptions, When In Use/Always choice, accuracy, background mode, services/account state | Allow/deny/reduced/full/no-fix/Settings changes, battery, background, and physical-device proof. |
| VisionKit live scanning | `DataScannerViewController` must compile and pass `isSupported`/`isAvailable` at runtime | Camera usage description, supported data types/languages, restriction/permission state | Physical scanner, poor lighting, language, interruption, stop/cancel, and review/fallback tests. |
| AVFoundation capture/audio | Capture/audio symbols compile in the app target and any UIKit bridge | Camera/microphone usage, session queue, audio category/route, background policy, hardware | Permission, interruption, route change, backpressure, export, thermal/memory, and physical-media tests. |
| Vision/Core ML | Request/model APIs, compiled model resources, and availability conditions compile | Model asset readiness, input/output schema, compute units, memory/thermal, privacy | Labeled fixtures, corrupt/unsupported input, latency/dropped frames, model revision, and representative hardware. |
| NFC / MusicKit / ShazamKit | Framework and target-specific APIs compile for the selected OS | NFC entitlement/reader config, music authorization/subscription/catalog, microphone permission/catalog state | Real tags/audio/account states, cancellation/no-match, physical device, and release entitlement proof. |

For every row, write the exact `@available` questions and target membership in the project plan. A compile-time availability branch can keep an older deployment target building, but it does not prove the newer branch was exercised on a device or system surface.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftData](https://developer.apple.com/documentation/swiftdata/)
- [CloudKit](https://developer.apple.com/documentation/cloudkit)
- [StoreKit](https://developer.apple.com/documentation/storekit)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [EntityQuery](https://developer.apple.com/documentation/appintents/entityquery)
- [AppShortcutsProvider](https://developer.apple.com/documentation/AppIntents/AppShortcutsProvider)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [TimelineProvider](https://developer.apple.com/documentation/widgetkit/timelineprovider)
- [AppIntentTimelineProvider](https://developer.apple.com/documentation/widgetkit/appintenttimelineprovider)
- [Keeping a widget up to date](https://developer.apple.com/documentation/widgetkit/keeping-a-widget-up-to-date)
- [ControlWidget](https://developer.apple.com/documentation/swiftui/controlwidget)
- [ControlWidgetButton](https://developer.apple.com/documentation/widgetkit/controlwidgetbutton)
- [ControlWidgetToggle](https://developer.apple.com/documentation/widgetkit/controlwidgettoggle)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [ActivityAttributes](https://developer.apple.com/documentation/activitykit/activityattributes)
- [ActivityConfiguration](https://developer.apple.com/documentation/widgetkit/activityconfiguration)
- [Displaying live data with Live Activities](https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [AccessibilityFocusState](https://developer.apple.com/documentation/swiftui/accessibilityfocusstate)
- [DynamicTypeSize](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [Performing accessibility testing for your app](https://developer.apple.com/documentation/accessibility/performing-accessibility-testing-for-your-app)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Performance Tests](https://developer.apple.com/documentation/xctest/performance-tests)
- [XCTHitchMetric](https://developer.apple.com/documentation/xctest/xcthitchmetric)
- [MetricKit](https://developer.apple.com/documentation/metrickit)
- [Monitoring app performance with MetricKit](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [MapKit](https://developer.apple.com/documentation/mapkit)
- [VisionKit](https://developer.apple.com/documentation/visionkit)
