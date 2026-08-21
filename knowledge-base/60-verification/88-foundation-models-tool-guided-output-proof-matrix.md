# Foundation Models iOS 26 tool and guided-output proof matrix

This matrix defines evidence for an iOS 26 Foundation Models feature that uses a LanguageModelSession, a Tool, guided generation, and a native review surface. It separates documentation knowledge, deterministic code proof, model behavior, device state, system state, and release evidence.

A route sketch or a successful preview is not proof that the on-device model is available, that a tool is authorized, or that a generated proposal is safe to commit.

## Evidence levels

| Level | What it can prove | What it cannot prove |
| --- | --- | --- |
| Official source review | The documented API shape, constraints, and guidance are understood | A project compiles or a device has model assets |
| Type and unit test | Validators, tool boundaries, idempotency, and error mapping behave deterministically | Real model quality or Apple Intelligence readiness |
| Preview | Static state rendering and layout composition | Model availability, tool concurrency, permission, or physical rendering |
| UI test | Focus, buttons, cancellation UI, review state, and fallback transitions with fakes | On-device model output, thermal behavior, or system settings |
| Simulator | Fake-service and state-machine behavior in a repeatable environment | Real Foundation Models availability, model assets, device performance, camera/microphone, or protected services |
| Physical device | Named device, OS build, language, settings, asset readiness, latency, and real model behavior for the tested fixture set | All eligible devices, future model versions, or universal quality |
| Signed/release artifact | Target configuration, entitlements, privacy manifest, package, and build evidence | App Review outcome, production traffic quality, or all regions |

## Source-to-contract map

| Contract | Primary evidence | Required app artifact |
| --- | --- | --- |
| Model availability | SystemLanguageModel availability documentation | Recorded device, OS, Apple Intelligence state, and availability reason |
| Session context | LanguageModelSession and context-window documentation | Prompt/schema/tool budget and overflow behavior |
| Prewarm | iOS 26 release notes and session documentation | Before/after timing trace with request timing separated |
| Guided output | Generable, Guide, GenerationSchema, GeneratedContent | Schema version, validator, complete/incomplete handling |
| Tool calling | Tool and tool-calling article | Tool registry, argument validation, output redaction, call log |
| Tool mode | ToolCallingMode documentation | Allowed/required/disallowed fixtures and exit proof |
| Safety | Generative AI HIG and Foundation Models safety guidance | Curated inputs, refusal/guardrail UI, feedback path |
| Native review | Liquid Glass and accessibility guidance | UI test, VoiceOver pass, Dynamic Type and Reduce Motion screenshots |
| iOS 26 compatibility | iOS 26 release notes | OS/SDK matrix and known-workaround record |
| Release | Xcode archive and testing documentation | Signed artifact, configuration, privacy/data-path review |

## Fixture catalog

Create a small named fixture set before changing a prompt or schema:

| Fixture ID | Input shape | Expected purpose |
| --- | --- | --- |
| FM26-001 | Typical short request | Baseline success |
| FM26-002 | Empty request | Validation and disabled action |
| FM26-003 | Whitespace-only request | Input normalization |
| FM26-004 | Maximum-length request | Boundary and latency |
| FM26-005 | One over the limit | Rejection without model call |
| FM26-006 | Ambiguous entity name | Review and source disambiguation |
| FM26-007 | No matching records | Empty tool result |
| FM26-008 | Stale record reference | Re-resolution and safe failure |
| FM26-009 | Unauthorized record | Tool scope enforcement |
| FM26-010 | Duplicate or conflicting records | Deterministic tie handling |
| FM26-011 | Sensitive source text | Guardrail/refusal and safe copy |
| FM26-012 | Prompt-injection text in a note | Treat retrieved content as data |
| FM26-013 | Unsupported language or locale | Availability and fallback |
| FM26-014 | Oversized source | Context-size recovery |
| FM26-015 | Cancellation during generation | No commit and correct UI |
| FM26-016 | Tool timeout | Retry/manual path |
| FM26-017 | Tool throws domain error | ToolCallError mapping |
| FM26-018 | Repeated Apply | Idempotency |
| FM26-019 | Model returns incomplete streamed output | Draft-only state |
| FM26-020 | Model returns a structurally valid but wrong value | Domain validation and review |
| FM26-021 | Account or workspace switch mid-request | Late-result isolation |
| FM26-022 | Model assets become unavailable | Readiness recovery |
| FM26-023 | Duplicate tool registration | Registry rejection |
| FM26-024 | Associated-value enum tool argument | iOS 26 decoding workaround |
| FM26-025 | Transcript restored without tools | Tool reattachment regression |

Keep private user content out of shared fixtures. Redact or synthesize content and document the retention policy for any captured transcript or output.

## Availability and readiness matrix

| Case | Setup | Expected evidence | Pass condition |
| --- | --- | --- | --- |
| Eligible and ready | Named Apple Intelligence-capable device, iOS 26 build, supported language | Availability result and real response | Feature reaches review with a recorded model state |
| Device not eligible | Device that runs iOS 26 but lacks the required Apple Intelligence capability | Availability result and fallback screenshot | No crash; manual route remains usable |
| Apple Intelligence disabled | Settings state changed before launch | Availability result and explanatory UI | No hidden retry loop or misleading “failed generation” |
| Assets not ready | Simulated or freshly prepared device state where supported | Readiness state and retry behavior | The person can leave and return without data loss |
| Unsupported locale | Device and request language outside the model’s support | Locale and error record | A translated/manual route or clear limitation appears |
| Temporary rate limiting | Repeated controlled requests where the SDK surfaces it | Error mapping and backoff record | No busy-loop; retry is user-visible |
| Offline | Airplane mode or no network | Request result and network trace | Local route remains local; network tool fails separately |

The physical-device record should include model identifier, OS build, app build, language, region, Apple Intelligence setting, model availability, and whether assets were still preparing.

## Session and context tests

| Test | Method | Expected result |
| --- | --- | --- |
| Context budget | Gradually increase instructions, tool definitions, source, and output | The app warns or recovers before an opaque failure |
| Oversized single source | Send a source above the tested budget | Context error maps to “choose a smaller source” |
| Multi-chunk source | Process bounded chunks in separate sessions | Combination is deterministic and provenance is retained |
| Session reuse | Run two related prompts in one session | Intended context is preserved and no stale source leaks |
| Session reset | Start a new record/task | Old source and proposal cannot appear in the new result |
| Concurrent request | Trigger a second request before first completion | App serializes, cancels, or uses another session |
| Prewarm | Measure a prewarm path and a cold path | Timing difference is recorded without calling prewarm readiness |
| Account switch | Switch scope during an active request | Late result is discarded or revalidated |
| Cancellation | Leave the screen or tap Cancel | Request state ends and no side effect occurs |

Record prompt version, schema version, tool registry version, OS build, and elapsed timing. Do not store raw private prompts merely to measure latency.

## Guided-generation proof

| Test | Expected evidence | Pass condition |
| --- | --- | --- |
| Basic Generable type | Complete typed response | All required fields decode |
| Guide range | Values outside the domain range | Validator rejects or route never enables Apply |
| Count constraint | Too many or too few list entries | UI and validator handle bounded result |
| Nested type | Nested properties and optional values | Schema is small enough for the context budget |
| Dynamic schema | Runtime menu or selection | Schema construction errors are preflighted |
| Invalid schema | Conflicting names or references | The feature shows a deterministic setup error |
| Streaming partial | Partial snapshots | Draft label and disabled commit |
| Incomplete GeneratedContent | Completion flag/state | Incomplete output is not persisted |
| Structurally valid wrong value | Plausible but unsupported data | Source lookup and domain validator reject it |
| Refusal | Model declines a guided request | Refusal UI offers a safe alternative |
| Unsupported guide | SDK/model rejects a guide | App narrows the guide or uses deterministic validation |
| Schema evolution | Old fixture against new schema | Versioned evaluator identifies a regression |

A typed value is accepted only after the domain validator succeeds. Guided generation reduces malformed output; it does not replace authorization or factual verification.

## Tool contract proof

For every Tool, run a fake repository or service:

| Test | Expected |
| --- | --- |
| Empty argument | Tool rejects before data access |
| Overlong argument | Tool rejects or clamps under an explicit rule |
| Unauthorized scope | Tool returns no private data |
| No match | Tool returns a bounded empty result |
| Stale reference | Tool or validator reports stale without mutation |
| Duplicate tool name | Registry fails before session creation |
| Concurrent independent calls | Repository remains safe and results are isolated |
| Tool timeout | Error maps to retry/manual state |
| Cancellation | Underlying work observes cancellation where supported |
| Sensitive output | Redaction removes tokens, private URLs, and hidden metadata |
| Large output | Tool truncates or summarizes before returning to the model |
| Tool throws | ToolCallError identifies the tool and app shows a useful recovery |
| Repeated call | Read-only result is safe to repeat |
| Mutation candidate | Mutation is not exposed until confirmation/use-case gate |

The tool output is new prompt context. Count its fields and size as part of the context budget.

## Tool mode proof

| Mode | Fixture | Pass condition |
| --- | --- | --- |
| allowed | Current record lookup | Model may call the tool and can still answer without looping |
| required | Mandatory policy or source lookup | At least one call occurs and the session reaches a final response |
| disallowed | Formatting an already-grounded result | No tool call occurs |
| required with failure | Tool throws or returns unavailable | App exits to a bounded error state |
| mode change | Only if a newer target SDK is explicitly used | Availability and behavior are separately documented |

A required tool without an exit condition is a release blocker. Do not rely on the model eventually deciding to stop.

## Safety and prompt-injection proof

| Test | Expected |
| --- | --- |
| Fixed safe prompt | Normal result |
| Sensitive source transformation | Guardrail behavior is mapped and the permitted transformation path is clear |
| Unsafe or out-of-scope request | Refusal or blocked state |
| Retrieved instruction text | It remains data and cannot alter authorization |
| Tool output with fake policy text | It does not change the app’s deterministic policy |
| Generated destructive request | It becomes a reviewable proposal, not an automatic action |
| Generated purchase/message/delete | No side effect without explicit confirmation and normal use case |
| Error detail | No private prompt, token, path, or account ID leaks to the UI |
| Feedback report | Person can voluntarily report a problematic result |

The permissive content transformation mode is not a general safety bypass and does not change the guided-generation safety path. Test the exact output type and purpose used by the feature.

## Native review and accessibility proof

| Surface | Test | Pass condition |
| --- | --- | --- |
| Ready | VoiceOver focus order | Source, status, input, and primary action are understandable |
| Generating | Cancel and status announcement | A person can stop work and knows it is still running |
| Partial | Draft label and action state | Apply is unavailable until complete and validated |
| Review | Editable fields and source references | Generated and saved values are distinguishable |
| Error | Retry/manual explanation | No raw exception-only message |
| Committed | Confirmation and undo where possible | Outcome is clear |
| Dynamic Type | Largest supported size | No clipped critical labels or unreachable actions |
| Reduce Motion | Re-run with setting enabled | State remains understandable without morphing |
| Increased contrast | System setting | Content and controls retain sufficient contrast |
| Keyboard or alternative input | External keyboard where supported | Focus and actions remain reachable |
| iPad size change | Split view and rotation | Review/action hierarchy remains usable |
| Glass fallback | Light/dark and busy background | Content remains legible without relying on translucency |

Use semantic system controls and roles. Treat custom glass as a visual layer, not as the accessibility contract.

## Physical-device run sheet

For each real model test, record:

- device family and model identifier;
- iOS 26 minor version and build;
- Xcode and SDK version;
- app build and configuration;
- Apple Intelligence setting;
- device language and region;
- model availability result and reason;
- whether model assets were ready;
- network state;
- battery/thermal context if performance is being measured;
- fixture IDs;
- prompt and schema versions;
- start, first-output, completion, and cancellation times;
- tool calls and redacted outcomes;
- validation result;
- review decision;
- whether any domain state changed.

Repeat at least one run after a cold launch and one after the app has been backgrounded. A single successful run does not establish universal device coverage.

## Release and privacy proof

Before shipping:

- inspect the archive’s deployment target and linked Foundation Models symbols;
- verify that no fallback silently changes the provider or data path;
- review entitlements and privacy manifest requirements for any other frameworks in the route;
- confirm no production log retains raw prompts, responses, images, audio, or tool output without a documented reason;
- include a user-facing AI disclosure and fallback;
- run the same acceptance fixtures against the release configuration;
- attach screenshots or recordings of the named device and key states;
- record known SDK or OS release-note issues and the decision to ship, mitigate, or hold.

## Acceptance gates

A feature is a candidate for release evidence only when all are true:

1. The iOS 26 compile slice succeeds with the exact target SDK.
2. Availability and model-readiness states are mapped.
3. Prompt, schema, and tool context are bounded.
4. The fake-service tests pass for validation, authorization, cancellation, and idempotency.
5. Guided output is treated as a proposal and incomplete output cannot commit.
6. Tool mode tests prove an exit path.
7. Safety and prompt-injection fixtures have been reviewed.
8. The SwiftUI review shell passes accessibility and adaptation checks.
9. A named physical device produces the intended behavior for the fixture set.
10. The signed artifact preserves the intended local/network data path.
11. The non-AI fallback remains usable.
12. The evidence is labeled as target-specific rather than universal.

## Evidence record template

~~~yaml
feature: "Foundation Models local proposal"
sdk: "Xcode 26.x / iOS 26 SDK"
deployment_target: "iOS 26.0"
app_build: "record build"
device:
  model: "record model identifier"
  os_build: "record OS build"
  language: "record language"
  region: "record region"
  apple_intelligence: "enabled or disabled"
  model_availability: "record documented state"
  assets_ready: "yes or no"
prompt_version: "fm26.prompt.1"
schema_version: "launch-summary.v1"
tool_registry_version: "tools.v1"
fixtures:
  - id: "FM26-001"
    result: "record"
    tool_calls: 0
    validation: "pass or fail"
    committed: false
ui:
  voiceover: "pass or fail"
  dynamic_type: "pass or fail"
  reduce_motion: "pass or fail"
fallback: "record"
privacy_review: "record"
evidence_limits: "named-device and fixture-specific"
~~~

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generating content and performing tasks with Foundation Models](https://developer.apple.com/documentation/foundationmodels/generating-content-and-performing-tasks-with-foundation-models)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Generating Swift data structures with guided generation](https://developer.apple.com/documentation/foundationmodels/generating-swift-data-structures-with-guided-generation)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GeneratedContent](https://developer.apple.com/documentation/foundationmodels/generatedcontent)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [LanguageModelSession.GenerationError](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/generationerror)
- [iOS and iPadOS 26 release notes](https://developer.apple.com/documentation/ios-ipados-release-notes/ios-ipados-26-release-notes)
- [Generative AI](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
