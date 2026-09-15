# iOS 27 SwiftUI refresh reference

Use this reference when a source-refresh task touches the iOS 27 SDK, SwiftUI
toolbar/document/collection behavior, MetricKit, or the interaction between
iOS 27 APIs and the iOS 26 Liquid Glass baseline.

## Evidence status

- Official source review date: **2026-09-14**.
- Apple’s current documentation describes Xcode 27 with Swift 6.4 and the
  iOS/iPadOS 27 SDKs.
- The current `xcode-select` exposes Xcode 27.0, the iOS 27.0 SDK, and Swift
  6.4. Xcode 26.4 with the iOS 26.4 SDK and Swift 6.3 remains an explicit
  earlier-toolchain fallback. The targeted API probe was type-checked with
  the selected Xcode 27 toolchain; it is symbol-level evidence, not an
  app-target or runtime proof. Local installation paths are intentionally
  omitted from the portable record.
- The available local simulator runtime is iOS 26.4. No iOS 27 simulator or
  physical-device run is claimed by this refresh.
- Beta-marked SwiftUI declarations and release-note migration details remain
  target-sensitive until the selected final Xcode 27 SDK is type-checked.

## Affected route matrix

| Route | iOS 27 source signal | Fallback and proof boundary |
| --- | --- | --- |
| Toolbar | `visibilityPriority`, `ToolbarOverflowMenu`, `topBarPinnedTrailing`, `toolbarMinimizationBehavior`, and status-bar toolbar color scheme | Standard toolbar items and automatic system overflow on earlier lanes; compact-width, search, Dynamic Type, accessibility, and physical/system proof remain separate. |
| Documents | `Document`, `ReadableDocument`, `WritableDocument`, `URLDocumentConfiguration`, asynchronous reader/writer work, and new `DocumentGroup` routes | `FileDocument`/`ReferenceFileDocument` compatibility route; local I/O does not prove provider sync, conflict, autosave, or multi-window behavior. |
| Collections and rows | `reorderContainer`, `reorderable`, `ReorderDifference`, and `swipeActionsContainer` | `List` editing/reordering or visible actions; validate stable IDs, domain mutation, cancellation, and accessibility. |
| Images/text/state | HTTP-aware `AsyncImage` caching and custom session/URLRequest support; interactive `textSelection`; macro-backed `@State` behavior | Feature-owned loader/legacy text selection/explicit state ownership; do not rely on initializer side effects or equate caching with persistence. |
| Performance | `MetricManager.metricReports` and `.diagnosticReports` async sequences replace the recommended new-adoption path for `MXMetricManager` | Legacy subscriber route for earlier deployment lanes; simulated MetricKit payloads are fixtures, not physical/system delivery. |
| Liquid Glass | System surfaces and custom `Glass`/`glassEffect`/`GlassEffectContainer` remain the iOS 26+ design baseline | Remove custom bars/backgrounds where the system owns the surface; preserve regular/clear/no-effect and reduced-effects behavior. |

## Operational rule

Link the affected knowledge-base route and the official Apple page next to the
claim. Use `if #available(iOS 27, *)` or an equivalent target gate only after
the selected SDK signature is verified. Keep source-level sketches labeled as
sketches, and never turn this reference into app-target build, device, archive,
TestFlight, App Store, or production evidence.

## Official sources

- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
- [What’s new in SwiftUI](https://developer.apple.com/swiftui/whats-new/)
- [Document](https://developer.apple.com/documentation/swiftui/document)
- [ToolbarOverflowMenu](https://developer.apple.com/documentation/swiftui/toolbaroverflowmenu)
- [toolbarMinimizationBehavior(_:for:)](https://developer.apple.com/documentation/swiftui/view/toolbarminimizationbehavior%28_%3Afor%3A%29)
- [MetricManager](https://developer.apple.com/documentation/metrickit/metricmanager)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
