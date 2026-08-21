# Apple Intelligence Context, Entities, and System Handoff

Apple Intelligence system surfaces and app-owned Foundation Models are related but not interchangeable. App-owned generation gives the product a controlled language task; App Intents, entities, schemas, Spotlight, Visual Intelligence, Writing Tools, and Siri/Apple Intelligence system experiences let Apple decide how and when to use the app’s structured actions and content.

## Ownership matrix

| Route | App contributes | Apple/system owns | App must prove |
| --- | --- | --- | --- |
| Foundation Models | Prompt/instructions, `@Generable` schema, tools, source data, review UI, deterministic use case | Model behavior, availability, guardrails/refusals, model updates, generation result | Availability, input bounds, validation, safety/evaluation, user review, fallback, device/resource behavior. |
| App Intents | `AppIntent`, parameters, `AppEntity`, queries, display representation, schemas, `perform()` use case | Natural-language interpretation, ranking, invocation context, system presentation | Entity resolution, current authorization, idempotent side effect, confirmation/error dialog, supported system invocation. |
| Spotlight/entity discovery | Redacted index/entity projection and stable IDs | Indexing, semantic matching, ranking, system result UI | Upsert/delete consistency, stale/deleted resolution, privacy/protection, deep-link revalidation. |
| Visual Intelligence | Documented `IntentValueQuery`/entity matching route and safe result representation | Capture/context, system UI, invocation availability, ranking | Label/pixel-buffer privacy, matching quality, ambiguity, stale entity handling, supported physical system route. |
| Writing Tools | Standard text surface or documented custom text-engine integration | Rewrite/proofread/summarize generation, temporary editing UI | Text semantics, synchronization pause/resume, accept/reject, attachments, accessibility, fallback. |
| Image Playground/Genmoji | Standard system entry point, output storage/metadata, user workflow | Image/text generation, safety, system presentation, availability | User control, provenance, persistence, unsupported/cancelled/rejected states, device/system proof. |

Never call an Apple Intelligence system surface “the app’s model.” Never call a Foundation Models response a verified fact, entity, authorization, or completed side effect.

## App Intents entity route

For a native app that should be understood by Apple Intelligence, define a small vocabulary:

```text
domain record -> app-facing entity -> stable query/resolver -> indexed/discoverable projection
                             -> AppIntent parameter -> validated domain use case
```

Use `AppEntity` as a system-facing representation rather than exposing the entire persistence model. Give it a stable `ID`, localized `DisplayRepresentation`, a `defaultQuery`, and only the properties needed for discovery and action resolution. If a current API/schema route applies, prefer the documented App Intents schema macros and verify the generated requirements in the selected SDK.

An `EntityQuery`/resolver must:

- resolve only records the current account/session can access;
- distinguish no match, ambiguous match, stale ID, deleted record, and unavailable store;
- avoid treating a display name as a unique identifier;
- return bounded results with privacy-safe labels;
- re-read current domain state before any mutation;
- return a user-readable error or a focused app route when a review is needed.

`AppIntent.perform()` is a command boundary, not a shortcut around the app architecture. It should call the same use case as the in-app button, enforce permissions and business rules, use an idempotency key, and return a result that distinguishes accepted, committed, rejected, and failed.

## Schema and discoverability matrix

| Layer | Concrete route | Configuration/availability | Failure state |
| --- | --- | --- | --- |
| Entity definition | `AppEntity`, `@Property`, `DisplayRepresentation`, `defaultQuery` | Target SDK, entity schema, localization, stable IDs, target membership | Unsupported/stale/deleted/unauthorized entity. |
| Query/resolution | `EntityQuery`, `EntityStringQuery`, documented schema query, resolver specifications | Account/store availability, query limits, main/extension process, actor isolation | No match, ambiguous, timeout, protected data, reauthorization. |
| Action | `AppIntent`, `@Parameter`, `IntentResult`, `OpenIntent`/domain-specific schema | App Intents target/extension, capability, schema, confirmation/parameter policy | Invalid input, stale entity, denied permission, conflict, commit failure. |
| Index/discovery | `CSSearchableIndex`, `CSSearchableItem`, indexed `AppEntity`, donations | Privacy/protection class, expiration, deletion synchronization, system indexing availability | Projection failed/stale/not ranked/not presented. |
| View context | SwiftUI entity/context annotations and `NSUserActivity` where appropriate | Current activity, target content ID, privacy/retention, system support | Context not delivered, expired, rejected, ambiguous, or unavailable. |
| Visual Intelligence | `IntentValueQuery`/semantic input and matching entities | Preliminary API/target/device/system invocation, capture permissions and privacy | No pixel buffer/label, ambiguous match, no result, stale entity, unsupported system route. |

## Context payload contract

Keep system context small and reconstructible:

| Field | Rule |
| --- | --- |
| `schemaVersion` | Migrate/reject unknown representations; do not guess. |
| `entityID`/`recordID` | Stable ID resolved against current authorized state. |
| `accountID`/scope | Used for reauthorization and account-switch protection, never as proof by itself. |
| `displayRepresentation` | Localized, redacted title/subtitle/image suitable for the system surface. |
| `sourceRevision`/`updatedAt`/`expiresAt` | Detect stale context and avoid displaying old truth as current. |
| `intent`/parameters | Bounded action request, not an authorization bypass. |
| `provenance` | Source references for app-owned AI proposals or derived content. |
| `recoveryRoute` | Focused app destination or manual fallback for review/error. |

Do not put full private records, secrets, raw camera frames, raw transcripts, credentials, or unreviewed model output into a system-facing projection. A system result must re-resolve the ID and current data before it reaches the domain layer.

## Foundation Models versus system context

Use Foundation Models when the app owns the bounded language task, prompt/schema, validation, and review. Use App Intents/entities/system schemas when the goal is discoverability and system invocation. They can compose:

```text
AppEntity/indexed record -> system resolves current entity
      -> AppIntent receives bounded parameter
      -> domain service reads current state
      -> optional Foundation Models proposal
      -> user review/deterministic validation
      -> commit and projection
```

The model may summarize or propose a next action after the entity is resolved, but it does not inherit the entity’s authority. Keep schema resolution, model availability, model safety, user approval, and domain commit as separate evidence records.

## Visual Intelligence route boundary

Visual Intelligence can provide a label or image context that helps the system search app entities. The captured context is a hint, not a verified real-world identity or measurement. Limit the entity set, match deterministically or through a bounded service, and show ambiguity/no-result states. Release the pixel buffer after the requested match unless the product’s explicit privacy policy requires storage.

Use the normal in-app search and navigation route when Visual Intelligence is unavailable. A compiling `IntentValueQuery` or an App Entity in Spotlight does not prove that the system will invoke it, rank it, or select the right entity on a physical device.

## Proof matrix

| Claim | Required evidence |
| --- | --- |
| Entity is discoverable | Compile schema/query, index projection, create/edit/delete synchronization, and actual Spotlight/Siri/Shortcuts/system invocation on the named configuration. |
| Action is safe | Parameter resolution, current authorization, stale/deleted handling, idempotent use case, confirmation, commit result, and failure recovery. |
| Apple Intelligence understands the app | Current documented schema/context route, indexed entities, supported OS/device/language, actual system invocation, and bounded result behavior. |
| Visual Intelligence match works | Physical system invocation, representative labels/images, ambiguous/no-result/false-positive fixtures, privacy handling, and entity revalidation. |
| Foundation Models proposal works inside the route | Model availability, prompt/schema/tool version, safety/refusal, validation, review, commit, and physical-device resource evidence. |
| System surface is shippable | Signed target/extension, entitlements, privacy metadata, App Store configuration where required, and release testing of the exact surface. |

## Sources

- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppIntent](https://developer.apple.com/documentation/appintents/appintent)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [Defining app entities for your custom data types](https://developer.apple.com/documentation/appintents/defining-app-entities-for-your-custom-data-types)
- [Making actions and content discoverable by Apple Intelligence](https://developer.apple.com/documentation/appintents/making-actions-and-content-discoverable-by-apple-intelligence)
- [Adopting App Intents to support system experiences](https://developer.apple.com/documentation/appintents/adopting-app-intents-to-support-system-experiences)
- [Apple Intelligence and Siri AI](https://developer.apple.com/documentation/appintents/apple-intelligence-and-siri-ai)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [CSSearchableIndex](https://developer.apple.com/documentation/corespotlight/cssearchableindex)
- [Visual Intelligence](https://developer.apple.com/documentation/visualintelligence)
- [Integrating your app with visual intelligence](https://developer.apple.com/documentation/visualintelligence/integrating-your-app-with-visual-intelligence)
- [Providing contextual cues to Apple Intelligence and Siri](https://developer.apple.com/documentation/appintents/providing-contextual-cues-to-apple-intelligence-and-siri)
- [Writing Tools](https://developer.apple.com/documentation/uikit/writing-tools)
- [Image Playground](https://developer.apple.com/documentation/imageplayground)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
