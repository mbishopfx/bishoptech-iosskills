# Evaluation fixtures for the Apple engineering team skill

Use these fixtures to judge whether an LLM behaves like a precise Apple
engineering team rather than returning generic Swift code. Each run should
record the model/version, source revision, target facts, selected route, files
changed, commands, evidence level, and unsupported claims.

## Fixture A: native Liquid Glass dashboard

**Prompt:** Build a SwiftUI dashboard with a chart, a filter control, a detail
sheet, and an optional on-device explanation. Make it feel native to iOS 26.

**Accept when the response:**

- chooses standard SwiftUI chart/control/navigation routes before custom views;
- treats Liquid Glass as functional grouping and preserves a no-glass fallback;
- includes Dynamic Type, VoiceOver, Reduce Motion/Transparency, localization,
  loading/empty/stale/error states, and chart accessibility;
- makes the AI explanation typed, source-linked, cancellable, stale-safe, and
  subordinate to the chart’s deterministic data;
- separates preview, simulator, physical, performance, and release proof.

**Reject when it:** copies Apple screens, invents a glass treatment as the
primary design, calls a model summary truth, or claims App Store approval.

## Fixture B: protected local intelligence

**Prompt:** Add an on-device feature that summarizes a private local record and
offers a suggested next action.

**Accept when the response:**

- checks Foundation Models/device/model availability and provides deterministic
  fallback;
- excludes secrets and unnecessary personal data from model context;
- uses typed output, source/revision binding, validation, review, cancellation,
  and an explicit commit boundary;
- proposes Swift Testing/evaluation fixtures for empty, stale, malformed,
  unavailable, and adversarial model output;
- states what physical-device and release evidence is still missing.

**Reject when it:** sends private data to a remote service by default, lets the
model mutate domain truth, or treats generated text as a verified action.

## Fixture C: accessory/system surface route

**Prompt:** Connect to a nearby accessory and expose a safe action through an
iOS system surface.

**Accept when the response:**

- chooses the narrowest accessory/discovery/transport/system-surface route;
- separates discovery, pairing/setup, app identity, authorization, transport,
  protocol, and side-effect receipt;
- lists entitlements, usage descriptions, extension/background constraints,
  cancellation/reconnect, privacy, and two-device/accessory proof;
- requires user review and deterministic validation before the action;
- includes a physical-device/system/release evidence matrix.

**Reject when it:** treats a display name or endpoint as trust, makes a
simulator callback physical proof, or starts a side effect from an AI proposal.

## Fixture D: identity and account linking

**Prompt:** Add Sign in with Apple and passkeys, then let a signed-in user link a
second credential.

**Accept when the response:**

- separates Apple code/token exchange from WebAuthn challenge/origin/RP
  verification;
- requires server-owned transactions, nonce/challenge freshness, session
  binding, idempotency, revocation, recovery, and collision handling;
- uses native system controls and distinct create/sign-in/link UI;
- keeps tokens, assertions, private keys, and account IDs out of model context
  and logs;
- tests real domains, physical device/key, credential provider, archive, and
  TestFlight behavior.

**Reject when it:** merges accounts by email/display name, trusts a callback, or
promises recovery without a registered recovery method.

## Fixture E: release audit

**Prompt:** Audit an iOS app before TestFlight submission.

**Accept when the response:**

- inspects the actual target, archive, entitlements, privacy manifest, usage
  descriptions, extension targets, signing, version/build, and metadata;
- reports findings with severity, evidence, exact file/artifact, remediation,
  and residual uncertainty;
- separates source, compile, simulator, physical, system, server, archive,
  TestFlight, App Store, and production claims;
- refuses to infer Apple approval from a successful archive.

**Reject when it:** returns a generic checklist without inspecting the artifact
or calls “build succeeded” release readiness.

## Fixture F: maintenance and source refresh

**Prompt:** An Apple API changed availability in the installed SDK. Update the
route and keep the skill bundle current.

**Accept when the response:**

- reopens official Apple docs and SDK headers;
- identifies affected pages, recipes, packages, availability rows, source
  registry, and tests;
- preserves historical evidence without presenting stale claims as current;
- reruns structural, source, compile, and package validation;
- records a concise receipt and next refresh trigger.

**Reject when it:** patches only an example, copies a stale blog, or leaves
unverified availability claims in the bundle.

## Sources

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [SwiftUI](https://developer.apple.com/documentation/swiftui/)
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Foundation Models](https://developer.apple.com/documentation/foundationmodels)
- [App Intents](https://developer.apple.com/documentation/appintents)
- [Swift Testing](https://developer.apple.com/documentation/testing)
- [XCTest](https://developer.apple.com/documentation/xctest)
- [Testing a release build](https://developer.apple.com/documentation/xcode/testing-a-release-build)
