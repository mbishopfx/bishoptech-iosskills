# Advanced Foundation Models provider and multimodal proof matrix

This matrix proves the advanced route one boundary at a time. Provider selection, model capability, image source, dynamic profile, tool loop, quality, privacy, and release evidence are separate claims.

## Claim matrix

| Claim | Minimum evidence | Not enough |
| --- | --- | --- |
| the selected provider is available | target/OS branch and provider availability result | provider initializer |
| the provider supports the request | LanguageModelCapabilities check for vision, tools, guided output, or reasoning | plain-text success |
| PCC is authorized | managed entitlement/eligibility and physical-device availability | a PCC symbol in source |
| PCC quota is usable | quota state and request result | available state |
| the route stays local | on-device model plus network/offline test and log review | “on device” copy |
| the data path is disclosed | UI copy, privacy review, and provider route record | a settings label |
| an image is the intended source | physical source selection, orientation, label, revision, and attachment record | a thumbnail |
| attachment orientation is correct | captured source and model/tool result with orientation fixture | default orientation |
| image output is source-faithful | Vision/OCR/barcode or human-reviewed fixture comparison | fluent description |
| dynamic instructions match app state | phase fixtures and transcript/tool-set inspection | a DynamicInstructions conformance |
| history transform is safe | before/after history fixtures and sensitive-entry test | a shorter context |
| profile handoff is controlled | transition matrix with provider, tools, history, and cancellation | a state variable |
| custom provider uses the framework contract | package, capabilities, executor, stream, error, and cancellation tests | LanguageModel conformance |
| custom provider authentication is safe | secret/transport/expiry/failure tests | a login screen |
| tool loop exits | required-mode exit test, call limit, cancellation, and failure | a tool result |
| tool output is current | deterministic source test and timestamp/revision | model statement |
| write action is authorized | approval and commit-time revalidation | tool-calling mode |
| provider choice improves quality | shared evaluation dataset and metrics | anecdotal output |
| advanced route is performant | Instruments trace with sanitized handling | stopwatch around respond |
| accessibility works | VoiceOver, Dynamic Type, reduced motion, keyboard, pointer, and alternate input | native controls alone |
| release artifact works | signed archive/TestFlight install on supported device | Debug compile |

## Environment record

Record for every provider or multimodal run:

- app version and build;
- target and deployment;
- Xcode and SDK;
- device model and OS build;
- provider identifier;
- provider availability;
- capabilities;
- PCC entitlement state when relevant;
- quota status when relevant;
- Apple Intelligence state for system model;
- model asset readiness for local custom provider;
- network state;
- locale and supported-language result;
- prompt and schema versions;
- profile and phase;
- attachment source, orientation, label, and revision;
- history transform identifier;
- tool list and calling mode;
- evaluation fixture ID;
- cancellation and timeout timing;
- sanitized output classification.

Keep raw image, prompt, transcript, and trace contents out of shared evidence unless the privacy policy explicitly permits them.

## Provider availability matrix

| Case | Expected behavior | Evidence |
| --- | --- | --- |
| system model available | local route offered | physical device |
| Apple Intelligence disabled | local route unavailable with fallback | settings state and fallback completion |
| system model not ready | retry-later state | device state or controlled branch |
| PCC unavailable on iOS 26 | guarded code uses on-device/fallback | deployment test |
| PCC unavailable by region/device | no misleading cloud action | provider state |
| PCC quota approaching | status and alternative route | quota fixture |
| PCC quota reached | no repeated failing requests | quota fixture |
| custom local model assets missing | asset-ready fallback | model delivery/device test |
| custom server unavailable | network error and local/manual fallback | offline test |
| provider capability missing | route disabled or staged fallback | capability test |

Do not test provider selection only on a device where every lane is ready. The fallback branch is part of the feature.

## Capability negotiation tests

For every request type:

1. select a model with the required capability;
2. verify the capability set;
3. dispatch the request;
4. select a model without that capability;
5. verify that the app prevents or catches unsupported capability;
6. show a useful fallback;
7. record the provider and capability result.

Test combinations:

- vision plus guided generation;
- vision plus tool calling;
- reasoning plus tool calling;
- guided generation without tools;
- plain text on every provider;
- external provider with no offline support.

## Image source proof

### Source fixtures

| Fixture | What it proves |
| --- | --- |
| CGImage with no rotation | baseline attachment |
| camera frame with right orientation | orientation transform |
| CIImage with color profile | image conversion path |
| CVPixelBuffer from capture | live-frame attachment and lifetime |
| image file URL | URL and UTType validation |
| cropped region | preprocessing and provenance |
| two labeled images | ordering and comparison |
| missing or deleted URL | failure and fallback |
| limited Photos selection | permission and ownership |
| image with sensitive metadata | privacy/metadata handling |

Capture the source revision, attachment label, and expected tool/model behavior. A generated caption must be compared against a human or specialized source criterion when quality matters.

### Image tool proof

For OCRTool, BarcodeReaderTool, and custom ImageReference tools:

- the model can identify the intended attachment label;
- a missing reference produces a clear failure;
- the tool receives only allowed images;
- orientation and crop are correct;
- output contains source/confidence/freshness where required;
- tool can be cancelled;
- repeated or parallel calls do not corrupt state;
- no sensitive image is retained beyond policy;
- the app distinguishes tool output from model interpretation.

## Dynamic profile proof

Create a transition table:

| From | To | Provider | Tools | History | User-visible change |
| --- | --- | --- | --- | --- | --- |
| inspect | classify | on-device | OCR/vision | selected image | typed label review |
| classify | enrich | PCC or approved provider | read-only search | compact result | data-path message |
| enrich | review | selected provider | no writes | proposal/source revision | approval action |
| review | commit | no model | domain service | none required | deterministic progress |
| any | fallback | local/manual | none | source preserved | standard workflow |

For each transition, prove:

- profile change occurs at a deterministic app state;
- capability check runs;
- provider availability runs;
- history projection is correct;
- tools are added/removed as expected;
- cancellation stops the old phase;
- late results do not overwrite the new phase;
- privacy copy updates when the data path changes;
- the user can return to the source.

## History transform and cache proof

Use controlled transcript entries:

- short prompt;
- response;
- tool call;
- tool output;
- sensitive entry;
- attachment;
- old phase instruction;
- current proposal.

Verify:

- the transform sends only allowed entries;
- sensitive entries are removed for the selected provider;
- global transcript is not accidentally destroyed;
- profile-specific context is enough for the request;
- stable prefixes remain stable when cache behavior matters;
- cache hit and token use are measured with Instruments;
- a cache hit does not alter semantic validation.

## Agentic tool-loop proof

| Test | Expected result |
| --- | --- |
| optional tool not needed | model completes without tool |
| required tool | model calls a tool, then exits |
| required tool repeated | call limit or dynamic mode exits |
| tool arguments invalid | tool rejects, no side effect |
| read tools in parallel | results are independent and combined safely |
| tool times out | readable failure and fallback |
| tool is cancelled | no unapproved commit |
| tool output is stale | re-fetch or reject |
| write tool requested | approval state, not immediate domain write |
| user denies | no write |
| user approves but record changed | conflict/review |
| late tool result | ignored if request/profile is stale |

Inspect the transcript call graph as evidence of what happened, not as a substitute for domain state.

## Custom provider proof

### Protocol and executor

- provider value is Sendable and contains only configuration;
- capabilities accurately list vision, tools, guided output, and reasoning;
- executor translates the framework request;
- instructions, prompts, tool calls, and history are mapped;
- generation channel streams the right events;
- metadata and usage are reported according to contract;
- cancellation propagates;
- errors map to app fallback;
- custom segments are tested if used;
- provider works in a real app target, not only a package test.

### Authentication

- no secret in source control;
- token storage is appropriate;
- expiry and refresh are deterministic;
- network errors do not leak raw credentials;
- logs and Instruments traces are sanitized;
- user consent and provider terms are visible;
- offline state has a fallback.

### Distribution

- package version is pinned or policy-defined;
- target platform declarations are correct;
- app archive includes the provider;
- release build can access required resources;
- TestFlight route works;
- App Store privacy and data-use disclosures match.

## PCC proof

PCC needs separate tests:

- availability on each supported OS path;
- managed entitlement and eligibility;
- region/device unavailable;
- network unavailable;
- quota below threshold;
- quota approaching limit;
- quota reached;
- reset date display;
- iCloud+ or quota-increase system route when applicable;
- fallback to on-device;
- privacy copy;
- no raw cloud prompt in standard logs;
- response quality versus on-device on the same fixture.

PCC availability does not prove a request succeeded, and quota does not prove a model is unavailable.

## Evaluation matrix

Run the same dataset through each provider that the product may ship:

| Criterion | On-device | PCC | Custom local | External |
| --- | --- | --- | --- | --- |
| source fidelity | measure | measure | measure | measure |
| schema validation | measure | measure | measure | measure |
| tool correctness | measure | measure | measure | measure |
| unwanted side effects | zero tolerance | zero tolerance | zero tolerance | zero tolerance |
| latency | measure | measure | measure | measure |
| token/cache use | measure | measure | measure | provider-specific |
| privacy | local policy | PCC policy | local policy | provider policy |
| offline fallback | required | no | required if claimed | no |
| quota/cost | none or policy | measure | device cost | provider cost |

Use rule-based checks for exact and safety-critical properties. Use human or model-as-judge evaluation only for nuanced quality and calibrate it against human judgment.

## Instruments proof

Record:

- model loading;
- time to first token;
- response duration;
- total duration;
- cached tokens;
- generated tokens;
- prompt, response, and tool durations;
- history transform effect;
- provider handoff;
- image preprocessing;
- thermal and performance state.

Treat traces as sensitive. Store only the minimum needed, and do not attach raw prompts or images to a general release ticket.

## Accessibility and privacy proof

### Accessibility

- every provider/status change is announced;
- image labels are meaningful;
- source and attachment removal work with VoiceOver;
- provider/quota is accessible as a value;
- phase and draft/final distinction is clear;
- cancel, deny, retry, and confirm are reachable;
- large text does not clip tool or approval content;
- reduced motion keeps phase meaning;
- keyboard/pointer/alternate input complete the route;
- focus is preserved across dynamic profile changes and sheets.

### Privacy

- provider path is documented;
- image and prompt inputs are minimized;
- external tools are disclosed;
- history transforms are tested;
- transcript retention is intentional;
- logs are redacted;
- Instruments traces are protected;
- feedback attachments are opt-in and sanitized;
- system surfaces do not expose private content accidentally.

## Physical and release proof

1. physical supported device, on-device ready;
2. model unavailable fallback;
3. image source selection and orientation;
4. profile transition;
5. tool loop and cancel;
6. PCC or custom provider branch when supported;
7. accessibility pass;
8. privacy/log inspection;
9. signed archive install;
10. TestFlight install;
11. App Store capability/privacy/review check.

## Evidence packet

Include:

- provider decision brief;
- capability matrix;
- availability/quota captures;
- attachment/source fixtures;
- dynamic profile transition report;
- history-transform report;
- tool call graph and approval evidence;
- provider evaluation comparison;
- Instruments trace handling note;
- accessibility checklist;
- privacy review;
- physical-device captures;
- archive and TestFlight identifiers;
- known limitations and fallback.

## Related local routes

- [Advanced provider and multimodal deep dive](../42-framework-deep-dives/112-swiftui-foundation-models-advanced-provider-multimodal-route-review.md)
- [Advanced provider and multimodal design](../21-design-deep-dives/140-swiftui-foundation-models-advanced-provider-multimodal-route-review-design.md)
- [Advanced provider and multimodal capability route](../50-capability-recipes/143-swiftui-foundation-models-advanced-provider-multimodal-route-review-route.md)
- [Foundation Models production proof matrix](136-swiftui-foundation-models-production-route-review-proof-matrix.md)
- [AI evaluation and safety checklist](03-ai-evaluation-and-safety-checklist.md)
- [Permission, entitlement, and privacy checklist](04-permission-entitlement-and-privacy-checklist.md)
- [Build, device, and release checklist](01-build-device-and-release-checklist.md)

## Sources

- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [LanguageModel](https://developer.apple.com/documentation/foundationmodels/languagemodel)
- [LanguageModelCapabilities](https://developer.apple.com/documentation/foundationmodels/languagemodelcapabilities)
- [Private Cloud Compute](https://developer.apple.com/documentation/foundationmodels/adding-server-side-intelligence-with-private-cloud-compute)
- [PrivateCloudComputeLanguageModel](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel)
- [Private Cloud Compute quota](https://developer.apple.com/documentation/foundationmodels/privatecloudcomputelanguagemodel/quotausage-swift.struct)
- [Composing dynamic sessions with instructions and profiles](https://developer.apple.com/documentation/foundationmodels/composing-dynamic-sessions-with-instructions-and-profiles)
- [DynamicInstructions](https://developer.apple.com/documentation/foundationmodels/dynamicinstructions)
- [LanguageModelSession.Profile](https://developer.apple.com/documentation/foundationmodels/languagemodelsession/profile)
- [Attachment](https://developer.apple.com/documentation/foundationmodels/attachment)
- [ImageReference](https://developer.apple.com/documentation/foundationmodels/imagereference)
- [Analyzing images with multimodal prompting](https://developer.apple.com/documentation/foundationmodels/analyzing-images-with-multimodal-prompting)
- [Expanding generation with tool calling](https://developer.apple.com/documentation/foundationmodels/expanding-generation-with-tool-calling)
- [Evaluations](https://developer.apple.com/documentation/evaluations)
- [Evaluating language model responses](https://developer.apple.com/documentation/evaluations/evaluating-language-model-responses)
- [Analyzing the runtime performance of your Foundation Models app](https://developer.apple.com/documentation/foundationmodels/analyzing-the-runtime-performance-of-your-foundation-models-app)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [Generative AI HIG](https://developer.apple.com/design/human-interface-guidelines/generative-ai)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Privacy HIG](https://developer.apple.com/design/human-interface-guidelines/privacy)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
