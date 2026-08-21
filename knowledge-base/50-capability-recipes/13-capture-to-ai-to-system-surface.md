# Capture to On-Device AI to System Surface

This blueprint composes a high-value Apple-native route: a person captures or selects media, the app performs a bounded Vision/Core ML analysis, Foundation Models optionally organizes a reviewable proposal, and only confirmed domain state is exposed to App Intents, Spotlight, widgets, notifications, or sharing.

It is an architecture route, not a claim that a particular app, model, system surface, or device is already working.

## User outcome

Write the outcome narrowly:

> A person can capture a supported image or document, correct the extracted fields, save a local record, and optionally find or share that confirmed record through an Apple system surface.

Change the source, domain object, and system surface for the actual product. Keep the approval boundary when the result affects money, health, identity, communication, private data, or an irreversible action.

## Route map

```text
user starts capture/import
  -> permission and source selection
  -> still image/document/frame
  -> Vision/Core ML observation
  -> deterministic normalization and validation
  -> optional Foundation Models proposal
  -> SwiftUI review/edit/reject
  -> SwiftData/domain commit
  -> AppEntity/Spotlight/widget/notification/share projection
```

The route can stop at any arrow. If the camera is unavailable, use PhotosUI or a manual form. If the model is unavailable, show the captured source and deterministic fields. If a proposal is rejected, keep the source and offer editing. If the system surface is unavailable, keep the in-app record usable.

## Ownership matrix

| Boundary | App owns | Apple/system owns | Proof required |
| --- | --- | --- | --- |
| Capture/import | User-started request, selected source, retention, preview, cancellation | Permission prompt, camera/photo picker, protected library | Physical permission/capture or picker run; privacy copy and deletion behavior. |
| Vision/Core ML | Model asset/version, input orientation/crop, request cadence, observation mapping | Framework execution and device compute resources | Compile/model load, representative fixtures, device latency/thermal, negative/ambiguous cases. |
| Foundation Models | Prompt/schema/tool, bounded context, proposal state, validation, review | Model availability, guardrails/refusals, model updates | Availability, context, prompt/schema/tool version, evaluation, resource and physical-device evidence. |
| Domain record | Authorization, schema, conflict, idempotency, persistence, canonical state | Storage/account/sync service state where applicable | Unit/persistence/conflict tests and actual storage/account/device run. |
| System projection | Redacted entity/action/content, stable IDs, deep link, stale recovery | Ranking, invocation, system UI, refresh/delivery schedules | Signed target, App Intent/entity compile, real system invocation, revalidation, release configuration. |

No model response or observation is a canonical record. No indexed entity or system result is authorization to mutate current domain state.

## State contract

```text
idle
 -> requestingPermission
 -> selectingSource
 -> capturing/importing
 -> analyzing
 -> enriching
 -> reviewable
 -> editing/validating
 -> committing
 -> committed
 -> projecting
```

Every state needs a cancellation and failure path:

| State | Preserve | Recovery |
| --- | --- | --- |
| Permission denied | User goal and explanatory copy | Settings/manual/import route. |
| Capture interrupted | Last confirmed source or draft | Resume, retake, or import. |
| Observation failed | Original source | Retry with supported input or manual fields. |
| Language model unavailable/refuses | Source and deterministic observation | Manual edit or save without enrichment. |
| Validation invalid | Proposal and issue list | Correct fields, request a new proposal, or reject. |
| Source stale/conflict | Current domain record and draft | Re-read, merge/review, or discard explicitly. |
| Projection fails | Confirmed domain record | Retry indexing/donation/deep link without reverting the record. |

## Data and provenance model

Use separate values for source, observation, proposal, draft, and record:

```text
CaptureAsset
  - user-selected source reference
  - capture/import timestamp
  - orientation and retention policy

Observation
  - model identifier/revision
  - request revision
  - fields/geometry/confidence/provenance

Proposal
  - prompt/schema/tool versions
  - source revision
  - generated values
  - validation issues

DomainRecord
  - canonical values
  - authorization/account scope
  - commit operation ID
  - updated revision

SystemProjection
  - redacted stable ID
  - display representation
  - deep-link/recovery route
  - expiry/source revision
```

Avoid storing raw images, transcripts, prompts, or model output in logs by default. Use security-scoped file access and Photos permissions only for the selected source. Make deletion and account-switch behavior explicit.

## Review surface

Use a native SwiftUI shell:

```text
NavigationStack
  -> source preview and provenance
  -> extracted fields / generated proposal Form
  -> validation and unknown-state explanation
  -> Edit / Reject / Approve actions
  -> committed record and optional system-projection status
```

Use standard controls, readable text, and a focused sheet or navigation route. A small Liquid Glass action group can provide functional hierarchy, but it must not obscure the source or validation text. Test long fields, Dynamic Type, RTL, increased contrast, reduced transparency, Reduce Motion, VoiceOver, Voice Control, Switch Control, compact width, and keyboard/pointer input.

## System-surface projection rules

Only confirmed domain state should be projected:

- AppEntity and Spotlight records use stable IDs and privacy-safe display representations;
- App Intent parameters resolve against current authorized state before mutation;
- widgets and Live Activities show a timestamp/revision and recover from stale state;
- notifications deep-link to the record or review route rather than embedding unreviewed model output as truth;
- ShareLink/Transferable exports the user-selected, confirmed representation;
- deletion, account switch, and permission revocation remove or invalidate projections.

The app should be able to reconstruct the current record from its ID and source revision. A system surface may be delayed, omitted, ranked differently, or unavailable; the in-app record remains canonical.

## Privacy and safety gates

Before implementation, answer:

- Is the source user-selected, continuously captured, or accessed from a protected store?
- Does any model/tool route send data outside the device or app process?
- Are prompts, transcripts, images, observations, or projections retained?
- Can source text contain instructions that should be treated as untrusted data?
- Can the proposal affect money, health, identity, messages, files, or access?
- What does the person review, edit, reject, and explicitly approve?
- What happens when the device, model, language asset, system surface, account, or network is unavailable?
- What privacy manifest, usage description, capability, entitlement, account, or App Store disclosure is required?

## Evidence plan

| Layer | Evidence |
| --- | --- |
| Source | Current Apple pages for capture, Vision/Core ML, Foundation Models, SwiftUI, persistence, App Intents, and the selected system surface. |
| Compile | Named Xcode target, deployment target, model/resource membership, imports, macros, capabilities, entitlements, and tests. |
| Fixture | Synthetic stills, no-result/ambiguous cases, long/private input, invalid proposal, refusal, stale source, duplicate approval, and projection failure. |
| Simulator | Review UI, navigation, fake capture/model states, Dynamic Type, appearance, reduced effects, and deep-link parsing. |
| Physical device | Camera/photo permission, model load/readiness, actual inference, latency/memory/thermal, capture interruption, accessibility task, and supported device family. |
| System surface | Signed App Intent/entity/widget/notification/share route, current authorization, real invocation, stale/deleted recovery, and target-specific configuration. |
| Release | Archive/privacy report, TestFlight, App Store metadata, account/service/server state, and claims matched to observed behavior. |

## Sources

- [AVFoundation Capture setup](https://developer.apple.com/documentation/avfoundation/capture-setup)
- [Setting up a capture session](https://developer.apple.com/documentation/avfoundation/setting-up-a-capture-session)
- [AVCam: Building a camera app](https://developer.apple.com/documentation/avfoundation/avcam-building-a-camera-app)
- [PhotosUI](https://developer.apple.com/documentation/photosui)
- [Core ML](https://developer.apple.com/documentation/coreml)
- [Vision](https://developer.apple.com/documentation/vision)
- [VNCoreMLRequest](https://developer.apple.com/documentation/vision/vncoremlrequest)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [SystemLanguageModel](https://developer.apple.com/documentation/foundationmodels/systemlanguagemodel)
- [LanguageModelSession](https://developer.apple.com/documentation/foundationmodels/languagemodelsession)
- [Generable](https://developer.apple.com/documentation/foundationmodels/generable)
- [Improving the safety of generative model output](https://developer.apple.com/documentation/foundationmodels/improving-the-safety-of-generative-model-output)
- [SwiftUI](https://developer.apple.com/documentation/swiftui)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [SwiftData](https://developer.apple.com/documentation/swiftdata)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [AppEntity](https://developer.apple.com/documentation/appintents/appentity)
- [Core Spotlight](https://developer.apple.com/documentation/corespotlight)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit)
- [UserNotifications](https://developer.apple.com/documentation/usernotifications)
- [Core Transferable](https://developer.apple.com/documentation/coretransferable)
- [Running your app on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
