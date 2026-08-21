# SwiftUI Foundation Models production-route recipes

These are route sketches for an iOS 26 app target. They are deliberately small enough to adapt, but they are not a substitute for compiling against the exact Xcode and SDK selected by the project. Foundation Models documentation includes beta and evolving APIs; treat compiler diagnostics and the current Apple pages as authoritative when a signature differs.

The sketches use the following boundary:

1. a capability coordinator checks model availability;
2. a session owner serializes access;
3. prompts and schemas are bounded;
4. responses stream into reviewable state;
5. tools return current data or proposals;
6. deterministic validation and user approval precede side effects;
7. SwiftUI renders every loading, cancellation, fallback, and error state.

No recipe below should silently save model output as a committed domain record.

## 1. Capability gate

Start with an explicit availability projection. Do not construct an AI screen that assumes the model is ready.

~~~swift
import Foundation
import FoundationModels

struct ModelAvailabilityState: Equatable, Sendable {
    enum Lane: Equatable, Sendable {
        case ready
        case unavailable(reason: String)
    }

    let lane: Lane
    let contextSize: Int?
    let supportedLanguages: Set<Locale.Language>?
}

@MainActor
final class ModelCapabilityCoordinator {
    private let model = SystemLanguageModel.default

    func snapshot() -> ModelAvailabilityState {
        switch model.availability {
        case .available:
            return ModelAvailabilityState(
                lane: .ready,
                contextSize: model.contextSize,
                supportedLanguages: model.supportedLanguages
            )
        case .unavailable(let reason):
            return ModelAvailabilityState(
                lane: .unavailable(reason: String(describing: reason)),
                contextSize: model.contextSize,
                supportedLanguages: model.supportedLanguages
            )
        }
    }

    func supports(locale: Locale) -> Bool {
        model.supportsLocale(locale)
    }
}
~~~

Design notes:

- Keep the unavailable reason in a typed internal state when the selected SDK exposes the cases you need.
- Use the current availability immediately before a request, not only at app launch.
- The example exposes context size and supported languages as diagnostics; the feature still needs its own product fallback.
- If a property is marked beta in the selected SDK, keep its use behind a small adapter.

## 2. SwiftUI availability view

The view should make the fallback useful, not just explain why the AI button is disabled.

~~~swift
import SwiftUI

struct ModelAvailabilityView<Content: View, Fallback: View>: View {
    let state: ModelAvailabilityState
    @ViewBuilder let content: () -> Content
    @ViewBuilder let fallback: () -> Fallback

    var body: some View {
        switch state.lane {
        case .ready:
            content()
        case .unavailable:
            ContentUnavailableView {
                Label("On-device suggestions unavailable", systemImage: "sparkles")
            } description: {
                Text("You can continue with the standard workflow.")
            } actions: {
                fallback()
            }
        }
    }
}
~~~

The system image is a visual label, not a reason to hide the actual state. Use a product-specific label and expose the same meaning to VoiceOver.

## 3. Session ownership

Keep one session behind one owner. The exact isolation annotation may change as the framework evolves, but the ownership rule does not.

~~~swift
import Foundation
import FoundationModels

@MainActor
final class FoundationSessionStore {
    private(set) var session: LanguageModelSession?
    private(set) var transcript: Transcript?
    private(set) var isResponding = false

    func start(instructions: String) {
        let newSession = LanguageModelSession(instructions: instructions)
        session = newSession
        transcript = newSession.transcript
        isResponding = false
    }

    func refreshTranscript() {
        transcript = session?.transcript
    }

    func prewarm(prefix: Prompt? = nil) {
        session?.prewarm(promptPrefix: prefix)
    }
}
~~~

Use one store per independent task. Do not make this a process-wide singleton used by unrelated screens. If the app needs a background actor or service, put the session behind that actor and expose Sendable request/result values at the boundary.

## 4. PromptBuilder with visible input boundaries

Dynamic prompt content should make imported text and user input visibly separate from instructions.

~~~swift
import FoundationModels

func makeSummaryPrompt(
    userRequest: String,
    selectedText: String,
    concise: Bool
) -> Prompt {
    Prompt {
        "Summarize only the selected source text."
        "Return an editable draft. Do not invent facts."
        if concise {
            "Use no more than three short paragraphs."
        } else {
            "Use a short heading followed by concise paragraphs."
        }
        "User request begins."
        userRequest
        "User request ends."
        "Selected source begins."
        selectedText
        "Selected source ends."
    }
}
~~~

The builder chooses sections; it does not sanitize content. Before calling it:

- cap or trim selectedText using a deterministic policy;
- remove data the feature does not need;
- preserve user-authored source separately from generated output;
- add a prompt version to the evaluation record;
- test empty, huge, malformed, and adversarial input.

## 5. Prompt and context budget probe

Use the model’s current context information during development. The exact overloads can be beta or change; isolate the calls in one diagnostic type.

~~~swift
import Foundation
import FoundationModels

struct ContextBudgetReport: Sendable {
    let contextSize: Int
    let instructionTokens: Int
    let promptTokens: Int
    let guidance: String
}

@MainActor
func measureContext(
    instructions: String,
    prompt: Prompt
) -> ContextBudgetReport {
    let model = SystemLanguageModel.default
    let instructionTokens = model.tokenCount(for: instructions)
    let promptTokens = model.tokenCount(for: prompt)

    return ContextBudgetReport(
        contextSize: model.contextSize,
        instructionTokens: instructionTokens,
        promptTokens: promptTokens,
        guidance: "Also measure schema, tools, transcript, and response usage."
    )
}
~~~

If the selected SDK does not accept Prompt in the token-counting overload, keep the adapter but compile the equivalent current API. The product rule is stable: measure the full session contributors, not just the visible user string.

## 6. Prewarm at a meaningful prediction point

Prewarm only when the user has signaled likely imminent use.

~~~swift
import FoundationModels

@MainActor
func prepareForComposer(
    store: FoundationSessionStore,
    userHasOpenedComposer: Bool,
    promptPrefix: Prompt?
) {
    guard userHasOpenedComposer else { return }
    store.prewarm(prefix: promptPrefix)
}
~~~

Apple’s documentation describes a useful window of at least about one second before a response call. Prewarm is not a readiness callback and does not guarantee that assets load immediately. Measure with Instruments before keeping it.

## 7. One-shot plain-text response

Use a fresh session for a bounded single-turn draft.

~~~swift
import Foundation
import FoundationModels

enum DraftError: Error {
    case unavailable
    case empty
}

@MainActor
func generateDraft(
    instructions: String,
    prompt: Prompt
) async throws -> String {
    let model = SystemLanguageModel.default
    guard model.isAvailable else {
        throw DraftError.unavailable
    }

    let session = LanguageModelSession(instructions: instructions)
    let response = try await session.respond(to: prompt)
    let content = response.content.trimmingCharacters(in: .whitespacesAndNewlines)

    guard !content.isEmpty else {
        throw DraftError.empty
    }
    return content
}
~~~

The string is a draft. If it will update a record, send it through validation and an approval surface first.

## 8. Streaming text into isolated view state

ResponseStream yields partial snapshots. Render them as draft state and protect against stale tasks.

~~~swift
import Foundation
import FoundationModels

@MainActor
final class StreamingDraftStore {
    enum Phase: Equatable {
        case idle
        case generating
        case candidate
        case cancelled
        case failed(String)
    }

    private(set) var phase: Phase = .idle
    private(set) var text = ""
    private(set) var requestID: UUID?
    private var task: Task<Void, Never>?

    func start(
        session: LanguageModelSession,
        prompt: Prompt
    ) {
        task?.cancel()
        let id = UUID()
        requestID = id
        phase = .generating
        text = ""

        task = Task { @MainActor [weak self] in
            guard let self else { return }
            do {
                let stream = session.streamResponse(to: prompt)
                for try await snapshot in stream {
                    try Task.checkCancellation()
                    guard self.requestID == id else { return }
                    self.text = snapshot.content
                }
                guard self.requestID == id else { return }
                self.phase = .candidate
            } catch is CancellationError {
                guard self.requestID == id else { return }
                self.phase = .cancelled
            } catch {
                guard self.requestID == id else { return }
                self.phase = .failed(String(describing: error))
            }
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
    }
}
~~~

Compile note: the current response-stream snapshot exposes content for the selected generic type. If the SDK’s spelling changes, keep the request ID and phase logic and update only the adapter.

Important behavior:

- do not save self.text to the domain store inside the loop;
- do not show candidate actions until the stream completes;
- make the cancel button available through the entire generating phase;
- test a late result from the old request after a new request starts.

## 9. Collect a stream when the final response matters

When incremental UI is optional, collect the stream and validate the completed response.

~~~swift
import FoundationModels

@MainActor
func collectDraft(
    session: LanguageModelSession,
    prompt: Prompt
) async throws -> String {
    let stream = session.streamResponse(to: prompt)
    let response = try await stream.collect()
    return response.content
}
~~~

A collected response still needs semantic validation. Collection is a lifecycle convenience, not a commit guarantee.

## 10. Typed proposal with Generable

Define the smallest reviewable shape. The app should own the final domain model.

~~~swift
import FoundationModels

@Generable
enum SuggestedCategory {
    case work
    case personal
    case followUp
}

@Generable
struct SuggestedTask {
    @Guide(description: "A concise task title the person can edit.")
    let title: String

    @Guide(description: "A short explanation based only on the supplied source.")
    let reason: String

    let category: SuggestedCategory
}
~~~

Schema rules:

- keep descriptions short;
- bound collections when the schema has collections;
- use finite choices for finite choices;
- include only fields the person can review;
- do not put authorization or database constraints in the schema;
- measure schema size and decoding behavior;
- keep a fallback if the model cannot decode a valid value.

## 11. Generate and validate a typed proposal

Typed output is a proposal. Validate it before showing the approval action.

~~~swift
import Foundation
import FoundationModels

struct ValidatedTaskProposal: Sendable {
    let title: String
    let reason: String
    let category: SuggestedCategory
}

enum ProposalValidationError: Error {
    case emptyTitle
    case titleTooLong
    case reasonTooLong
}

func validate(_ value: SuggestedTask) throws -> ValidatedTaskProposal {
    let title = value.title.trimmingCharacters(in: .whitespacesAndNewlines)
    let reason = value.reason.trimmingCharacters(in: .whitespacesAndNewlines)

    guard !title.isEmpty else { throw ProposalValidationError.emptyTitle }
    guard title.count <= 120 else { throw ProposalValidationError.titleTooLong }
    guard reason.count <= 500 else { throw ProposalValidationError.reasonTooLong }

    return ValidatedTaskProposal(
        title: title,
        reason: reason,
        category: value.category
    )
}

@MainActor
func suggestTask(
    session: LanguageModelSession,
    prompt: Prompt
) async throws -> ValidatedTaskProposal {
    let response = try await session.respond(
        to: prompt,
        generating: SuggestedTask.self
    )
    return try validate(response.content)
}
~~~

The validation layer should also verify identity, permissions, duplicate rules, and current domain state before a write. Those checks do not belong in a Guide.

## 12. Stream a typed proposal

Typed streaming is useful for a review form, but partial fields are still provisional.

~~~swift
import Foundation
import FoundationModels

@MainActor
final class TypedProposalStore {
    private(set) var partial: SuggestedTask?
    private(set) var final: ValidatedTaskProposal?
    private(set) var error: Error?

    func generate(
        session: LanguageModelSession,
        prompt: Prompt
    ) async {
        partial = nil
        final = nil
        error = nil

        do {
            let stream = session.streamResponse(
                to: prompt,
                generating: SuggestedTask.self
            )

            for try await snapshot in stream {
                try Task.checkCancellation()
                partial = snapshot.content
            }

            let response = try await stream.collect()
            final = try validate(response.content)
        } catch {
            self.error = error
        }
    }
}
~~~

If the selected SDK does not permit collecting after iteration, retain the last complete response according to its current ResponseStream contract or use only collect. The UI contract remains: partial fields are not approved fields.

## 13. Dynamic schema adapter

Use DynamicGenerationSchema when the output shape is genuinely determined at runtime. Keep construction and conversion isolated.

~~~swift
import FoundationModels

struct DynamicProposalAdapter {
    func makeSchema(
        fieldNames: [String]
    ) throws -> GenerationSchema {
        // Build only from a validated, app-owned field definition.
        // Reject duplicate names before creating the schema.
        // Confirm the current DynamicGenerationSchema initializer in the SDK.
        fatalError("Implement with the selected SDK's DynamicGenerationSchema API")
    }

    func decode(
        _ content: GeneratedContent
    ) throws -> [String: String] {
        // Convert only fields declared by the app-owned schema.
        // Do not treat arbitrary generated keys as domain fields.
        fatalError("Implement with the selected SDK's GeneratedContent API")
    }
}
~~~

Dynamic schemas are not a license to let the model invent a database schema. The app must own allowed fields, references, limits, and semantic validation.

## 14. Read-only tool

A read tool should have a narrow argument type and return only the current information needed for the response.

~~~swift
import FoundationModels

struct SearchNotesTool: Tool {
    let name = "search_notes"
    let description = "Find a small set of notes matching a user-provided phrase."

    @Generable
    struct Arguments {
        @Guide(description: "A short phrase to search for.")
        let query: String
    }

    let search: @Sendable (String) async throws -> [NoteSearchResult]

    func call(arguments: Arguments) async throws -> String {
        let query = arguments.query
            .trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty, query.count <= 120 else {
            throw ToolInputError.invalidQuery
        }

        let results = try await search(query)
        return results
            .prefix(5)
            .map { "\($0.id): \($0.title)" }
            .joined(separator: "\n")
    }
}

struct NoteSearchResult: Sendable {
    let id: String
    let title: String
}

enum ToolInputError: Error {
    case invalidQuery
}
~~~

Compile note: Tool output must conform to the prompt-representable contract for the current SDK. A String is the simplest route. If the app needs structured results, return a small Generable output or the current supported generated-content type.

## 15. Tool-backed session

Construct a session with only the tools needed for this task.

~~~swift
import FoundationModels

@MainActor
func makeSearchSession(
    search: @escaping @Sendable (String) async throws -> [NoteSearchResult]
) -> LanguageModelSession {
    let tool = SearchNotesTool(search: search)
    return LanguageModelSession(
        tools: [tool],
        instructions: """
        Help the person find notes.
        Use the search tool when current note data is needed.
        Never claim that a note exists unless the tool returned it.
        Do not edit or delete notes.
        """
    )
}
~~~

Keep the tool description and instruction concise. The tool definition consumes context on every request in the session.

## 16. Tool approval as a proposal

A write tool should first produce a proposed operation or enter an approval state. The view model can represent the separation.

~~~swift
import Foundation

struct ProposedNoteEdit: Identifiable, Sendable {
    let id: UUID
    let noteID: String
    let newTitle: String
    let explanation: String
}

@MainActor
final class NoteEditApprovalStore {
    enum Phase {
        case idle
        case awaitingApproval(ProposedNoteEdit)
        case committing
        case completed
        case failed(String)
    }

    private(set) var phase: Phase = .idle
    private let save: @MainActor (ProposedNoteEdit) throws -> Void

    init(save: @escaping @MainActor (ProposedNoteEdit) throws -> Void) {
        self.save = save
    }

    func receive(_ proposal: ProposedNoteEdit) {
        phase = .awaitingApproval(proposal)
    }

    func approve() {
        guard case .awaitingApproval(let proposal) = phase else { return }
        phase = .committing

        do {
            try save(proposal)
            phase = .completed
        } catch {
            phase = .failed(String(describing: error))
        }
    }

    func deny() {
        phase = .idle
    }
}
~~~

Before save, re-check the current note version, user authorization, and any conflict. The generated proposal is not a permission grant.

## 17. Tool-calling mode adapter

Tool-calling mode is a policy choice. Keep it at the route boundary so prompts and tests can exercise it explicitly.

~~~swift
import FoundationModels

enum AppToolPolicy {
    case allowed
    case required
    case disallowed
}

struct ToolPolicyNote {
    let policy: AppToolPolicy
    let exitCondition: String
}

func policyNote(_ policy: AppToolPolicy) -> ToolPolicyNote {
    switch policy {
    case .allowed:
        return ToolPolicyNote(
            policy: policy,
            exitCondition: "The model may answer without a tool when current data is not needed."
        )
    case .required:
        return ToolPolicyNote(
            policy: policy,
            exitCondition: "The session must stop after the required current-data result is available."
        )
    case .disallowed:
        return ToolPolicyNote(
            policy: policy,
            exitCondition: "The response must remain a bounded generative draft."
        )
    }
}
~~~

Map this policy to the selected SDK’s GenerationOptions.ToolCallingMode after confirming the exact property and enum cases. Required mode needs an exit condition; otherwise repeated calls can become a product failure.

## 18. Error adapter

The current SDK separates model errors, session misuse, and tool-call errors. Keep user copy separate from developer diagnostics.

~~~swift
import Foundation
import FoundationModels

enum AIUserFacingState: Equatable {
    case unavailable
    case notReady
    case cancelled
    case contextTooLarge
    case refused
    case invalidOutput
    case toolFailed
    case concurrentRequest
    case genericFailure
}

func mapFoundationModelError(_ error: Error) -> AIUserFacingState {
    if error is CancellationError {
        return .cancelled
    }

    switch error {
    case let error as LanguageModelError:
        let description = String(describing: error)
        if description.localizedCaseInsensitiveContains("context") {
            return .contextTooLarge
        }
        if description.localizedCaseInsensitiveContains("refusal") {
            return .refused
        }
        return .genericFailure
    case let error as LanguageModelSession.Error:
        let description = String(describing: error)
        if description.localizedCaseInsensitiveContains("concurrent") {
            return .concurrentRequest
        }
        return .genericFailure
    default:
        return .genericFailure
    }
}
~~~

Prefer exhaustive typed matching when the selected SDK exposes stable cases. The string checks above are a migration sketch, not a final diagnostic policy. Never show raw error descriptions if they can contain private prompt or tool data.

## 19. Session cancellation and stale-result protection

Cancellation belongs in the coordinator, not only in the Button action.

~~~swift
import Foundation
import FoundationModels

@MainActor
final class RequestCoordinator {
    private var task: Task<Void, Never>?
    private var activeID: UUID?
    private(set) var output = ""
    private(set) var phase = "idle"

    func run(
        session: LanguageModelSession,
        prompt: Prompt,
        apply: @escaping @MainActor (String) -> Void
    ) {
        task?.cancel()
        let id = UUID()
        activeID = id
        output = ""
        phase = "generating"

        task = Task { @MainActor [weak self] in
            guard let self else { return }
            do {
                let response = try await session.respond(to: prompt)
                try Task.checkCancellation()
                guard self.activeID == id else { return }
                self.output = response.content
                self.phase = "candidate"
                apply(response.content)
            } catch is CancellationError {
                guard self.activeID == id else { return }
                self.phase = "cancelled"
            } catch {
                guard self.activeID == id else { return }
                self.phase = "failed"
            }
        }
    }

    func cancel() {
        task?.cancel()
        task = nil
        phase = "cancelled"
    }
}
~~~

The apply closure is still only allowed to update reviewable UI or a draft. Commit requires a separate, explicit domain operation.

## 20. Transcript inspection without accidental persistence

Expose transcript entries for development or a review surface only when the product has a clear retention policy.

~~~swift
import FoundationModels

struct TranscriptSummary: Sendable {
    let entryCount: Int
    let hasToolActivity: Bool
}

func summarizeTranscript(_ transcript: Transcript) -> TranscriptSummary {
    var count = 0
    var hasToolActivity = false

    for entry in transcript {
        count += 1
        if String(describing: entry).localizedCaseInsensitiveContains("tool") {
            hasToolActivity = true
        }
    }

    return TranscriptSummary(
        entryCount: count,
        hasToolActivity: hasToolActivity
    )
}
~~~

Do not use String(describing:) as a privacy-safe export format. This sketch is for a local development count only. For a real viewer, switch over the current Transcript.Entry and Segment cases and render only approved fields.

## 21. Rehydrate only an app-owned transcript

Rehydration should be explicit and scoped to a task.

~~~swift
import FoundationModels

struct RehydrationRecord: Sendable {
    let promptVersion: String
    let entries: [Transcript.Entry]
    let sourceRecordID: String
}

@MainActor
func rehydrate(
    record: RehydrationRecord,
    expectedPromptVersion: String
) -> LanguageModelSession? {
    guard record.promptVersion == expectedPromptVersion else {
        return nil
    }

    let transcript = Transcript(entries: record.entries)
    return LanguageModelSession(transcript: transcript)
}
~~~

After rehydration, re-check availability, user identity, current source data, tool authorization, and model-version policy. A transcript does not restore side effects or current data.

## 22. Prompt-version selection

Use an app-owned version policy and test it against the current model versions.

~~~swift
import Foundation
import FoundationModels

struct PromptVariant: Sendable {
    let identifier: String
    let instructions: String
}

func choosePromptVariant(
    model: SystemLanguageModel,
    newest: PromptVariant,
    fallback: PromptVariant
) -> PromptVariant {
    // Prefer the newest tested variant only when the current target supports it.
    // The exact model-version API may evolve; keep selection in one adapter.
    if model.isAvailable {
        return newest
    }
    return fallback
}
~~~

Availability is not model-version detection. In production, populate the variant from the current documented version surface or a build-time policy and record the selected identifier in evaluation logs.

## 23. Fixture-based prompt evaluation

Build a deterministic fixture layer around the session boundary.

~~~swift
import Foundation

struct PromptFixture: Identifiable, Sendable {
    let id: String
    let input: String
    let expectedProperties: Set<String>
    let promptVersion: String
}

struct FixtureResult: Sendable {
    let fixtureID: String
    let promptVersion: String
    let output: String?
    let propertiesPassed: Set<String>
    let propertiesFailed: Set<String>
}

protocol DraftEvaluator: Sendable {
    func generate(_ input: String) async throws -> String
}

struct FixtureRunner {
    let evaluator: any DraftEvaluator
    let check: @Sendable (String, Set<String>) -> (passed: Set<String>, failed: Set<String>)

    func run(_ fixture: PromptFixture) async -> FixtureResult {
        do {
            let output = try await evaluator.generate(fixture.input)
            let checks = check(output, fixture.expectedProperties)
            return FixtureResult(
                fixtureID: fixture.id,
                promptVersion: fixture.promptVersion,
                output: output,
                propertiesPassed: checks.passed,
                propertiesFailed: checks.failed
            )
        } catch {
            return FixtureResult(
                fixtureID: fixture.id,
                promptVersion: fixture.promptVersion,
                output: nil,
                propertiesPassed: [],
                propertiesFailed: ["generation failed"]
            )
        }
    }
}
~~~

The evaluator can use a live physical-device model during development, but the fixture result must record OS, device, model, prompt, schema, and tool metadata outside the raw output.

## 24. Typed proposal fixture validation

Test semantic rules separately from model generation.

~~~swift
import Foundation

struct TaskProposalFixture: Sendable {
    let title: String
    let category: SuggestedCategory
}

enum SemanticResult: Equatable {
    case accepted
    case rejected(reason: String)
}

func checkDomainRules(_ proposal: ValidatedTaskProposal) -> SemanticResult {
    guard proposal.title.count <= 120 else {
        return .rejected(reason: "title too long")
    }

    // Real code should query the current domain state here.
    // Do not let a model-created identifier bypass authorization.
    return .accepted
}
~~~

Keep this validator deterministic and unit-testable. A model should never be used to decide whether a user owns a record.

## 25. SwiftUI review shell

Use normal SwiftUI controls and add Liquid Glass only to the related action cluster.

~~~swift
import SwiftUI

struct AIReviewShell<Source: View, Output: View>: View {
    let isGenerating: Bool
    let isCandidate: Bool
    let source: () -> Source
    let output: () -> Output
    let onGenerate: () -> Void
    let onCancel: () -> Void
    let onApprove: () -> Void
    let onDismiss: () -> Void

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                source()

                GroupBox {
                    output()
                } label: {
                    Label(
                        isGenerating ? "Draft is generating" : "Suggested draft",
                        systemImage: "sparkles"
                    )
                }
                .accessibilityElement(children: .contain)

                GlassEffectContainer {
                    HStack {
                        if isGenerating {
                            Button("Cancel", action: onCancel)
                                .buttonStyle(.bordered)
                        } else if isCandidate {
                            Button("Apply after review", action: onApprove)
                                .buttonStyle(.borderedProminent)
                        } else {
                            Button("Generate suggestion", action: onGenerate)
                                .buttonStyle(.borderedProminent)
                        }

                        Button("Dismiss", action: onDismiss)
                            .buttonStyle(.bordered)
                    }
                }
            }
            .padding()
        }
    }
}
~~~

The exact Liquid Glass modifier and container availability depend on the deployment target and SDK. Keep the state machine usable without the material. The approval label must match the consequence.

## 26. Accessible streaming status

Announce meaningful phase changes rather than every partial token.

~~~swift
import SwiftUI

struct AccessibleDraftStatus: View {
    let phase: String
    let output: String

    var body: some View {
        VStack(alignment: .leading) {
            Text(phase)
                .font(.subheadline)
                .foregroundStyle(.secondary)
                .accessibilityAddTraits(.isHeader)

            Text(output.isEmpty ? "No draft yet." : output)
                .textSelection(.enabled)
                .accessibilityLabel("Suggested draft")
                .accessibilityValue(output.isEmpty ? "No draft yet" : output)
        }
        .accessibilityElement(children: .contain)
    }
}
~~~

For a live streaming route, consider a separate status announcement strategy so VoiceOver does not be interrupted on every update. Ensure the stop action is reachable by VoiceOver, keyboard, and pointer.

## 27. Tool approval sheet

A sheet should say what will happen, what data is involved, and which button authorizes it.

~~~swift
import SwiftUI

struct ToolApprovalSheet: View {
    let title: String
    let affectedItems: [String]
    let explanation: String
    let onApprove: () -> Void
    let onDeny: () -> Void

    var body: some View {
        NavigationStack {
            List {
                Section("Suggested action") {
                    Text(title)
                    Text(explanation)
                        .foregroundStyle(.secondary)
                }

                Section("Affected items") {
                    ForEach(affectedItems, id: \.self) { item in
                        Text(item)
                    }
                }

                Section {
                    Button("Confirm and apply", action: onApprove)
                        .buttonStyle(.borderedProminent)
                    Button("Don't apply", action: onDeny)
                }
            }
            .navigationTitle("Review before applying")
        }
    }
}
~~~

Do not dismiss the sheet and perform the write in an unrelated callback. The approval event should enter the domain operation through one explicit method.

## 28. Deterministic commit boundary

The commit function should accept an app-owned validated proposal, not raw generated content.

~~~swift
import Foundation

struct TaskRecord: Identifiable, Sendable {
    let id: String
    let title: String
    let category: SuggestedCategory
}

@MainActor
protocol TaskRepository {
    func currentRecord(id: String) throws -> TaskRecord
    func save(_ record: TaskRecord) throws
}

@MainActor
func commit(
    proposal: ValidatedTaskProposal,
    recordID: String,
    repository: any TaskRepository
) throws {
    let current = try repository.currentRecord(id: recordID)
    let updated = TaskRecord(
        id: current.id,
        title: proposal.title,
        category: proposal.category
    )
    try repository.save(updated)
}
~~~

Add version checks, permissions, conflict handling, undo, and audit metadata for a real product. This function should be testable without Foundation Models.

## 29. Context-exhaustion recovery

When the session is full, choose a recovery path explicitly.

~~~swift
import FoundationModels

enum ContextRecovery {
    case removeIrrelevantEntries
    case startWithAppSummary(String)
    case narrowTask
    case fallback
}

func chooseRecovery(
    hasCompactSummary: Bool,
    canNarrowTask: Bool
) -> ContextRecovery {
    if hasCompactSummary {
        return .startWithAppSummary("App-owned summary goes here")
    }
    if canNarrowTask {
        return .narrowTask
    }
    return .fallback
}
~~~

Do not repeatedly append a larger prompt to a full session. App-authored summaries must be scoped, reviewed, and labeled; they are not a hidden memory channel.

## 30. Language and locale gate

Check supported language before presenting a model route that promises a particular language.

~~~swift
import Foundation
import FoundationModels

@MainActor
func modelSupportsCurrentLocale() -> Bool {
    let model = SystemLanguageModel.default
    return model.supportsLocale(Locale.current)
}
~~~

If the locale is unsupported, provide a deterministic or alternate-language fallback. Do not silently pretend that a successful response is fluent or semantically equivalent in every language.

## 31. Feedback attachment policy

Feedback artifacts can be valuable during development, but they may contain interaction context. Gate them behind a deliberate action.

~~~swift
import Foundation
import FoundationModels

struct FeedbackPolicy {
    let userOptedIn: Bool
    let allowsSensitiveContent: Bool
}

@MainActor
func makeFeedbackAttachment(
    session: LanguageModelSession,
    policy: FeedbackPolicy
) -> Data? {
    guard policy.userOptedIn else { return nil }
    guard policy.allowsSensitiveContent else {
        // Prefer a redacted or synthetic reproduction in a real product.
        return nil
    }

    return session.logFeedbackAttachment(
        sentiment: nil,
        issues: [],
        desiredResponseText: nil
    )
}
~~~

Review the current feedback API and data-handling policy before shipping. Do not automatically upload or persist this data.

## 32. Instruments measurement record

Keep measurement metadata separate from user content.

~~~swift
import Foundation

struct ModelPerformanceRecord: Codable, Sendable {
    let build: String
    let os: String
    let device: String
    let promptVersion: String
    let modelLabel: String
    let timeToFirstOutputMS: Int?
    let totalLatencyMS: Int?
    let inputTokens: Int?
    let responseTokens: Int?
    let cancelled: Bool
}
~~~

Use Instruments and the response usage values available in the selected SDK. Measure on a supported physical device; a Mac simulator does not represent on-device model latency, memory, or readiness.

## 33. Unit-test the route boundary

Keep model-dependent work behind a protocol so deterministic state logic can be tested.

~~~swift
import Foundation

protocol SuggestionGenerating: Sendable {
    func suggest(input: String) async throws -> String
}

struct FixedSuggestionGenerator: SuggestionGenerating {
    let result: Result<String, Error>

    func suggest(input: String) async throws -> String {
        try result.get()
    }
}

struct SuggestionStateReducer {
    enum State: Equatable {
        case idle
        case generating
        case candidate(String)
        case failed
        case cancelled
    }

    private(set) var state: State = .idle

    mutating func start() {
        state = .generating
    }

    mutating func succeed(_ value: String) {
        state = .candidate(value)
    }

    mutating func fail() {
        state = .failed
    }

    mutating func cancel() {
        state = .cancelled
    }
}
~~~

The important boundary is that UI transitions, cancellation, validation, and approval can be tested without invoking a live model.

## 34. UI test checklist as code comments

Use a test plan with named cases. The code comments can become test IDs.

~~~swift
// FM-AVAIL-001: model unavailable shows fallback.
// FM-AVAIL-002: model not ready shows retry-later state.
// FM-SESSION-001: second request is serialized or rejected.
// FM-SESSION-002: transcript is not mutated while responding.
// FM-CONTEXT-001: long fixture reaches recovery path.
// FM-STREAM-001: cancel leaves no committed result.
// FM-STREAM-002: late old result cannot replace new request.
// FM-TYPED-001: invalid schema value reaches validation failure.
// FM-TOOL-001: read tool receives bounded arguments.
// FM-TOOL-002: write requires explicit approval.
// FM-TOOL-003: tool failure does not commit.
// FM-A11Y-001: VoiceOver exposes draft and approval meaning.
// FM-PRIV-001: raw prompt is absent from normal logs.
// FM-RELEASE-001: signed archive works on supported device.
~~~

Keep the fixture IDs in the evaluation report and release evidence packet.

## 35. App lifecycle and view disappearance

Decide whether work follows the view or the feature. Do not let a default task modifier make that decision accidentally.

~~~swift
import SwiftUI

struct DraftScreen: View {
    @State private var requestTask: Task<Void, Never>?
    @State private var isGenerating = false

    var body: some View {
        VStack {
            Text(isGenerating ? "Generating…" : "Ready")
            Button("Cancel") {
                requestTask?.cancel()
                requestTask = nil
                isGenerating = false
            }
        }
        .onDisappear {
            requestTask?.cancel()
            requestTask = nil
        }
    }
}
~~~

For durable work, move the operation into an app-owned service and show its state when the view returns. For a one-screen draft, cancellation on disappearance is usually the safer default.

## 36. Privacy-safe logging

Log state transitions and identifiers, not raw prompts or transcripts.

~~~swift
import OSLog

let modelLogger = Logger(
    subsystem: "com.example.app",
    category: "foundation-models"
)

func logGenerationStarted(
    requestID: String,
    promptVersion: String,
    modelAvailable: Bool
) {
    modelLogger.info(
        "generation started id=\(requestID, privacy: .public) prompt=\(promptVersion, privacy: .public) available=\(modelAvailable, privacy: .public)"
    )
}
~~~

Use the actual bundle identifier and choose privacy annotations appropriate to the log value. Never interpolate raw user input into normal production logs.

## 37. Release evidence manifest

A small manifest makes the release boundary auditable.

~~~swift
import Foundation

struct FoundationModelsReleaseEvidence: Codable, Sendable {
    let target: String
    let deploymentTarget: String
    let sdk: String
    let device: String
    let os: String
    let modelAvailabilityTested: Bool
    let fallbackTested: Bool
    let cancellationTested: Bool
    let toolApprovalTested: Bool
    let accessibilityTested: Bool
    let privacyReviewed: Bool
    let archiveInstalled: Bool
    let testFlightInstalled: Bool
}
~~~

This manifest is an evidence index, not proof by itself. Attach the actual test notes, screenshots, logs, and signed-artifact identifiers.

## 38. Recipe assembly checklist

When turning a sketch into an app feature:

- create a named SwiftUI target and set the deployment target;
- import Foundation Models only in the service or feature module that needs it;
- compile every API against the selected SDK;
- put model availability behind an adapter;
- isolate session ownership;
- keep prompts and schemas versioned;
- measure context and latency;
- add a deterministic fallback before adding tools;
- validate typed output;
- require approval for consequential writes;
- test cancellation and concurrent-request protection;
- review VoiceOver, Dynamic Type, reduced motion, keyboard, pointer, and localization;
- inspect privacy logs and transcript retention;
- test on a supported physical device;
- archive and install the signed release artifact;
- exercise TestFlight before calling the route release-ready.

## Related local routes

- [Foundation Models production-route review](../42-framework-deep-dives/111-swiftui-foundation-models-production-route-review.md)
- [Foundation Models production-route design](../21-design-deep-dives/139-swiftui-foundation-models-production-route-review-design.md)
- [Foundation Models production route](../50-capability-recipes/142-swiftui-foundation-models-production-route-review-route.md)
- [Foundation Models sessions](../31-on-device-ai-recipes/00-foundation-model-sessions.md)
- [Foundation Models tool-guided-output recipes](106-foundation-models-tool-guided-output-recipes.md)
- [Prompt evaluation and model-update recipe](../31-on-device-ai-recipes/09-prompt-evaluation-and-model-update-recipe.md)
- [AI review and Liquid Glass shell recipes](23-ai-review-and-liquid-glass-shell-recipes.md)
- [Model capture and device-proof recipes](25-model-capture-and-device-proof-recipes.md)
- [Build, device, and release checklist](../60-verification/01-build-device-and-release-checklist.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SystemLanguageModel unavailable reasons](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.enum/unavailablereason)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [LanguageModelSession response](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/response)
- [LanguageModelSession response content](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/response/content)
- [LanguageModelSession response stream](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/responsestream)
- [Prompt](https://developer.apple.com/documentation/foundationmodels/prompt)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [GenerationOptions](https://developer.apple.com/documentation/foundationmodels/generationoptions)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Guide(description:)](https://developer.apple.com/documentation/foundationmodels/guide%28description%3A%29)
- [GenerationGuide](https://developer.apple.com/documentation/foundationmodels/generationguide)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [LanguageModelError](https://developer.apple.com/documentation/foundationmodels/languagemodelerror)
- [LanguageModelSession.Error](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/error)
- [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
