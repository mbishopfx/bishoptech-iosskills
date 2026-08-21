# AI Review and Liquid Glass Shell Recipes

These sketches show how to connect an app-owned Foundation Models proposal to a native SwiftUI review surface without confusing model output, user edits, and committed domain state. The Liquid Glass layer is deliberately small: it groups related actions while ordinary SwiftUI content carries the meaning of the proposal.

These are route sketches, not compile proof. Confirm the exact signatures, macro behavior, availability attributes, and target requirements in the selected Xcode/iOS 26 SDK before copying them into an app.

## Recipe 1: Gate the model before constructing the workflow

Treat readiness as an explicit dependency of the feature. `SystemLanguageModel.default.availability` describes whether the system language model can be used on the current configuration; `isAvailable` is useful when a feature only needs a boolean gate. Keep the unavailable reason in state so the UI can explain a manual path rather than presenting a dead control.

```swift
import FoundationModels

@MainActor
@Observable
final class AIReviewCoordinator {
    enum Phase: Equatable {
        case checking
        case unavailable(String)
        case ready
        case generating
        case review(Proposal)
        case failed(String)
    }

    var phase: Phase = .checking

    func checkAvailability() {
        let availability = SystemLanguageModel.default.availability

        switch availability {
        case .available:
            phase = .ready
        case .unavailable(let reason):
            phase = .unavailable(String(describing: reason))
        @unknown default:
            phase = .unavailable("This device configuration is not supported.")
        }
    }
}
```

The enum cases and `@Observable` import/availability must be checked against the selected SDK. A physical device audit should record device model, OS build, language/locale, Apple Intelligence settings, model readiness, memory/thermal behavior, and the fallback shown for each unavailable reason. Do not treat simulator output or a non-nil session as model-readiness proof.

## Recipe 2: Generate a bounded proposal, not a domain record

Use a small `@Generable` type for the proposal and keep the canonical record outside the model schema. Use bounded guides where a value must fit the review UI, then repeat those checks in deterministic Swift code.

```swift
import FoundationModels

@Generable
struct ReviewProposal {
    @Guide(description: "A concise title of 80 characters or fewer")
    var title: String

    @Guide(.anyOf(["low", "medium", "high"]))
    var priority: String

    var summary: String
}

struct ProposalEnvelope<Value: Sendable>: Sendable {
    let operationID: UUID
    let sourceRevision: String
    let promptVersion: String
    let schemaVersion: Int
    let value: Value
}

func makeProposal(
    source: String,
    session: LanguageModelSession
) async throws -> ReviewProposal {
    let prompt = """
    Prepare a review proposal from the source below. Do not claim facts not present in the source.

    SOURCE:
    \(source)
    """

    let response = try await session.respond(
        to: prompt,
        generating: ReviewProposal.self
    )
    return response.content
}
```

The `Guide` overloads and response property are version-sensitive; check the current Foundation Models documentation. The generated result is still untrusted. Validate length, allowed values, source revision, account scope, duplicate behavior, policy, and user intent before the review UI offers an approval action. Keep prompt and schema versions alongside the proposal so a later model/OS update can be evaluated rather than silently mixed with old fixtures.

## Recipe 3: Put a deterministic validator between proposal and review

The validator should be a pure boundary wherever possible. It can reject a proposal, normalize safe presentation fields, or return repair instructions; it must not silently turn a failed validation into a successful commit.

```swift
struct ValidationIssue: Equatable, Sendable {
    let field: String
    let message: String
}

struct ValidationResult<Value: Sendable>: Sendable {
    let value: Value?
    let issues: [ValidationIssue]

    var isValid: Bool { value != nil && issues.isEmpty }
}

func validate(_ proposal: ReviewProposal) -> ValidationResult<ReviewProposal> {
    var issues: [ValidationIssue] = []

    if proposal.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        issues.append(.init(field: "title", message: "Add a title."))
    }

    if proposal.title.count > 80 {
        issues.append(.init(field: "title", message: "Use 80 characters or fewer."))
    }

    guard ["low", "medium", "high"].contains(proposal.priority) else {
        issues.append(.init(field: "priority", message: "Choose a supported priority."))
        return .init(value: nil, issues: issues)
    }

    return .init(value: issues.isEmpty ? proposal : nil, issues: issues)
}
```

In a real feature, validation also re-reads current authorization and the source revision. Keep `proposal`, `reviewDraft`, and the canonical persisted value in separate types or state slots. A model’s structured output can satisfy a schema while still being incomplete, misleading, stale, or inappropriate for the current account.

## Recipe 4: Compose the native review shell with a small glass action cluster

The review shell should work with ordinary system materials and controls before any decorative effect is added. Use `GlassEffectContainer` to group related glass controls when the effect itself adds useful hierarchy or a deliberate morph. Keep the source, generated content, validation text, and editable fields outside the glass cluster.

```swift
import SwiftUI

struct ProposalReviewView: View {
    let proposal: ReviewProposal
    let issues: [ValidationIssue]
    let onEdit: () -> Void
    let onReject: () -> Void
    let onApprove: () -> Void

    var body: some View {
        NavigationStack {
            Form {
                Section("Proposal") {
                    Text(proposal.title)
                        .font(.headline)
                    Text(proposal.summary)
                        .foregroundStyle(.secondary)
                }

                Section("Validation") {
                    if issues.isEmpty {
                        Label("Ready for your review", systemImage: "checkmark.circle")
                            .foregroundStyle(.green)
                    } else {
                        ForEach(issues, id: \.field) { issue in
                            Label(issue.message, systemImage: "exclamationmark.triangle")
                        }
                    }
                }
            }
            .navigationTitle("Review")
            .safeAreaInset(edge: .bottom) {
                GlassEffectContainer(spacing: 12) {
                    HStack(spacing: 12) {
                        Button("Edit", action: onEdit)
                            .buttonStyle(.glass)

                        Button("Reject", role: .destructive, action: onReject)
                            .buttonStyle(.glass)

                        Button("Approve", action: onApprove)
                            .buttonStyle(.glassProminent)
                            .disabled(!issues.isEmpty)
                    }
                    .padding(.horizontal)
                }
            }
        }
    }
}
```

For a real product, use `TextField`/`TextEditor` or a dedicated edit sheet for fields that need correction. Add a confirmation step for consequential changes. Give the buttons stable semantic labels and a non-gesture path. Test long localization, Dynamic Type, increased contrast, reduced transparency, Reduce Motion, VoiceOver focus order, keyboard/pointer input, compact width, iPad presentation, and the unavailable/refusal/error state.

If the action cluster changes between loading, review, and committed states, use stable identities only for genuine relationships. `glassEffectID`, `glassEffectTransition`, `glassEffectUnion`, and `withAnimation` describe visual relationships; they do not establish state, permission, or commit truth. The same state reducer should drive both content and action availability.

## Recipe 5: Commit only after explicit approval and current-state revalidation

The approval button should call an app-owned use case. It should not call a model session, accept a tool callback as proof, or write a record from the rendered proposal without checking the current source revision.

```swift
struct ApprovalRequest: Sendable {
    let operationID: UUID
    let sourceRevision: String
    let editedProposal: ReviewProposal
}

enum CommitOutcome: Sendable {
    case committed(recordID: String)
    case staleSource
    case conflict
    case rejected(String)
}

protocol ProposalCommitter: Sendable {
    func commit(_ request: ApprovalRequest) async throws -> CommitOutcome
}
```

The implementation should reauthorize the current user/account, compare `sourceRevision` with the current domain record, enforce business rules, use an idempotency key based on `operationID`, and return the canonical result. Only after `.committed` should the app update widgets, Live Activities, indexed entities, App Intent projections, or other system-facing surfaces. A duplicate tap, app termination, network failure, protected-data lock, or conflict must remain observable and recoverable.

## Recipe 6: Keep tools and App Intents outside the approval shortcut

A Foundation Models `Tool` is a typed model-facing boundary. It can read current data or prepare a preview, but a model choosing to call it is not the same as a person approving a side effect. An `AppIntent` is a system-facing action boundary and should use the same authorized domain service as the in-app button.

```text
Foundation Models session
  -> read-only Tool / deterministic preview
  -> proposal + provenance
  -> SwiftUI review and explicit approval
  -> domain use case / authorization / idempotency
  -> committed canonical state
  -> AppEntity, Spotlight, widget, notification, or other projection
```

For each tool or intent, document:

- input schema and maximum size;
- account/permission checks performed inside the boundary;
- whether the result is a query, preview, or mutation;
- stale data and conflict behavior;
- cancellation and retry policy;
- whether user confirmation is required;
- the exact domain result that counts as committed;
- what system-facing projection is allowed after commit.

Treat retrieved text, files, webpages, tool output, and camera-derived labels as untrusted data. Keep trusted instructions separate from external content, and do not place secrets, raw private transcripts, or full private records into model context or indexed/system-facing representations unless the product’s explicit privacy design calls for it.

## State and evidence checklist

| State or claim | Local code/preview can prove | Physical or signed evidence still required |
| --- | --- | --- |
| Model gate renders | Availability mapping and manual fallback branches | Named device/OS/language/Apple Intelligence readiness and resource behavior |
| Proposal renders | Fixture proposal, validation, editing, refusal/error states | Actual model output quality, latency, context limits, and thermal/memory behavior |
| Glass cluster looks correct | Layout, labels, transitions, Dynamic Type, and accessibility fixtures | Material legibility, touch ergonomics, performance, VoiceOver/Voice Control, and reduced effects |
| Approve is safe | Reducer, validator, idempotency, stale/conflict tests | Real persistence/service/device commit and recovery behavior |
| App Intent/entity route works | Schema/query compile and deterministic resolver tests | Siri/Shortcuts/Spotlight/Apple Intelligence invocation, ranking, permissions, and current-system behavior |
| Release surface is ready | Signed target/configuration checks | TestFlight/release-build run, privacy/entitlement review, exact supported device matrix |

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Transcript](https://developer.apple.com/documentation/foundationmodels/transcript)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Updating prompts for new model versions](https://developer.apple.com/documentation/foundationmodels/updating-prompts-for-new-model-versions)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Glass](https://developer.apple.com/documentation/swiftui/glass)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [GlassEffectTransition](https://developer.apple.com/documentation/swiftui/glasseffecttransition)
- [NavigationStack](https://developer.apple.com/documentation/swiftui/navigationstack)
- [SwiftUI presentation modifiers](https://developer.apple.com/documentation/swiftui/view-presentation)
- [SwiftUI accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
