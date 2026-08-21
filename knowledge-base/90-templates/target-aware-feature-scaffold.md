# Target-Aware Feature Scaffold Brief

Use this template when turning an idea into the first vertical slice. It keeps the feature’s meaning shared while making target, framework, process, permission, AI, and system-surface differences explicit before code spreads across the project.

## 1. Outcome and route

- Outcome sentence: A person can…
- Primary object/record:
- Source input: text, photo, camera, audio, location, sensor, local record, system surface, or other:
- First transform:
- Review or confirmation step:
- Durable truth:
- Final side effect, if any:
- Narrowest Apple framework route:
- Why a standard SwiftUI/system route is insufficient, if custom UI or UIKit is proposed:

Route shape:

~~~text
input -> capability adapter -> normalized evidence/proposal -> review -> deterministic use case -> persistence/system surface
~~~

Do not let a view, model session, extension, or delegate skip the normalization and authorization boundary.

## 2. Target and module plan

| Layer | Proposed owner | Imports | Public contract | Must not own |
| --- | --- | --- | --- | --- |
| Domain model/policy |  |  |  | SwiftUI view state, controller, raw framework object |
| Feature state/use case |  |  |  | Target membership, global singleton, unmanaged side effect |
| Capability adapter |  |  |  | Product truth before validation, UI hierarchy |
| Persistence/transport |  |  |  | Permission decision, visual layout |
| App surface |  |  |  | Database migration, model prompt policy, raw delegate lifecycle |
| Extension/system surface |  |  |  | Main app process, unversioned shared mutable state |
| Tests/fixtures |  |  |  | Production secrets, physical-device claims from mocks |

Target rows:

| Target | Platform/OS | Process/host | Feature files | Frameworks/packages | Capabilities/entitlements | Proof destination |
| --- | --- | --- | --- | --- | --- | --- |
| Main app |  |  |  |  |  |  |
| Extension/system surface |  |  |  |  |  |  |
| Companion/alternate platform |  |  |  |  |  |  |
| Unit/integration/UI test |  |  |  |  |  |  |

## 3. State machine

Name states rather than hiding them in optional values:

~~~text
idle
  -> preparing
  -> needsPermission / unavailable / needsAsset / needsPairing
  -> ready
  -> processing
  -> proposalReady
  -> reviewRequired
  -> saving / invoking
  -> saved / invoked
  -> cancelled / failed / stale
~~~

For each state:

| State | User-visible meaning | Owner | Can retry? | Can background? | Accessibility announcement/action | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |

Rules:

- `unavailable` is not the same as empty data.
- `permissionDenied` is not the same as a framework error.
- `cancelled` is not a failed save.
- `proposalReady` is not durable truth.
- `saved` is not proof that a widget, notification, server, or companion device has refreshed.

## 4. Capability adapter contract

Define the adapter around the outcome, not the framework object:

~~~swift
protocol FeatureCapability {
    associatedtype Input
    associatedtype Evidence

    func availability(for input: Input) async -> CapabilityAvailability
    func run(_ input: Input) async throws -> Evidence
    func cancel()
}

enum CapabilityAvailability: Equatable {
    case ready
    case needsPermission
    case unavailable(reason: String)
    case needsAsset(String)
    case needsPairedDevice
}
~~~

This is a planning sketch, not a universal protocol to paste into every project. The selected framework may need a different concurrency, actor, delegate, session, or authorization model. Record the actual Apple API types and availability in the route table before implementing the adapter.

Adapter questions:

- Which actor owns framework calls and observable state?
- Which permission is requested, when, and with what user-facing explanation?
- Which entitlement/capability and Info.plist usage description belong to which target?
- What hardware, OS, language, model, asset, account, service, or paired-device state is required?
- What resources start and stop with the feature?
- What event cancels the work?
- How are duplicate taps and late callbacks handled?
- What evidence/provenance travels with the result?
- What deterministic validation happens before persistence or side effects?

## 5. On-device AI route, if used

- AI framework: Foundation Models, Core ML, Vision, Speech, Translation, Natural Language, Sound Analysis, or other:
- Device/model/OS/language availability:
- Input privacy class:
- Prompt/instruction version:
- Schema or typed output:
- Context/session lifetime:
- Tool definitions:
- Read-only versus write-capable tool boundary:
- User confirmation required before:
- Deterministic validator:
- Confidence/uncertainty/provenance fields:
- Model unavailable/error/fallback UI:
- Evaluation fixtures and representative device matrix:

The model can propose text, classification, extraction, or a typed action. It cannot grant permission, create an entitlement, prove identity, or approve its own consequential side effect. Keep the model session behind the feature service and keep the review surface in the target UI that can express the consequence.

## 6. Surface composition

| Target | Primary container | Main content hierarchy | System surface | Input path | Glass/material decision | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
| iPhone |  |  |  | Touch/VoiceOver |  |  |
| iPad |  |  |  | Touch/pointer/keyboard/Pencil |  |  |
| Mac Catalyst/macOS |  |  |  | Pointer/keyboard/menus |  |  |
| visionOS |  |  |  | Eyes/hands/pointer/keyboard |  |  |
| watchOS |  |  |  | Touch/crown/short action |  |  |

Before a custom surface, check:

- [ ] A standard SwiftUI control or container does not already express the outcome.
- [ ] A system-owned toolbar, tab, sheet, menu, notification, widget, or App Intent is considered.
- [ ] The feature remains understandable without animation, haptic feedback, color, hover, or spatial gesture alone.
- [ ] Labels, values, traits, focus, keyboard actions, and alternate input are defined.
- [ ] Dynamic Type, localization, right-to-left, reduced motion, reduced transparency, and high-contrast states are named.
- [ ] Any Liquid Glass group is functional, bounded, legible, and target-specific.

## 7. Persistence and system projection

- Source of truth:
- Record/version identifier:
- Migration strategy:
- Deletion/retention policy:
- Local-first/offline state:
- Cloud/server sync, if any:
- Extension/App Group projection:
- Widget/Live Activity/notification projection:
- App Intent/deep-link projection:
- Freshness timestamp:
- Stale/error behavior:
- Conflict policy:

System projections should be disposable and rebuildable from valid domain data where possible. A projection may be stale, unavailable, or terminated; never present it as current merely because it rendered.

## 8. Test and proof plan

### Deterministic tests

- [ ] Domain rules and validation are tested without SwiftUI or device hardware.
- [ ] Availability and fallback mapping are tested with fakes.
- [ ] Duplicate actions, cancellation, stale results, and retry are tested.
- [ ] AI proposals are checked against schema, range, provenance, and approval rules.
- [ ] Persistence migration, deletion, and relaunch behavior are tested.
- [ ] App Intent/system-surface inputs call the same use case as visible UI.

### UI/system tests

- [ ] Empty, loading, permission, unavailable, review, success, failure, and offline states.
- [ ] Navigation, sheets, keyboard/focus, deep links, and state restoration.
- [ ] Accessibility identifiers and meaningful labels/actions.
- [ ] Dynamic Type, localization, right-to-left, reduced motion/transparency, and contrast fixtures.
- [ ] Target-specific extension/system host flows where automation can cover them.

### Physical and release evidence

| Claim | Required environment | Record |
| --- | --- | --- |
| Camera/microphone/sensor/haptic behavior | Named physical device and permission state | Device/OS/build, hardware route, interruptions, observed result |
| On-device model availability/quality/latency | Representative supported devices/languages/model state | Fixture, prompt/schema version, model state, timing, result |
| Widget/Live Activity/Control/App Intent delivery | Signed build, physical device, system/account/APNs state as applicable | Invocation/update/termination/stale evidence |
| Watch/CarPlay/visionOS behavior | Named paired/physical/system target | Pairing/vehicle/spatial state and interaction record |
| Accessibility task completion | Physical target with relevant assistive technologies | Task, setting, focus/announcement/action result |
| Release readiness | Intended Release archive and distribution metadata | Bundle/configuration/entitlements/privacy/signing/archive evidence |

## 9. Implementation handoff

Before opening a new file, produce:

1. Target graph and module graph.
2. Framework route table with exact symbols and source links.
3. Permission/entitlement/privacy table.
4. Feature state machine and cancellation policy.
5. UI/input/accessibility matrix.
6. AI evaluation and review contract, if applicable.
7. Test-plan and evidence ledger.

If one of these is unknown, label it as an open verification item rather than inventing a default. The scaffold is ready for implementation when the missing items are target-specific questions, not unbounded architecture ambiguity.

## Sources

- [Configuring a new target in your project](https://developer.apple.com/documentation/xcode/configuring-a-new-target-in-your-project)
- [Building and running an app](https://developer.apple.com/documentation/xcode/building-and-running-an-app)
- [Customizing the build schemes for a project](https://developer.apple.com/documentation/xcode/customizing-the-build-schemes-for-a-project)
- [Adding package dependencies to your app](https://developer.apple.com/documentation/xcode/adding-package-dependencies-to-your-app)
- [PackageDescription](https://docs.swift.org/swiftpm/documentation/packagedescription/)
- [Target](https://docs.swift.org/swiftpm/documentation/packagedescription/target/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
- [App Intents](https://developer.apple.com/documentation/appintents/)
- [WidgetKit](https://developer.apple.com/documentation/widgetkit/)
- [ActivityKit](https://developer.apple.com/documentation/activitykit/)
- [ExtensionKit](https://developer.apple.com/documentation/extensionkit)
- [App Groups Entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.application-groups)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)
