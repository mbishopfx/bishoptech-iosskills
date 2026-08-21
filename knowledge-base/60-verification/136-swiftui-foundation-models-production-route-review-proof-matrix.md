# Foundation Models production-route proof matrix

This matrix defines evidence for an iOS 26 Foundation Models feature. It separates source compatibility, model readiness, output quality, domain correctness, privacy, accessibility, physical-device behavior, and release readiness. A single artifact may support one claim without proving the others.

## Claim-to-evidence matrix

| Claim | Minimum evidence | Helpful artifact | Not proof by itself |
| --- | --- | --- | --- |
| the target can use Foundation Models | named target, SDK, deployment, import, availability branch | build log and configuration snapshot | a source file or autocomplete result |
| the device can run the model lane | supported physical device, Apple Intelligence state, availability result | sanitized device matrix | simulator or compile |
| model assets are ready | physical run showing available state and a successful request | model readiness capture | device eligibility alone |
| a prompt is stable enough | fixture results labeled with prompt and model version | evaluation report | one successful response |
| context is within budget | token measurements for instructions, prompt, schema, tools, transcript, and response | Instruments or token report | a short-looking string |
| a session is safe to reuse | one-owner lifecycle, no concurrent requests, no transcript mutation while responding | concurrency tests and logs | a singleton session |
| streaming is correct | partial output, stop, cancellation, stale-result protection, final-state test | UI test and physical run | a stream loop that renders text |
| typed generation is valid | schema decode, field validation, semantic checks, fallback | fixture table | Generable conformance |
| a tool is safe | argument validation, authorization, repeated-call behavior, failure, cancellation | tool test harness | a successful callback |
| a write is authorized | explicit user approval and commit-time revalidation | approval recording and domain test | tool-calling mode |
| model quality meets the product bar | fixture suite across input classes and model versions | signed evaluation artifact | fluent prose |
| fallback is usable | Apple Intelligence disabled/not-ready path still completes core task | physical fallback capture | an alert |
| privacy behavior matches policy | input, transcript, tool, logs, feedback attachment, and external data-flow review | privacy checklist and redacted log | “on device” copy |
| accessibility works | VoiceOver, Dynamic Type, reduced motion, keyboard, pointer, alternate input | accessibility run record | default SwiftUI controls alone |
| physical UI works | real target device and settings, including interruption and model readiness | screen recording and test notes | simulator screenshot |
| archive is releasable | signed archive installed and tested as release build | archive/export receipt | successful Debug build |
| TestFlight route works | TestFlight install on a supported device and real flow | tester evidence | local archive |
| App Store route is ready | metadata, entitlements, privacy, capabilities, and review notes checked | release checklist | upload success |

## Required environment record

Every Foundation Models fixture or bug report should record:

- app version and build;
- target name and configuration;
- Xcode and SDK version;
- deployment target;
- device model;
- OS build;
- Apple Intelligence enabled or disabled;
- model availability and unavailable reason when applicable;
- model/use-case selection;
- prompt version;
- schema version;
- tool set and tool-calling mode;
- language and locale;
- network state when the route contains tools;
- whether the request was single-turn, multi-turn, or rehydrated;
- token measurements if available;
- latency and cancellation timing;
- sanitized output classification.

Do not attach raw private prompts or transcripts to a shared report by default.

## Availability and fallback tests

### Device and settings matrix

| Case | Expected behavior | Evidence |
| --- | --- | --- |
| supported device, Apple Intelligence on, model ready | model affordance enabled | physical-device capture and log |
| Apple Intelligence off | clear explanation and deterministic fallback | settings state plus flow completion |
| device ineligible | no misleading retry loop | physical or supported simulation of branch |
| model not ready | retry later and fallback | controlled test or observed device state |
| app returns from Settings | availability refreshes | scene transition test |
| OS/model update | fixture suite rerun | versioned evaluation comparison |
| unknown unavailable reason | generic safe fallback | unit test over default branch |

The UI should not infer availability from device model alone. The current framework result is authoritative for the request.

## Session, transcript, and concurrency tests

Test the session coordinator rather than only the view:

1. start one request and observe isResponding state;
2. attempt a second request before the first finishes;
3. verify the app prevents or handles concurrentRequests;
4. attempt transcript mutation while a request is responding;
5. verify the app does not mutate history in the invalid window;
6. cancel a request and start a new one;
7. verify the old result cannot overwrite the new state;
8. rehydrate a sanitized transcript;
9. verify the rehydrated session is associated with the right task and prompt version;
10. force context exhaustion;
11. verify compaction or restart preserves the user-owned source but not untrusted hidden state;
12. navigate away during generation and inspect task cancellation and late-result behavior.

Evidence should include request IDs and phase transitions without raw private content.

## Context-budget tests

Use a deterministic fixture set:

| Fixture | Stress |
| --- | --- |
| short prompt | baseline latency and output |
| long user input | prompt trimming policy |
| long instructions | instruction budget |
| large schema | Generable overhead |
| many tools | tool-definition overhead |
| long transcript | context exhaustion and recovery |
| long output cap | malformed or incomplete response behavior |
| mixed attachments | supported content and retention policy |

Record prompt, instructions, transcript, and response token counts where the selected SDK exposes them. Compare the measured values to the current context-size property. A route should fail predictably before it becomes a blank screen.

## Streaming and cancellation proof

| Test | Expected result |
| --- | --- |
| first partial snapshot | shows draft state and stable controls |
| stop during generation | stream ends or task cancels; no commit |
| view disappears | request is cancelled or intentionally transferred |
| new request supersedes old | old partials and final output are ignored |
| response completes | final candidate is validated before promotion |
| refusal/error arrives | readable state with fallback |
| repeated cancel | idempotent UI behavior |
| slow device | no permanent glass spinner or inaccessible control |

Use a fake model boundary or fixture driver for deterministic UI tests, then repeat the key route on a supported physical device. A fake response proves state handling, not model performance.

## Guided-generation proof

For each Generable or dynamic schema:

- schema construction succeeds for the target SDK;
- required fields decode;
- enum and range constraints are validated;
- optional values have explicit UI treatment;
- maximum collection count is enforced;
- malformed or incomplete output reaches an error/fallback state;
- semantic validation rejects impossible or unauthorized values;
- schema complexity and token use are measured;
- includeSchemaInPrompt behavior is compared when relevant;
- typed candidates remain editable before commit.

Do not count a decoding success as a semantic success.

## Tool-calling proof

### Read tool

- arguments are narrow and validated;
- current data source is deterministic;
- tool output contains only necessary fields;
- parallel or repeated calls do not corrupt state;
- tool failure is visible;
- user data scope is intentional;
- model cannot use the tool to bypass app authorization.

### Write tool

- model call creates a proposal or enters an approval state;
- approval names the consequence;
- authorization is rechecked at commit;
- record versions or conflicts are checked;
- retry is idempotent;
- cancellation has a defined boundary;
- denial produces no write;
- partial tool output produces no write;
- post-commit UI reflects the real domain result.

### Required tool mode

If tool calling is required, prove that the session has an exit condition. A tool that always returns a successful response can accidentally create a loop if the prompt does not define completion.

## Error and safety matrix

| Failure | UI state | Deterministic response |
| --- | --- | --- |
| model unavailable | unavailable | fallback |
| assets not ready | preparing/not ready | retry later |
| context exceeded | error with recovery | compact/restart/narrow |
| refusal or guardrail | respectful failure | edit input or fallback |
| rate limited | retry state | bounded retry |
| timeout | timeout state | retry or fallback |
| unsupported language/locale | explain limitation | supported-language route |
| decoding failure | invalid candidate | plain or manual route |
| unsupported guide | developer-visible diagnostic | simplify schema/fallback |
| concurrent request | guarded UI | serialize or separate session |
| tool failure | tool-specific error | retry or deny |
| cancellation | cancelled | preserve source, no commit |

Do not expose raw error diagnostics that reveal private prompt or tool data.

## Prompt and model-version evaluation

Run each fixture against:

- the oldest supported OS/model combination;
- the current development OS/model;
- the next model version when available for testing;
- Apple Intelligence unavailable fallback;
- the target language and locale set.

Compare:

- successful completion;
- structural validation;
- semantic validation;
- refusal/guardrail behavior;
- unwanted tool calls;
- token usage;
- time to first output;
- total latency;
- cancellation;
- privacy/logging behavior.

If an update changes output, record whether the prompt, schema, tool descriptions, fallback, or product copy needs a versioned change. Do not overwrite old evidence.

## Privacy and accessibility proof

### Privacy

- inventory prompt inputs;
- identify data that remains on device;
- identify tool or server boundaries;
- review transcript retention and deletion;
- inspect analytics and crash logs;
- sanitize feedback attachments;
- test notification, screenshot, and background surfaces;
- verify App Intent, Spotlight, widget, and system-context exposure.

### Accessibility

- VoiceOver reads source, draft status, output, and approval consequence;
- Dynamic Type does not clip the result or hide controls;
- reduced motion does not remove state meaning;
- increased contrast preserves control boundaries;
- keyboard and pointer can start, stop, edit, approve, deny, and dismiss;
- focus moves predictably through sheets and changing result regions;
- localized strings remain concise and accurate;
- no state depends only on shimmer, color, or blur.

## Physical-device and release proof

The final gate must include:

1. supported physical device;
2. Apple Intelligence enabled and model ready;
3. model-unavailable fallback;
4. cancellation and interruption;
5. accessibility pass;
6. privacy/log review;
7. signed release archive installed;
8. TestFlight install;
9. App Store capability and metadata review.

Archive validation proves the artifact is packaged and signed. It does not prove model assets are ready, output quality, tool authorization, or physical behavior. TestFlight distribution proves the delivered build can be installed through that path; it still needs the real feature flow on the target device.

## Evidence packet template

Use one packet per release candidate:

- build and target;
- OS, device, SDK, and model version;
- availability matrix;
- fixture report;
- token and latency report;
- session/concurrency/cancellation tests;
- guided-generation validation;
- tool approval and failure tests;
- privacy and accessibility sign-off;
- physical-device capture;
- archive/export/install result;
- TestFlight result;
- known limitations and fallback copy.

## Related local routes

- [Foundation Models production-route review](../42-framework-deep-dives/111-swiftui-foundation-models-production-route-review.md)
- [Foundation Models production-route design](../21-design-deep-dives/139-swiftui-foundation-models-production-route-review-design.md)
- [Foundation Models production route](../50-capability-recipes/142-swiftui-foundation-models-production-route-review-route.md)
- [AI evaluation and safety checklist](03-ai-evaluation-and-safety-checklist.md)
- [Build, device, and release checklist](01-build-device-and-release-checklist.md)
- [Permission, entitlement, and privacy checklist](04-permission-entitlement-and-privacy-checklist.md)
- [Accessibility and adaptability checklist](02-accessibility-and-adaptability-checklist.md)
- [Foundation Models tool-guided-output proof matrix](88-foundation-models-tool-guided-output-proof-matrix.md)
- [Prompt evaluation and model-update recipe](../31-on-device-ai-recipes/09-prompt-evaluation-and-model-update-recipe.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [SystemLanguageModel availability](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.property)
- [SystemLanguageModel unavailable reasons](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel/availability-swift.enum/unavailablereason)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [LanguageModelSession.Error](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/error)
- [Transcript](https://developer.apple.com/documentation/foundationmodels/transcript)
- [Prompt](https://developer.apple.com/documentation/foundationmodels/prompt)
- [Managing the context window](https://developer.apple.com/documentation/foundationmodels/managing-the-context-window)
- [GenerationOptions](https://developer.apple.com/documentation/foundationmodels/generationoptions)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [GenerationGuide](https://developer.apple.com/documentation/foundationmodels/generationguide)
- [Tool](https://developer.apple.com/documentation/foundationmodels/tool)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Foundation Models updates](https://developer.apple.com/documentation/updates/foundationmodels)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
