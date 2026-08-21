# Package modules and Apple-native design architecture

## Design objective

A reusable package should make a native screen easier to build and verify without
turning the app into a generic visual kit. Keep product meaning, platform behavior,
design composition, and device intelligence in distinct modules that can be
reviewed independently.

A useful design graph is:

    Domain and feature state
      -> semantic design tokens/components
      -> app-owned SwiftUI screen
      -> system-owned surface or navigation
      -> physical device proof

The package supplies reusable building blocks. The app target chooses the
destination, authorization, system surface, and product voice.

## Module map

| Module | Owns | Avoids |
| --- | --- | --- |
| ProductDomain | IDs, value types, reducers, policies, authorization decisions | SwiftUI/UIKit, Foundation Models sessions, system permissions |
| ProductFeature | feature state, use cases, typed capability protocols | View-specific layout or target-only entitlements |
| ProductDesign | tokens, semantic components, previews, accessibility labels | Database mutations, raw URLs, network calls, hidden side effects |
| ProductAIAdapter | model availability, prompt/session adapter, typed proposals, evaluation seams | Direct navigation, payment/health/match mutations |
| ProductPlatform | Core Location, AVFoundation, Vision, HealthKit, StoreKit, or other adapters | Assuming every target/platform has the same framework |
| ProductSystemSurface | widget/control/Live Activity/App Intent projections | Treating extension process state as the app’s live model |
| ProductFixtures | deterministic data, accessibility states, AI proposal fixtures | Shipping test-only frameworks or private customer data |

Use package products to expose only the modules that a consuming target needs.
A widget may need ProductDomain and a small projection module, but not the
entire ProductDesign or ProductAIAdapter. A macro implementation target should
not be linked into the app as if it were runtime code.

## Liquid Glass as a surface contract

Liquid Glass is a functional material and hierarchy, not a package-wide background.
Place it at the surface that owns the related controls:

    app content
      -> navigation/toolbar
      -> compact functional glass group
      -> explicit action/review

A design package should provide semantic components such as:

- NativeActionGroup for related actions;
- StatusCapsule for loading/offline/verified/stale states;
- ReviewSheetActions for approve/edit/reject/retry;
- AdaptiveToolbarContent for navigation and context;
- AccessibleEmptyState and RecoveryState.

The component should choose a documented native material only where the selected
deployment target supports it. Provide a standard semantic fallback for reduced
transparency, increased contrast, older deployment targets, and system surfaces
that apply their own rendering rules.

Do not export a View called UniversalGlassBackground and apply it to every screen.
That pattern hides hierarchy, makes accessibility harder, and can fight the system’s
own Liquid Glass treatment.

## State belongs outside the component

A package component should receive state and emit typed intents:

~~~swift
struct ReviewState: Equatable, Sendable {
    let title: String
    let detail: String
    let status: Status
    let canApprove: Bool
    let canRetry: Bool
}

enum ReviewIntent: Sendable {
    case approve
    case edit
    case reject
    case retry
}

struct ReviewSurface: View {
    let state: ReviewState
    let send: (ReviewIntent) -> Void

    var body: some View {
        VStack(alignment: .leading) {
            Text(state.title)
            Text(state.detail)
            HStack {
                if state.canApprove {
                    Button("Approve") { send(.approve) }
                }
                if state.canRetry {
                    Button("Retry") { send(.retry) }
                }
            }
        }
        .glassEffect()
    }
}
~~~

The exact Liquid Glass API and availability must be compiled against the selected
SDK. The important boundary is that the component emits an intent; it does not
save a record, call a model, or open a system URL.

If the app target supports a different Liquid Glass API set than the package
deployment target, use a target-specific component or availability wrapper. Do not
make the package’s public API require a newer iOS version than the consuming
targets can support without documenting that product decision.

## On-device AI as a package contract

Keep model work behind a protocol that the app can replace with a deterministic
fixture:

~~~swift
struct ReviewInput: Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let visibleText: String
    let privacyScope: PrivacyScope
}

struct ReviewProposal: Sendable {
    let sourceID: UUID
    let sourceRevision: Int
    let summary: String
    let suggestedIntent: ReviewIntent?
    let modelRoute: String
}

protocol ReviewIntelligence: Sendable {
    func propose(for input: ReviewInput) async throws -> ReviewProposal
}
~~~

The UI package renders loading, ready, unavailable, stale, and rejected states.
The AI adapter owns Foundation Models/Core ML/Vision/Speech/Translation
availability and cancellation. The domain owns validation and the app owns review
and commit.

This allows:

    real device model
      -> proposal
      -> deterministic validator
      -> human review
      -> domain command

A preview fixture can demonstrate the design, but it must not imply model
availability, model quality, or a physical-device inference result.

## Package resource design

Keep resources close to the module that owns them:

| Resource | Package owner | Review |
| --- | --- | --- |
| Color/typography tokens | Design module | Contrast, Dynamic Type, localization |
| Localized labels | Design/feature module | Pluralization, RTL, VoiceOver |
| Symbols/image assets | Design module or app target | Rendering mode, tinted/clear surfaces, licensing |
| Widget snapshots | System-surface fixture target | Privacy/redaction and extension size |
| Model/evaluation fixture | AI adapter or test target | Do not ship test data or prompts |
| App icon/launch assets | App target | App Store/release target membership |
| Privacy manifest | Owning target/package resource | Required-reason API declarations and archive inspection |

Use Bundle.module in package code and make resource loading failure a visible
state. A missing resource should not silently fall back to private system content
or a random image.

## Cross-platform and extension design

Let package products express the stable domain contract. Let target-specific
products express platform composition:

    SharedDomain
      -> iOSDesign
      -> iOSApp

    SharedDomain
      -> WidgetProjection
      -> WidgetExtension

    SharedDomain
      -> watchOSDesign
      -> WatchApp

    SharedDomain
      -> visionOSDesign
      -> VisionApp

A package that imports SwiftUI can still be multiplatform, but every symbol,
resource, and component must be tested against each declared platform. A package
that imports an iOS-only framework should not be linked into a watch or macOS
target merely because the source folder is shared.

For extensions:

- keep the projection small and versioned;
- avoid assuming the app process is alive;
- do not share a live ObservableObject across processes;
- keep app-group files atomic and redacted;
- keep target-specific entitlements in target-specific products;
- make the extension’s UI and action budget explicit;
- route back to the main app through typed App Intent/URL/activity contracts.

## Macro and plugin design as visible tooling

Macros and plugins can reduce repetition in an iOS design system, but the
generated result should remain reviewable:

- a macro may generate a typed token or accessibility metadata declaration;
- a build plugin may generate asset catalogs, localized key tables, or typed
  fixture code;
- a command plugin may format or document a package;
- none should silently call a network service, read a user’s private data, or
  decide production authorization;
- generated public API needs a diff and compatibility review;
- plugin output needs declared inputs/outputs and a deterministic work directory;
- macro implementation and plugin executables are build-time tooling, not app
  runtime modules.

For accessibility, generated labels must be reviewed in VoiceOver and Dynamic
Type contexts. Generated Liquid Glass modifiers must not bypass standard control
semantics.

## Navigation and system-surface ownership

The package component should not own the app’s navigation destination. Accept a
typed intent or callback and let the app coordinate:

    package surface
      -> typed intent
      -> app route coordinator
      -> NavigationStack/sheet/system controller
      -> domain validation
      -> committed projection

This matters for Universal Links, App Intents, widgets, Game Center, StoreKit,
HealthKit, and system composers. The package can render a Review button; only the
app/domain layer can decide whether the current account may proceed.

## Design review matrix

| Review question | Healthy package answer | Failure signal |
| --- | --- | --- |
| Does the module have one reason to change? | Domain, design, AI, and system targets are separate where their lifecycles differ | One “Shared” target imports every framework |
| Is Liquid Glass functional? | Material groups a small semantic action set | Every view receives a translucent background |
| Is AI reviewable? | Proposal has source/revision and requires app/domain validation | AI call is hidden in a View initializer |
| Does the extension survive termination? | It reads a versioned projection or uses an explicit system input | It reaches into the app’s live singleton |
| Are platform differences visible? | Package products/conditions and target compositions state them | Scattered availability branches with no ownership |
| Are resources secure? | Bundle ownership, localization, privacy, and release membership are explicit | Main bundle assumptions or copied resources |
| Are generated APIs reviewable? | Macro/plugin outputs are fixture-tested and diff-reviewed | Build success is treated as generated-code correctness |
| Is accessibility native? | Controls are semantic; labels/focus/reduced-effects are tested | Glass/animation substitutes for semantics |

## A native screen package checklist

- [ ] Domain values are independent of SwiftUI/UIKit.
- [ ] Design components accept state and emit typed intents.
- [ ] Liquid Glass is scoped to functional groups.
- [ ] Standard system controls remain the default.
- [ ] Dynamic Type, contrast, reduced transparency, and Reduce Motion have
      documented behavior.
- [ ] AI adapters expose availability, cancellation, proposal, and error states.
- [ ] Source revision and privacy scope accompany proposals.
- [ ] Widgets/extensions receive redacted projections, not live domain contexts.
- [ ] Navigation and system handoff remain app-owned.
- [ ] Resources use Bundle.module and are target-verified.
- [ ] Macros/plugins generate visible, testable code only.
- [ ] Package products and target platform declarations match consuming targets.

## Sources

- [Swift packages](https://developer.apple.com/documentation/xcode/swift-packages)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [Creating a standalone Swift package with Xcode](https://developer.apple.com/documentation/xcode/creating-a-standalone-swift-package-with-xcode)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [Package](https://docs.swift.org/swiftpm/documentation/packagedescription/package/)
- [Introducing Packages](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/introducingpackages/)
- [Macros](https://docs.swift.org/swift-book/documentation/the-swift-programming-language/macros/)
- [PackagePlugin](https://docs.swift.org/swiftpm/documentation/packageplugin/)
- [Plugins](https://docs.swift.org/swiftpm/documentation/packagemanagerdocs/plugins/)
- [Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/liquid-glass)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing system accessibility features in your app](https://developer.apple.com/documentation/accessibility/testing-system-accessibility-features-in-your-app)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
