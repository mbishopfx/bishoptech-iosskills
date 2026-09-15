# Skill catalog

This catalog explains the purpose, feature set, and handoff for every role-oriented package in the BishopTech iOS 27 Skills Lab. iOS 26 remains the compatibility and historical fallback lane where a target has not moved to Xcode 27.

The packages are not generic “write some Swift” prompts. Each role is expected to inspect the real project, consult the relevant official Apple or Swift sources, preserve availability and entitlement gates, state uncertainty, and return evidence that another role can verify.

## Fast routing

| If the task sounds like… | Start with… |
| --- | --- |
| “Turn this app idea into the right Apple architecture.” | [Agentic Apple engineering team](../knowledge-base/skills/packages/ios-agentic-apple-engineering-team/SKILL.md), then [capability route planner](../knowledge-base/skills/packages/ios-capability-route-planner/SKILL.md) |
| “Which framework, target, extension, entitlement, or system surface should we use?” | [Apple SDK route](../knowledge-base/skills/packages/apple-sdk-route/SKILL.md) and [project, target, and module architect](../knowledge-base/skills/packages/ios-project-target-architect/SKILL.md) |
| “Make this feel native, adaptive, accessible, and Liquid Glass.” | [SwiftUI native design](../knowledge-base/skills/packages/swiftui-native-design/SKILL.md), [Liquid Glass design](../knowledge-base/skills/packages/liquid-glass-design/SKILL.md), [native design verification](../knowledge-base/skills/packages/ios-native-design-verification/SKILL.md), and the [iOS 27 native design brief](../knowledge-base/90-templates/ios27-native-design-brief.md) |
| “Add Apple Intelligence, Foundation Models, Core ML, Vision, speech, or another local model.” | [On-device AI feature](../knowledge-base/skills/packages/on-device-ai-feature/SKILL.md) and [on-device intelligence evaluation](../knowledge-base/skills/packages/ios-on-device-intelligence-evaluation/SKILL.md) |
| “Test, audit, profile, run on hardware, archive, or ship.” | [Testing and release assurance](../knowledge-base/skills/packages/ios-testing-and-release-assurance/SKILL.md), [device and release proof](../knowledge-base/skills/packages/ios-device-release-proof/SKILL.md), [privacy, performance, and release proof](../knowledge-base/skills/packages/ios-privacy-performance-release-proof/SKILL.md), and the [iOS 27 performance/on-device proof template](../knowledge-base/90-templates/ios27-performance-and-on-device-proof.md) |
| “Apple changed something; refresh the route and packages.” | [Source refresh and availability maintenance](../knowledge-base/skills/packages/ios-source-refresh-and-availability/SKILL.md) |
| “Build an iOS app for Meta glasses or the Ray-Ban Display.” | [Meta Wearables agentic team](../knowledge-base/skills/packages/meta-wearables-agentic-team/SKILL.md), then [Meta route planner](../knowledge-base/skills/packages/meta-wearables-route-planner/SKILL.md) |

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

## Meta Wearables extension team

These twenty-three packages cover the current public Meta Wearables development surface for iOS/Android companions and Meta Ray-Ban Display Web Apps. They keep the native DAT SDKs, their dedicated release-anchored iOS/Android API atlases and parity maps, the 30-row version-pinned API surface register, full-SDK capability auditing, native Display and physical input/sensor semantics, security/attestation and credential boundaries, version/device compatibility, Web Apps, MockDevice/browser simulation, physical glasses, privacy, on-device compliance, transport/reliability, read-only debugging/observability, operational readiness/recovery, shared application architecture, implementation recipes, Developer Center project/release operations, preview/publishing, and source-refresh boundaries explicit. The [machine-readable team manifest](../knowledge-base/skills/packages/meta-wearables-agentic-team/references/team-manifest.yaml) pins the 23 local roles, 32 upstream role handoffs, device-claim gates, and consolidated preflight workflow.

### 20. Meta Wearables agentic team

[Open the package](../knowledge-base/skills/packages/meta-wearables-agentic-team/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-agentic-team.skill)

**Use it for:** coordinating a full Meta Wearables request across route planning, DAT iOS, media, Display, Web Apps, proof, privacy, and source refresh.

**Produces:** one route decision, compatibility table, state/privacy contract, exact team-manifest role receipt, specialist handoffs, evidence ledger, and open gates.

### 21. Meta Wearables route planner

[Open the package](../knowledge-base/skills/packages/meta-wearables-route-planner/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-route-planner.skill)

**Use it for:** resolving native DAT, native Display, Web App, phone fallback, unsupported models, and ambiguous “regular SDK” or “Gen 3” language before implementation.

**Produces:** a source/version/device/capability matrix with rejected alternatives and proof requirements.

### 22. Meta DAT iOS integration

[Open the package](../knowledge-base/skills/packages/meta-dat-ios-integration/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-dat-ios-integration.skill)

**Use it for:** adding or reviewing the official DAT iOS package, registration, permissions, callbacks, session lifecycle, target configuration, and 0.9 migration traps.

**Produces:** a target/configuration inventory, adapter state machine, lifecycle plan, mock plan, and unresolved API questions.

### 23. Meta DAT API atlas

[Open the package](../knowledge-base/skills/packages/meta-dat-api-atlas/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-dat-api-atlas.skill)

**Use it for:** mapping release-anchored public DAT modules, symbols, lifecycle, camera/photo, HFP/A2DP, Display, MockDevice, samples, debugging, MCP, and the DAT/Web Apps boundary.

**Produces:** a confirmed-versus-to-verify API inventory, normalized manifest-row handoff, migration traps, upstream-tool handoff, and build/mock/physical proof gates.

### 24. Meta DAT Android API atlas

[Open the package](../knowledge-base/skills/packages/meta-dat-android-api-atlas/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-dat-android-api-atlas.skill)

**Use it for:** mapping exact Android Maven artifacts, Kotlin/Java symbols, `DatResult`/`Flow` contracts, 0.9 camera/Display/DAM/R8 migrations, Android debugging, MockDevice, and the DAT/Web Apps boundary.

**Produces:** an Android artifact/symbol inventory with normalized manifest rows, source conflicts, compile gates, platform handoff, and separate mock/build/connected/physical/release evidence.

### 25. Meta Wearables full-SDK audit

[Open the package](../knowledge-base/skills/packages/meta-wearables-full-sdk-audit/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-full-sdk-audit.skill)

**Use it for:** auditing “full SDK,” “regular SDK,” all-capability, Gen 2/Gen 3, Meta Glasses, Ray-Ban Display, and iOS/Android parity requests against the product-label/SDK-identity/runtime-capability matrix, four runtime DAT module/artifact lanes plus the iOS test-only MockDevice client, Web Apps runtime, source conflicts, and evidence gates.

**Produces:** a capability matrix, normalized API-row selection, stale/conflicting-source ledger, target dependency audit, phone/web fallback, privacy/release gates, and separate mock/build/connected/physical evidence rows.

### 26. Meta DAT Android integration

[Open the package](../knowledge-base/skills/packages/meta-dat-android-integration/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-dat-android-integration.skill)

**Use it for:** integrating the public DAT Android route with Maven artifacts, Kotlin lifecycle, Manifest/privacy configuration, `DatResult`, `Flow`/`StateFlow`, R8, and Android target proof.

**Produces:** an Android artifact/configuration inventory, 0.9 migration map, cross-platform boundary notes, mock/build/connected/physical proof gates, and unresolved device or release questions.

### 27. Meta DAT camera and audio

[Open the package](../knowledge-base/skills/packages/meta-dat-camera-audio/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-dat-camera-audio.skill)

**Use it for:** camera previews, capture, audio, transcription, media ownership, AVFoundation boundaries, backpressure, consent, and clean cancellation.

**Produces:** a capability/media/privacy contract with separate phone, mock, connected-device, and physical evidence.

### 28. Meta DAT Display

[Open the package](../knowledge-base/skills/packages/meta-dat-display/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-dat-display.skill)

**Use it for:** native glasses Display surfaces, capability checks, compact state, ButtonGroup/input, focus, clear teardown, and phone handoff.

**Produces:** a Display state/input plan, unsupported fallback, mock fixture, and physical test script.

### 29. Meta Wearables Web Apps

[Open the package](../knowledge-base/skills/packages/meta-wearables-web-apps/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-web-apps.skill)

**Use it for:** HTML/CSS/JavaScript experiences delivered to Ray-Ban Display through the official Web App route.

**Produces:** a 600×600 layout/input/performance contract, public HTTPS deployment check, browser-simulator cases, and physical Display test script.

### 30. Meta Wearables device proof

[Open the package](../knowledge-base/skills/packages/meta-wearables-device-proof/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-device-proof.skill)

**Use it for:** freezing a reproducible iOS/Android/Web App target preflight, then deciding what source, target/static, build, MockDevice, browser simulator, connected device, and physical glasses evidence actually establishes before executing the named-task device/release packet.

**Produces:** a redacted target-preflight summary, `PRE-*` task statuses, named-device evidence matrix, and release gate checklist.

### 31. Meta Wearables privacy and publishing

[Open the package](../knowledge-base/skills/packages/meta-wearables-privacy-publishing/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-privacy-publishing.skill)

**Use it for:** camera/audio consent, permissions, data flow, privacy manifests, Meta terms, acceptable use, review metadata, and preview/release gates.

**Produces:** a data-flow matrix, permission/review packet, retention policy, and open legal/product/device gates.

### 32. Meta Wearables on-device compliance

[Open the package](../knowledge-base/skills/packages/meta-wearables-on-device-compliance/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-on-device-compliance.skill)

**Use it for:** enforcing glasses-native versus phone-local versus remote processing claims, raw camera/audio/sensor boundaries, consent, thermal/lifecycle/network fallback, local-first behavior, and runtime compliance across DAT and Web Apps.

**Produces:** an explicit processing/data-flow contract, capability and fallback gates, retention/network policy, and evidence requirements for honest on-device claims.

### 33. Meta Wearables operational readiness

[Open the package](../knowledge-base/skills/packages/meta-wearables-operational-readiness/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-operational-readiness.skill)

**Use it for:** diagnosing companion, firmware, on-glasses DAT-app, Developer Mode, release-channel, update-required, thermal/power, transport, and recovery problems without exposing credentials or overstating evidence.

**Produces:** a frozen compatibility tuple, first-failure classification, bounded recovery action, post-action state, redacted incident packet, and explicit release gate.

### 34. Meta Wearables application architecture

[Open the package](../knowledge-base/skills/packages/meta-wearables-app-architecture/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-app-architecture.skill)

**Use it for:** designing shared product state and policy with separate iOS DAT, Android DAT, native Display, Web App, and phone-fallback adapters.

**Produces:** a module/target boundary map, lifecycle/event/epoch contract, capability ownership, concurrency/resource policy, fallback matrix, test seams, and implementation evidence gates.

### 35. Meta Wearables implementation recipes

[Open the package](../knowledge-base/skills/packages/meta-wearables-implementation-recipes/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-implementation-recipes.skill)

**Use it for:** turning one selected API row and vertical-slice playbook into source-aligned Swift, Kotlin/Java, native Display, or Web App scaffolding without inventing generated signatures.

**Produces:** a target/package tuple, confirmed-versus-to-verify symbol list, adapter skeleton, ownership/epoch/stop order, on-device data-flow contract, typed fallback, test/evidence ladder, and next compile or physical proof task.

### 36. Meta Wearables source refresh

[Open the package](../knowledge-base/skills/packages/meta-wearables-source-refresh/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-source-refresh.skill)

**Use it for:** refreshing DAT iOS/Android, Web Apps, device mappings, terms, API migrations, access gaps, and role-package impact.

**Produces:** a dated registry/freshness update, migration notes, source-to-role map, and next refresh trigger.

### 37. Meta Wearables developer operations

[Open the package](../knowledge-base/skills/packages/meta-wearables-developer-operations/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-developer-operations.skill)

**Use it for:** managing the Developer Center organization/team, project and platform-app identity, product listing, permission rationale, version/build readiness, release channels, tester accounts, telemetry, and recovery boundaries.

**Features:** identity-layer mapping; account/project/version/channel evidence separation; build-status and Major/Minor/Patch checks; tester versus organization-member boundaries; telemetry opt-out handling; destructive-operation stops; and explicit separation of public source, authenticated account state, signed artifact, and physical/release proof.

**Produces:** a redacted Developer Center operations packet with the identity tuple, source and account evidence, version/channel state, tester/telemetry notes, recovery decision, authorization boundary, and unresolved access gates.

### 38. Meta Wearables transport and runtime reliability

[Open the package](../knowledge-base/skills/packages/meta-wearables-transport-reliability/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-transport-reliability.skill)

**Use it for:** auditing Bluetooth control, Wi-Fi/local-network parity, HFP/A2DP audio routes, camera/Display backpressure, route changes, background behavior, thermal/power failures, disconnects, and bounded recovery across DAT iOS and Android.

**Features:** transport-hop and processing-location mapping; iOS local-network/Bonjour and Android Manifest/artifact configuration checks; queue/drop/stop policy; audio-route verification; source-conflict handling for Android Wi-Fi parity; typed thermal/lifecycle fallbacks; and TRN evidence rows that remain separate from mock, physical, signed, and release proof.

**Produces:** a platform transport matrix, reliability state machine, privacy/data-flow boundary, failure/recovery table, and named-target test script with unresolved parity and hardware gates.

### 39. Meta Wearables debugging and observability

[Open the package](../knowledge-base/skills/packages/meta-wearables-debugging-observability/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-debugging-observability.skill)

**Use it for:** diagnosing DAT iOS/Android initialization, registration, permission, device-link, session, camera, audio, Display, transport, and companion-boundary failures, especially when a local DAT Inspector/live-debugging MCP server is available.

**Features:** read-only baseline sequencing; explicit separation of debug-server connection, SDK readiness, registration, permission, device, link, session, capability, and stream failures; iOS/Android state and error maps; narrow event waits; first-failure ownership; typed fallback routing; and redacted diagnostic-bundle rules.

**Produces:** a frozen compatibility tuple, evidence-plane label, first failing state, bounded event/error digest, likely owner, next action, fallback, redaction review, and proof still missing.

### 40. Meta Wearables input and sensors

[Open the package](../knowledge-base/skills/packages/meta-wearables-input-sensors/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-input-sensors.skill)

**Use it for:** routing native DAT Display callbacks, Web App D-pad/EMG/focus and temple behavior, browser motion/orientation/geolocation, phone sensor fallbacks, lifecycle epochs, sensor privacy, and named-target evidence.

**Features:** signal-source and surface separation; exact-symbol and capability gates; source-conflict handling for Web App text/offline/back/gesture/sensor guidance; normalized input events with stale/duplicate/teardown rules; bounded sensor sampling; processing-location and retention review; and mock/browser/connected/physical/release evidence rows.

**Produces:** an input/sensor capability ledger, adapter/event contract, permission and secure-context matrix, privacy/thermal/fallback plan, physical test script, and `INP-*` evidence handoff.

### 41. Meta Wearables security and attestation

[Open the package](../knowledge-base/skills/packages/meta-wearables-security-attestation/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-security-attestation.skill)

**Use it for:** auditing DAT iOS/Android bundle/package identity, Meta AI callback boundaries, Developer Mode versus release-channel attestation, GitHub package and signing credentials, privacy-manifest/App Store gates, Web App origin boundaries, redaction, and honest on-device claims.

**Features:** platform-specific identity tuples; mode/channel and attestation separation; callback validation and stale/duplicate rejection; secure package-token and artifact handling; processing-location handoff; `SEC-*` evidence rows; and explicit Gen 3 and publishing non-claims.

**Produces:** a redacted identity/configuration matrix, callback and credential contract, attestation/release evidence ledger, privacy/on-device handoff, first-failure recovery note, and unresolved account/build/physical/review gates.

### 42. Meta Wearables device compatibility

[Open the package](../knowledge-base/skills/packages/meta-wearables-device-compatibility/SKILL.md) · [Download the artifact](../knowledge-base/skills/dist/meta-wearables-device-compatibility.skill)

**Use it for:** resolving Gen 2/Gen 3, Meta Glasses, Ray-Ban Display, firmware, Meta AI companion, DAT iOS/Android artifact, Web Apps revision, version-dependency, or device-compatibility questions.

**Features:** exact compatibility-tuple capture; product-label versus SDK/runtime identity separation; authenticated version-table access tracking; DAT 0.8→0.9 migration gates; first-party versus community-source classification; firmware-drift diagnosis; explicit Gen 2 treatment; and strict Gen 3/“regular SDK” non-claims.

**Produces:** a version/device matrix, access-gated dependency result, capability-by-capability status, bounded firmware/recovery handoff, `COMP-*` evidence rows, and the next source or physical-device gate.

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
