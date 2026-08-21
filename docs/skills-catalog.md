# Skill catalog

This catalog explains the purpose, feature set, and handoff for every role-oriented package in the BishopTech iOS 26 Skills Lab.

The packages are not generic “write some Swift” prompts. Each role is expected to inspect the real project, consult the relevant official Apple or Swift sources, preserve availability and entitlement gates, state uncertainty, and return evidence that another role can verify.

## Fast routing

| If the task sounds like… | Start with… |
| --- | --- |
| “Turn this app idea into the right Apple architecture.” | [Agentic Apple engineering team](../knowledge-base/skills/packages/ios-agentic-apple-engineering-team/SKILL.md), then [capability route planner](../knowledge-base/skills/packages/ios-capability-route-planner/SKILL.md) |
| “Which framework, target, extension, entitlement, or system surface should we use?” | [Apple SDK route](../knowledge-base/skills/packages/apple-sdk-route/SKILL.md) and [project, target, and module architect](../knowledge-base/skills/packages/ios-project-target-architect/SKILL.md) |
| “Make this feel native, adaptive, accessible, and Liquid Glass.” | [SwiftUI native design](../knowledge-base/skills/packages/swiftui-native-design/SKILL.md), [Liquid Glass design](../knowledge-base/skills/packages/liquid-glass-design/SKILL.md), and [native design verification](../knowledge-base/skills/packages/ios-native-design-verification/SKILL.md) |
| “Add Apple Intelligence, Foundation Models, Core ML, Vision, speech, or another local model.” | [On-device AI feature](../knowledge-base/skills/packages/on-device-ai-feature/SKILL.md) and [on-device intelligence evaluation](../knowledge-base/skills/packages/ios-on-device-intelligence-evaluation/SKILL.md) |
| “Test, audit, profile, run on hardware, archive, or ship.” | [Testing and release assurance](../knowledge-base/skills/packages/ios-testing-and-release-assurance/SKILL.md), [device and release proof](../knowledge-base/skills/packages/ios-device-release-proof/SKILL.md), and [privacy, performance, and release proof](../knowledge-base/skills/packages/ios-privacy-performance-release-proof/SKILL.md) |
| “Apple changed something; refresh the route and packages.” | [Source refresh and availability maintenance](../knowledge-base/skills/packages/ios-source-refresh-and-availability/SKILL.md) |

## Complete role catalog

### 1. Agentic Apple engineering team

[Open the package](../knowledge-base/skills/packages/ios-agentic-apple-engineering-team/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-agentic-apple-engineering-team.skill)

**Use it for:** coordinating a complete app-building task from brief to evidence-backed handoff.

**Features:** progressive-disclosure role routing; architect, designer, implementer, AI evaluator, test auditor, device auditor, release auditor, and source maintainer handoffs; shared evidence vocabulary; source and availability gates; explicit stop conditions; representative evaluation fixtures.

**Produces:** a project brief, role assignments, route decision, required inputs, source-backed plan, evidence ledger, open risks, and the next smallest verifiable gate.

### 2. Apple SDK route

[Open the package](../knowledge-base/skills/packages/apple-sdk-route/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/apple-sdk-route.skill)

**Use it for:** mapping a product outcome to Apple frameworks, APIs, system surfaces, permissions, entitlements, targets, and proof.

**Features:** capability-first selection; native versus custom boundary; lifecycle and ownership questions; availability and hardware checks; privacy and authorization gates; fallback and release routing.

**Produces:** a framework decision matrix and a source-linked route that can be handed to the capability planner or project architect.

### 3. iOS capability route planner

[Open the package](../knowledge-base/skills/packages/ios-capability-route-planner/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-capability-route-planner.skill)

**Use it for:** deciding what the app must do before deciding which API to call.

**Features:** outcome-to-capability mapping; state and failure contracts; system-surface composition; native UI and Liquid Glass checkpoints; on-device AI boundaries; proportional proof planning.

**Produces:** a capability route with chosen lanes, rejected alternatives, target and device assumptions, and evidence requirements.

### 4. iOS project, target, and module architect

[Open the package](../knowledge-base/skills/packages/ios-project-target-architect/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-project-target-architect.skill)

**Use it for:** designing the Xcode project graph before implementation expands.

**Features:** app, extension, widget, test, package, scheme, and configuration boundaries; App Groups; capabilities; privacy resources; test plans; signing and artifact ownership; module and dependency boundaries.

**Produces:** a target graph, module plan, configuration matrix, capability checklist, and build-proof plan.

### 5. SwiftUI native design

[Open the package](../knowledge-base/skills/packages/swiftui-native-design/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/swiftui-native-design.skill)

**Use it for:** designing adaptive SwiftUI screens, components, navigation, previews, and state-driven UI.

**Features:** semantic hierarchy; Dynamic Type; loading, empty, partial, stale, denied, unavailable, and error states; navigation and presentation; input adaptation; accessibility; preview matrices; native control selection.

**Produces:** a screen and state blueprint that a SwiftUI implementer can build without inventing missing behavior.

### 6. Liquid Glass design

[Open the package](../knowledge-base/skills/packages/liquid-glass-design/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/liquid-glass-design.skill)

**Use it for:** adopting Liquid Glass as a functional, system-first design material.

**Features:** content versus control layering; glass groups and shared transitions; legibility and contrast; safe-area and toolbar placement; reduced-effects fallback; hit targets and accessibility; restrained custom effects; interaction-state review.

**Produces:** a Liquid Glass composition plan with material roles, action hierarchy, fallback behavior, and device review tasks.

### 7. iOS native design and Liquid Glass verification

[Open the package](../knowledge-base/skills/packages/ios-native-design-verification/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-native-design-verification.skill)

**Use it for:** auditing whether an implementation actually feels native rather than merely decorated.

**Features:** Human Interface Guidelines hierarchy; semantic controls; Dynamic Type; accessibility; Reduce Motion and Reduce Transparency; haptics; focus; adaptive layouts; Liquid Glass grouping; visual and physical-device review.

**Produces:** a design audit with concrete findings, severity, affected states, and the smallest corrective change.

### 8. On-device AI feature

[Open the package](../knowledge-base/skills/packages/on-device-ai-feature/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/on-device-ai-feature.skill)

**Use it for:** adding a local intelligence feature without letting a model become an unreviewed product authority.

**Features:** Foundation Models and framework selection; prompt and context versioning; typed outputs; model availability; tool approval; privacy; refusal and fallback; user review; deterministic commit boundaries; App Intent handoff.

**Produces:** an AI feature contract with input provenance, schema, validation, refusal states, review UI, fallback, and evaluation plan.

### 9. iOS on-device intelligence evaluation

[Open the package](../knowledge-base/skills/packages/ios-on-device-intelligence-evaluation/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-on-device-intelligence-evaluation.skill)

**Use it for:** determining whether an AI feature is useful, safe, repeatable, and appropriate for the device and data.

**Features:** fixture design; schema and source validation; quality and safety scoring; availability and compute policy; latency and energy concerns; model update discipline; human calibration; privacy and retention boundaries; physical-device checks.

**Produces:** an evaluation report that separates deterministic correctness from model quality and human judgment.

### 10. iOS media, ML, and physical inputs

[Open the package](../knowledge-base/skills/packages/ios-media-ml-and-inputs/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-media-ml-and-inputs.skill)

**Use it for:** camera, microphone, media, Vision, Core ML, Natural Language, NFC, MusicKit, ShazamKit, and other physical-input pipelines.

**Features:** capture ownership; queues and backpressure; pixel and audio provenance; bounded processing; permissions; privacy; model and codec readiness; interruption and teardown; physical performance; user-visible source labeling.

**Produces:** a media or sensor route with lifecycle ownership, privacy declarations, model policy, cancellation, and device evidence.

### 11. iOS data and device services

[Open the package](../knowledge-base/skills/packages/ios-data-and-device-services/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-data-and-device-services.skill)

**Use it for:** SwiftData, CloudKit, HealthKit, Contacts, EventKit, WeatherKit, HomeKit, Bluetooth, Nearby Interaction, Network, and related services.

**Features:** authorization and account state; local-first storage; schema and migration; synchronization and conflicts; device and accessory lifecycle; privacy; system ownership; bounded AI proposals; two-device proof.

**Produces:** a service contract that keeps local truth, system truth, remote truth, and generated suggestions distinct.

### 12. iOS system surfaces and background

[Open the package](../knowledge-base/skills/packages/ios-system-surfaces-and-background/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-system-surfaces-and-background.skill)

**Use it for:** widgets, Live Activities, controls, App Intents, document providers, PhotosUI, WebKit, sharing, extensions, App Groups, and background tasks.

**Features:** app versus extension ownership; system scheduling; scene and deep-link routing; update budgets; background cancellation; shared storage; privacy; system-hosted UI; device and release proof.

**Produces:** a system-surface and background handoff with target graph, lifecycle, update policy, recovery states, and verification matrix.

### 13. iOS companion and communications

[Open the package](../knowledge-base/skills/packages/ios-companion-communications/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-companion-communications.skill)

**Use it for:** WatchConnectivity, CarPlay, App Clips, CallKit, LiveCommunicationKit, PushKit, APNs, and notifications.

**Features:** paired-device and system-host lifecycle; communication privacy; push and background boundaries; account and identity separation; audio/session ownership; extension configuration; physical multi-device evidence.

**Produces:** a companion or communications plan that separates delivery claims from user-visible and system-visible proof.

### 14. iOS spatial, graphics, and games

[Open the package](../knowledge-base/skills/packages/ios-spatial-graphics-and-games/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-spatial-graphics-and-games.skill)

**Use it for:** ARKit, RealityKit, visionOS surfaces, Metal, SpriteKit, GameplayKit, GameKit, and spatial or graphics-heavy apps.

**Features:** renderer and runtime selection; scene and entity ownership; deterministic game state; GPU and frame pacing; resource budgets; accessibility; semantic overlays; physical-device performance; multiplayer proof.

**Produces:** a graphics or spatial architecture with device capability gates, frame/resource evidence, fallback, and release constraints.

### 15. iOS commerce, identity, and security

[Open the package](../knowledge-base/skills/packages/ios-commerce-identity-and-security/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-commerce-identity-and-security.skill)

**Use it for:** StoreKit 2, PassKit, Apple Pay, Wallet, Sign in with Apple, passkeys, Keychain, LocalAuthentication, CryptoKit, DeviceCheck, App Attest, URLSession, and Network trust.

**Features:** server-authoritative identity and entitlement boundaries; secrets and key lifecycle; authentication and recovery; payment and Wallet system ownership; entitlement configuration; privacy; challenge verification; release and audit evidence.

**Produces:** a security and commerce route that never lets a token, callback, local flag, or model suggestion stand in for authorization or server truth.

### 16. iOS privacy, performance, and release proof

[Open the package](../knowledge-base/skills/packages/ios-privacy-performance-release-proof/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-privacy-performance-release-proof.skill)

**Use it for:** privacy manifests, required-reason APIs, performance diagnostics, MetricKit, OSLog, accessibility evidence, archive inspection, TestFlight, and App Store Connect release work.

**Features:** privacy inventory; sensitive-data review; signposts and workload baselines; test plans; audit trails; archive target membership; entitlements; build and version checks; distribution boundaries.

**Produces:** a release-readiness packet with measurable findings and a clear separation between evidence collected and evidence still missing.

### 17. iOS device and release proof

[Open the package](../knowledge-base/skills/packages/ios-device-release-proof/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-device-release-proof.skill)

**Use it for:** deciding what source reading, compilation, simulator work, physical-device runs, signed artifacts, TestFlight, and production checks actually establish.

**Features:** evidence vocabulary; device matrix; entitlements and permission checks; fresh install and update tasks; system-surface proof; archive and signing inspection; TestFlight handoff; explicit non-proof statements.

**Produces:** an evidence ledger and gate checklist instead of a vague “it works” status.

### 18. iOS testing and release assurance

[Open the package](../knowledge-base/skills/packages/ios-testing-and-release-assurance/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-testing-and-release-assurance.skill)

**Use it for:** Swift Testing, XCTest, XCUIAutomation, accessibility audits, Liquid Glass regression, AI evaluation, performance, physical/system behavior, archives, and TestFlight.

**Features:** deterministic fixtures; parameterized tests; async confirmations; semantic UI queries; accessibility audit versus assistive-task separation; performance baselines; test plans; AI evaluation; device and signed-release gates.

**Produces:** a testing and release-assurance handoff that states what each test proves, what it excludes, and what must happen next.

### 19. iOS source refresh and availability maintenance

[Open the package](../knowledge-base/skills/packages/ios-source-refresh-and-availability/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/ios-source-refresh-and-availability.skill)

**Use it for:** refreshing a route when Apple documentation, SDK interfaces, availability, entitlements, privacy rules, HIG guidance, or release requirements change.

**Features:** change-signal capture; official source and installed SDK audit; affected-route graph; current versus historical classification; narrow updates; recipe and package validation; live link checking; archive portability; refresh receipts.

**Produces:** an Apple source-refresh handoff with the changed signal, affected files, availability facts, evidence level, uncertainty, and next refresh trigger.

## Shared handoff contract

Every role should return:

- the user-visible claim and highest-consequence failure;
- project, target, SDK, OS, device, entitlement, permission, account, and data facts;
- official sources and version-sensitive assumptions;
- files inspected and files changed;
- outputs for the next role;
- tests, fixtures, and evidence level;
- what the result proves;
- what it does not prove;
- the smallest next gate.

## Evidence levels

Use these labels consistently:

| Level | Meaning |
| --- | --- |
| Source | Apple or Swift documentation was checked. |
| Target/static | Project files, targets, entitlements, privacy resources, or configuration were inspected. |
| Compile | Code typechecked or built against a named SDK and target. |
| Fixture/unit | Deterministic logic passed controlled fixtures. |
| Simulator/UI | A simulator or UI automation workflow passed. |
| Physical/system | A named device, accessory, assistive technology, or system host was tested. |
| Account/server | A required service, account, server, or provider behavior was verified. |
| Signed artifact | Archive, signing, entitlements, versions, and target membership were inspected. |
| TestFlight/App Store | A real distribution or review path was exercised. |
| Production | The shipped environment and affected operation were verified. |

The levels are cumulative only when the task requires them. A higher-looking artifact does not erase a missing device, account, accessibility, privacy, or production check.

## Package anatomy

Each role package keeps the main SKILL.md short and routes detail to one-level references:

1. trigger and role scope;
2. read-before-acting checklist;
3. role workflow;
4. output contract;
5. hard boundaries;
6. official Sources;
7. focused references, fixtures, or audit matrices.

The package archive should contain only the intended skill files. It must not include secrets, user data, private workspace paths, generated test output, or claims that are not reviewable.

## Related maps

- [Knowledge-base map](../knowledge-base/README.md)
- [Coverage matrix](../knowledge-base/coverage-matrix.md)
- [Official source registry](../knowledge-base/sources/official-source-registry.md)
- [Package index](../knowledge-base/skills/packages/README.md)
- [Contribution guide](../CONTRIBUTING.md)
