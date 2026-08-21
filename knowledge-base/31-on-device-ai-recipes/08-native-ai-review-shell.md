# Native AI Review Shell

This recipe composes Foundation Models with a native SwiftUI review workflow and a restrained Liquid Glass action layer. It is for proposals that can help a person draft, organize, summarize, classify, or prepare a change, while deterministic code and explicit user review remain responsible for domain truth and side effects.

## Capability contract

```text
source -> availability -> bounded session -> proposal
       -> deterministic validation -> review/edit
       -> explicit approval -> domain commit -> confirmed projection
```

Never make the model response the final state. The source may be a text document, selected photo, camera observation, transcript, translation, or local record. Preserve the source and provenance so the person can inspect what the proposal was based on.

## API and ownership matrix

| Responsibility | API route | App-owned contract | Evidence needed |
| --- | --- | --- | --- |
| Check model readiness | `SystemLanguageModel.default.availability`, `isAvailable`, `supportsLocale(_:)`, `contextSize` | Map `.available` and each `UnavailableReason` to a useful UI/manual route | Physical target OS/device/region/language/Apple Intelligence configuration, not only a simulator enum. |
| Create a bounded session | `LanguageModelSession(instructions:)` or the current model/tools/transcript initializer | Prompt/instruction version, input budget, cancellation, transcript retention, session lifetime, and privacy | Compile selected signature, context fixture, cancellation, model-not-ready, and memory/latency measurement. |
| Generate typed output | `@Generable`, `@Guide`, `LanguageModelSession.respond(generating:)` | Small schema, allowed ranges/enums/counts, partial/invalid/refusal handling, deterministic validation | Fixture quality/evaluation, schema migration, context size, refusal, and manual correction burden. |
| Read current app state | Foundation Models `Tool` with typed arguments/output | Tool is query-only unless an explicit approval boundary exists; re-read current state and minimize output | Tool schema/context cost, stale data, authorization, cancellation, error, and no-network behavior. |
| Perform a side effect | App-owned use case after review, or a separately designed App Intent/system route | Idempotency key, authorization, confirmation, conflict policy, commit result, and recovery | Domain persistence/server/device evidence; model/tool callback is never commit proof. |
| Preserve/restore context | `Transcript`, session `transcript`, `prewarm(promptPrefix:)` where useful | Store only the minimum safe history; version prompts/schemas and expire sensitive context | Rehydration, context overflow, app termination, account switch, privacy/retention, and performance. |
| Render the review | SwiftUI `NavigationStack`, `Form`, `sheet`, `confirmationDialog`, focus/accessibility APIs, optional `GlassEffectContainer` | Source/provenance/proposal/validation/draft/commit state; glass only for related actions | Preview matrix, accessibility task completion, Dynamic Type/localization, reduced effects, and physical ergonomics. |

## Availability state

```text
checking -> available
checking -> deviceIneligible | appleIntelligenceDisabled | modelNotReady
checking -> unsupportedLanguage | unavailableOther
available -> sessionPreparing -> generating
generating -> proposalReceived | cancelled | contextExceeded | refusal | guardrailViolation | failed
```

Use the exact current availability and error cases from the selected SDK. `modelNotReady` is not the same as “the prompt failed”; it may require the person to wait or change system settings. If the model is unavailable, retain the manual workflow rather than repeatedly retrying or showing an empty glass panel.

## Proposal data model

Keep the proposal separate from the record it may change:

```swift
struct ProposalEnvelope<Value: Sendable>: Sendable {
    let operationID: UUID
    let sourceRevision: String
    let promptVersion: String
    let schemaVersion: Int
    let createdAt: Date
    let value: Value
    let provenance: [SourceReference]
    let validation: ValidationState
}
```

The example is an architecture shape, not a complete model implementation. Add only the fields the review requires. Keep generated text, tool output, source references, user edits, and canonical record values distinguishable in storage and analytics. Do not log raw private prompts or transcripts by default.

## Guided generation discipline

Use `@Generable` for a small, task-specific output type. Add `@Guide` only when names and the type shape are not enough; guide descriptions and schema structure consume context. Use bounded enums/counts/ranges for values that must be safe to render, then validate them again in Swift.

```swift
@Generable
struct DraftAction {
    @Guide(description: "A short title with no more than 80 characters")
    var title: String

    @Guide(.anyOf(["low", "medium", "high"]))
    var priority: String

    var explanation: String
}
```

The exact `Guide` overloads and literal constraints must be checked in the selected SDK. Guided output constrains generation; it does not make content true, authorized, or safe. Validate length, dates, IDs, access, duplication, policy, and user intent before rendering an approval action.

## Tool boundary

Tools can gather current information or perform code-defined work, but a model deciding to call a tool is not user authorization. Separate tools into:

| Tool kind | Safe default |
| --- | --- |
| Read-only query | Return the minimum current data needed to answer; enforce account/permission checks inside the tool. |
| Preview/calculation | Return a deterministic proposal or estimate with inputs and limitations; no external mutation. |
| Consequential action | Do not mutate directly from an opaque model call; require an approval record and an idempotent domain use case. |
| System-surface action | Use App Intent/system ownership when appropriate, with parameter resolution and a separate confirmation/result route. |

Keep tool names/descriptions/schemas short because they consume context. Treat retrieved text, webpages, files, and tool output as untrusted data, not instructions. If a tool returns an error or stale record, show that state to the model/UI and do not silently substitute a fabricated value.

## SwiftUI review composition

```text
NavigationStack
  -> source/provenance header
  -> proposal Form/editor
  -> validation and unknown-state explanation
  -> optional GlassEffectContainer
       -> Edit
       -> Reject
       -> Approve / Save
       -> Retry / Cancel
  -> committed result or repair route
```

Use a standard `Button`, `Form`, `TextEditor`, `Label`, `ProgressView`, or `ContentUnavailableView` before adding custom glass. The custom effect, if justified, belongs around the related action group and should not obscure source content, generated text, or validation messages. Set focus to the new proposal/error/result intentionally, and provide an accessibility action equivalent for every gesture or morph.

## Safety and evaluation contract

Apple’s Foundation Models guidance describes built-in guardrails and refusal states while also requiring app-specific safety design. Add a feature-specific layer:

- bound user/external input before prompting;
- keep untrusted content out of trusted instructions;
- test nonsensical, sensitive, vague, adversarial, and combined-context inputs;
- handle string refusals and guided-generation refusal errors without pretending they are valid proposals;
- show a clear recovery message and manual path;
- version prompts, schemas, model/OS configuration, and fixture sets;
- measure correctness, harmful/unsafe output, validation rejection, correction burden, latency, context use, memory, thermal, and battery where relevant;
- provide a user feedback/reporting route without retaining more private content than necessary.

## Verification matrix

| Level | Proves | Does not prove |
| --- | --- | --- |
| Unit/reducer | Availability mapping, schema validation, proposal state, idempotency, conflict, fallback | Model quality, UI accessibility, hardware readiness, real system delivery |
| Prompt/evaluation fixture | Behavior for recorded inputs/configuration and correction burden | All users, languages, models, devices, or future OS updates |
| SwiftUI preview/UI test | Review layout, focus, labels, loading/error/approval states | Foundation Model availability, camera/audio, actual glass material/performance |
| Simulator | Deterministic UI and fake service branches | On-device model readiness, Neural Engine/memory/thermal, physical system surface |
| Physical device | Named model/OS/language, material legibility, input, accessibility, latency/thermal, system integration | Every supported device or production delivery |
| Signed/release | Target membership, entitlements, privacy metadata, TestFlight/App Store configuration | User comprehension, model quality, App Review approval, or production success without those tests |

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel.Availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.enum)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Transcript](https://developer.apple.com/documentation/foundationmodels/transcript)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Updating prompts for new model versions](https://developer.apple.com/documentation/foundationmodels/updating-prompts-for-new-model-versions)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [GlassEffectContainer](https://developer.apple.com/documentation/swiftui/glasseffectcontainer)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
