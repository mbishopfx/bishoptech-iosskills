# Prompt Evaluation and Model-Update Recipe

Use this recipe when an app depends on Foundation Models for summarization, extraction, classification, drafting, or tool-assisted work. It turns a prompt from a demo artifact into a versioned, repeatable product input with measurable failure boundaries.

The recipe does not claim that a prompt, model, or fixture set is universally accurate. It records what was tested, under which SDK/device/model configuration, and what remains unproven.

## Route contract

```text
user outcome
  -> bounded input and trusted instructions
  -> versioned prompt/schema/tools
  -> availability and context checks
  -> model response/proposal
  -> deterministic validation
  -> human review or safe fallback
  -> domain action and recorded result
```

A passing language response is only one step. A feature is useful when the complete route reduces work for the person without introducing unacceptable safety, privacy, authorization, or resource failures.

## Evaluation record

Create a redacted record for every evaluation run:

```swift
struct EvaluationConfiguration: Sendable, Codable {
    let featureID: String
    let appVersion: String
    let sdkVersion: String
    let osBuild: String
    let device: String
    let locale: String
    let promptVersion: String
    let schemaVersion: Int
    let toolVersion: String?
    let fixtureSetVersion: String
}

struct EvaluationFixture: Sendable, Codable {
    let id: String
    let category: Category
    let redactedInput: String
    let expectedInvariants: [String]

    enum Category: String, Codable {
        case representative
        case empty
        case ambiguous
        case long
        case multilingual
        case adversarial
        case privacySensitive
        case lifecycle
        case sideEffect
    }
}
```

This is a documentation shape, not a complete Foundation Models test harness. Store only the minimum input needed for reproducibility. Use synthetic or redacted fixtures for private prompts, files, transcripts, health data, credentials, and tool payloads.

## Fixture taxonomy

| Category | Include |
| --- | --- |
| Representative | Normal inputs from the primary workflow, with expected user outcome. |
| Empty | No text, no detected content, no matching entity, or missing required field. |
| Ambiguous | Multiple plausible interpretations, similar names, unclear dates, or conflicting evidence. |
| Long/large | Inputs near context, character, image, or processing limits. |
| Multilingual | Supported locales, RTL text, names/numbers, code switching, and unsupported-language fallback. |
| Adversarial/untrusted | Instruction-like source content, prompt injection, malformed tool arguments, and hostile text. |
| Privacy-sensitive | Redaction, deletion, denied access, account switch, protected data, and retention boundaries. |
| Lifecycle | Cancellation, view disappearance, repeated submission, interruption, background/foreground, restart, and model-not-ready. |
| Side effect | Duplicate approval, stale source, revoked authorization, conflict, rejection, and partial failure. |

Each fixture should state the expected boundary, not a brittle exact paragraph. For structured output, define field-level invariants, allowed ranges, required source coverage, and forbidden claims.

## Metrics that match the feature

| Metric | What to measure |
| --- | --- |
| Schema validity | Whether generated output can be represented by the selected type and satisfies basic field constraints. |
| Groundedness | Whether values can be traced to supplied source material or a verified tool result. |
| Omission/invention | Important source facts omitted; unsupported facts added. |
| Constraint adherence | Length, enum, date, range, locale, policy, and formatting rules. |
| Safety/refusal | Unsafe, private, or disallowed input handling and useful recovery path. |
| Tool correctness | Tool selected when appropriate, arguments valid, output bounded, and exit condition reached. |
| Review burden | Fields edited, rejected proposals, time to approval, and reason for correction. |
| User outcome | Whether the person completed the task more reliably or quickly than the manual baseline. |
| Context/resource | Token use, context overflow, latency, cancellation, memory, thermal, and battery notes. |

Do not report one aggregate score without preserving the failure categories. A higher average can hide an unacceptable regression in safety, authorization, or a high-impact field.

## Prompt experiment discipline

Change one meaningful variable at a time:

1. freeze the fixture set and evaluator;
2. record the prompt/instructions/schema/tool configuration;
3. run the baseline and candidate under the same configuration;
4. compare every metric and inspect failures by category;
5. keep the candidate only when it improves the user outcome without violating safety or resource thresholds;
6. rerun the full set after any accepted change.

Short, explicit prompts are usually easier to measure and less expensive in context. If a long task fails, split it into simpler sessions or use deterministic preprocessing. Do not hide a prompt change inside a copy edit without incrementing its version.

## Model-update procedure

When Apple updates the system model or the app changes its deployment/SDK boundary:

```text
old model + old prompt -> baseline results
new model + old prompt -> compatibility results
new model + candidate prompt -> adoption results
                         -> decision / rollback / new version
```

Record the OS/build and model configuration even when the Swift source is unchanged. Review:

- instruction following and schema validity;
- tool selection and required/allowed/disallowed behavior;
- groundedness and unsupported claims;
- refusals and sensitive-input handling;
- correction/rejection burden;
- context usage and overflow recovery;
- latency, memory, thermal, and battery behavior.

If a new model is more fluent but less grounded or more expensive, keep the old prompt/route or narrow the task. Do not widen a product claim from “tested on this fixture set” to “reliable everywhere.”

## Prompt storage options

| Strategy | Strength | Boundary |
| --- | --- | --- |
| Bundled Swift/text resource | Offline and simple | Requires an app update to change. |
| String catalog | Versionable and localizable in Xcode | Localization changes require evaluation; do not assume translation preserves behavior. |
| Remote configuration | Faster rollout/rollback | Requires network, signature/integrity, caching, offline, privacy, and server-availability policy. |
| Availability-selected variants | Can adapt to known OS/model behavior | Availability checks do not replace old/new evaluation. |

Keep a prompt changelog and associate the active version with every proposal and evaluation result.

## Route sketch for a testable coordinator

```swift
enum EvaluationPhase: Equatable {
    case checkingAvailability
    case preparingContext
    case generating(fixtureID: String)
    case validating(fixtureID: String)
    case recorded(EvaluationResult)
    case skipped(reason: String)
    case failed(String)
}

struct EvaluationResult: Equatable, Sendable {
    let fixtureID: String
    let schemaValid: Bool
    let grounded: Bool
    let safetyPassed: Bool
    let reviewRequired: Bool
    let notes: [String]
}
```

The coordinator should use a fake model/proposal source for deterministic unit and UI tests, then run the real Foundation Models route separately on named physical devices. Do not make previews or simulator fixtures depend on model availability.

## Privacy and retention

Evaluation infrastructure is part of the product’s data surface. Decide before collecting results:

- whether raw prompts, images, audio, transcripts, or tool output are retained;
- how private fixtures are synthesized or redacted;
- who can access results and how long they live;
- whether logs include prompt text, model output, entity IDs, or account scope;
- how account-switch and deletion requests affect stored evaluations;
- how a production feedback report is separated from a test fixture.

Prefer aggregate scores and failure labels. If a raw artifact is necessary, document consent, access control, encryption, retention, and deletion.

## Ship/hold decision

| Result | Decision |
| --- | --- |
| API does not compile or availability is not mapped | Hold implementation. |
| Schema/validation failure on critical fields | Narrow the task or keep the manual path. |
| Unsafe/private/unauthorized proposal | Hold; add guardrails, source boundaries, and review. |
| High correction burden | Compare with the deterministic baseline before shipping. |
| Context overflow or resource failure | Split the route, reduce context, or narrow supported inputs. |
| Fixture regression after model update | Keep the prior route, revise/version the prompt, or expand fallback. |
| All recorded thresholds pass | Candidate for target-specific device/system/release verification; not universal proof. |

## Evidence matrix

| Evidence level | Proves | Does not prove |
| --- | --- | --- |
| Source review | The documented API and guidance are understood | Compilation or runtime availability |
| Unit/evaluator fixture | Deterministic scoring and recorded behavior for fixtures | Every user, locale, model, or device |
| Preview/UI test | State rendering, review controls, accessibility labels, fallback layout | Real model quality or hardware readiness |
| Simulator | Fake service branches and repeatable UI behavior | On-device model, thermal, camera/audio, or system-surface behavior |
| Physical device | Named model/OS/language/resource behavior | All supported devices or future model versions |
| Signed/release build | Target/configuration/privacy/package evidence | App Review approval, production delivery, or universal quality |

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [Prompting an on-device foundation model](https://developer.apple.com/documentation/foundationmodels/prompting-an-on-device-foundation-model)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Evaluating prompts to measure performance and improve model responses](https://developer.apple.com/documentation/foundationmodels/evaluating-prompts-to-measure-performance-and-improve-model-responses)
- [Evaluating language model responses](https://developer.apple.com/documentation/Evaluations/evaluating-language-model-responses)
- [Updating prompts for new model versions](https://developer.apple.com/documentation/foundationmodels/updating-prompts-for-new-model-versions)
- [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [GenerationOptions](https://developer.apple.com/documentation/foundationmodels/generationoptions)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [Testing asynchronous code](https://developer.apple.com/documentation/testing/testing-asynchronous-code)
- [XCTest](https://developer.apple.com/documentation/xctest)
