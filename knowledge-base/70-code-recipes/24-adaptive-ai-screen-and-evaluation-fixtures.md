# Adaptive AI Screen and Evaluation Fixture Recipes

This recipe combines a state-driven Foundation Models workflow with SwiftUI adaptation tools. It is intended for a feature that receives text, media, or a local record; produces a proposal; lets the person review/edit/reject it; and commits only after deterministic validation and explicit approval.

The snippets are compile-oriented route sketches. Confirm the exact signatures, availability, macro imports, and Liquid Glass behavior in the selected iOS 26 SDK before using them in an app.

## Recipe 1: Make the feature state explicit

Keep model availability, proposal trust, user edits, and domain commit separate from the view’s visual treatment.

```swift
enum AIReviewState<Value: Equatable>: Equatable {
    case idle
    case checkingAvailability
    case unavailable(reason: String)
    case preparing
    case generating
    case proposal(value: Value, issues: [ValidationIssue])
    case editing(value: Value, issues: [ValidationIssue])
    case committing(value: Value)
    case committed(recordID: String)
    case cancelled
    case failed(message: String)
}

struct ValidationIssue: Equatable, Identifiable {
    let id: String
    let message: String
}
```

Do not use `.proposal` as proof that the record is saved. The view should render the last confirmed domain value separately from the generated proposal and the editable draft. If the app is terminated or the model becomes unavailable, preserve the source and confirmed result and show a manual recovery path.

## Recipe 2: Adapt action density with `ViewThatFits`

When the same actions can be presented in a few intentional forms, use `ViewThatFits` rather than measuring individual labels or hard-coding a device width.

```swift
struct ReviewActions: View {
    let canApprove: Bool
    let onEdit: () -> Void
    let onReject: () -> Void
    let onApprove: () -> Void

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) {
                Button("Edit", action: onEdit)
                Button("Reject", role: .destructive, action: onReject)
                Button("Approve", action: onApprove)
                    .disabled(!canApprove)
            }

            HStack {
                Button("Edit", action: onEdit)
                Menu("More") {
                    Button("Reject", role: .destructive, action: onReject)
                    Button("Approve", action: onApprove)
                        .disabled(!canApprove)
                }
            }
        }
        .buttonStyle(.bordered)
    }
}
```

The first child is the preferred option; later children are deliberate fallbacks. Keep all actions discoverable and semantically labeled. Do not rely on an icon-only fallback for a consequential action unless the accessibility label, Voice Control name, keyboard route, and user comprehension are verified.

## Recipe 3: Change the content layout without destroying state

Use `AnyLayout` when the same source/proposal content should move between horizontal and vertical arrangements. Dynamic Type is one signal; available width and platform context may be additional signals.

```swift
struct SourceAndProposal<ValueView: View, SourceView: View>: View {
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    let source: SourceView
    let proposal: ValueView

    init(
        @ViewBuilder source: () -> SourceView,
        @ViewBuilder proposal: () -> ValueView
    ) {
        self.source = source()
        self.proposal = proposal()
    }

    var body: some View {
        let layout = dynamicTypeSize >= .accessibility1
            ? AnyLayout(VStackLayout(spacing: 20))
            : AnyLayout(HStackLayout(spacing: 20))

        layout {
            source
                .frame(maxWidth: .infinity, alignment: .leading)
            proposal
                .frame(maxWidth: .infinity, alignment: .leading)
        }
    }
}
```

This sketch needs the selected SDK’s current `DynamicTypeSize` comparison and layout API checked. In a real screen, also consider width proposals, right-to-left layout, long localization, empty content, and regular-width iPad composition. Avoid fixed heights around model-generated text.

## Recipe 4: Add Liquid Glass only to a functional action group

The source and proposal should remain readable in standard content containers. If a glass treatment adds useful hierarchy to the related review actions, place it around that group and keep the button semantics intact.

```swift
struct GlassReviewBar: View {
    let canApprove: Bool
    let onEdit: () -> Void
    let onReject: () -> Void
    let onApprove: () -> Void

    var body: some View {
        GlassEffectContainer(spacing: 12) {
            HStack(spacing: 12) {
                Button("Edit", action: onEdit)
                    .buttonStyle(.glass)

                Button("Reject", role: .destructive, action: onReject)
                    .buttonStyle(.glass)

                Button("Approve", action: onApprove)
                    .buttonStyle(.glassProminent)
                    .disabled(!canApprove)
            }
            .padding(.horizontal)
        }
    }
}
```

Treat `.glass` and `.glassProminent` as current SDK routes, not timeless signatures. Test standard controls before custom effects, and provide a readable result when transparency is reduced or contrast is increased. The glass bar must not be the only place where the validation state is communicated.

## Recipe 5: Render all model and domain states

Use ordinary SwiftUI content to explain what is happening. A model-generated proposal, a refusal, an unavailable model, and a committed record need different user-facing states.

```swift
struct AIReviewContent<Proposal: View>: View {
    let phase: Phase
    @ViewBuilder let proposal: () -> Proposal

    enum Phase {
        case checking
        case unavailable(String)
        case generating
        case review
        case invalid([ValidationIssue])
        case committed(String)
        case failed(String)
    }

    var body: some View {
        switch phase {
        case .checking:
            ProgressView("Checking availability")
        case .unavailable(let message):
            ContentUnavailableView(
                "AI feature unavailable",
                systemImage: "text.badge.xmark",
                description: Text(message)
            )
        case .generating:
            ProgressView("Preparing a proposal")
        case .review:
            proposal()
        case .invalid(let issues):
            VStack(alignment: .leading) {
                Text("Review needed").font(.headline)
                ForEach(issues) { issue in
                    Label(issue.message, systemImage: "exclamationmark.triangle")
                }
            }
        case .committed(let recordID):
            Label("Saved \(recordID)", systemImage: "checkmark.circle")
        case .failed(let message):
            ContentUnavailableView(
                "Couldn’t finish",
                systemImage: "exclamationmark.circle",
                description: Text(message)
            )
        }
    }
}
```

The `@ViewBuilder` stored-property shape may need to be adapted to the chosen project style. The important contract is that every state has readable content, a recovery action, and an accessibility path. Do not announce a generated result as saved until the domain service returns its canonical commit result.

## Recipe 6: Inject deterministic proposals into previews and UI tests

Previews and UI tests should not depend on Foundation Models availability. Inject a fake proposal provider and exercise the same reducer with recorded fixtures.

```swift
struct AIReviewFixture: Sendable {
    let name: String
    let source: String
    let proposal: ReviewProposal?
    let issues: [ValidationIssue]
    let expectedPhase: String
}

enum ProposalProviderError: Error {
    case unavailable
    case refused
    case contextExceeded
}

protocol ProposalProvider: Sendable {
    func propose(from source: String) async throws -> ReviewProposal
}

struct FixtureProposalProvider: ProposalProvider {
    let fixture: AIReviewFixture

    func propose(from source: String) async throws -> ReviewProposal {
        guard let proposal = fixture.proposal else {
            throw ProposalProviderError.refused
        }
        return proposal
    }
}
```

Use fixtures for representative, empty, ambiguous, long, multilingual, adversarial, privacy-sensitive, cancellation, unavailable, refusal, invalid, duplicate-approval, stale-source, and commit-conflict states. Keep the fixture’s expected invariants and source revision explicit. Then run the real provider separately on the named physical device and record model, OS, language, resource, latency, memory, and thermal evidence.

## Recipe 7: Verification matrix for the adaptive screen

| Check | Fixture or environment | Evidence |
| --- | --- | --- |
| Normal review | Valid proposal with provenance | Content hierarchy, edit/reject/approve task completion. |
| Invalid proposal | Missing/overlong/unsupported fields | Field-level explanation and repair path. |
| Unavailable/refusal | Fake provider branch and physical model-unavailable state | Manual route remains usable; no dead glass action. |
| Long text | Largest supported fixture and accessibility text sizes | No clipping, lost focus, or hidden action. |
| Compact/regular | Small iPhone width and iPad/regular width | `ViewThatFits`/`AnyLayout` preserve outcome and state. |
| RTL/localization | Long translated labels and right-to-left locale | Reading order, formatting, action discoverability. |
| Reduced effects | Reduce Motion, increased contrast, reduced transparency | Same semantics without reliance on morph/blur/tint. |
| Assistive technology | VoiceOver, Voice Control, Switch Control, keyboard/pointer | Person can inspect, edit, reject, and approve. |
| Commit safety | Duplicate tap, stale source, conflict, persistence failure | Idempotency, current-state validation, recovery. |
| Physical target | Named iOS 26 device/build | Material legibility, touch targets, model readiness, performance, thermal/memory. |

## Sources

- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [ViewThatFits](https://developer.apple.com/documentation/swiftui/viewthatfits)
- [AnyLayout](https://developer.apple.com/documentation/swiftui/anylayout)
- [Layout](https://developer.apple.com/documentation/swiftui/layout)
- [Dynamic Type](https://developer.apple.com/documentation/swiftui/dynamictypesize)
- [ContentUnavailableView](https://developer.apple.com/documentation/swiftui/contentunavailableview)
- [Accessibility modifiers](https://developer.apple.com/documentation/swiftui/view-accessibility)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
