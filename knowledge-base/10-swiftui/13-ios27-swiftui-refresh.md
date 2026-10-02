# iOS 27 SwiftUI and SDK refresh

This route records current iOS 27 SwiftUI and SDK guidance for the Apple skill
bundle. It includes a targeted API type-check against the locally installed
Xcode 27.0 SDK and newer beta-only source references; it is not a claim that
the newer beta APIs compile here, that this workspace is an iOS app target, or
that a physical iOS 27 device/runtime was exercised.

Reviewed **2026-10-01** against [Apple's Xcode SDK/system requirements](https://developer.apple.com/xcode/system-requirements),
[Xcode 27.2 beta release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes),
[iOS and iPadOS 27.2 beta release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27_2-release-notes),
the [SwiftUI updates](https://developer.apple.com/documentation/updates/swiftui),
and [What’s new in SwiftUI](https://developer.apple.com/swiftui/whats-new/).
Apple currently lists Xcode 27.2 beta 2 with the iOS 27.2 SDK and Swift 6.4
as its newest prerelease lane. The locally selected toolchain is still Xcode
27.0 with the iOS 27.0 SDK and Swift 6.4. Xcode 26.6 with the iOS 26.5 SDK and
Swift 6.3 is the latest documented earlier-version lane. The API probe below
was type-checked with the selected Xcode 27.0 toolchain; it does not verify
the newer beta APIs. Local installation paths are intentionally not part of
the portable repository record.

## Version lanes

Keep these facts separate in every route:

| Lane | Current source-grounded claim | Implementation boundary | Earlier fallback |
| --- | --- | --- | --- |
| Xcode and Swift | As checked 2026-10-01, Apple lists Xcode 27.2 beta 2 with iOS 27.2 and Swift 6.4; the local Xcode 27.0/iOS 27.0/Swift 6.4 lane is a separate observation. | Record Xcode, Swift, SDK, deployment target, target platform, and prerelease status before using a declaration. Do not infer beta API availability from the locally selected SDK. | Use the Xcode 26.6/iOS 26.5/Swift 6.3 lane where the target has not adopted the iOS 27 SDK, and preserve existing APIs. |
| Liquid Glass | Standard SwiftUI/UIKit system surfaces adopt the current treatment on iOS 26 and later. | Let navigation, tab, toolbar, search, sheet, and controls own their system appearance; use custom glass only for a small functional group. | Preserve the iOS 26 system-first route and a legible non-glass fallback. |
| iOS 27 SwiftUI | The established APIs below are documented for iOS 27 or require iOS 27 SDK build behavior. September 2026 `ArrangementView` and reserved-region APIs are explicitly beta-marked. | Gate source and runtime behavior with the selected target; type-check beta APIs only with the matching beta SDK and recheck final names and behavior before adoption. | Use standard adaptive containers, safe areas, legacy document protocols, `List`, or the existing loader/gesture route. |
| MetricKit | `MetricManager` delivers typed metric and diagnostic async sequences on iOS 27. | Hold one long-lived manager and distinguish simulated payloads from reports delivered by a physical system. | Use the legacy `MXMetricManager` subscriber route for older deployment lanes, with the same evidence limits. |

## New SwiftUI API lanes

### Toolbar composition and minimization

The iOS 27 SwiftUI documentation adds explicit control over toolbar overflow
and scrolling behavior. Prefer semantic priorities and the system overflow
menu over a hand-built “more” button:

```swift
ContentView()
    .toolbar {
        ToolbarItem {
            SecondaryAction()
        }
        .visibilityPriority(.low)

        ToolbarItem(placement: .topBarPinnedTrailing) {
            PrimaryAction()
        }

        ToolbarOverflowMenu {
            Button("Additional action") {
                performAdditionalAction()
            }
        }
    }
    .toolbarMinimizationBehavior(.onScrollDown, for: .navigationBar)
```

Use `.toolbarColorScheme(_, for: .statusBar)` only when the selected iOS 27
route needs a status-bar scheme coordinated with the bar. Keep the content
readable when the bar minimizes, and test compact width, search activation,
Dynamic Type, localization, VoiceOver, and reduced-effects settings. The
current Apple spelling is `toolbarMinimizationBehavior`; older beta material
used `toolbarMinimizeBehavior`, which must not be copied into new guidance.

Official routes: [`visibilityPriority(_:)`](https://developer.apple.com/documentation/swiftui/toolbarcontent/visibilitypriority%28_%3A%29),
[`ToolbarOverflowMenu`](https://developer.apple.com/documentation/swiftui/toolbaroverflowmenu),
[`topBarPinnedTrailing`](https://developer.apple.com/documentation/swiftui/toolbaritemplacement/topbarpinnedtrailing),
[`toolbarMinimizationBehavior(_:for:)`](https://developer.apple.com/documentation/swiftui/view/toolbarminimizationbehavior%28_%3Afor%3A%29),
and [`toolbarColorScheme(_:for:)`](https://developer.apple.com/documentation/swiftui/view/toolbarcolorscheme%28_%3Afor%3A%29).

### Documents and file coordination

For new iOS 27 document apps, evaluate `Document` when the model both reads
and writes, or use `ReadableDocument`/`WritableDocument` independently. The
route is designed for asynchronous, incremental disk work and integrates with
`DocumentGroup`, `URLDocumentConfiguration`, observation, progress, undo, and
file coordination. Snapshot model state on the main actor and keep the reader
or writer’s file work off the main actor according to the final SDK’s
concurrency annotations.

```swift
@Observable
final class TextDocument: Document {
    static let readableContentTypes = [UTType.plainText]

    var text = ""

    // Implement reader, writer, snapshot, and apply using the
    // ReadableDocument/WritableDocument contract from the selected SDK.
}
```

Apple’s iOS 27 release notes say new applications should prefer these
protocols; `FileDocument` and `ReferenceFileDocument` remain the compatibility
route for an iOS 26 deployment or an existing project until its migration is
type-checked. Do not call a local byte round trip proof of provider sync,
conflict resolution, autosave, or multi-window behavior.

Official routes: [`Document`](https://developer.apple.com/documentation/swiftui/document),
[`ReadableDocument`](https://developer.apple.com/documentation/swiftui/readabledocument),
[`WritableDocument`](https://developer.apple.com/documentation/swiftui/writabledocument),
[`DocumentGroup`](https://developer.apple.com/documentation/swiftui/documentgroup),
and [SwiftUI document apps](https://developer.apple.com/documentation/swiftui/document-based-apps).

### Reordering and swipe actions in custom containers

Use the iOS 27 reorder container APIs when a product needs drag reordering in
a `List`, `LazyVGrid`, `LazyVStack`, or another supported layout. Keep stable,
`Sendable` identifiers and apply the returned `ReorderDifference` to domain
state only after the feature validates the change:

```swift
VStack {
    ForEach(items) { item in
        ItemRow(item)
    }
    .reorderable()
}
.reorderContainer(for: Item.self) { difference in
    apply(difference)
}
```

For custom row layouts, apply `.swipeActionsContainer()` to the containing
`ScrollView` or equivalent. `List` already coordinates dismissal and mutual
exclusion, so applying the modifier there is a no-op. Keep a visible action
for important or destructive work; a swipe gesture is never the only route.

Official routes: [`reorderContainer(for:isEnabled:move:)`](https://developer.apple.com/documentation/swiftui/view/reordercontainer%28for%3Aisenabled%3Amove%3A%29),
[`reorderable()`](https://developer.apple.com/documentation/swiftui/dynamicviewcontent/reorderable%28%29),
and [`swipeActionsContainer()`](https://developer.apple.com/documentation/swiftui/view/swipeactionscontainer%28%29).

### Images, text selection, and state behavior

- In iOS 27, `AsyncImage` uses standard HTTP caching behavior and supports
  `URLRequest` initializers plus `asyncImageURLSession(_:)` for a custom
  `URLSession`. Preserve loading, failure, cancellation, privacy, and
  downsampling boundaries; caching does not make remote content domain truth.
- `.textSelection(.enabled)` remains the source-compatible modifier, but apps
  built with the iOS 27 SDK receive the newer interactive text-selection UI on
  iOS 27. If a custom gesture competes with selection, test whether
  `.highPriorityGesture()` is appropriate.
- The iOS 27 `@State` implementation is macro-backed and avoids repeatedly
  initializing class state during view re-instantiation; Apple documents the
  behavior as back-deploying to aligned iOS 17 and later runtimes. Do not put
  required side effects in a `@State` initializer, and re-check source
  compatibility for unusual property-wrapper patterns.
- Xcode 27 also improves `ViewBuilder` type-checking and exposes
  `ContentBuilder`; treat this as a compiler/source-compatibility improvement,
  not as permission to make a view own domain state or side effects.

Official routes: [`AsyncImage`](https://developer.apple.com/documentation/swiftui/asyncimage),
[`asyncImageURLSession(_:)`](https://developer.apple.com/documentation/swiftui/view/asyncimageurlsession%28_%3A%29),
[`textSelection(_:)`](https://developer.apple.com/documentation/swiftui/view/textselection%28_%3A%29),
and the [SwiftUI 2027 performance and data-flow notes](https://developer.apple.com/swiftui/whats-new/).

### Adaptive arrangements (Beta)

The September 2026 SwiftUI updates introduce `ArrangementView` for primary
and secondary content that adapts to the available environment. The built-in
split style places the views side by side; the overlay style layers them and
can transition to a split layout. Use these APIs as beta-only routes until
the selected final SDK documents them as stable and the target's device and
OS support are confirmed. They complement established navigation and layout
containers; they do not replace product-specific navigation, safe areas, or
accessibility review.

```swift
ArrangementView {
    PrimaryContent()
} secondary: {
    SecondaryContent()
}
.arrangementViewStyle(.split.axes(.horizontal))
```

Official routes: [SwiftUI updates](https://developer.apple.com/documentation/updates/swiftui),
[`ArrangementView` styles](https://developer.apple.com/documentation/swiftui/view/arrangementviewstyle%28_%3A%29),
and [adaptive layouts on iPhone Duo](https://developer.apple.com/videos/play/tech-talks/111463/).

### Hardware-reserved regions (Beta)

SwiftUI's beta `GeometryProxy.reservedRegions` route and UIKit's
`UIView.ReservedRegion` describe areas another entity occupies, including
occlusion and division regions such as a camera or hinge. Use these APIs only
when the selected SDK and target expose them, keep the normal safe-area and
single-screen routes working, and test the actual form factor before changing
content placement. Source documentation alone does not prove that a target
device reports a particular reserved region.

Official routes: [SwiftUI GeometryProxy](https://developer.apple.com/documentation/swiftui/geometryproxy),
[`UIView.ReservedRegion`](https://developer.apple.com/documentation/uikit/uiview/reservedregion),
and [`UIView.reservedRegions(kind:options:)`](https://developer.apple.com/documentation/uikit/uiview/reservedregions%28kind%3Aoptions%3A%29).

## MetricKit performance lane

On iOS 27, `MetricManager` is an instantiable, `Sendable` object with
`metricReports` and `diagnosticReports` async sequences. Keep one long-lived
instance per report domain and consume the sequences in bounded tasks:

```swift
let manager = MetricManager()

Task {
    for await report in manager.metricReports {
        process(report)
    }
}
```

The original `MXMetricManager` subscriber APIs are no longer recommended for
new adoption in the iOS 27 release notes, but remain the older deployment
fallback. MetricKit reports are system-delivered evidence, not an immediate
per-interaction logger; Xcode’s simulated payloads are useful fixtures, while
real delivery requires a supported physical device and system conditions.

Official routes: [`MetricManager`](https://developer.apple.com/documentation/metrickit/metricmanager),
[`MetricReport`](https://developer.apple.com/documentation/metrickit/metricreport),
[`DiagnosticReport`](https://developer.apple.com/documentation/metrickit/diagnosticreport),
and [MetricKit updates](https://developer.apple.com/documentation/updates/metrickit).

## Liquid Glass overlay

Liquid Glass is a system-first iOS 26+ route, not an iOS 27 replacement for
content hierarchy. Standard navigation, tab, toolbar, search, sheet, and
control surfaces should own their treatment. For custom functional groups,
use the documented `Glass`/`glassEffect`/`GlassEffectContainer` route and
choose `regular`, `clear`, or an identity/no-effect fallback according to
legibility and content. Keep custom glass away from dense content unless it
has a real interaction role.

Recheck [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass),
[Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views),
the [Materials HIG](https://developer.apple.com/design/human-interface-guidelines/materials),
and the [Accessibility HIG](https://developer.apple.com/design/human-interface-guidelines/accessibility)
for every target. Test light/dark appearance, contrast, Dynamic Type,
localization, VoiceOver, reduced transparency, reduced motion, and scrolling
content behind the functional layer. The iOS 27 toolbar APIs above should
cooperate with system glass rather than prompt a custom replacement bar.

## Verification contract

For each iOS 27 route, record:

1. the exact API and official URL;
2. minimum OS, SDK, platform, and target/deployment assumptions;
3. the iOS 26 or earlier fallback;
4. beta/deprecation or final-name uncertainty;
5. source, SDK, compile, fixture, simulator, physical/system, signed, and
   release evidence separately.

The current workspace can validate Markdown, links, source-registry wiring,
portable package sources, and the previously recorded iOS 27 API probe. The
selected local toolchain is Xcode 27.0 / iOS 27.0 SDK / Swift 6.4; the latest
27.2 beta references above were source-reviewed but not type-checked here.
`xcrun simctl list runtimes` returned no installed runtimes on 2026-10-01.
This refresh did not exercise an app target, simulator, physical device,
archive, TestFlight, App Store, or production behavior.

### Targeted SDK probe

The following declarations were type-checked with Xcode 27.0 / iOS 27.0 SDK
for `arm64-apple-ios27.0`: `reorderable`, `reorderContainer`,
`swipeActionsContainer`, `visibilityPriority`, `topBarPinnedTrailing`,
`ToolbarOverflowMenu`, `toolbarMinimizationBehavior`, `toolbarColorScheme`
with `.statusBar`, `asyncImageURLSession`, `AsyncImage(request:)`,
`textSelection`, `MetricManager.metricReports`, and the SwiftUI `Document`
protocol reference. This is symbol-level compile evidence only; it does not
prove an app target’s configuration or runtime behavior.

## Sources

- [Xcode SDK and system requirements](https://developer.apple.com/xcode/system-requirements)
- [Xcode 27 release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes)
- [Xcode 27.2 beta release notes](https://developer.apple.com/documentation/xcode-release-notes/xcode-27_2-release-notes)
- [iOS and iPadOS 27 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27-release-notes)
- [iOS and iPadOS 27.2 beta release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-27_2-release-notes)
- [SwiftUI updates](https://developer.apple.com/documentation/updates/swiftui)
- [What’s new in SwiftUI](https://developer.apple.com/swiftui/whats-new/)
- [ArrangementView styles](https://developer.apple.com/documentation/swiftui/view/arrangementviewstyle%28_%3A%29)
- [SwiftUI GeometryProxy](https://developer.apple.com/documentation/swiftui/geometryproxy)
- [UIKit UIView.ReservedRegion](https://developer.apple.com/documentation/uikit/uiview/reservedregion)
- [AppTrackingTransparency](https://developer.apple.com/documentation/apptrackingtransparency)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/liquid-glass)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
