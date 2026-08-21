# TipKit contextual discovery route recipes

These snippets are reusable route sketches, not compile proof. TipKit macros, protocol signatures, availability, and SwiftUI/UIKit presentation APIs must be compiled in a named target. Verify persistence, localization, accessibility, App Group/CloudKit configuration, and physical behavior separately.

## 1. Define a concise feature tip

```swift
import SwiftUI
import TipKit

struct AdvancedFilterTip: Tip {
    var title: Text {
        Text("Pin a filter")
    }

    var message: Text? {
        Text("Keep this filter at the top of your list.")
    }

    var image: Image? {
        Image(systemName: "pin")
    }

    var actions: [Tips.Action] {
        [
            Tips.Action(id: "try-filter", title: "Try it") {
                // Route sketch: focus the existing filter control or open a
                // safe example state. Do not commit a hidden side effect.
            }
        ]
    }

    var rules: [Rule] {
        // Route sketch: add a #Rule macro after confirming the selected SDK.
        []
    }

    var options: [any TipOption] {
        [MaxDisplayCount(3)]
    }
}
```

Keep copy short and action-oriented. Do not use generated marketing language or make the tip the only way to reach the feature.

## 2. Configure TipKit during app initialization

```swift
@main
struct ExampleApp: App {
    init() {
        do {
            #if DEBUG
            // Route sketch: reset only in a dedicated first-launch/test build.
            // try Tips.resetDatastore()
            #endif

            try Tips.configure([
                .displayFrequency(.daily)
            ])
        } catch {
            // Record diagnostics. The app and feature remain usable without tips.
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

`Tips.resetDatastore()` must run before configuration and should never execute as ordinary production startup logic. A custom datastore or CloudKit option requires its own target/entitlement/account proof.

## 3. Use a persistent parameter for feature state

```swift
enum FilterDiscoveryState {
    @Parameter
    static var hasUsedPinnedFilters = false
}

struct PinnedFiltersTip: Tip {
    var title: Text { Text("Pin a filter") }
    var message: Text? { Text("Keep a useful filter close at hand.") }

    var rules: [Rule] {
        #Rule(FilterDiscoveryState.$hasUsedPinnedFilters) {
            $0 == false
        }
    }
}
```

This syntax is an SDK-sensitive macro route. The semantic contract is that the parameter changes when app-owned feature truth changes, not when the tip appears. Use `ParameterOption.transient` only when a reset-on-first-reference policy is intentional.

## 4. Donate a bounded event after completion

```swift
struct EditorDiscoveryTip: Tip {
    static let didOpenAdvancedEditor = Tips.Event(id: "opened-advanced-editor")

    var title: Text { Text("Try the advanced editor") }

    var rules: [Rule] {
        #Rule(Self.didOpenAdvancedEditor) {
            $0.donations.count >= 2
        }
    }
}

func recordAdvancedEditorCompleted() {
    Task {
        // Call this only after the app-owned workflow reaches its chosen
        // completion boundary.
        await EditorDiscoveryTip.didOpenAdvancedEditor.donate()
    }
}
```

If event donations carry values, use bounded Codable/Sendable values such as an enum or coarse mode. Do not donate raw text, locations, health details, embeddings, or model transcripts as a convenience.

## 5. Present an inline tip or popover

```swift
struct FilterToolbar: View {
    private let tip = PinnedFiltersTip()

    var body: some View {
        HStack {
            Button("Filters", systemImage: "line.3.horizontal.decrease") {
                // Open the real filter control.
            }
            .popoverTip(tip, arrowEdge: .bottom)

            // Route alternative:
            // TipView(tip, arrowEdge: .bottom)
        }
    }
}
```

Place the tip near the control it describes. Keep standard button semantics, labels, focus, and Dynamic Type behavior. A custom glass style must preserve the TipKit action/dismissal contract.

## 6. Sequence a small group of tips

```swift
struct WorkspaceDiscovery: View {
    @State private var tips = TipGroup(.ordered) {
        PinnedFiltersTip()
        EditorDiscoveryTip()
    }

    var body: some View {
        VStack {
            // Route sketch: cast or otherwise present the current tip in the
            // target SDK’s supported TipView/popover form.
            Text("Workspace")
        }
        .task {
            for await current in tips.currentTipUpdates {
                // Update a view projection; do not mutate domain truth here.
                _ = current
            }
        }
    }
}
```

Use `.firstAvailable` when the next relevant tip depends on current feature state. Keep groups small and provide a Help destination for people who dismiss the sequence.

## 7. Observe tip status for a UIKit container

```swift
final class FeatureViewController: UIViewController {
    private let featureTip = AdvancedFilterTip()
    private var observationTask: Task<Void, Never>?
    private weak var tipView: TipUIView?

    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)

        observationTask = Task { @MainActor [weak self] in
            guard let self else { return }

            for await shouldDisplay in featureTip.shouldDisplayUpdates {
                if shouldDisplay {
                    // Route sketch: construct TipUIView with the current SDK
                    // initializer, constrain it near the relevant control,
                    // and preserve removal/dismissal semantics.
                } else {
                    tipView?.removeFromSuperview()
                    tipView = nil
                }
            }
        }
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        observationTask?.cancel()
        observationTask = nil
    }
}
```

Cancel observation tasks with the view lifecycle. Do not leave a UIKit tip view attached after its feature becomes unavailable.

## 8. Separate AI proposal from TipKit eligibility

```swift
struct TipExplanationProposal: Sendable {
    let featureID: String
    let sourceState: String
    let explanation: String
    let modelVersion: String
    let requiresReview: Bool
}

actor FeatureDiscoveryAdvisor {
    func proposeExplanation(for feature: FeatureState) async -> TipExplanationProposal? {
        // Route sketch: local model may suggest an explanation for a review
        // surface. Do not modify TipKit parameters or display a tip here.
        nil
    }
}
```

TipKit eligibility should remain deterministic and product-owned. A model can help author or explain a feature, but the shipped tip copy, rule, localization, and action need review. An AI proposal is not an authorization or a completed action.

## 9. Test with TipKit controls

```swift
enum TipTestMode {
    case showAll
    case hideAll
    case showSelected
}

func configureTipTestMode(_ mode: TipTestMode) throws {
    // Route sketch: call showAllTipsForTesting(), hideAllTipsForTesting(),
    // showTipsForTesting(_:), or hideTipsForTesting(_:) in a test-only
    // harness after reset/configuration rules are satisfied.
}
```

Pair forced-display tests with rule-driven tests. Forced display proves layout and actions; it does not prove eligibility or respectful frequency.

## 10. Deterministic feature-completion test

```swift
struct TipFixture {
    let initialFeatureState: Bool
    let expectedEligibility: Bool
    let actionCompletesFeature: Bool
}

@Test
func tipEligibilityFollowsFeatureTruth() async throws {
    let fixture = TipFixture(
        initialFeatureState: false,
        expectedEligibility: true,
        actionCompletesFeature: true
    )

    // Route sketch:
    // 1. Reset/configure TipKit in the test harness.
    // 2. Assert the tip is eligible from the initial state.
    // 3. Perform the real feature action.
    // 4. Update the app-owned parameter/event.
    // 5. Assert status becomes pending/invalidated according to the rule.
    _ = fixture
}
```

Do not assert completion from the tip’s dismissal callback alone. Assert the real feature state and then the TipKit projection.

## Verification boundary

Before treating a recipe as implemented, prove target compilation, TipKit configuration/error handling, rule transitions, persistent/restart state, group/frequency behavior, SwiftUI/UIKit placement, accessibility, localization, AI availability/review, and any App Group/CloudKit or Release claims.

## Sources

- [TipKit](https://developer.apple.com/documentation/tipkit)
- [Tip](https://developer.apple.com/documentation/tipkit/tip)
- [Tip actions](https://developer.apple.com/documentation/tipkit/tip/actions)
- [Tip action initializer](https://developer.apple.com/documentation/tipkit/tips/action/init%28id%3Atitle%3Aperform%3A%29)
- [Tip options](https://developer.apple.com/documentation/tipkit/tipoption)
- [Rule](https://developer.apple.com/documentation/tipkit/tips/rule)
- [Parameter](https://developer.apple.com/documentation/tipkit/tips/parameter)
- [Event](https://developer.apple.com/documentation/tipkit/tips/event)
- [Event donation](https://developer.apple.com/documentation/tipkit/tips/event/donate%28%29)
- [TipGroup](https://developer.apple.com/documentation/tipkit/tipgroup)
- [Tips.configure](https://developer.apple.com/documentation/tipkit/tips/configure%28_%3A%29)
- [Tips testing and reset](https://developer.apple.com/documentation/tipkit/tips/resetdatastore%28%29)
- [TipView](https://developer.apple.com/documentation/tipkit/tipview)
- [TipUIView](https://developer.apple.com/documentation/tipkit/tipuiview)
- [Offering help](https://developer.apple.com/design/human-interface-guidelines/offering-help)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Swift Testing](https://developer.apple.com/documentation/testing)
