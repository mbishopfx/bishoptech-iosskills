# Release-ready native design and privacy

## Design objective

Release quality is a design property as well as a build property. A screen that
looks Apple-native in a preview can still fail when the signed build has a
different environment, missing extension, privacy declaration, model asset,
permission state, or Release performance profile.

Use this design graph:

    user task
      -> semantic state and source truth
      -> adaptive SwiftUI/Liquid Glass composition
      -> accessibility/privacy behavior
      -> target and resource membership
      -> signed Release/TestFlight artifact
      -> system/production observation

The goal is not to make the user see signing details. The goal is to make the
product’s visible behavior honest about its availability, privacy, freshness,
model confidence, and release state.

## Design for signed state, not just source state

For every feature, distinguish:

| Product state | Visible behavior | Release question |
| --- | --- | --- |
| Available | Full action and native hierarchy | Is the required target/capability in the artifact? |
| Preparing | Bounded progress and cancel/retry | Does Release handle slow resources and termination? |
| Restricted | Explanation and supported fallback | Is the limitation policy/hardware/account/service? |
| Permission denied | Useful alternate path | Does the signed target include correct usage text? |
| Offline | Local/stale state with age | Does the build use the correct endpoint/cache policy? |
| Model unavailable | Deterministic manual path | Does the physical device/profile support the model route? |
| Stale | Age and refresh action | Does update/migration preserve source revision? |
| Review required | Typed proposal with edit/reject/accept | Can generated output bypass commit policy? |
| System host unavailable | App-owned equivalent or explanation | Is the extension/system target included and authorized? |
| Release mismatch | Safe diagnostics, not a false success | Can build/version/account state be identified? |

Do not hide a missing capability with a decorative glass button that appears
active. The native surface should communicate what the current artifact can do.

## Functional Liquid Glass and distribution

Functional Liquid Glass belongs around app-owned actions and content hierarchy.
The visual treatment must remain subordinate to:

- semantic role and label;
- enabled/disabled state;
- focus and hit target;
- privacy/reduced-effects behavior;
- source freshness;
- confirmation and result;
- accessible alternative;
- target availability.

Before shipping a custom glass group, inspect:

1. the selected SDK and minimum deployment;
2. the app-owned controls inside the group;
3. behavior in light/dark, increased contrast, reduced transparency/effects, and
   large Dynamic Type;
4. VoiceOver/Voice Control/Switch Control and keyboard/pointer paths;
5. Release scroll/animation/hitch behavior on a representative device;
6. whether the visual group accidentally imitates or obscures a system-owned
   widget, notification, control, Handoff prompt, or Apple Intelligence surface.

System-owned surfaces use their documented configuration and host behavior. The
app provides safe state and handoff context; it does not redraw the host.

## Privacy is part of the visual hierarchy

Privacy copy is not a legal footer that can be filled in after design. The user
needs to understand why camera, microphone, location, health, photos, contacts,
network, model input, or account information is needed at the moment of action.

Design a privacy state with:

- the least-privilege request;
- plain-language purpose;
- current authorization/restriction status;
- a useful fallback;
- a settings or recovery path when appropriate;
- no sensitive values in widget, notification, lock-screen, preview, log, or
  TestFlight feedback surface without a deliberate policy.

The privacy manifest describes app or SDK data and required-reason API use. The
visible privacy explanation, manifest, App Store Connect App Privacy answers,
actual collection, and retention behavior must agree.

## Resource and target-aware design

Keep a release map for each surface:

| Surface | Owner | Bundle/resource boundary | Design consequence |
| --- | --- | --- | --- |
| Main app | App target | App bundle | Full feature state and user workflow |
| Widget/control | Extension | Archived/timeline/shared projection | Compact, redacted, host-owned, no live app assumptions |
| Live Activity | Activity extension/system host | Activity state and push/local update route | Time-bounded, stale/end states, locked-device privacy |
| App Intent | App/extension/package target | System invocation process | Typed parameters, auth, confirmation, result |
| App Clip | Clip target | Small invocation surface | Narrow capability, short handoff, no full-app assumption |
| Watch | Watch app/extension | Paired device and transfer | Projection, reachability, queue/dedupe |
| CarPlay | CarPlay scene/target | Vehicle host and category | Attention-safe template hierarchy |
| Share/document/provider | Extension | Host process and file/security scope | Host lifecycle, security-scoped access, no main-app memory |
| On-device AI asset | App/package/resource target | Bundled/downloaded/system model | Readiness, version, privacy, fallback |

The app-owned design should be robust if a system projection is delayed,
redacted, unavailable, or terminated. A system surface can say queued or
accepted; only the owning domain can say completed.

## Versioned release identity in the UI

Support and beta feedback improve when the app can expose a safe diagnostic
identity:

- app version and build string;
- feature/schema/model profile version;
- environment name, never a secret;
- source or record ID only when it is safe;
- a privacy-safe correlation ID for support.

Do not expose signing certificates, provisioning data, API keys, account tokens,
full URLs with credentials, private model prompts, or personal source records.
Use a redacted diagnostics screen or export with explicit user consent.

When a person reports a problem, the team should be able to map the build to an
archive, TestFlight upload, target graph, privacy report, and source revision.

## Design for TestFlight feedback

TestFlight is a user-like distribution step with its own statuses and time
window. Give testers a short path to report:

- the app build and device/OS;
- the screen/task;
- whether the issue occurred after update or first install;
- permission/account/network/model state;
- whether a system surface was involved;
- safe diagnostic context.

For AI features, let testers distinguish:

- generated proposal;
- edited proposal;
- accepted domain record;
- rejected result;
- fallback/manual path.

Do not call a TestFlight response a production result, and do not ask testers to
paste personal prompts or credentials into public issue channels.

## Release-ready AI design

At release time, keep these layers visible:

| Layer | UI | Release gate |
| --- | --- | --- |
| Capability | Available/preparing/unavailable | Device/OS/profile readiness |
| Input | Source and consent | Permission, retention, redaction |
| Generation | Progress/cancel/refusal | Async lifecycle and resource behavior |
| Proposal | Typed fields and changes | Schema, policy, revision validation |
| Review | Edit/reject/accept | Accessibility and explicit action |
| Commit | Saved state | Domain transaction/idempotency |
| Projection | Widget/Handoff/notification | Extension/system target and privacy |
| Evaluation | Quality and safety status | Dataset, criteria, model/profile version |

The Release build must preserve the same review contract. Do not add a
development-only auto-accept path because the real model is slow or because a
TestFlight test used a seeded fixture.

## App Store metadata as product design

The app record, version metadata, screenshots, previews, privacy answers,
accessibility declarations, age rating, export compliance, support URLs, and
review notes describe the product that Apple reviews. They must match the
shipped artifact:

- screenshots must not show unavailable or unshipped behavior;
- metadata must not promise a server/model/device route that lacks fallback;
- accessibility information should reflect tested behavior;
- reviewer notes should explain required login, hardware, or system setup;
- premium or system features should use the correct Apple distribution path;
- release options should match the operational rollout and support capacity.

Marketing copy is an external product claim. It should not be inferred from a
successful local fixture or from an AI-generated preview.

## Privacy review table

| Input | Visible use | Retention | Release check |
| --- | --- | --- | --- |
| Camera/photo | Draft/scan/review | Source/derivative policy | Usage string, manifest, deletion |
| Microphone/audio | Transcription/classification | Recording/transcript policy | Usage string, session route, archive |
| Location | Map/context | Precision/cache policy | Permission, accuracy, background config |
| Health/contact/calendar | User-authorized projection | Sensitive-data policy | Capability, authorization, redaction |
| On-device AI input | Proposal | Local/session/evaluation policy | Model readiness, logs, retention |
| Network data | Sync/server feature | Cache/server policy | ATS/TLS, domains, privacy manifest |
| Account identifiers | Entitlement/sync | Account/deletion policy | App privacy, keychain, server mapping |

The table should point to the actual code/configuration and the signed artifact
inspection. A privacy manifest does not prove that the runtime behaves according
to the declared policy.

## Native release review

Run the following user tasks in the signed Release/TestFlight build:

1. first launch and permission explanation;
2. empty state to first useful result;
3. long content and Dynamic Type;
4. VoiceOver completion of the primary task;
5. reduced motion/effects and increased contrast;
6. offline or service failure;
7. AI unavailable/refusal/review/accept/reject;
8. background or system-surface return;
9. update from the previous version with existing data;
10. sign out/revoke/permission change where relevant;
11. support diagnostics without exposing private data;
12. clean install and update install.

Record what was observed, not what the design intends.

## Sources

- [Adopting Liquid Glass](https://developer.apple.com/documentation/TechnologyOverviews/adopting-liquid-glass)
- [Applying Liquid Glass to custom views](https://developer.apple.com/documentation/swiftui/applying-liquid-glass-to-custom-views)
- [Privacy manifest files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Adding a privacy manifest to your app or third-party SDK](https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk)
- [Describing use of required reason API](https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api)
- [Accessibility fundamentals](https://developer.apple.com/documentation/swiftui/accessibility-fundamentals)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
- [Distributing your app for beta testing and releases](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases)
- [Upload builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds)
- [TestFlight overview](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview)
- [Choose a build to submit](https://developer.apple.com/help/app-store-connect/manage-builds/choose-a-build-to-submit)
- [Submit an app](https://developer.apple.com/help/app-store-connect/manage-submissions-to-app-review/submit-an-app/)
- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels/)
